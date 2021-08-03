import random
from typing import List
from models.solution import Solution
from utils.graph_utils import travel_time

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
    optimal_departure: float
        Most preferred departure time
    optimal_arrival: float
        Most preferred arrival time
    status: float
        Current status (waiting, onboard, served)
        of this Passenger

    Methods
    ----------
    rank_solutions(solutions: List[Solution])
        Ranks a set of solutions using this Passenger's
        solution utility function

    get_solution_utility(solution: Solution)
        Passenger's solution utility function

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
    def __init__(self, id: int, start: int, destination: int, optimal_departure: float, optimal_arrival: float):

        self.id = id
        self.start_id = start
        self.destination_id = destination
        self.beta = random.uniform(0.1, 1)
        self.board_utility_threshold = 1 - self.beta
        self.optimal_departure = optimal_departure
        self.optimal_arrival = optimal_arrival
        self.status = "waiting"

    def rank_solutions(self, solutions: List[Solution], kwargs=None) -> List[Solution]:
        return sorted(solutions, key=lambda sol: self.get_solution_utility(sol), reverse=True)
    
    def get_solution_utility(self, solution: Solution) -> float:
        departure_time = solution.rider_schedule.get("departure").get(self.id)
        arrival_time = solution.rider_schedule.get("arrival").get(self.id)
        return self.__utility_function(departure_time, arrival_time)

    def rank_locations(self, location_ids: List[int], kwargs=None) -> List[int]:

        # Passengers rank locations based on existing solution
        solution = kwargs["solution"]
        utilities = [self.get_location_utility(location_id, solution) for location_id in location_ids]

        # In case of ties, this Passenger's start_id or destination_id attribute gets
        # ranked first. Passengers are assumed to be indifferent to the other locations
        if all(utility == utilities[0]  for utility in utilities):
            if self.status == "waiting":
                best_location = self.start_id
            elif self.status == "onboard":
                best_location = self.destination_id
            best_location_index = location_ids.index(best_location)
            location_ids[0], location_ids[best_location_index] = best_location, location_ids[0]
            return location_ids
        
        else:
            return sorted(location_ids, key=lambda location_id: self.get_location_utility(location_id, solution), reverse=True)

    def get_location_utility(self, location_id: int, solution: Solution) -> float:
        # Computes the utility for a location_id, given the existing Solution

        # The utility of any location l_i when this Passenger is not boarded is calculated as follows:
        # 1. Assume that after reaching l_i from the current location, the bus immediately goes to start_id
        # 2. Assume that after reaching start_id, the bus immediately goes to destination_id
        # 3. The corresponding departure and arrival times are assumed to be the actual departure and arrival times
        # 4. The assumed departure and arrival times will be used as arguments to the unique utility function
        # 5. The obtained utility will be the utility for l_i

        # The utility of any location l_i when this Passenger is onboard is calculated as follows:
        # 1. Assume that after reaching l_i from the current location, the bus immediately goes to destination_id
        # 2. The corresponding arrival time at destination_id is assumed to be the actual arrival time at destination_id
        # 3. Use the real departure time, and the assumed arrival time as arguments to the unique utility function
        # 4. The obtained utility will be the utility for l_i

        graph = solution.graph
        current_node = solution.get_current_node()

        if self.status == "waiting":
            timestamp_at_l_i = current_node.departure_time + travel_time(current_node.location_id, location_id, graph)
            timestamp_at_origin = timestamp_at_l_i + travel_time(location_id, self.start_id, graph)
            timestamp_at_destination = timestamp_at_origin + travel_time(self.start_id, self.destination_id, graph)
            return self.__utility_function(timestamp_at_origin, timestamp_at_destination)

        elif self.status == "onboard":
            timestamp_at_origin = solution.rider_schedule.get("departure").get(self.id)
            timestamp_at_destination = current_node.departure_time + travel_time(location_id, self.destination_id, graph)
            return self.__utility_function(timestamp_at_origin, timestamp_at_destination)

    def choose_to_board(self, location_id: int, departure_time: float, solution: Solution) -> bool:
        if self.status == "waiting" and location_id == self.start_id:

            # Immediately board if actual departure time exceed the preferred departure time
            if self.optimal_departure - departure_time < 0:
                return True

            # This condition determines whether it is too early to board the bus
            elif self.get_location_utility(location_id, solution) >= self.board_utility_threshold:
                return True

        return False

    def choose_to_disembark(self, location_id: int) -> bool:
        if self.status == "onboard" and location_id == self.destination_id:
            return True
        return False

    def __utility_function(self, departure_time: float, arrival_time: float) -> float:
        utility = (self.beta**(abs(self.optimal_departure - departure_time)) + \
            self.beta**(abs(self.optimal_arrival - arrival_time))) / 2

        return utility

    def __str__(self) -> str:
        return f"Passenger {self.id}: {{Start: {self.start_id} | End: {self.destination_id}}}"
    
    def __repr__(self) -> str:
        return self.__str__()
