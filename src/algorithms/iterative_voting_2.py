from typing import Callable, List
from models.agent import IterativeVotingAgent
from models.solution import Solution, TourNodeValue
from algorithms.voting_rules import VotingRules
from pyllist import dllistnode
from models.graph import Graph
import numpy as np

from utils.info_utils import strategy_info

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
        self.params = params
        self.iterative_voting_rule = self.__voting_rule(params.get("iterative_voting_rule"))
        self.final_voting_rule = self.__voting_rule(params.get("final_voting_rule"))
        self.wait_time = params.get('wait_time')
    
    def __filter_by_location(self, unallocated, solution: Solution):
        agents = []
        for agent in unallocated:
            location_id = agent.rider.start_id if agent.status == "waiting" else agent.rider.destination_id
            if not location_id in solution.existing_locations:
                agents.append(agent)

        if len(agents) == 0:
            return unallocated
        else:
            return agents

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return VotingRules.borda_count
        elif rule == 'popularity':
            return VotingRules.popularity

    def optimise(self):
        
        np.random.shuffle(self.agents)

        # initialise solution
        solution = Solution(self.agents, self.graph)
        candidate_nodes = []
        funcs = []
        candidate_voter_map = dict()

        for voter in self.agents:
            node = TourNodeValue(voter.rider.start_id, voter.rider.optimal_departure, 0)
            candidate_nodes.append(node)
            funcs.append(voter.rank_tour_nodes)
            candidate_voter_map[node] = voter

        best_candidate = self.iterative_voting_rule(candidate_nodes, funcs)
        winner = candidate_voter_map[best_candidate]
        best_candidate.add_rider(winner.rider, "waiting")
        solution.append(dllistnode(best_candidate))
        winner.departure_node = solution.tail()
        winner.status = "onboard"

        unallocated = [agent for agent in self.agents]

        while len(unallocated) != 0:
            agents = self.__filter_by_location(unallocated, solution)
            agent = self.iterative_voting(agents, solution)
            if agent.status == "served":
                unallocated.remove(agent)

        solution.create_rider_schedule()
        solution.calculate_objectives()

        return solution
        
    def iterative_voting(self, voters, solution: Solution):
        strats = []
        candidate_nodes = []
        funcs = []
        strat_dict = dict()

        for voter in voters:
            strat = self.__best_allocation(voter, solution)
            candidate = strat.strat['allocated_node'].value

            funcs.append(voter.rank_tour_nodes)
            strats.append(strat)
            candidate_nodes.append(candidate)
            strat_dict[candidate] = strat
        
        best_candidate = self.iterative_voting_rule(candidate_nodes, funcs)
        best_strategy = strat_dict[best_candidate]
        agent = best_strategy.strat['agent']

        if agent.status == "waiting":
            agent.status = "onboard"
            depart_node = best_strategy.apply(solution)
            agent.departure_node = depart_node
            
        elif agent.status == "onboard":
            agent.status = "served"
            arrival_node = best_strategy.apply(solution)
            agent.arrival_node = arrival_node

        return agent


    def __best_allocation(self, agent, solution: Solution):
        
        if agent.status == "waiting":
            current_best_strat = None
            for node in solution.iterator():
                departure_strategy = self.__create_strategy(agent, node, 'waiting', insert_position='before')

                if departure_strategy:
                    if not current_best_strat:
                        current_best_strat = departure_strategy

                    current_depart_time = current_best_strat.strat['allocated_node'].value.departure_time
                    new_depart_time = departure_strategy.strat['allocated_node'].value.departure_time

                    if agent.rider.utility(new_depart_time, None) >= agent.rider.utility(current_depart_time, None):
                        current_best_strat = departure_strategy
                    else:
                        if agent.rider.optimal_departure - departure_strategy.strat['allocated_node'].value.departure_time < 0 and \
                            departure_strategy.strat['allocated_node'].value.location_id == agent.rider.start_id:
                            break

                # Special case at tail of linked list: Attempt to create an 
                # additional departure strategy by inserting after the current node
                if node.next == None:
                    departure_strategy = self.__create_strategy(agent, node, 'waiting', insert_position='after')
                    if not current_best_strat:
                        current_best_strat = departure_strategy
                    current_depart_time = current_best_strat.strat['allocated_node'].value.departure_time
                    new_depart_time = departure_strategy.strat['allocated_node'].value.departure_time

                    if agent.rider.utility(new_depart_time, None) > agent.rider.utility(current_depart_time, None):
                        current_best_strat = departure_strategy
                    else:
                        if agent.rider.optimal_departure - departure_strategy.strat['allocated_node'].value.departure_time < 0 and \
                            departure_strategy.strat['allocated_node'].value.location_id == agent.rider.start_id:
                            break
                    
            return current_best_strat

        else:
            curr_best_strat = None
            for node in solution.iterator(start_node=agent.departure_node):
                arrival_strategy = self.__create_strategy(agent, node, 'onboard', insert_position='after')
                if arrival_strategy:
                    if not curr_best_strat:
                        curr_best_strat = arrival_strategy

                    curr_arrival_time = curr_best_strat.strat['allocated_node'].value.arrival_time
                    new_arrival_time = arrival_strategy.strat['allocated_node'].value.arrival_time
                    
                    if agent.rider.utility(agent.departure_node.value.departure_time, new_arrival_time) >= \
                        agent.rider.utility(agent.departure_node.value.departure_time, curr_arrival_time):
                        curr_best_strat = arrival_strategy
                    else:
                        if agent.rider.optimal_arrival - arrival_strategy.strat['allocated_node'].value.arrival_time < 0 and \
                            arrival_strategy.strat['allocated_node'].value.location_id == agent.rider.destination_id:
                            break

            return curr_best_strat

    def __create_strategy(self, agent, ref_node, status, insert_position=None):
        rider = agent.rider
        location_id = rider.start_id if status == 'waiting' else rider.destination_id

        if self.__check_valid_insert(ref_node, location_id, position=insert_position):
            strategy = self.__insert_at_node(agent, ref_node, status, position=insert_position)

        elif ref_node.value.location_id == location_id:
            strategy = self.__stay_at_node(agent, ref_node, status)
            return strategy
        else:
            strategy = None        
        return strategy

    def __stay_at_node(self, agent, ref_node, current_status):
        strategy_details = {
            'action': 'stay',
            'agent': agent,
            'current_status': current_status,
            'allocated_node': ref_node
        }
        return Strategy(strategy_details)

    def __insert_at_node(self, agent, ref_node, current_status, position='before'):
        new_node_value = self.__create_new_value_by_insertion(agent.rider, ref_node, position, current_status)
        strategy_details = {
            'action': f'insert_{position}',
            'agent': agent,
            'ref_node': ref_node,
            'current_status': current_status,
            'allocated_node': dllistnode(new_node_value)
        }
        return Strategy(strategy_details)
    def __check_valid_insert(self, ref_node, location_id, position='before'):
        
        # Verify adjacent nodes, before attempting to insert between them
        if position == 'before':
            left_node = ref_node.prev
            right_node = ref_node
        else:
            left_node = ref_node
            right_node = ref_node.next
        
        # If either nodes have the same location_id, reject insert
        if left_node and left_node.value.location_id == location_id or \
            right_node and right_node.value.location_id == location_id:
            return False
        
        # Left node is empty: right_node is the head of linked list.
        # Accept the insertion if inserting before the head node does not cause
        # the new arrival time of the head node to exceed its departure time
        elif not left_node:
            right_node_new_arrival_time = self.graph.travel_time(location_id, right_node.value.location_id)
            if right_node_new_arrival_time > right_node.value.departure_time:
                return False

        # Right node is empty (left_node is the tail of linked list) There is no right_node
        # to check wehther it's new arrival time exceeds its departure time due to the insert.
        # Therefore, always accept the insertion in this case
        elif not right_node:
            return True

        # Accept insertion if inserting between these two nodes do not cause the new 
        # arrival time of the right_node to exceed its departure time
        else:
            left_to_new_travel_time = self.graph.travel_time(left_node.value.location_id, location_id)
            new_to_right_travel_time = self.graph.travel_time(location_id, right_node.value.location_id)

            new_node_arrival_time = left_node.value.departure_time + left_to_new_travel_time
            right_node_new_arrival_time = new_node_arrival_time + new_to_right_travel_time
            if right_node_new_arrival_time > right_node.value.departure_time:
                return False
        
        return True
        
    def __create_new_value_by_insertion(self, rider, ref_node, insert_position, status):
        new_node_location_id = rider.start_id if status == 'waiting' else rider.destination_id
        preferred_time = rider.optimal_departure if status == 'waiting' else rider.optimal_arrival

        # Verify adjacent nodes, before calculating time features for the new TourNodeValue
        if insert_position == 'before':
            left_node = ref_node.prev
            right_node = ref_node
        else:
            left_node = ref_node
            right_node = ref_node.next
        
        # Inserting before the start node. Here, right_node is the start node
        if not left_node:
            right_node_new_arrival_time = self.graph.travel_time(new_node_location_id, right_node.value.location_id)

            # Waiting time for new TourNodeValue is dependent on the remainding waiting time
            # for right_node after performing the insert before right_node.
            allowable_waiting_time = right_node.value.departure_time - right_node_new_arrival_time
            new_node_wait_time = min(allowable_waiting_time, preferred_time)
            
            # arrival time is 0, since insertion happens before the head node
            new_node_arrival_time = 0
        
        # Inserting after the tail node. Here, left_node is the tail node
        elif not right_node:

            # Waiting time is 
            new_node_arrival_time = left_node.value.departure_time + self.graph.travel_time(left_node.value.location_id, new_node_location_id)
            new_node_wait_time = max(preferred_time - new_node_arrival_time, 0)
        
        else:
            prev_to_new_travel_time = self.graph.travel_time(left_node.value.location_id, new_node_location_id)
            new_to_next_travel_time = self.graph.travel_time(new_node_location_id, right_node.value.location_id)

            new_node_arrival_time = left_node.value.departure_time + prev_to_new_travel_time
            next_node_arrival_time = new_node_arrival_time + new_to_next_travel_time

            allowable_delay = right_node.value.departure_time - next_node_arrival_time
            new_node_wait_time = min(allowable_delay, max(preferred_time - new_node_arrival_time, 0))

        new_node_value = TourNodeValue(new_node_location_id, new_node_arrival_time, new_node_wait_time)
        new_node_value.add_rider(rider, status)
        
        return new_node_value



