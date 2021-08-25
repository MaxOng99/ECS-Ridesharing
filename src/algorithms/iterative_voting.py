from hashlib import new
from os import stat
from typing import Callable, Tuple, Set, List
from pyllist.dllist import dllistnode
from models.passenger import Passenger
from models.solution import Solution, TourNodeValue
from algorithms.voting_rules import VotingRules
from copy import deepcopy

class IterativeVoting:
    """Voting algorithm to find sub-optimal Solution

    Attributes
    ----------
    riders: Set[Passenger]
        Set of Passengers for this simulation instance
    graph: igraph.Graph
        Pruned graph that only consists of start and end location of Passengers
    voting_rule: Callable
        Voting rule can either be majority or borda_count
    
    Methods
    ----------
    optimise()
        Constructs n solutions based on the iterative voting procedure,
        and then vote on these solutions
    """

    def __init__(self, riders: Set[Passenger], time_matrix, params) -> None:
        self.riders = riders
        self.time_matrix = time_matrix
        self.voting_rule = self.__voting_rule(params.get("voting_rule"))
    
    def optimise(self):

        candidate_solutions = []
        location_ids = set([source for source, _ in self.time_matrix])

        for location_id in location_ids:
            candidate_solutions.append(self.__initiate_voting(location_id))

        # List of solution ranking function from each Passenger
        solution_ranking_functions = [rider.rank_solutions for rider in self.riders]
        return self.voting_rule(candidate_solutions, solution_ranking_functions)

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return VotingRules.borda_count
        else:
            # TO-DO: Implement majority voting
            pass

    
    def __stations_to_visit(self, waiting, onboard):
        stations = set()

        for rider in waiting:
            stations.add(rider.start_id)
        for rider in onboard:
            stations.add(rider.destination_id)
        
        return stations

    def __initiate_voting(self, start_location: int):
        
        # Initialise Solution object
        new_riders = deepcopy(self.riders)
        new_solution = Solution(new_riders, self.time_matrix)
        first_tour_node_value = TourNodeValue(start_location, 0, 0)
        new_solution.append(first_tour_node_value)

        # Initialise internal state
        waiting = set([rider for rider in new_riders])
        serving = set([rider for rider in new_riders])
        onboard = set()

        # Repeat voting process until all Passengers are served
        while len(serving) > 0:
            current_node = new_solution.tail()
            candidate_locations = self.__stations_to_visit(waiting, onboard)

            # Supply candidate locations AND riders' location ranking function to the voting rule
            location_ranking_functions = [rider.rank_locations for rider in serving]
            voted_location = self.voting_rule(candidate_locations, location_ranking_functions, kwargs={'current_node': current_node})
            
            # Grow the Solution if the voted location is different
            # than the current location
            if voted_location != current_node.value.location_id:
                arrival_time = current_node.value.departure_time + self.time_matrix[(current_node.value.location_id, voted_location)]
                new_node_value = TourNodeValue(voted_location, arrival_time, 0)
                new_node = new_solution.append(new_node_value)
                current_node = new_node

            # Increase the waiting time at the current location if riders
            # vote for the same location id as the previous iteration
            # vote for waiting time
            else:
                current_node.value.update_waiting_time(current_node.value.waiting_time + 10)
            
            # Update service status
            boarded_riders = set()
            served_riders = set()

            for rider in waiting:
                if rider.choose_to_board(current_node):
                    rider.departure_node = current_node
                    current_node.value.add_rider(rider, 'waiting')
                    rider.status = 'onboard'
                    boarded_riders.add(rider)
            
            for rider in onboard:
                if rider.choose_to_disembark(current_node):
                    rider.arrival_node = current_node
                    served_riders.add(rider)
                    current_node.value.add_rider(rider, 'onboard')
                    rider.status = 'served'

            waiting = waiting - boarded_riders
            onboard = onboard - served_riders
            onboard = onboard.union(boarded_riders)
            serving = serving - served_riders

        new_solution.create_rider_schedule()
        return new_solution
