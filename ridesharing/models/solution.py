from collections import Counter
from typing import Dict, Any, Tuple
from dataclasses import dataclass, field

import numpy as np
from prettytable import PrettyTable
from pyllist import dllist
from poverty import gini

from models.passenger import Passenger
from utils.info_utils import solution_info
from models.graph import Graph

@dataclass(frozen=True)
class TourNodeValue:
    location_id: Any
    arrival_time: int
    waiting_time: int
    pick_ups: Tuple[Passenger] = field(default_factory=tuple)
    drop_offs: Tuple[Passenger] = field(default_factory=tuple)

    def __post_init__(self):
        if self.arrival_time < 0:
            raise TourNodeValueError("Arrival time of TourNode cannot be less than 0")
        
        if self.waiting_time < 0:
            raise TourNodeValueError("Waiting time of TourNode cannot be less than 0")
        object.__setattr__(self, 'departure_time', self.arrival_time + self.waiting_time)

## Exception Messages
class TourNodeValueError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class SolutionConstraintError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.location_id}, {self.arrival_time}, {self.waiting_time}, P:{self.pick_up}, D:{self.drop_off})"

class Solution:

    def __init__(self, riders, graph: Graph):
        self.llist = dllist()
        self.graph = graph
        self.rider_utilities = dict()
        self.objectives = dict()
        self.riders = sorted(list(riders), key=lambda rider: rider.id)
        self.rider_schedule = {"departure": dict(), "arrival": dict()}

    def check_constraint(self, complete=False) -> bool:
        pick_ups = []
        drop_offs = []

        for node in self.llist.first.iternext():
            if node.next:
                # Check time matrix consistency
                arrival_time = node.value.departure_time + self.graph.travel_time(
                    node.value.location_id,
                    node.next.value.location_id
                )
                if not arrival_time == node.next.value.arrival_time:
                    raise SolutionConstraintError("Inconsistent time matrix")

                # Check location constraint
                if node.value.location_id == node.next.value.location_id:
                    raise SolutionConstraintError("Adjacent location constraint not satisfied")

            pick_ups.extend(node.value.pick_ups)
            drop_offs.extend(node.value.drop_offs)
            
        # Check rider allocation duplication
    
        pick_up_counter = Counter(pick_ups)
        drop_off_counter = Counter(drop_offs)
        invalid_pick_ups = list(filter(lambda counter: counter > 1, pick_up_counter.values()))
        invalid_drop_offs = list(filter(lambda counter: counter > 1, drop_off_counter.values()))
        if invalid_drop_offs or invalid_pick_ups:
            raise SolutionConstraintError("Riders are being allocated twice")

    def calculate_objectives(self):
        utils = []
        for rider in self.riders:
            departure_time = self.rider_schedule.get("departure").get(rider.id)
            arrival_time = self.rider_schedule.get("arrival").get(rider.id)
            utils.append(rider.utility(departure_time, arrival_time))

        self.objectives['avg_utility'] = np.mean(utils)
        self.objectives['utilitarian'] = sum(utils)
        self.objectives['egalitarian'] = min(utils)
        self.objectives['proportionality'] = np.std(utils)
        self.objectives['gini_index'] = gini(utils)
        self.objectives['percentile'] = np.percentile(utils, 20)

    def create_rider_schedule(self) -> Dict[str, Dict[int, int]]:
        time_taken = 0
        current_node = self.llist.first
        
        for node in self.llist.iternodes():
            location_i = current_node.value.location_id
            location_j = node.value.location_id
            travel_time = self.graph.travel_time(location_i, location_j)
            time_taken += travel_time

            departure_time = node.value.departure_time
            arrival_time = node.value.arrival_time

            for rider in node.value.pick_ups:
                self.rider_schedule['departure'][rider.id] = departure_time
            
            for rider in node.value.drop_offs:
                self.rider_schedule['arrival'][rider.id] = arrival_time
            
            current_node = node
        return self.rider_schedule

    def __str__(self) -> str:
        schedule = PrettyTable()
        schedule.field_names = ['Visit Order', 'Location ID', 'Pick Ups', 'Drop Offs', 'Arrival', 'Wait Time', 'Departure Time']
    
        for index, tour_node in enumerate(self.llist.iternodes()):
            row_data = [index, tour_node.value.location_id, list(tour_node.value.pick_ups), list(tour_node.value.drop_offs), tour_node.value.arrival_time, tour_node.value.waiting_time, tour_node.value.departure_time]
            schedule.add_row(row_data)
    
        return "\n".join(['Schedule', f'{schedule.get_string()}']) 

    def __repr__(self) -> str:
        return self.__str__()
