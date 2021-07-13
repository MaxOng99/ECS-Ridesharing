import igraph as ig
from typing import List, Callable
from models.passenger import Passenger
from models.solution import Solution
from algorithms import tsp_heuristics as heuristic_algo
from algorithms import voting as vote_algo

class Optimiser:

    def __init__(self, graph: ig.Graph, passengers: Passenger):
        self.graph = graph
        self.passengers = passengers

    def optimise(self, solution_constructor: str = "nearest_neighbour") -> Solution:
        solutions = []
        pruned_graph = self.__prune_graph(self.graph, self.passengers)
        construction_function = self.__get_construction_function(solution_constructor)

        # Construct initial solution for each passenger, taking their start location as the start node.
        for passenger in self.passengers:
            solution = construction_function(pruned_graph, passenger.start_id)
            solutions.append(solution)

        voted_solution = vote_algo.borda_count(solutions, self.passengers)
        return voted_solution
    
    def __prune_graph(self, graph: ig.Graph, passengers: List[Passenger]) -> ig.Graph:
        passenger_locations = set()

        for passenger in passengers:
            passenger_locations.add(passenger.start_id)
            passenger_locations.add(passenger.destination_id)
        
        return graph.subgraph(passenger_locations)

    def __get_construction_function(self, function_identifier: str) -> Callable:
        if function_identifier == "nearest_neighbour":
            return heuristic_algo.nearest_neighbour