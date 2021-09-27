from typing import Callable, List, OrderedDict
from models.agent import IterativeVotingAgent
from models.solution import Solution, TourNodeValue
from algorithms.voting_rules import VotingRules
from pyllist import dllistnode
from models.graph import Graph

class IterativeVoting2:
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

    def __init__(self, agents: List[IterativeVotingAgent], graph: Graph, params) -> None:
        self.agents = agents
        self.graph = graph
        self.iterative_voting_rule = self.__voting_rule(params.get("iterative_voting_rule"))
        self.final_voting_rule = self.__voting_rule(params.get("final_voting_rule"))
        self.wait_time = params.get('wait_time')
    
    def optimise(self):

        candidate_solutions = []

        start_locations = OrderedDict()
        for agent in self.agents:
            start_locations[agent.rider.start_id] = None
        
        for start_location in list(start_locations.keys()):
            for agent in self.agents:
                agent.reset_status()              
            solution = self.__initiate_voting(start_location)
            candidate_solutions.append(solution)

        # List of solution ranking function from each Passenger
        solution_ranking_functions = [agent.rank_solutions for agent in self.agents]
        weights = [agent.weight for agent in self.agents]
        return self.final_voting_rule(candidate_solutions, solution_ranking_functions, weights)

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return VotingRules.borda_count
        elif rule == 'popularity':
            return VotingRules.popularity
    
    def __stations_to_visit(self, selected_voters) -> List[int]:
        stations = []

        for voter in selected_voters:
            if voter.status == "waiting":
                stations.append(voter.rider.start_id)
            else:
                stations.append(voter.rider.destination_id)
        return stations

    def __select_voters(self, current_node, serving: List[IterativeVotingAgent]):
        selected_voters = []

        for agent in serving:
            rider = agent.rider
            if agent.status == "waiting":
                location_id = rider.start_id
                travel_time = self.graph.travel_time(current_node.value.location_id, location_id)
                expected_arrival_time = current_node.value.departure_time + travel_time

                if (expected_arrival_time >= rider.optimal_departure - rider.beta*self.wait_time and \
                    expected_arrival_time < rider.optimal_departure + rider.beta*self.wait_time) or \
                        current_node.value.departure_time >= rider.optimal_departure:
                    selected_voters.append(agent)
                
            elif agent.status == "onboard":
                if current_node.value.departure_time >= rider.optimal_arrival:
                    selected_voters.append(agent)

        return selected_voters

    def __initiate_voting(self, start_location: int):

        # Initialise Solution object
        new_solution = Solution(self.agents, self.graph)
        first_tour_node_value = TourNodeValue(start_location, 0, 0)
        new_solution.append(dllistnode(first_tour_node_value))
        
        serving: List[IterativeVotingAgent] = []
        for agent in self.agents:
            agent.current_node = new_solution.tail()
            serving.append(agent)
            
        # Repeat voting process until all Passengers are served
        while len(serving) > 0:

            current_node = new_solution.tail()
            voters = self.__select_voters(current_node, serving)
            
            # If there are no interested voters, increase current time and move to next iteration
            if len(voters) == 0:
                current_node.value.update_waiting_time(current_node.value.waiting_time + self.wait_time)
                continue
            
            candidate_locations = self.__stations_to_visit(voters)
            location_ranking_functions = [agent.rank_locations for agent in voters]
            weights = [agent.weight for agent in voters]
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
                current_node.value.update_waiting_time(current_node.value.waiting_time + self.wait_time)
            
            served_agents = []
            for agent in voters:
                agent.current_node = current_node
                if agent.status == "waiting" and agent.rider.start_id == current_node.value.location_id:
                    agent.departure_node = current_node
                    current_node.value.add_rider(agent.rider, 'waiting')
                    agent.status = "onboard"
                
                elif agent.status == "onboard" and agent.rider.destination_id == current_node.value.location_id:
                    agent.arrival_node = current_node
                    current_node.value.add_rider(agent.rider, 'onboard')
                    agent.status = "served"
                    served_agents.append(agent)

            for agent in served_agents:
                serving.remove(agent)
        
        new_solution.create_rider_schedule()
        return new_solution
