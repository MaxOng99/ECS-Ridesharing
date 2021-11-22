from typing import Callable, Dict, Set
from collections import OrderedDict
from algorithms.iterative_voting_1 import IterativeVoting1
from algorithms.iterative_voting_2 import IterativeVoting2
from models.agent import GreedyInsertAgent, IterativeVotingAgent, Agent
from models.passenger import Passenger
from models.solution import Solution
from algorithms import tsp_heuristics as heuristic_algo
from algorithms.greedy_insert import GreedyInsert
from algorithms.greedy_insert_2 import GreedyInsert2
from models.graph import Graph
import numpy as np

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

    def __init__(self, seed, graph: Graph, passengers: Set[Passenger]):
        self.seed = seed
        self.graph = graph
        self.passengers = passengers
        
        np.random.seed(seed)
        self.pruned_graph = self.__prune_graph(graph, passengers)
        self.objective_function = None

    def optimise(self, options) -> Solution:
        algorithm = self.__customise_algorithm(options)
        solution: Solution = algorithm.optimise()
        return solution
        
    def __prune_graph(self, graph: Graph, passengers: Set[Passenger]) -> Graph:
        passenger_locations = OrderedDict()

        for passenger in passengers:
            start = passenger.start_id
            destination = passenger.destination_id

            passenger_locations[start] = None
            passenger_locations[destination] = None

        # Prune location_ids
        new_location_ids = []
        for location_id in graph.locations:
            if location_id in passenger_locations:
                new_location_ids.append(location_id)
        
        # Update time and distance matrix
        new_time_matrix = dict()
        new_distance_matrix = dict()

        for (source, target) in graph.distance_matrix:
            if source in passenger_locations and \
                target in passenger_locations:

                new_time_matrix[(source, target)] = graph.time_matrix[(source, target)]
                new_distance_matrix[(source, target)] = graph.distance_matrix[(source, target)]
        
        return Graph(graph.igraph, new_location_ids, None, new_time_matrix, new_distance_matrix)

    def __customise_algorithm(self, options: Dict[str, object]) -> Callable:

        algorithm = options.get("algorithm")
        params = options.get("algorithm_params", None)

        if algorithm == "tsp algorithms":
            agents = [Agent(rider, self.graph) for rider in self.passengers]
            return heuristic_algo.TspHeuristic(agents, self.graph, params=params)

        elif algorithm == "iterative voting 1":
            agents = [IterativeVotingAgent(rider, self.graph) for rider in self.passengers]
            return IterativeVoting1(agents, self.pruned_graph, params=params)
        
        elif algorithm == "iterative voting":
            agents = [IterativeVotingAgent(rider, self.graph) for rider in self.passengers]
            return IterativeVoting2(agents, self.pruned_graph, params=params)

        elif algorithm == 'greedy insert':
            agents = [GreedyInsertAgent(rider, self.graph) for rider in self.passengers]
            return GreedyInsert(agents, self.pruned_graph, params=params)

        elif algorithm == "greedy insert ++":
            agents = [GreedyInsertAgent(rider, self.graph) for rider in self.passengers]
            return GreedyInsert2(agents, self.pruned_graph, params=params)
