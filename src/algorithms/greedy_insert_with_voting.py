import copy
from typing import List

import numpy as np

from models.graph import Graph
from models.passenger import Passenger
from models.solution import Solution, TourNodeValue

from algorithms.greedy_insert import GreedyInsert
from algorithms.voting_system import BordaCount, Popularity

class RGVA:
    def __init__(self, riders: List[Passenger], graph: Graph, params) -> None:
        self.riders = riders
        self.params = params
        self.graph = graph

    def initialise_solution(self, first_rider: Passenger) -> None:
        sol = Solution(self.riders, self.graph)
        optimal_depart = first_rider.optimal_departure
        depart_loc = first_rider.start_id
        depart_node_val = TourNodeValue(depart_loc, 0, optimal_depart, pick_ups=tuple([first_rider]))
        sol.llist.append(depart_node_val)
        return sol

    def optimise(self) -> Solution:
        np.random.shuffle(self.riders)
        solutions: Solution = []

        for rider in self.riders:
            temp_riders = copy.copy(self.riders)
            temp_riders.remove(rider)
            sol: Solution = self.initialise_solution(rider)
            greedy_insert_algo = GreedyInsert(self.riders, self.graph, self.params)

            for rider in temp_riders:
                depart_node = greedy_insert_algo.allocate_rider(rider, sol, departure_node=None)
                arrival_node = greedy_insert_algo.allocate_rider(rider, sol, departure_node=depart_node)
            
            sol.check_constraint(complete=True)
            sol.create_rider_schedule()
            sol.calculate_objectives()
            solutions.append(sol)
        
        # Vote for len(self.riders) solution
        if self.params['final_voting_rule'] == "borda_count":
            voting_system = BordaCount(self.riders, solutions, additional_info=None)
        elif self.params['final_voting_rule'] == "popularity":
            voting_system = Popularity(self.riders, solutions, additional_info=None)
        
        return voting_system.winner





