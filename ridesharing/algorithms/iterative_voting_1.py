from collections import defaultdict
from dataclasses import replace
from typing import Callable, List

from models.solution import Solution, TourNodeValue
from models.graph import Graph
from models.passenger import Passenger
from algorithms.voting_system import BordaCount, Popularity
from models.utility_functions import location_utility

class IterativeVoting1:
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

    def __init__(self, riders: List[Passenger], graph: Graph, params) -> None:
        self.riders= riders
        self.graph = graph
        self.iterative_voting_rule = self.__voting_rule(params.get("iterative_voting_rule"))
        self.final_voting_rule = self.__voting_rule(params.get("final_voting_rule"))
        self.params = params

    
    def optimise(self):

        candidate_solutions = []
        location_ids = set([source for source, _ in self.graph.time_matrix])
        return self.__initiate_voting(list(location_ids)[0])

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return BordaCount
        elif rule == 'popularity':
            return Popularity

    def __choose_to_board(self, rider, current_node):
        node_val = current_node.value
        additional_info = {
            "graph": self.graph,
            "current_node": current_node,
            "rider_depart_node_dict": {}
        }
        if rider.optimal_departure - node_val.departure_time < 0:
            return True
        elif location_utility(rider, node_val.location_id, additional_info=additional_info) >= \
            1 - rider.beta:
            return True
        
        return False

    def __initiate_voting(self, start_location: int):

        rider_depart_node_dict = dict()
        new_solution = Solution(self.riders, self.graph)
        first_tour_node_value = TourNodeValue(start_location, 0, 0)
        new_solution.llist.append(first_tour_node_value)

        # Initialise internal state
        to_pick_up = self.riders[:]
        to_drop_off = self.riders[:]
        
        # Repeat voting process until all Passengers are served
        while len(to_pick_up + to_drop_off) > 0:
            current_node = new_solution.llist.last

            candidate_rider_map = defaultdict(list)
            for rider in to_pick_up:
                candidate_rider_map[rider.start_id].append(rider)
            for rider in to_drop_off:
                candidate_rider_map[rider.destination_id].append(rider)
            
            candidate_locations = list(candidate_rider_map.keys())
            
            # Supply candidate locations AND riders' location ranking function to the voting rule
            additional_info = {
                "current_node": current_node,
                "graph": self.graph,
                "rider_depart_node_dict": rider_depart_node_dict
            }
            vote_system = self.iterative_voting_rule(to_pick_up + to_drop_off, candidate_locations, additional_info=additional_info)
            voted_location = vote_system.winner
            winner_riders = set(candidate_rider_map[voted_location])

            # Grow the Solution if the voted location is different
            # than the current location
            if voted_location != current_node.value.location_id:
                arrival_time = current_node.value.departure_time + self.graph.travel_time(current_node.value.location_id, voted_location)
                new_node_value = TourNodeValue(voted_location, arrival_time, 0)
                new_node = new_solution.llist.append(new_node_value)
                current_node = new_node

            # Increase the waiting time at the current location if riders
            # vote for the same location id as the previous iteration
            # vote for waiting time
            else:
                val = current_node.value
                updated_val = replace(val, waiting_time=val.waiting_time + 5)
                current_node.value = updated_val
            
            # Update service status
            on_ground_winners = \
                set(filter(
                    lambda rider: rider_depart_node_dict.get(rider, None) is None,
                    winner_riders
                ))
            on_board_winners = \
                winner_riders.difference(on_ground_winners)
            
            ##### BOARD THRESHOLD #####
            for rider in on_ground_winners:
                current_val = current_node.value
                if self.__choose_to_board(rider, current_node):
                    updated_val = replace(current_val, pick_ups=current_val.pick_ups + tuple([rider]))
                    current_node.value = updated_val
                    to_pick_up.remove(rider)
                    rider_depart_node_dict[rider] = current_node

            for rider in on_board_winners:
                val = current_node.value
                updated_val = replace(val, drop_offs=val.drop_offs + tuple([rider]))
                current_node.value = updated_val
                to_drop_off.remove(rider)
            
        #     new_solution.check_constraint()

        # new_solution.check_constraint(complete=True)
        new_solution.create_rider_schedule()
        new_solution.calculate_objectives()

        return new_solution