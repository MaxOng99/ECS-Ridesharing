import random
import numpy as np
import igraph as ig

class Passenger:

    def __init__(self, id, start, destination):
        """
        Args:
            start (int): Node ID of start location
            destination (int): Node ID of destination
        """
        self.id = id
        self.start_id = start
        self.destination_id = destination
    
    def __str__(self):
        return f"Passenger {self.id}: {{Start: {self.start_id} | End: {self.destination_id}}}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Environment:
    def __init__(self, num_locations=10, num_passengers=10, max_coordinates=(100, 100), avg_vehicle_speed=2.0):
        """
        Args:
            max_coordinates ((int, int)): Largest coordinates - specifies the boundary of euclidean space
            avg_vehicle_speed (float): Speed in km/min
        """

        self.num_locations = num_locations
        self.num_passengers = num_passengers
        self.max_coordinates = max_coordinates
        self.avg_speed = avg_vehicle_speed
        self.graph = self.generate_graph(num_locations, max_coordinates, avg_vehicle_speed)
        self.passengers = self.generate_passengers(self.graph, num_passengers)

    def generate_graph(self, num_locations, max_coordinates, avg_speed):
        # Create fully connected graph with n locations
        g = ig.Graph.Full(n=num_locations, loops=False)
        
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

    def generate_passengers(self, graph, num_passengers):

        location_ids = [location_id for location_id in range(len(graph.vs['coordinate']))]
        passengers = []

        for id in range(num_passengers):

            # Sample 2 elements w/o replacement - avoids having same start and end location
            start_id, destination_id = random.sample(location_ids, 2)
            passengers.append(Passenger(id, start_id, destination_id))

        return passengers

    def plot_graph(self):
        visual_style = {
            "bbox": (600, 600),
            "margin": 30,
        }
        self.graph.vs['label'] = self.graph.vs['coordinate']
        self.graph.es['label'] = self.graph.es['time']
        ig.plot(self.graph, **visual_style)
    

env = Environment(num_locations=5)
env.plot_graph()

