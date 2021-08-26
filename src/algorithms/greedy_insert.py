from utils.info_utils import strategy_info
from pyllist.dllist import dllistnode
from models.solution import Solution, TourNodeValue
from models.passenger import Passenger
from typing import List
import random
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
    def __init__(self, agents: List[GreedyInsertAgent], time_matrix, params) -> None:
        self.agents = agents
        self.params = params
        self.time_matrix = time_matrix

    def optimise(self) -> Solution:

        solutions = []
        for _ in range(1):
            random.shuffle(self.agents)
            start_agent = random.choice(self.agents)
            
            # Create new Solution
            solution = self.__initialise_new_solution(start_agent)
            # Assign n other riders
            other_agents = set(self.agents) - set([start_agent])
            for agent in other_agents:
                self.__best_allocation(agent, solution)

            solution.create_rider_schedule()
            solutions.append(solution)

        # Vote on these solutions
        return solutions[0]
    
    def __initialise_new_solution(self, start_agent):
        solution = Solution(self.agents, self.time_matrix)

        # Create TourNodeValue for departure
        start_rider = start_agent.rider
        depart_node_value = TourNodeValue(start_rider.start_id, 0, start_rider.optimal_departure)
        depart_node_value.add_rider(start_rider, 'waiting')
        
        # Create TourNodeValue for arrival
        depart_to_arrival_travel_time = self.time_matrix[(start_rider.start_id, start_rider.destination_id)]
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

        strategy_util_pairs = dict()

        # Create Departure strategies
        departure_strategies = []
        for node in solution.llist.iternodes():

            # Departure strategy can be allocating this rider to current node,
            # or creating a new node, and insert it before the current node
            departure_strategy = self.__create_departure_strategy(agent, node, solution, insert_position='before')
            if departure_strategy:
                departure_strategies.append(departure_strategy)
            
            # Special case at tail of linked list: Attempt to create an 
            # additional departure strategy by inserting after the current node
            if node.next == None:
                departure_strategy = self.__create_departure_strategy(agent, node, solution, insert_position='after')
                if departure_strategy:
                    departure_strategies.append(departure_strategy)
        
        # Create Arrival strategies for each departure strategy
        for departure_strategy in departure_strategies:

            # Apply departure strategy to linked list
            departure_strategy.apply_strategy(solution)
            depart_node = departure_strategy.allocated_node

            # Only consider nodes after depart_node
            for node in depart_node.iternext():

                # Arrival Strategy can be allocating this rider to current node
                # or create a new node, and insert it after current node.
                arrival_strategy = self.__create_arrival_strategy(agent, node, depart_node, solution, insert_position='after')
                if arrival_strategy:

                    # Apply arrival strategy to llist
                    arrival_strategy.apply_strategy(solution)

                    # Record utility for this strategy pair
                    departure_time = departure_strategy.allocated_node.value.departure_time
                    arrival_time = arrival_strategy.allocated_node.value.arrival_time
                    strategy_util_pairs[(departure_strategy, arrival_strategy)] = \
                        agent.rider.utility(departure_time, arrival_time)

                    # Revert to previous llist state (before applying arrival strategy)
                    arrival_strategy.revert_strategy(solution)
            
            # Revert to previous llist state (before applying departure strategy)
            departure_strategy.revert_strategy(solution)

        best_depart_strat, best_arrive_strat = max(strategy_util_pairs, key=strategy_util_pairs.get)
        best_depart_strat.apply_strategy(solution, commit=True)
        arrival_strat = ArrivalStrategy(best_arrive_strat.strat, best_depart_strat.allocated_node)
        arrival_strat.apply_strategy(solution, commit=True)

    def __create_departure_strategy(self, agent, ref_node, solution: Solution, insert_position='before'):
        rider = agent.rider
        try:
            solution.check_valid_insert(ref_node=ref_node, location_id=rider.start_id, position=insert_position)
            strategy_details = strategy_details = self.__insert_at_node(agent, ref_node, 'waiting', position=insert_position)
            return DepartStrategy(strategy_details)
        except:
            if ref_node.value.location_id == rider.start_id:
                strategy_details = self.__stay_at_node(agent, ref_node, 'waiting')
                return DepartStrategy(strategy_details)
            else:
                return None

    def __create_arrival_strategy(self, agent, ref_node, depart_node, solution, insert_position='after'):
        rider = agent.rider
        try:
            solution.check_valid_insert(ref_node, rider.destination_id, position=insert_position)
            strategy_details = self.__insert_at_node(agent, ref_node, 'onboard', position=insert_position)
            return ArrivalStrategy(strategy_details, depart_node)
        except:
            if ref_node.value.location_id == rider.destination_id:
                strategy_details = self.__stay_at_node(agent, ref_node, 'onboard')
                return ArrivalStrategy(strategy_details, depart_node)
            else:
                return None

    def __stay_at_node(self, agent, ref_node, current_status):
        strategy_details = {
            'action': 'stay',
            'agent': agent,
            'current_status': current_status,
            'ref_node': ref_node
        }
        return strategy_details

    def __insert_at_node(self, agent, ref_node, current_status, position='before'):
        new_node_value = self.__create_new_value_by_insertion(agent.rider, ref_node, position, current_status)
        strategy_details = {
            'action': f'insert_{position}',
            'agent': agent,
            'ref_node': ref_node,
            'current_status': current_status,
            'new_node_value': new_node_value
        }
        return strategy_details

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
            right_node_new_arrival_time = self.time_matrix[(new_node_location_id, right_node.value.location_id)]

            # Waiting time for new TourNodeValue is dependent on the remainding waiting time
            # for right_node after performing the insert before right_node.
            allowable_waiting_time = right_node.value.departure_time - right_node_new_arrival_time
            new_node_wait_time = min(allowable_waiting_time, preferred_time)
            
            # arrival time is 0, since insertion happens before the head node
            new_node_arrival_time = 0
        
        # Inserting after the tail node. Here, left_node is the tail node
        elif not right_node:

            # Waiting time is 
            new_node_arrival_time = left_node.value.departure_time + self.time_matrix[(left_node.value.location_id, new_node_location_id)]
            new_node_wait_time = max(preferred_time - new_node_arrival_time, 0)
        
        else:
            prev_to_new_travel_time = self.time_matrix[(left_node.value.location_id, new_node_location_id)]
            new_to_next_travel_time = self.time_matrix[(new_node_location_id, right_node.value.location_id)]

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
    this strategy (wait/insert), as well as the updated state after applying this strategy.
    This form of state management is requried to ensure that the linked list is at the correct,
    original state before testing each combination of departure and arrival strategies.

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
        self.allocated_node: dllistnode = None

    def apply_strategy(self, solution: Solution, commit=False):
        """Carry out this strategy (wait/insert), affecting the state of llist. If there are more strategies
        to check, ensure that revert_strategy is called afterwards to revert the changes, so that other
        strategies can be correctly applied with an untouched state of the linked list.

        """
        strat = self.strat
        # Either wait at the current node, or insert a new one
        if strat['action'] == 'stay':
            strat['ref_node'].value.add_rider(strat['agent'].rider, strat['current_status'])
            self.allocated_node = strat['ref_node']

        elif strat['action'] == 'insert_before':
            self.allocated_node = solution.insert_before(ref_node=strat['ref_node'], new_node_value=strat['new_node_value'])

        elif strat['action'] == 'insert_after':
            self.allocated_node = solution.insert_after(ref_node=strat['ref_node'], new_node_value=strat['new_node_value'])

        if commit:
            if strat['current_status'] == 'waiting':
                strat['agent'].departure_node = self.allocated_node
            else:
                strat['agent'].arrival_node = self.allocated_node

    def revert_strategy(self, solution: Solution):
        """This function should only be called after apply_strategy() is called. This reverts
        the linked list back to its original state before this strategy is applied in order
        to ensure that the changes made by this strategy does not affect other strategies being tested.
        """
        strat = self.strat

        if strat['action'] == 'stay':
            strat['ref_node'].value.remove_rider(strat['agent'].rider, strat['current_status'])

        elif strat['action'] == 'insert_before' or \
            strat['action'] == 'insert_after':

            solution.remove_node(self.allocated_node)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        strategy_info(self)

class DepartStrategy(Strategy):
    pass

class ArrivalStrategy(Strategy):
    def __init__(self, strategy_dictionary, depart_node) -> None:
        super().__init__(strategy_dictionary)
        if self.strat and depart_node and \
            self.strat['ref_node'].value == depart_node.value:
            self.strat['ref_node'] = depart_node