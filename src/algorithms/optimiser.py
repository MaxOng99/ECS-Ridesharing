import igraph as ig
from typing import Callable, Dict, Set
from models.passenger import Passenger
from models.solution import Solution
from algorithms import tsp_heuristics as heuristic_algo
from algorithms import voting as vote_algo

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

    def __init__(self, graph: ig.Graph, passengers: Set[Passenger]):
        self.pruned_graph = self.__prune_graph(graph, passengers)
        self.passengers = passengers

    def optimise(self, options) -> Solution:
        algorithm = self.__customise_algorithm(options)
        return algorithm.optimise()

    def __prune_graph(self, graph: ig.Graph, passengers: Set[Passenger]) -> ig.Graph:
        passenger_locations = set()

        for passenger in passengers:
            passenger_locations.add(passenger.start_id)
            passenger_locations.add(passenger.destination_id)
        
        return graph.subgraph(passenger_locations)

    def __customise_algorithm(self, options: Dict[str, object]) -> Callable:

        algorithm = options.get("algorithm")
        params = options.get("parameters")

        if algorithm == "nearest_neighbour":
            return heuristic_algo.nearest_neighbour

        elif algorithm == "iterative_voting":
            return vote_algo.IterativeVoting(self.passengers, self.pruned_graph, params=params)
