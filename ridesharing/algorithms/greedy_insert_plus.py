import copy
from typing import List

import numpy as np

from models.graph import Graph
from models.passenger import Passenger
from models.solution import Solution, TourNodeValue

from algorithms.greedy_insert import GreedyInsert
class GreedyInsertPlus:

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

        if self.params['multiple_iterations']:
            solutions: List[Solution] = []

            for rider in self.riders:
                rider_depart_node_dict = dict()
                sol: Solution = self.initialise_solution(rider)
                temp_riders = copy.copy(self.riders)
                temp_riders.remove(rider)

                rider_depart_node_dict[rider.id] = sol.llist.first
                greedy_insert_algo = GreedyInsert(self.riders, self.graph, self.params)

                for rider in temp_riders:
                    depart_node = greedy_insert_algo.allocate_rider(rider, sol, departure_node=None)
                    rider_depart_node_dict[rider.id] = depart_node
                
                self.riders.reverse()

                for rider in temp_riders:
                    arrival_node = greedy_insert_algo.allocate_rider(rider, sol, departure_node=rider_depart_node_dict.get(rider.id))
                
                # sol.check_constraint(complete=True)
                sol.create_rider_schedule()
                sol.calculate_objectives()
                solutions.append(sol)
                
            return max(solutions, key=lambda sol: sol.objectives[self.params['objective']])
            
        else:

            rider_depart_node_dict = dict()
            first_rider = self.riders[0]
            sol: Solution = self.initialise_solution(first_rider)
            rider_depart_node_dict[first_rider.id] = sol.llist.first
            greedy_insert_algo = GreedyInsert(self.riders, self.graph, self.params)

            for rider in self.riders[1:]:
                depart_node = greedy_insert_algo.allocate_rider(rider, sol, departure_node=None)
                rider_depart_node_dict[rider.id] = depart_node
            
            self.riders.reverse()

            for rider in self.riders:
                arrival_node = greedy_insert_algo.allocate_rider(rider, sol, departure_node=rider_depart_node_dict.get(rider.id))
            
            # sol.check_constraint(complete=True)
            sol.create_rider_schedule()
            sol.calculate_objectives()
            return sol
