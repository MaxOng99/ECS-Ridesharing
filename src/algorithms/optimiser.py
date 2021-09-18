import igraph as ig
from typing import Callable, Dict, Set
from models.agent import GreedyInsertAgent, IterativeVotingAgent
from models.passenger import Passenger
from models.solution import Solution
from algorithms import tsp_heuristics as heuristic_algo
from algorithms.iterative_voting import IterativeVoting
from algorithms.greedy_insert import GreedyInsert
from models.graph import Graph

class Optimiser:
    """Wrapper class for the various optimiser algorithms

    Methods
    ----------
    optimise(options: Dict[str, object])
        Find a solution based on a configured set of options. Options include:
        - 'algorithm': 'iterative_voting' | 'greedy_insert'
        - 'parameters': Parameters for the chosen algorithm:

        Parameters for 'iterative_voting'
        - 'voting_rule': 'borda_count' | 'majority'
        Parameters for 'greedy_insert'

    """

    def __init__(self, graph: Graph, passengers: Set[Passenger]):
        self.graph = graph
        self.passengers = passengers
        self.pruned_graph = self.__prune_graph(graph, passengers)
        self.objective_function = None

    def optimise(self, options) -> Solution:
        algorithm = self.__customise_algorithm(options)

        solution: Solution = algorithm.optimise()
        solution.calculate_objectives()
        return solution
        
    def __prune_graph(self, graph: Graph, passengers: Set[Passenger]) -> Graph:
        passenger_locations = set()

        for passenger in passengers:
            passenger_locations.add(passenger.start_id)
            passenger_locations.add(passenger.destination_id)
        
        # Prune location_ids
        new_location_ids = set()
        for location_id in graph.locations:
            if location_id in passenger_locations:
                new_location_ids.add(location_id)
        
        # Update time and distance matrix
        new_time_matrix = dict()
        new_distance_matrix = dict()

        for (source, target) in graph.distance_matrix:
            if source in passenger_locations and \
                target in passenger_locations:

                new_time_matrix[(source, target)] = graph.time_matrix[(source, target)]
                new_distance_matrix[(source, target)] = graph.distance_matrix[(source, target)]
        
        return Graph(None, None, new_location_ids, None, new_time_matrix, new_distance_matrix)

    def __customise_algorithm(self, options: Dict[str, object]) -> Callable:

        algorithm = options.get("algorithm")
        params = options.get("algorithm_params", None)

        if algorithm == "nearest_neighbour":
            return heuristic_algo.nearest_neighbour

        elif algorithm == "iterative_voting":
            agents = [IterativeVotingAgent(rider, self.graph) for rider in self.passengers]
            return IterativeVoting(agents, self.graph, params=params)
            
        elif algorithm == 'greedy_insert':
            agents = [GreedyInsertAgent(rider, self.graph) for rider in self.passengers]
            return GreedyInsert(agents, self.graph, params=params)
