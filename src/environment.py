import numpy as np
from igraph import Graph
import igraph as ig

class Environment:
    def __init__(self,
                 num_locations=10,
                 max_coordinates=(100, 100),
                 avg_vehicle_speed=2.0):

        self.graph = self.generate_graph(num_locations, max_coordinates, avg_vehicle_speed)

    def generate_graph(self, num_locations, max_coordinates, avg_speed):
        """
        Args:
            num_locations (Int): Total number of locations
            max_coordinates ((Int, Int))): Largest coordinates - specifies the boundary of euclidean space
            avg_speed [Float]: Speed in km/min

        Returns:
            Graph: Fully connected graph, satisfying triangle inequality with travel time as edge weight
        """

        # Create fully connected graph with n locations
        g = Graph.Full(n=num_locations, loops=False)
        
        # Generate random coordinates
        max_x = max_coordinates[0]
        max_y = max_coordinates[1]
        
        x_coordinates = np.random.choice(max_x, num_locations, replace=False)
        y_coordinates = np.random.choice(max_y, num_locations, replace=False)
        
        coordinates = [(x, y) for x, y in zip(x_coordinates, y_coordinates)]
        g.vs['coordinate'] = coordinates
        
        # Compute distance matrix (euclidean) and travel time (weight of graph)
        for location_1, location_2 in g.get_edgelist():
            
            location_1_coordinate = g.vs[location_1]['coordinate']
            location_2_coordinate = g.vs[location_2]['coordinate']
            distance = np.linalg.norm(np.array(location_1_coordinate) - np.array(location_2_coordinate))
            
            # Assume distance in km, and time in minutes
            edge_id = g.get_eid(location_1, location_2)
            g.es[edge_id]['distance'] = round(distance, 2)
            g.es[edge_id]['time'] = round(distance / avg_speed, 2)
                    
        return g
    
    def plot_graph(self):
        visual_style = {
            "bbox": (600, 600),
            "margin": 30,
        }
        self.graph.vs['label'] = self.graph.vs['coordinate']
        self.graph.es['label'] = self.graph.es['time']
        ig.plot(self.graph, **visual_style)

np.random.seed(42)
env = Environment(num_locations=5)
env.plot_graph()