from typing import Callable, Set
from models.agent import IterativeVotingAgent
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

    def __init__(self, agents: Set[IterativeVotingAgent], time_matrix, params) -> None:
        self.agents = agents
        self.time_matrix = time_matrix
        self.voting_rule = self.__voting_rule(params.get("voting_rule"))
    
    def optimise(self):

        candidate_solutions = set()
        location_ids = set([source for source, _ in self.time_matrix])

        for location_id in location_ids:
            candidate_solutions.add(self.__initiate_voting(location_id))

        # List of solution ranking function from each Passenger
        solution_ranking_functions = [agent.rank_solutions for agent in self.agents]
        return self.voting_rule(candidate_solutions, solution_ranking_functions)

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return VotingRules.borda_count
        else:
            # TO-DO: Implement majority voting
            pass

    
    def __stations_to_visit(self, waiting, onboard):
        stations = set()

        for agent in waiting:
            stations.add(agent.rider.start_id)
        for agent in onboard:
            stations.add(agent.rider.destination_id)
        
        return stations

    def __initiate_voting(self, start_location: int):
        
        # Initialise Solution object
        new_agents = deepcopy(self.agents)
        new_solution = Solution(new_agents, self.time_matrix)
        first_tour_node_value = TourNodeValue(start_location, 0, 0)
        new_solution.append(first_tour_node_value)

        # Initialise internal state
        waiting: Set[IterativeVotingAgent] = set()
        serving: Set[IterativeVotingAgent] = set()
        onboard: Set[IterativeVotingAgent] = set()

        for agent in new_agents:
            agent.current_node = new_solution.tail()
            waiting.add(agent)
            serving.add(agent)

        # Repeat voting process until all Passengers are served
        while len(serving) > 0:
            current_node = new_solution.tail()
            candidate_locations = self.__stations_to_visit(waiting, onboard)

            # Supply candidate locations AND riders' location ranking function to the voting rule
            location_ranking_functions = [agent.rank_locations for agent in serving]
            voted_location = self.voting_rule(candidate_locations, location_ranking_functions)
            
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
            boarded_agents = set()
            served_agents = set()

            for agent in waiting:
                agent.current_node = current_node
                if agent.choose_to_board():
                    agent.departure_node = current_node
                    current_node.value.add_rider(agent.rider, 'waiting')
                    agent.status = 'onboard'
                    boarded_agents.add(agent)
            
            for agent in onboard:
                agent.current_node = current_node
                if agent.choose_to_disembark():
                    agent.arrival_node = current_node
                    served_agents.add(agent)
                    current_node.value.add_rider(agent.rider, 'onboard')
                    agent.status = 'served'

            waiting = waiting - boarded_agents
            onboard = onboard - served_agents
            onboard = onboard.union(boarded_agents)
            serving = serving - served_agents
        
        new_solution.create_rider_schedule()
        return new_solution
