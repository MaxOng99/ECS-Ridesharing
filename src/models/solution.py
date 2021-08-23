from typing import Dict, Set
from pyllist import dllist
from utils.info_utils import solution_info

class TourNodeValue:

    def __init__(self, location_id: int, arrival_time: int, waiting_time: int) -> None:
        self.location_id = location_id
        self.arrival_time = arrival_time
        self.waiting_time = waiting_time
        self.departure_time = self.arrival_time + self.waiting_time

        self.pick_up = set()
        self.drop_off = set()

    def add_rider(self, rider, current_status):
        if current_status == 'waiting':
            self.pick_up.add(rider)
        
        elif current_status == 'onboard':
            self.drop_off.add(rider)
    
    def remove_rider(self, rider, current_status):
        if current_status == 'waiting':
            self.pick_up.remove(rider)
        
        elif current_status == 'onboard':
            self.drop_off.remove(rider)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.location_id}, {self.arrival_time}, {self.waiting_time}, P:{self.pick_up}, D:{self.drop_off})"

class Solution:
    def __init__(self, riders: Set['Passenger'], time_matrix):
        self.llist = dllist()
        self.rider_schedule = {"departure": dict(), "arrival": dict()}
        self.riders = sorted(list(riders), key=lambda x: x.id)
        self.time_matrix = time_matrix

    def insert_after(self, ref_node, new_node_value):
        self.check_valid_insert(ref_node, new_node_value.location_id, position='after')
        affected_node = ref_node.next
        new_node = self.llist.insert(new_node_value, after=ref_node)
        self.__updated_affected_node(affected_node)
        return new_node
    
    def insert_before(self, ref_node, new_node_value):
        self.check_valid_insert(ref_node, new_node_value.location_id, position='before')
        affected_node = ref_node
        new_node = self.llist.insert(new_node_value, before=ref_node)
        self.__updated_affected_node(affected_node)
        return new_node

    def check_valid_insert(self, ref_node, location_id, position='before'):
        
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
            raise ValueError("Adjacent node have the same location_id")
        
        # Left node is empty: right_node is the head of linked list.
        # Accept the insertion if inserting before the head node does not cause
        # the new arrival time of the head node to exceed its departure time
        elif not left_node:
            right_node_new_arrival_time = self.time_matrix[(location_id, right_node.value.location_id)]
            if right_node_new_arrival_time > right_node.value.departure_time:
                raise ValueError("New arrival time of next node exceeds its departure time")

        # Right node is empty (left_node is the tail of linked list) There is no right_node
        # to check wehther it's new arrival time exceeds its departure time due to the insert.
        # Therefore, always accept the insertion in this case
        elif not right_node:
            return None

        # Accept insertion if inserting between these two nodes do not cause the new 
        # arrival time of the right_node to exceed its departure time
        else:
            left_to_new_travel_time = self.time_matrix[(left_node.value.location_id, location_id)]
            new_to_right_travel_time = self.time_matrix[(location_id, right_node.value.location_id)]

            new_node_arrival_time = left_node.value.departure_time + left_to_new_travel_time
            right_node_new_arrival_time = new_node_arrival_time + new_to_right_travel_time
            if right_node_new_arrival_time > right_node.value.departure_time:
                raise ValueError("New arrival time of next node exceeds its departure time")
        
        return None

    def remove_node(self, ref_node):
        affected_node = ref_node.next
        self.llist.remove(ref_node)
        self.__updated_affected_node(affected_node)
    
    def create_rider_schedule(self) -> Dict[str, Dict[int, int]]:
        for node in self.llist.iternodes():
            departure_time = node.value.departure_time
            arrival_time = node.value.arrival_time

            for rider in node.value.pick_up:
                self.rider_schedule['departure'][rider.id] = departure_time
            
            for rider in node.value.drop_off:
                self.rider_schedule['arrival'][rider.id] = arrival_time
        
        return self.rider_schedule

    def __updated_affected_node(self, affected_node):
        if affected_node:
            if affected_node.prev:
                affecting_node = affected_node.prev
                source = affecting_node.value.location_id
                target = affected_node.value.location_id

                new_arrival_time = affecting_node.value.departure_time + self.time_matrix[(source, target)]
                new_waiting_time = affected_node.value.departure_time - new_arrival_time

                affected_node.value.arrival_time = new_arrival_time
                affected_node.value.waiting_time = new_waiting_time            
            else:
                affected_node.value.arrival_time = 0
                affected_node.value.waiting_time = affected_node.value.departure_time
        
            if affected_node.value.waiting_time < 0:
                print("bruh dude")

    def __str__(self) -> str:
        return solution_info(self)

    def __repr__(self) -> str:
        return self.__str__()