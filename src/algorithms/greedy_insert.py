from utils.info_utils import strategy_info
from pyllist.dllist import dllist, dllistnode
from models.solution import Solution, TourNodeValue
from models.passenger import Passenger
from typing import List
import random

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
    def __init__(self, passengers: List[Passenger], time_matrix, params) -> None:
        self.passengers = passengers
        self.params = params
        self.time_matrix = time_matrix

    def optimise(self) -> Solution:

        solutions = []
        for _ in range(self.params["iterations"]):
            random.shuffle(self.passengers)
            start_rider = random.choice(self.passengers)
            
            # Create new Solution
            solution = self.__initialise_new_solution(start_rider)

            # Assign n other riders
            other_riders = set(self.passengers) - set([start_rider])

            for rider in other_riders:
                self.__best_allocation(rider, solution)

            solution.update_rider_schedule()
            solutions.append(solution)

        # Vote on these solutions
        return solutions[0]
    
    def __initialise_new_solution(self, start_rider):
        solution = Solution(self.passengers)

        # Create TourNodeValue for departure
        depart_node_value = TourNodeValue(start_rider.start_id, 0, start_rider.optimal_departure)
        depart_node_value.pick_up.add(start_rider)
        
        # Create TourNodeValue for arrival
        depart_to_arrival_travel_time = self.time_matrix[(start_rider.start_id, start_rider.destination_id)]
        arrival_time = start_rider.optimal_departure + depart_to_arrival_travel_time
        waiting_time = start_rider.optimal_arrival - arrival_time
        arrive_node_value = TourNodeValue(start_rider.destination_id, arrival_time, waiting_time)
        arrive_node_value.drop_off.add(start_rider)

        solution.llist.append(dllistnode(depart_node_value))
        solution.llist.append(dllistnode(arrive_node_value))

        return solution

    def __best_allocation(self, rider: Passenger, solution: Solution):

        strategy_util_pairs = dict()

        # Create Departure strategies
        departure_strategies = []
        for node in solution.llist.iternodes():

            # Departure strategy can be allocating this rider to current node,
            # or creating a new node, and insert it before the current node
            departure_strategy = self.__create_departure_strategy(rider, node, insert_position='before')
            if departure_strategy:
                departure_strategies.append(departure_strategy)
            
            # Special case at tail of linked list: Attempt to create an 
            # additional departure strategy by inserting after the current node
            if node.next == None:
                departure_strategy = self.__create_departure_strategy(rider, node, insert_position='after')
                if departure_strategy:
                    departure_strategies.append(departure_strategy)
        
        # Create Arrival strategies for each departure strategy
        for departure_strategy in departure_strategies:

            # Apply departure strategy to linked list
            departure_strategy.apply_strategy(solution.llist)
            depart_node = departure_strategy.allocated_node

            # Only consider nodes after depart_node
            for node in depart_node.iternext():

                # Arrival Strategy can be allocating this rider to current node
                # or create a new node, and insert it after current node.
                arrival_strategy = self.__create_arrival_strategy(rider, node, depart_node, insert_position='after')
                if arrival_strategy:

                    # Apply arrival strategy to llist
                    arrival_strategy.apply_strategy(solution.llist)

                    # Record utility for this strategy pair
                    departure_time = departure_strategy.allocated_node.value.departure_time
                    arrival_time = arrival_strategy.allocated_node.value.arrival_time
                    strategy_util_pairs[(departure_strategy, arrival_strategy)] = \
                        rider.get_utility_by_time(departure_time, arrival_time)

                    # Revert to previous llist state (before applying arrival strategy)
                    arrival_strategy.revert_strategy(solution.llist)
            
            # Revert to previous llist state (before applying departure strategy)
            departure_strategy.revert_strategy(solution.llist)

        best_depart_strat, best_arrive_strat = max(strategy_util_pairs, key=strategy_util_pairs.get)
        best_depart_strat.apply_strategy(solution.llist)
        arrival_strat = ArrivalStrategy(best_arrive_strat.strat, best_depart_strat.allocated_node)
        arrival_strat.apply_strategy(solution.llist)

    def __create_departure_strategy(self, rider, ref_node, insert_position='before'):
        if ref_node.value.location_id == rider.start_id:
            strategy_details = self.__stay_at_node(rider, ref_node, status='waiting')
            return DepartStrategy(strategy_details)

        elif self.__valid_insert(ref_node, rider.start_id, position=insert_position):
            strategy_details = self.__insert_at_node(rider, ref_node, position=insert_position, status='waiting')
            return DepartStrategy(strategy_details)
        
        else:
            return None

    def __create_arrival_strategy(self, rider, ref_node, depart_node, insert_position='after'):
        if ref_node.value.location_id == rider.destination_id:
            strategy_details = self.__stay_at_node(rider, ref_node, status='onboard')
            return ArrivalStrategy(strategy_details, depart_node)
        
        elif self.__valid_insert(ref_node, rider.destination_id, position=insert_position):
            strategy_details = self.__insert_at_node(rider, ref_node, position=insert_position, status='onboard')
            return ArrivalStrategy(strategy_details, depart_node)
        else:
            return None

    def __stay_at_node(self, rider, ref_node, status='waiting'):
        new_tour_node_value = self.__duplicate_value(ref_node.value)

        if status == 'waiting':
            new_tour_node_value.pick_up.add(rider)
        else:
            new_tour_node_value.drop_off.add(rider)
        
        strategy_details = {
            'action': 'stay',
            'ref_node': ref_node,
            'ref_node_old_value': ref_node.value,
            'ref_node_new_value': new_tour_node_value
        }
        
        return strategy_details

    def __duplicate_value(self, tour_node_value):
        location_id = tour_node_value.location_id
        arrival_time = tour_node_value.arrival_time
        wait_time = tour_node_value.waiting_time
        duplicated_val = TourNodeValue(location_id, arrival_time, wait_time)

        duplicated_val.pick_up = duplicated_val.pick_up.union(tour_node_value.pick_up)
        duplicated_val.drop_off = duplicated_val.drop_off.union(tour_node_value.drop_off)
        return duplicated_val

    def __insert_at_node(self, rider, ref_node, position='before', status='waiting'):

        next_node = ref_node if position == 'before' else ref_node.next
        new_node_value = self.__create_new_value_by_insertion(rider, ref_node, position, status)
        next_node_new_value = self.__update_affected_node(new_node_value, next_node)

        strategy_details = {
            'action': f'insert_{position}',
            'ref_node': ref_node,
            'ref_node_old_value': ref_node.value,
            'new_node_value': new_node_value,
            'next_node': next_node,
            'next_node_old_value': None if not next_node else next_node.value,
            'next_node_new_value': None if not next_node else next_node_new_value
        }

        return strategy_details

    def __create_new_value_by_insertion(self, rider, ref_node, insert_position, status):

        if status == 'waiting':
            time_features = self.__calculate_time_features(ref_node, rider.start_id, rider.optimal_departure, insert_position)
            new_node_value = TourNodeValue(rider.start_id, time_features['arrival'], time_features['wait'])
            new_node_value.pick_up.add(rider)

        elif status == 'onboard':
            time_features = self.__calculate_time_features(ref_node, rider.destination_id, rider.optimal_arrival, insert_position)
            new_node_value = TourNodeValue(rider.destination_id, time_features['arrival'], time_features['wait'])
            new_node_value.drop_off.add(rider)
        
        return new_node_value

    def __update_affected_node(self, new_node_value, next_node):
        """Updates the immediate node to the right of a newly inserted node"""
        if next_node:

            # Calculate new arrival and waiting time of next_node
            # due to inserting new_node_value before next_node
            new_arrival_time = new_node_value.departure_time + self.time_matrix[(new_node_value.location_id, next_node.value.location_id)]
            new_waiting_time = next_node.value.departure_time - new_arrival_time

            updated_next_node = self.__duplicate_value(next_node.value)
            updated_next_node.waiting_time = new_waiting_time
            updated_next_node.arrival_time = new_arrival_time
            updated_next_node.departure_time = new_waiting_time + new_arrival_time

            return updated_next_node
        
        return None



    def __calculate_time_features(self, ref_node, new_node_location_id, preferred_time, insert_position):
        """Calculates the arrival and waiting time for the new node to be inserted"""

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
            wait_time = min(allowable_waiting_time, preferred_time)

            # arrival time is 0, since insertion happens before the head node
            return {'arrival': 0, 'wait': wait_time}
        
        # Inserting after the tail node. Here, left_node is the tail node
        elif not right_node:

            # Waiting time is 
            new_node_arrival_time = left_node.value.departure_time + self.time_matrix[(left_node.value.location_id, new_node_location_id)]
            wait_time = max(preferred_time - new_node_arrival_time, 0)
            return {'arrival': new_node_arrival_time, 'wait': wait_time}
        
        else:
            prev_to_new_travel_time = self.time_matrix[(left_node.value.location_id, new_node_location_id)]
            new_to_next_travel_time = self.time_matrix[(new_node_location_id, right_node.value.location_id)]

            new_node_arrival_time = left_node.value.departure_time + prev_to_new_travel_time
            next_node_arrival_time = new_node_arrival_time + new_to_next_travel_time

            allowable_delay = right_node.value.departure_time - next_node_arrival_time
            wait_time = min(allowable_delay, max(preferred_time - new_node_arrival_time, 0))
            return {'arrival': new_node_arrival_time, 'wait': wait_time}

    def __valid_insert(self, ref_node, location_id, position='before'):
        
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
            right_node_new_arrival_time = self.time_matrix[(location_id, right_node.value.location_id)]
            if right_node_new_arrival_time <= right_node.value.departure_time:
                return True
            else:
                return False
        
        # Right node is empty (left_node is the tail of linked list) There is no right_node
        # to check wehther it's new arrival time exceeds its departure time due to the insert.
        # Therefore, always accept the insertion in this case
        elif not right_node:
            return True
        
        # Accept insertion if inserting between these two nodes do not cause the new 
        # arrival time of the right_node to exceed its departure time
        else:
            left_to_new_travel_time = self.time_matrix[(left_node.value.location_id, location_id)]
            new_to_right_travel_time = self.time_matrix[(location_id, right_node.value.location_id)]

            new_node_arrival_time = left_node.value.departure_time + left_to_new_travel_time
            right_node_new_arrival_time = new_node_arrival_time + new_to_right_travel_time
            if right_node_new_arrival_time <= right_node.value.departure_time:
                return True
            else:
                return False

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

    def apply_strategy(self, llist: dllist):
        """Carry out this strategy (wait/insert), affecting the state of llist. If there are more strategies
        to check, ensure that revert_strategy is called afterwards to revert the changes, so that other
        strategies can be correctly applied with an untouched state of the linked list.

        """
        strat = self.strat
        # Either wait at the current node, or insert a new one
        if strat['action'] == 'stay':
            strat['ref_node'].value = strat['ref_node_new_value']
            self.allocated_node = strat['ref_node']

        elif strat['action'] == 'insert_before':
            self.allocated_node = llist.insert(strat['new_node_value'], before=strat['ref_node'])
            if strat['next_node']:
                strat['next_node'].value = strat['next_node_new_value']

        elif strat['action'] == 'insert_after':
            self.allocated_node = llist.insert(strat['new_node_value'], after=strat['ref_node'])
            if strat['next_node']:
                strat['next_node'].value = strat['next_node_new_value']

    def revert_strategy(self, llist: dllist):
        """This function should only be called after apply_strategy() is called. This reverts
        the linked list back to its original state before this strategy is applied in order
        to ensure that the changes made by this strategy does not affect other strategies being tested.
        """
        strat = self.strat

        if strat['action'] == 'stay':
            strat['ref_node'].value = strat['ref_node_old_value']
        
        elif strat['action'] == 'insert_before' or \
            strat['action'] == 'insert_after':
            llist.remove(self.allocated_node)

            if strat['next_node']:
                strat['next_node'].value = strat['next_node_old_value']
    
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