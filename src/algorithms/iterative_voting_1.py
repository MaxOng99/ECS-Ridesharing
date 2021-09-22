from typing import Callable, Set, List
from models.agent import IterativeVotingAgent
from models.solution import Solution, TourNodeValue
from algorithms.voting_rules import VotingRules
from pyllist import dllistnode
from models.graph import Graph

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

    def __init__(self, agents: Set[IterativeVotingAgent], graph: Graph, params) -> None:
        self.agents = agents
        self.graph = graph
        self.iterative_voting_rule = self.__voting_rule(params.get("iterative_voting_rule"))
        self.final_voting_rule = self.__voting_rule(params.get("final_voting_rule"))

    
    def optimise(self):

        candidate_solutions = []
        location_ids = set([source for source, _ in self.graph.time_matrix])

        for location_id in location_ids:
            candidate_solutions.append(self.__initiate_voting(location_id))

        # List of solution ranking function from each Passenger
        solution_ranking_functions = [agent.rank_solutions for agent in self.agents]
        weights = [agent.weight for agent in self.agents]
        return self.final_voting_rule(candidate_solutions, solution_ranking_functions, weights)

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return VotingRules.borda_count
        elif rule == 'majority':
            return VotingRules.majority
    
    def __stations_to_visit(self, waiting, onboard) -> List[int]:
        stations = []

        for agent in waiting:
            stations.append(agent.rider.start_id)
        for agent in onboard:
            stations.append(agent.rider.destination_id)
        
        return stations

    def __initiate_voting(self, start_location: int):
        
        # Initialise Solution object
        for agent in self.agents:
            agent.reset_status()
        new_solution = Solution(self.agents, self.graph)
        first_tour_node_value = TourNodeValue(start_location, 0, 0)
        new_solution.append(dllistnode(first_tour_node_value))

        # Initialise internal state
        waiting: List[IterativeVotingAgent] = []
        serving: List[IterativeVotingAgent] = []
        onboard: List[IterativeVotingAgent] = []

        for agent in self.agents:
            agent.current_node = new_solution.tail()
            waiting.append(agent)
            serving.append(agent)

        # Repeat voting process until all Passengers are served
        while len(serving) > 0:
            current_node = new_solution.tail()
            candidate_locations = self.__stations_to_visit(waiting, onboard)

            # Supply candidate locations AND riders' location ranking function to the voting rule
            location_ranking_functions = [agent.rank_locations for agent in serving]
            weights = [agent.weight for agent in serving]
            voted_location = self.iterative_voting_rule(candidate_locations, location_ranking_functions, weights)
            
            # Grow the Solution if the voted location is different
            # than the current location
            if voted_location != current_node.value.location_id:
                arrival_time = current_node.value.departure_time + self.graph.travel_time(current_node.value.location_id, voted_location)
                new_node_value = TourNodeValue(voted_location, arrival_time, 0)
                new_node = new_solution.append(dllistnode(new_node_value))
                current_node = new_node

            # Increase the waiting time at the current location if riders
            # vote for the same location id as the previous iteration
            # vote for waiting time
            else:
                current_node.value.update_waiting_time(current_node.value.waiting_time + 10)
            
            # Update service status
            boarded_agents = []
            served_agents = []

            for agent in waiting:
                agent.current_node = current_node
                if agent.choose_to_board():
                    agent.departure_node = current_node
                    current_node.value.add_rider(agent.rider, 'waiting')
                    agent.status = 'onboard'
                    boarded_agents.append(agent)
            
            for agent in onboard:
                agent.current_node = current_node
                if agent.choose_to_disembark():
                    agent.arrival_node = current_node
                    served_agents.append(agent)
                    current_node.value.add_rider(agent.rider, 'onboard')
                    agent.status = 'served'

            waiting = [agent for agent in waiting if agent not in boarded_agents]
            onboard = [agent for agent in onboard if agent not in served_agents]
            onboard.extend(boarded_agents)
            serving = [agent for agent in serving if agent not in served_agents]
        
        new_solution.create_rider_schedule()
        return new_solution