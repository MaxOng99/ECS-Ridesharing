from typing import Dict, Set
from pyllist import dllist, dllistnode
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
    
    def update_waiting_time(self, new_waiting_time):
        self.waiting_time = new_waiting_time
        self.departure_time = self.arrival_time + new_waiting_time

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.location_id}, {self.arrival_time}, {self.waiting_time}, P:{self.pick_up}, D:{self.drop_off})"

class Solution:

    def __init__(self, agents: Set["Agent"], time_matrix):
        self.llist = dllist()
        self.rider_schedule = {"departure": dict(), "arrival": dict()} # nullify
        self.agents = sorted(list(agents), key=lambda x: x.rider.id)
        self.time_matrix = time_matrix

    def head(self):
        return self.llist.first
    
    def tail(self):
        return self.llist.last

    def iterator(self, start_node: dllistnode=None):
        if start_node:
            return start_node.iternext()
        else:
            return self.llist.iternodes()

    def insert_after(self, ref_node, new_node: dllistnode):
        if not self.__valid_insert(new_node.value, ref_node, position='after'):
            raise Exception("Invalid Insert")

        affected_node = ref_node.next
        new_node = self.llist.insert(new_node, after=ref_node)
        self.__update_after_insert(affected_node)
        return new_node

    def insert_before(self, ref_node, new_node: dllistnode):
        if not self.__valid_insert(new_node.value, ref_node, position='before'):
            raise Exception("Invalid Insert")

        affected_node = ref_node
        new_node = self.llist.insert(new_node, before=ref_node)
        self.__update_after_insert(affected_node)
        return new_node
    
    def append(self, new_node: dllistnode):
        if not self.__valid_insert(new_node.value, self.tail(), position='after'):
            raise Exception("Invalid Insert")

        new_node = self.llist.append(new_node)
        return new_node
    
    def create_rider_schedule(self) -> Dict[str, Dict[int, int]]:
        for node in self.llist.iternodes():
            departure_time = node.value.departure_time
            arrival_time = node.value.arrival_time

            for rider in node.value.pick_up:
                self.rider_schedule['departure'][rider.id] = departure_time
            
            for rider in node.value.drop_off:
                self.rider_schedule['arrival'][rider.id] = arrival_time
        
        return self.rider_schedule

    def __valid_insert(self, new_node_value, ref_node, position=None):

        if not self.tail():
            return True 
        
        if ref_node:
            new_location = new_node_value.location_id
            arrival_time = new_node_value.arrival_time

            if position == 'before':
                left_node = ref_node.prev
                right_node = ref_node
            elif position == 'after':
                left_node = ref_node
                right_node = ref_node.next

            # If either nodes have the same location_id, reject insert
            if left_node and left_node.value.location_id == new_location or \
                right_node and right_node.value.location_id == new_location:
                return False
            
            elif left_node:
                left_node_location = left_node.value.location_id
                left_node_depart_time = left_node.value.departure_time
                travel_time = self.time_matrix[(left_node_location, new_location)]
                if left_node_depart_time + travel_time != arrival_time:
                    return False
        return True

    def __update_after_insert(self, affected_node):
        if affected_node:
            for node in affected_node.iternext():
                prev = node.prev
                travel_time = self.time_matrix[(prev.value.location_id, node.value.location_id)]
                arrival_time = prev.value.departure_time + travel_time

                if arrival_time > affected_node.value.departure_time:
                    affected_node.value.departure_time = arrival_time
                    affected_node.value.arrival_time = arrival_time
                    affected_node.value.waiting_time = 0
                else:
                    new_waiting_time = affected_node.value.departure_time - arrival_time
                    affected_node.value.arrival_time = arrival_time
                    affected_node.value.waiting_time = new_waiting_time
                    break
                
    def __str__(self) -> str:
        return solution_info(self)

    def __repr__(self) -> str:
        return self.__str__()
