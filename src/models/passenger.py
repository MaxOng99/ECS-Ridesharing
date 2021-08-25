from hashlib import new
import random
from typing import List

from pyllist.dllist import dllistnode
from models.solution import Solution, TourNodeValue

class Passenger:

    """Model for Passenger

    Attributes
    ----------
    id: int
        Identifier for this Passenger
    start_id: int
        ID of this Passenger's origin station
    destination_id: int
        ID of this Passenger's destination station
    beta: float
        Convenience parameter. Higher beta means that this
        Passenger is less affected by temporal deviation,
        and vice versa
    optimal_departure: int
        Most preferred departure time
    optimal_arrival: int
        Most preferred arrival time
    status: str
        Current status (waiting, onboard, served)
        of this Passenger

    Methods
    ----------
    rank_solutions(solutions: List[Solution])
        Ranks a set of solutions using this Passenger's
        solution utility function

    get_solution_utility(solution: Solution)
        Passenger's solution utility function

    get_utility_by_time(departure_time, arrival_time)
        Obtain rider's utility by directly supplying their
        departure and arrival time

    rank_locations(location_ids: List[int], kwargs)
        Ranks a set of location_ids, given the existing Solution
        obtained from kwargs. Ranking is done according to this
        Passenger's location utility function

    get_location_utility(location_id: int, solution: Solution)
        Passenger's location utility function

    choose_to_board(location_id: int, departure_time: float, solution: Solution)
        Function that decides whether to board the bus
        given the location_id and departure_time

    choose_to_disembark(location_id: int)
        Function that decides whether to disembark the bus given
        the location_id
    """
    def __init__(self, id: int, start: int, destination: int, optimal_departure: int, optimal_arrival: int):
        self.id = id
        self.start_id = start
        self.destination_id = destination
        self.beta = random.uniform(0.1, 1)
        self.board_utility_threshold = 1 - self.beta
        self.optimal_departure = optimal_departure
        self.optimal_arrival = optimal_arrival
        self.status = "waiting"
        self.departure_node = None
        self.arrival_node = None
        self.time_matrix = None

    def rank_solutions(self, solutions: List[Solution], kwargs=None) -> List[Solution]:
        return sorted(solutions, key=lambda sol: (self.get_solution_utility(sol), random.random()), reverse=True)
    
    def get_solution_utility(self, solution: Solution) -> float:
        departure_time = solution.rider_schedule.get("departure").get(self.id)
        arrival_time = solution.rider_schedule.get("arrival").get(self.id)
        return self.__utility_function(departure_time, arrival_time)

    def rank_locations(self, location_ids: List[int], kwargs=None) -> List[int]:
        current_node = kwargs['current_node']
        ranked_locations = sorted(location_ids, key=lambda id: (self.get_utility_by_next_location(current_node, id), random.random()), reverse=True)    
        return ranked_locations

    def get_utility_by_next_location(self, current_node, new_location) -> float:
        new_location_arrival_time = current_node.value.departure_time + self.time_matrix[(current_node.value.location_id, new_location)]
        
        # Make sure node exist in the linked list solution
        if self.status == 'waiting':
            new_location_arrival_time = current_node.value.departure_time + new_location_arrival_time
            departure_time = new_location_arrival_time + self.time_matrix[(new_location, self.start_id)]
            arrival_time = departure_time + self.time_matrix[(self.start_id, self.destination_id)]
            return self.get_utility_by_time(departure_time, arrival_time)
        
        elif self.status == 'onboard':
            departure_time = self.departure_node.value.departure_time
            arrival_time = new_location_arrival_time + self.time_matrix[(self.start_id, self.destination_id)]
            return self.get_utility_by_time(departure_time, arrival_time)

    def get_utility_by_time(self, departure_time: int, arrival_time: int) -> float:
        return self.__utility_function(departure_time, arrival_time)

    def choose_to_board(self, new_node) -> bool:
        next_location = new_node.value.location_id
        prev_node = new_node.prev

        if self.status == "waiting" and next_location == self.start_id:
            # Immediately board if actual departure time exceed the preferred departure time
            if self.optimal_departure - new_node.value.departure_time < 0:
                return True

            # This condition determines whether it is too early to board the bus. 
            # The board_utility_threshold is computed as (1 - beta)
            elif self.get_utility_by_next_location(prev_node, new_node.value.location_id) >= self.board_utility_threshold:
                return True
        
        return False

    def choose_to_disembark(self, node) -> bool:
        if self.status == "onboard" and node.value.location_id == self.destination_id:
            return True

        return False

    def __utility_function(self, departure_time: float, arrival_time: float) -> float:
        utility = (self.beta**(abs(self.optimal_departure - departure_time)) + \
            self.beta**(abs(self.optimal_arrival - arrival_time))) / 2

        return utility

    def __str__(self) -> str:
        return f"P:{self.id}"
    
    def __repr__(self) -> str:
        return self.__str__()
