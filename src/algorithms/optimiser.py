from typing import Set
from collections import OrderedDict
from algorithms.iterative_voting_1 import IterativeVoting1
from algorithms.iterative_voting_2 import IterativeVoting2
from models.agent import IterativeVotingAgent
from models.passenger import Passenger
from algorithms import tsp_heuristics as heuristic_algo
from algorithms.greedy_insert import GreedyInsert
from algorithms.greedy_insert_plus import GreedyInsertPlus
from models.graph import Graph
import numpy as np

def prune_graph(graph: Graph, passengers: Set[Passenger]) -> Graph:
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
        
def create_algorithm(seed, params, graph, riders):
    algo_name = params.get("algorithm", None)
    algo_params = params.get("algorithm_params", None)
    pruned_graph = prune_graph(graph, riders)

    np.random.seed(seed)
    algorithm_mapping = {
        # First one not gonna work
        "iterative voting 1": IterativeVoting1([IterativeVotingAgent(rider, graph) for rider in riders], pruned_graph, algo_params),
        "iterative voting 2": IterativeVoting2([IterativeVotingAgent(rider, graph) for rider in riders], pruned_graph, algo_params),
        "greedy insert": GreedyInsert(riders, pruned_graph, algo_params),
        "greedy insert ++": GreedyInsertPlus(riders, pruned_graph, algo_params)
        # "tsp algorithms": heuristic_algo.TspHeuristic([Agent(rider, graph) for rider in riders], pruned_graph, algo_params)
    }
    return algorithm_mapping.get(algo_name)