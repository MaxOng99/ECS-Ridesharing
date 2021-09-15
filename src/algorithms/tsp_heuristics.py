import igraph as ig
from src.models.solution import Solution
import src.utils.graph_utils as graph_utils

def __nn(graph: ig.Graph, solution: Solution) -> Solution:

    start_node = solution.get_current_node()
    current_arrival_time = start_node.arrival_time
    unvisited_node_ids = list(set(graph.vs["location_id"]) - set([start_node.location_id]))

    while unvisited_node_ids:
        current_node_id = solution.get_current_node().location_id
        nearest_node_id = min(unvisited_node_ids, \
            key=lambda node: graph_utils.travel_time(current_node_id, node, graph))
        
        edge = graph_utils.get_edge(current_node_id, nearest_node_id, graph)
        current_arrival_time += edge["travel_time"]
        unvisited_node_ids.remove(nearest_node_id)
        solution.expand_tour(location_id=nearest_node_id, arrival_time=current_arrival_time, waiting_time=0)
    
    return solution

def nearest_neighbour(graph: ig.Graph, start_location_id: int) -> Solution:

    solution = Solution()
    solution.expand_tour(location_id=start_location_id, arrival_time=0, waiting_time=0)

    first_tour_solution = __nn(graph, solution)
    complete_tour_solution = __nn(graph, first_tour_solution)

    return complete_tour_solution










