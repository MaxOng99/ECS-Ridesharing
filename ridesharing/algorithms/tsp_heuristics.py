from dataclasses import replace

import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.heuristics import solve_tsp_local_search, solve_tsp_simulated_annealing

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
        elif self.params['driver'] == "dp":
            return solve_tsp_dynamic_programming

    def __join_routes(self, routes):
        for route_i, route_j in zip(routes[:-1], routes[1:]):
            if route_i[-1] == route_j[0]:
                route_i.pop()
        return [loc_id for route in routes for loc_id in route]

    def optimise(self) -> Solution:
        journey_time = 0
        routes = []
        processing_time = self.params['max_processing_time']

        while journey_time < 1440:
            if processing_time != 0:
                route, travel_time = self.algorithm(np.array(self.time_matrix), max_processing_time=processing_time)
            else:
                route, travel_time = self.algorithm(np.array(self.time_matrix))
            routes.append(route)
            journey_time += travel_time

        # Construct solution based on solved TSP route
        joined_routes = self.__join_routes(routes)
        solution = Solution(self.riders, self.graph)
        start_tour_node = TourNodeValue(self.mapping[joined_routes[0]], 0, 0)
        solution.llist.append(start_tour_node)

        for loc_index in joined_routes[1:]:
            current_node = solution.llist.last
            travel_time = self.graph.travel_time(current_node.value.location_id, self.mapping[loc_index])
            arrival_time = current_node.value.departure_time + travel_time
            node = TourNodeValue(self.mapping[loc_index], arrival_time, 0)
            solution.llist.append(node)
        solution.check_constraint(complete=True)
        
        # Find best nodes to board and alight:
        for rider in self.riders:
            start_end_pairs = []
            start_nodes = filter(
                lambda node: node.value.location_id == rider.start_id,
                solution.llist.iternodes()
            )
            for start in start_nodes:
                end_nodes = filter(
                    lambda node: node.value.arrival_time >= start.value.departure_time and node.value.location_id == rider.destination_id,
                    start.iternext() 
                )
                for end in end_nodes:
                    start_end_pairs.append((start, end))
        
            best_node_pair = max(
                start_end_pairs,
                key=lambda pair: rider.utility(pair[0].value.departure_time, pair[1].value.arrival_time)
            )
            for best_node in list(best_node_pair):
                best_node_val = best_node.value
                best_node.value = replace(best_node_val, pick_ups=best_node_val.pick_ups + tuple([rider]))
        
        solution.create_rider_schedule()
        solution.calculate_objectives()
        return solution