# HELPER CLASS
class Strategy:
    """Helper class that records the previous state of the linked list before applying
    this strategy (wait/insert). This form of state management is helpful to find the best
    strategy, before applying it.

    Attributes
    ----------

    strategy_dictionary: Dict[str, object]
        Key value pairs consisting of affected nodes due to applying
        this strategy, as well as their previous and updated state. Additionally,
        any new TourNode objects will also be recorded (if this is an insert
        strategy).

    allocated_node: dllistnode(TourNode)
        The allocated departure/arrival node for the current Passenger
        after applying this strategy.

    """
    def __init__(self, strategy_dictionary) -> None:
        self.strat = strategy_dictionary

    def apply(self, solution: Solution):
        """Carry out this strategy (wait/insert), affecting the state of llist.
        """
        strat = self.strat
        # Either wait at the current node, or insert a new one
        if strat['action'] == 'stay':
            strat['allocated_node'].value.add_rider(strat['agent'].rider, strat['current_status'])
            return strat['allocated_node']

        elif strat['action'] == 'insert_before':
            new_node = solution.insert_before(strat['ref_node'], strat['allocated_node'])
            return new_node
        elif strat['action'] == 'insert_after':
            return solution.insert_after(strat['ref_node'], strat['allocated_node'])

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return strategy_info(self)
        




    # def optimise(self):

    #     candidate_solutions = []

    #     start_locations = OrderedDict()
    #     for agent in self.agents:
    #         start_locations[agent.rider.start_id] = None
        
    #     for start_location in list(start_locations.keys()):
    #         for agent in self.agents:
    #             agent.reset_status()              
    #         solution = self.__initiate_voting(start_location)
    #         candidate_solutions.append(solution)

    #     # List of solution ranking function from each Passenger
    #     solution_ranking_functions = [agent.rank_solutions for agent in self.agents]
    #     weights = [agent.weight for agent in self.agents]
    #     return self.final_voting_rule(candidate_solutions, solution_ranking_functions, weights)

    # def __voting_rule(self, rule: str) -> Callable:
    #     if rule == "borda_count":
    #         return VotingRules.borda_count
    #     elif rule == 'popularity':
    #         return VotingRules.popularity
    
    # def __stations_to_visit(self, selected_voters) -> List[int]:
    #     stations = []

    #     for voter in selected_voters:
    #         if voter.status == "waiting":
    #             stations.append(voter.rider.start_id)
    #         else:
    #             stations.append(voter.rider.destination_id)
    #     return stations

    # def __select_voters(self, current_node, serving: List[IterativeVotingAgent]):
    #     selected_voters = []

    #     for agent in serving:
    #         rider = agent.rider
    #         if agent.status == "waiting":
    #             location_id = rider.start_id
    #             travel_time = self.graph.travel_time(current_node.value.location_id, location_id)
    #             expected_arrival_time = current_node.value.departure_time + travel_time

    #             if (expected_arrival_time >= rider.optimal_departure - self.graph.avg_travel_time):
    #                 selected_voters.append(agent)
                
    #         elif agent.status == "onboard":
    #             if current_node.value.departure_time >= rider.optimal_arrival:
    #                 selected_voters.append(agent)

    #     return selected_voters

    # def __initiate_voting(self, start_location: int):

        # # Initialise Solution object
        # new_solution = Solution(self.agents, self.graph)
        # first_tour_node_value = TourNodeValue(start_location, 0, 0)
        # new_solution.append(dllistnode(first_tour_node_value))
        
        # serving: List[IterativeVotingAgent] = []
        # for agent in self.agents:
        #     agent.current_node = new_solution.tail()
        #     serving.append(agent)
            
        # # Repeat voting process until all Passengers are served
        # while len(serving) > 0:

        #     current_node = new_solution.tail()
        #     voters = self.__select_voters(current_node, serving)
            
        #     # If there are no interested voters, increase current time and move to next iteration
        #     if len(voters) == 0:
        #         current_node.value.update_waiting_time(current_node.value.waiting_time + self.wait_time)
        #         continue
            
        #     candidate_locations = self.__stations_to_visit(voters)
        #     location_ranking_functions = [agent.rank_locations for agent in voters]
        #     weights = [agent.weight for agent in voters]
        #     voted_location = self.iterative_voting_rule(candidate_locations, location_ranking_functions, weights)
            
        #     # Grow the Solution if the voted location is different
        #     # than the current location
        #     if voted_location != current_node.value.location_id:
        #         arrival_time = current_node.value.departure_time + self.graph.travel_time(current_node.value.location_id, voted_location)
        #         new_node_value = TourNodeValue(voted_location, arrival_time, 0)
        #         new_node = new_solution.append(dllistnode(new_node_value))
        #         current_node = new_node

        #     # Increase the waiting time at the current location if riders
        #     # vote for the same location id as the previous iteration
        #     # vote for waiting time
        #     else:
        #         current_node.value.update_waiting_time(current_node.value.waiting_time + self.wait_time)
            
        #     served_agents = []
        #     for agent in voters:
        #         agent.current_node = current_node
        #         if agent.status == "waiting" and agent.rider.start_id == current_node.value.location_id:
        #             agent.departure_node = current_node
        #             current_node.value.add_rider(agent.rider, 'waiting')
        #             agent.status = "onboard"
                
        #         elif agent.status == "onboard" and agent.rider.destination_id == current_node.value.location_id:
        #             agent.arrival_node = current_node
        #             current_node.value.add_rider(agent.rider, 'onboard')
        #             agent.status = "served"
        #             served_agents.append(agent)

        #     for agent in served_agents:
        #         serving.remove(agent)
        
        # new_solution.create_rider_schedule()
        # new_solution.calculate_objectives()
        # return new_solution
