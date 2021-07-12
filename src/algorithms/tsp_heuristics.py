from models.solution import Solution
import utils.graph_utils as graph_utils

def __nn(graph, solution):

    start_node = solution.get_current_node()
    current_timestamp = start_node.timestamp
    unvisited_node_ids = list(set(graph.vs["identifier"]) - set([start_node.node_id]))

    while unvisited_node_ids:
        current_node_id = solution.get_current_node().node_id
        nearest_node_id = min(unvisited_node_ids, \
            key=lambda node: graph_utils.travel_time(current_node_id, node, graph))
        
        edge = graph_utils.get_edge(current_node_id, nearest_node_id, graph)
        current_timestamp += edge["travel_time"]
        unvisited_node_ids.remove(nearest_node_id)
        solution.expand_tour(node_id=nearest_node_id, timestamp=current_timestamp, waiting_time=0)
    
    return solution

def nearest_neighbour(graph, start_node_id):

    solution = Solution()
    solution.expand_tour(node_id=start_node_id, timestamp=0, waiting_time=0)

    first_tour_solution = __nn(graph, solution)
    complete_tour_solution = __nn(graph, first_tour_solution)

    return complete_tour_solution









