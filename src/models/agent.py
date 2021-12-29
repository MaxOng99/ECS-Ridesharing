from models.passenger import Passenger
from models.solution import Solution, TourNodeValue
from models.graph import Graph
import numpy as np

from typing import List

class Agent:
    def __init__(self, rider: Passenger, graph: Graph) -> None:
        self.rider: Passenger = rider
        self.graph = graph
        self.status = 'waiting'
        self.departure_node = None
        self.arrival_node = None

    def reset_status(self):
        self.status = "waiting"
        self.departure_node = None
        self.arrival_node = None
        self.current_node = None

    def rank_solutions(self, solutions: List[Solution]) -> List[Solution]:
        
        # 1. Shuffle solutions, to take into account solution with similar utility
        # 2. Rank the solution
        np.random.shuffle(solutions)
        return sorted(solutions, key=lambda sol: self.get_solution_utility(sol), reverse=True)
    
    def get_solution_utility(self, solution: Solution):
        departure_time = solution.rider_schedule.get("departure").get(self.rider.id)
        arrival_time = solution.rider_schedule.get("arrival").get(self.rider.id)
        return self.rider.utility(departure_time, arrival_time)

class IterativeVotingAgent(Agent):
    def __init__(self, rider: Passenger, graph: Graph) -> None:
        super().__init__(rider, graph)
        self.board_threshold = self.__board_threshold()
        self.weight = self.board_threshold
        self.current_node = None
    
    def __board_threshold(self):
        board_threshold = 1 - self.rider.beta
        return board_threshold

    def rank_tour_nodes(self, tour_nodes: List[TourNodeValue]):
        interested_nodes = [node for node in tour_nodes if self.node_utility(node) > 0]
        return sorted(interested_nodes, key=lambda node: self.node_utility(node), reverse=True)

    def node_utility(self, node: TourNodeValue):
        
        if self.status == "waiting":
            if node.location_id == self.rider.start_id:
                return self.rider.utility(node.departure_time, None)
            else:
                return 0
        else:
            if node.location_id == self.rider.destination_id:
                return self.rider.utility(self.departure_node.value.departure_time, node.arrival_time)
            else:
                return 0

    def rank_locations(self, location_ids: List[int]) -> List[int]:
        np.random.shuffle(location_ids)
        return sorted(location_ids, key=lambda id: self.location_utility(id), reverse=True)    
        # return ranked_locations

    def location_utility(self, new_location) -> float:
        
        rider_start = self.rider.start_id
        rider_end = self.rider.destination_id
        travel_time = self.graph.travel_time(self.current_node.value.location_id, new_location)
        new_location_arrival_time = self.current_node.value.departure_time + travel_time
        
        # Make sure node exist in the linked list solution
        if self.status == 'waiting':
            potential_departure_time = new_location_arrival_time + self.graph.travel_time(new_location, rider_start)
            potential_arrival_time = potential_departure_time + self.graph.travel_time(rider_start, rider_end)
            return self.rider.utility(potential_departure_time, potential_arrival_time)
        
        elif self.status == 'onboard':
            departure_time = self.departure_node.value.departure_time
            potential_arrival_time = new_location_arrival_time + self.graph.travel_time(rider_start, rider_end)
            return self.rider.utility(departure_time, potential_arrival_time)

    def choose_to_board(self) -> bool:

        current_location = self.current_node.value.location_id

        if self.status == "waiting" and \
            current_location == self.rider.start_id:
            return True            
        else:
            return False

    def choose_to_disembark(self) -> bool:
        if self.status == "onboard" and \
            self.current_node.value.location_id == self.rider.destination_id:
            return True
        else:
            return False
