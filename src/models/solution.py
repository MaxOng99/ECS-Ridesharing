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

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.location_id}, {self.arrival_time}, {self.waiting_time}, P:{self.pick_up}, D:{self.drop_off})"

class Solution:
    def __init__(self, riders: Set['Passenger']):
        self.llist = dllist()
        self.rider_schedule = {"departure": dict(), "arrival": dict()}
        self.riders = sorted(list(riders), key=lambda x: x.id)
    
    def update_rider_schedule(self) -> Dict[str, Dict[int, int]]:
        for node in self.llist.iternodes():
            departure_time = node.value.departure_time
            arrival_time = node.value.arrival_time

            for rider in node.value.pick_up:
                self.rider_schedule['departure'][rider.id] = departure_time
            
            for rider in node.value.drop_off:
                self.rider_schedule['arrival'][rider.id] = arrival_time
        
        return self.rider_schedule

    def __str__(self) -> str:
        return solution_info(self)

    def __repr__(self) -> str:
        return self.__str__()