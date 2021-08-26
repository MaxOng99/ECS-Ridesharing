import igraph as ig
from typing import Callable, Dict, Set
from models.agent import GreedyInsertAgent, IterativeVotingAgent
from models.passenger import Passenger
from models.solution import Solution
from algorithms import tsp_heuristics as heuristic_algo
from algorithms.iterative_voting import IterativeVoting
from algorithms.greedy_insert import GreedyInsert
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
        self.time_matrix = self.__create_time_matrix(self.pruned_graph)
        self.passengers = passengers

        for rider in self.passengers:
            rider.time_matrix = self.time_matrix

    def optimise(self, options) -> Solution:
        algorithm = self.__customise_algorithm(options)
        return algorithm.optimise()

    def __prune_graph(self, graph: ig.Graph, passengers: Set[Passenger]) -> ig.Graph:
        passenger_locations = set()

        for passenger in passengers:
            passenger_locations.add(passenger.start_id)
            passenger_locations.add(passenger.destination_id)
        
        return graph.subgraph(passenger_locations)

    def __create_time_matrix(self, graph: ig.Graph):
        travel_time_loc = dict()
        for edge in graph.es:
            source = graph.vs[edge.source]['location_id']
            target = graph.vs[edge.target]['location_id']
            travel_time_loc[(source, target)] = edge['travel_time']
            travel_time_loc[(target, source)] = edge['travel_time']

        for vertex in graph.vs:
            travel_time_loc[(vertex['location_id'], vertex['location_id'])] = 0

        return travel_time_loc

    def __customise_algorithm(self, options: Dict[str, object]) -> Callable:

        algorithm = options.get("algorithm")
        params = options.get("parameters", None)

        if algorithm == "nearest_neighbour":
            return heuristic_algo.nearest_neighbour

        elif algorithm == "iterative_voting":
            agents = [IterativeVotingAgent(rider, self.time_matrix) for rider in self.passengers]
            return IterativeVoting(agents, self.time_matrix, params=params)
            
        elif algorithm == 'greedy_insert':
            agents = [GreedyInsertAgent(rider, self.time_matrix) for rider in self.passengers]
            return GreedyInsert(agents, self.time_matrix, params=params)
