from pyllist.dllist import dllistnode
from models.solution import Solution, TourNodeValue
from python_tsp.heuristics import solve_tsp_local_search, solve_tsp_simulated_annealing
from python_tsp.exact import solve_tsp_dynamic_programming
import numpy as np
from pathlib import Path
import pickle

class TspHeuristic:
    def __init__(self, agents, graph, params) -> None:
        self.agents = agents
        self.graph = graph
        self.params = params
        self.dataset = self.params.pop("dataset")
        self.algorithm = self.__get_algorithm()
        self.time_matrix = self.__construct_time_matrix()
        self.mapping = {id: location for id, location in enumerate(self.graph.locations)}
        self.journey_time = 0
    
    def __check_route(self):
        path = Path(f"./tsp_solutions/{self.dataset}/{self.__format_params()}.pkl")
        try:
            with path.open('rb') as f:
                solution = pickle.load(f)
                return solution
        except OSError:
            return None

    def __construct_time_matrix(self):
        matrix = []
        for x in self.graph.locations:
            travel_times = []
            for y in self.graph.locations:
                travel_time = self.graph.travel_time(x, y)
                travel_times.append(travel_time)
            matrix.append(travel_times)
        return matrix

    def __format_params(self):
        params = []
        for key, val in self.params.items():
            params.append(f"{key}_{val}")
        
        return "_".join(params)

    def __save_solution(self, solution):
        path = Path(f"./tsp_solutions/{self.dataset}/{self.__format_params()}.pkl")
        with path.open("wb") as output:
            pickle.dump(solution, output)
    
    def __get_algorithm(self):
        if self.params['driver'] == "2_opt":
            return solve_tsp_local_search
        elif self.params['driver'] == "simulated_annealing":
            return solve_tsp_simulated_annealing
        elif self.params['driver'] == "dp":
            return solve_tsp_dynamic_programming

    def construct_sol_from_route(self, route):
        solution = Solution(self.agents, self.graph)
        solution.append(dllistnode(TourNodeValue(route[0], 0, 0)))

        for location in route[1:]:
            curr_node = solution.tail()
            travel_time = self.graph.travel_time(curr_node.value.location_id, location)
            arrival_time = curr_node.value.departure_time + travel_time
            solution.append(dllistnode(TourNodeValue(location, arrival_time, 0)))
        self.journey_time = solution.tail().value.arrival_time
        return solution

    def optimise(self) -> Solution:
        
        route = self.__check_route()
        if route:
            solution = self.construct_sol_from_route(route)
        else:
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
            
            self.journey_time = journey_time

            # Construct solution based on solved TSP route
            solution = Solution(self.agents, self.graph)
            start_tour_node = TourNodeValue(self.mapping[routes[0][0]], 0, 0)
            solution.append(dllistnode(start_tour_node))
            routes[0].pop()

            for route in routes:
                for location in route:
                    current_node = solution.tail().value
                    if current_node.location_id != location:
                        travel_time = self.graph.travel_time(current_node.location_id, self.mapping[location])
                        arrival_time = current_node.departure_time + travel_time
                        node = TourNodeValue(self.mapping[location], arrival_time, 0)
                        solution.append(dllistnode(node))
            
            self.__save_solution(solution.get_route())

        list_solution = solution.to_list()
        # Find best nodes to board and alight:
        for agent in self.agents:
            eligible_depart_nodes = [node for node in list_solution if node.value.location_id == agent.rider.start_id]
            eligible_arrival_nodes = [node for node in list_solution if node.value.location_id == agent.rider.destination_id]

            eligible_pairs = []
            for depart_node in eligible_depart_nodes:
                for arrival_node in eligible_arrival_nodes:
                    if depart_node.value.departure_time < arrival_node.value.arrival_time:
                        eligible_pairs.append((depart_node, arrival_node))
            
            best_depart, best_arrival = max(eligible_pairs, key=lambda x: agent.rider.utility(x[0].value.departure_time, x[1].value.arrival_time))
            best_depart.value.add_rider(agent.rider, "waiting")
            best_arrival.value.add_rider(agent.rider, "onboard")
            agent.departure_node = best_depart
            agent.arrival_node = best_arrival

        solution.create_rider_schedule()
        solution.calculate_objectives()

        return solution



        





        




        









