from models.passenger import Passenger
from models.solution import Solution
from typing import List, Set

class Agent:
    def __init__(self, rider: Passenger, time_matrix) -> None:
        self.rider: Passenger = rider
        self.time_matrix = time_matrix
        self.status = 'waiting'
        self.departure_node = None
        self.arrival_node = None
        
    def rank_solutions(self, solutions: Set[Solution]) -> List[Solution]:
        return sorted(solutions, key=lambda sol: self.get_solution_utility(sol), reverse=True)
    
    def get_solution_utility(self, solution: Solution):
        departure_time = solution.rider_schedule.get("departure").get(self.rider.id)
        arrival_time = solution.rider_schedule.get("arrival").get(self.rider.id)
        return self.rider.utility(departure_time, arrival_time)

class IterativeVotingAgent(Agent):
    def __init__(self, rider: Passenger, time_matrix) -> None:
        super().__init__(rider, time_matrix)
        self.board_threshold = self.__board_threshold()
        self.current_node = None
    
    def __board_threshold(self):
        board_threshold = 1 - self.rider.beta
        return board_threshold

    def rank_locations(self, location_ids: Set[int]) -> List[int]:
        return sorted(location_ids, key=lambda id: self.location_utility(id), reverse=True)    
        # return ranked_locations

    def location_utility(self, new_location) -> float:
        
        rider_start = self.rider.start_id
        rider_end = self.rider.destination_id
        travel_time = self.time_matrix[(self.current_node.value.location_id, new_location)]
        new_location_arrival_time = self.current_node.value.departure_time + travel_time
        
        # Make sure node exist in the linked list solution
        if self.status == 'waiting':
            potential_departure_time = new_location_arrival_time + self.time_matrix[(new_location, rider_start)]
            potential_arrival_time = potential_departure_time + self.time_matrix[(rider_start, rider_end)]
            return self.rider.utility(potential_departure_time, potential_arrival_time)
        
        elif self.status == 'onboard':
            departure_time = self.departure_node.value.departure_time
            potential_arrival_time = new_location_arrival_time + self.time_matrix[(rider_start, rider_end)]
            return self.rider.utility(departure_time, potential_arrival_time)

    def choose_to_board(self) -> bool:

        rider_end = self.rider.destination_id
        current_location = self.current_node.value.location_id
        current_depart_time = self.current_node.value.departure_time

        if self.status == "waiting" and \
            current_location == self.rider.start_id:

            # Immediately board if actual departure time exceed the preferred departure time
            if self.rider.optimal_departure - current_depart_time < 0:
                return True

            # This condition determines whether it is too early to board the bus. 
            # The board_utility_threshold is computed as (1 - beta)
            else:
                start_to_target_time = self.time_matrix[(current_location, rider_end)]
                potential_arrival_time = current_depart_time + start_to_target_time
                potential_utility = self.rider.utility(current_depart_time, potential_arrival_time)
                
                if potential_utility >= self.board_threshold:
                    return True
        else:
            return False

    def choose_to_disembark(self) -> bool:
        if self.status == "onboard" and \
            self.current_node.value.location_id == self.rider.destination_id:
            return True
        else:
            return False

class GreedyInsertAgent(Agent):
    def __init__(self, rider: Passenger, time_matrix) -> None:
        super().__init__(rider, time_matrix)
