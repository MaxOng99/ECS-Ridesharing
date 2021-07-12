from collections import namedtuple

TourNode = namedtuple("TourNode", "node_id timestamp waiting_time")

class Solution:

    def __init__(self):
        self.tour_nodes = []
        self.first_trip = False

    def expand_tour(self, node_id, timestamp, waiting_time):
        self.tour_nodes.append(TourNode(node_id, timestamp, waiting_time))

    def get_current_node(self):
        return self.tour_nodes[-1]

    def eligible_node_pairs(self, source_id, destination_id):

        eligible_pairs = []
        departure_nodes = list(filter(lambda node: node.node_id == source_id, self.tour_nodes))
        arrival_nodes = list(filter(lambda node: node.node_id == destination_id, self.tour_nodes))

        for departure_node in departure_nodes:
            for arrival_node in arrival_nodes:
                if departure_node.timestamp < arrival_node.timestamp:
                    eligible_pairs.append((departure_node, arrival_node))

        return eligible_pairs
    
    def get_nodes_from_id(self, node_id):
        return list(filter(lambda node: node.node_id == node_id, self.tour_nodes))

    def get_tour(self):
        return self.tour_nodes
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        tour_repr = [str((node.node_id, node.timestamp, node.waiting_time)) for node in self.tour_nodes]
        return " -> ".join(tour_repr)

