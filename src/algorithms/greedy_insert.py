from algorithms.voting_rules import VotingRules
from utils.info_utils import strategy_info
from pyllist.dllist import dllistnode
from models.solution import Solution, TourNodeValue
from typing import List
import numpy as np
from models.graph import Graph
from models.agent import GreedyInsertAgent

class GreedyInsert:

    """Greedy algorithm to find sub-optimal Solution

    Attributes
    ----------
    riders: List[Passenger]
        List of Passengers for this simulation instance
    time_matrix: Dict[Tuple[int, int], int]
        Keys consist of location_id tuples, and values 
        consist of the travel time between the 2 location_ids
    params: Dict
        Additional options for the algorithm in the form of key-value pairs
        - 'iterations': <an integer>
        - <Potential parameters, to be added>

    Methods
    ----------
    optimise()
        Constructs n solutions based on the greedy insert procedure
    """
    def __init__(self, agents: List[GreedyInsertAgent], graph: Graph, params) -> None:
        self.agents = agents
        self.params = params
        self.graph = graph
        self.voting_rule = self.__get_voting_rule(params['final_voting_rule'])

    def __filter_by_location(self, unallocated, solution: Solution):

        if len(solution.existing_locations) == len(self.graph.locations):
            return unallocated[0]

        else:
            for agent in unallocated:
                location_id = agent.rider.start_id if agent.status == "waiting" else agent.rider.destination_id
                if not location_id in solution.existing_locations:
                    return agent

        return unallocated[0]

    def optimise(self) -> Solution:

        solutions = []
        for _ in range(self.params['iterations']):
            np.random.shuffle(self.agents)
            start_agent = self.agents[0]

            # Create new Solution
            solution = self.__initialise_new_solution(start_agent)
            # Assign n other riders
            unallocated = [agent for agent in self.agents[1:]]

            while len(unallocated) != 0:
                agent = self.__filter_by_location(unallocated, solution)
                self.__best_allocation(agent, solution)
                unallocated.remove(agent)

            solution.create_rider_schedule()
            solution.calculate_objectives()
            solutions.append(solution)
        if not self.voting_rule:
            if self.params['objective'] == "gini_index":
                return min(solutions, key=lambda sol: sol.objectives['gini_index'])
            else:
                return max(solutions, key=lambda sol: sol.objectives[self.params['objective']])

        else:
            ranking_functions = [agent.rank_solutions for agent in self.agents]
            voted_solution = self.voting_rule(solutions, ranking_functions)
            return voted_solution

    def __get_voting_rule(self, voting_rule: str):
        if voting_rule == 'popularity':
            return VotingRules.popularity
        
        elif voting_rule == 'borda_count':
            return VotingRules.borda_count
        
        return None
        
    def __initialise_new_solution(self, start_agent):
        solution = Solution(self.agents, self.graph)

        # Create TourNodeValue for departure
        start_rider = start_agent.rider
        depart_node_value = TourNodeValue(start_rider.start_id, 0, start_rider.optimal_departure)
        depart_node_value.add_rider(start_rider, 'waiting')
        
        # Create TourNodeValue for arrival
        depart_to_arrival_travel_time = self.graph.travel_time(start_rider.start_id, start_rider.destination_id)
        arrival_time = start_rider.optimal_departure + depart_to_arrival_travel_time
        waiting_time = start_rider.optimal_arrival - arrival_time
        arrive_node_value = TourNodeValue(start_rider.destination_id, arrival_time, waiting_time)
        arrive_node_value.add_rider(start_rider, 'onboard')

        depart_node = solution.llist.append(dllistnode(depart_node_value))
        arrival_node = solution.llist.append(dllistnode(arrive_node_value))

        start_agent.departure_node = depart_node
        start_agent.arrival_node = arrival_node

        return solution

    def __best_allocation(self, agent: GreedyInsertAgent, solution: Solution):

        best_depart_strat = None
        for node in solution.iterator():
            departure_strategy = self.__create_strategy(agent, node, 'waiting', insert_position='before')
            if departure_strategy:
                if not best_depart_strat:
                    best_depart_strat = departure_strategy

                current_depart_time = best_depart_strat.strat['allocated_node'].value.departure_time
                new_depart_time = departure_strategy.strat['allocated_node'].value.departure_time

                if agent.rider.utility(new_depart_time, None) >= agent.rider.utility(current_depart_time, None):
                    best_depart_strat = departure_strategy
                else:
                    if agent.rider.optimal_departure - departure_strategy.strat['allocated_node'].value.departure_time < 0 and \
                        departure_strategy.strat['allocated_node'].value.location_id == agent.rider.start_id:
                        break

            # Special case at tail of linked list: Attempt to create an 
            # additional departure strategy by inserting after the current node
            if node.next == None:
                departure_strategy = self.__create_strategy(agent, node, 'waiting', insert_position='after')
                if not best_depart_strat:
                    best_depart_strat = departure_strategy

                current_depart_time = best_depart_strat.strat['allocated_node'].value.departure_time
                new_depart_time = departure_strategy.strat['allocated_node'].value.departure_time

                if agent.rider.utility(new_depart_time, None) >= agent.rider.utility(current_depart_time, None):
                    best_depart_strat = departure_strategy
                else:
                    if agent.rider.optimal_departure - departure_strategy.strat['allocated_node'].value.departure_time < 0 and \
                        departure_strategy.strat['allocated_node'].value.location_id == agent.rider.start_id:
                        break

        depart_node = best_depart_strat.apply(solution)
        agent.departure_node = depart_node

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
        
        arrival_node = curr_best_strat.apply(solution)
        agent.arrival_node = arrival_node

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
