from dataclasses import replace

import numpy as np
from python_tsp.heuristics import solve_tsp_local_search
from python_tsp.heuristics import solve_tsp_simulated_annealing

from models.solution import Solution, TourNodeValue

class TspHeuristic:
    def __init__(self, riders, graph, params) -> None:
        self.riders = riders
        self.graph = graph
        self.params = params
        self.algorithm = self.__get_algorithm()
        self.time_matrix = self.__construct_time_matrix()
        self.mapping = {id: location for id, location in enumerate(self.graph.locations())}

    def __construct_time_matrix(self):
        matrix = []
        for x in self.graph.locations():
            travel_times = []
            for y in self.graph.locations():
                travel_time = self.graph.travel_time(x, y)
                travel_times.append(travel_time)
            matrix.append(travel_times)
        return matrix
            
    def __get_algorithm(self):
        if self.params['driver'] == "2_opt":
            return solve_tsp_local_search
        elif self.params['driver'] == "simulated_annealing":
            return solve_tsp_simulated_annealing

    def optimise(self) -> Solution:
        processing_time = self.params['max_processing_time']

        route, travel_time = self.algorithm(np.array(self.time_matrix), max_processing_time=processing_time)
        joined_routes = route * 2

        # Construct solution based on solved TSP route
        solution = Solution(self.riders, self.graph)
        start_tour_node = TourNodeValue(self.mapping[joined_routes[0]], 0, 0)
        solution.llist.append(start_tour_node)

        for loc_index in joined_routes[1:]:
            current_node = solution.llist.last
            travel_time = self.graph.travel_time(current_node.value.location_id, self.mapping[loc_index])
            arrival_time = current_node.value.departure_time + travel_time
            node = TourNodeValue(self.mapping[loc_index], arrival_time, 0)
            solution.llist.append(node)
        
        # Find best nodes to board and alight:
        for rider in self.riders:
            start_end_pairs = []
            start_nodes = filter(
                lambda node: node.value.location_id == rider.start_id,
                solution.llist.iternodes()
            )
            for start in start_nodes:
                curr_best_end = None
                curr_best_end_util = -1

                for end_node in start.iternext():
                    if end_node.value.arrival_time >= start.value.departure_time and end_node.value.location_id == rider.destination_id:
                        depart_time = start.value.departure_time
                        arrival_time = end_node.value.arrival_time
                        util = rider.utility(depart_time, arrival_time)
                        if util > curr_best_end_util:
                            curr_best_end = end_node
                            curr_best_end_util = util
                        else:
                            break
                if curr_best_end:
                    start_end_pairs.append((start, curr_best_end))

            best_node_pair = max(
                start_end_pairs,
                key=lambda pair: rider.utility(pair[0].value.departure_time, pair[1].value.arrival_time)
            )
            best_depart_node, best_arrival_node = best_node_pair

            best_depart_node_val = best_depart_node.value
            best_arrival_node_val = best_arrival_node.value

            updated_depart_val = replace(best_depart_node_val, pick_ups=best_depart_node_val.pick_ups + tuple([rider]))
            best_depart_node.value = updated_depart_val

            updated_arrival_val = replace(best_arrival_node_val, drop_offs=best_arrival_node_val.drop_offs + tuple([rider]))
            best_arrival_node.value = updated_arrival_val

        # solution.check_constraint(complete=True)
        solution.create_rider_schedule()
        solution.calculate_objectives()
        return solution