from typing import List
import igraph as ig

import numpy as np

from models.graph import Graph
from models.passenger import Passenger
from algorithms.iterative_voting_1 import IterativeVoting1
from algorithms.iterative_voting_2 import IterativeVoting2
from algorithms import tsp_heuristics as heuristic_algo
from algorithms.greedy_insert import GreedyInsert
from algorithms.greedy_insert_plus import GreedyInsertPlus
from algorithms.greedy_insert_with_voting import RGVA

algos = {
    "IV1": IterativeVoting1,
    "IV2": IterativeVoting2,
    "RGA": GreedyInsert,
    "RGA ++": GreedyInsertPlus,
    "RGVA": RGVA,
    "tsp algorithms": heuristic_algo.TspHeuristic
}

def prune_graph(graph: Graph, riders: List[Passenger]) -> Graph:

    start_ids = [rider.start_id for rider in riders]
    destination_ids = [rider.destination_id for rider in riders]
    required_locations = set(start_ids + destination_ids)
    required_vertices = [graph.find_vertex(loc) for loc in required_locations]

    igraph: ig.Graph = graph.igraph
    pruned_igraph = igraph.induced_subgraph(required_vertices)
    return Graph(pruned_igraph)
        
def create_algorithm(seed, params, graph, riders):
    algo_name = params.get("algorithm", None)
    algo_params = params.get("algorithm_params", None)
    pruned_graph = prune_graph(graph, riders)

    np.random.seed(seed)
    return algos[algo_name](riders, pruned_graph, algo_params)