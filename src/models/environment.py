import random
import numpy as np
import igraph as ig
from models.passenger import Passenger
from utils.info_utils import environment_info
from typing import Tuple, List

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

    def generate_graph(self, num_locations: int, max_coordinates: Tuple[int, int], avg_speed: float) -> ig.Graph:
        # Create fully connected graph with n locations
        g = ig.Graph.Full(n=num_locations, loops=False)
        g.vs["location_id"] = [id for id in range(len(g.vs))]

        # Generate random coordinates
        max_x = max_coordinates[0]
        max_y = max_coordinates[1]
        
        x_coordinates = np.random.choice(max_x, num_locations, replace=False)
        y_coordinates = np.random.choice(max_y, num_locations, replace=False)
        
        coordinates = [(x, y) for x, y in zip(x_coordinates, y_coordinates)]
        g.vs['coordinate'] = coordinates
        
        # Compute distance matrix (euclidean) and travel time (weight of graph)
        for edge in g.es:
            source_index = edge.source
            target_index = edge.target

            source_coordinate = np.array(g.vs[source_index]["coordinate"])
            target_coordinate = np.array(g.vs[target_index]["coordinate"])

            distance = round(np.linalg.norm(source_coordinate - target_coordinate), 2)
            travel_time = round(distance / avg_speed, 0)

            edge["distance"] = distance
            edge["travel_time"] = travel_time

        return g

    def generate_passengers(self, graph: ig.Graph, num_passengers: int) -> List[Passenger]:

        location_ids = [location_id for location_id in graph.vs["location_id"]]
        passengers = []

        for id in range(num_passengers):

            # Sample 2 elements w/o replacement - avoids having same start and end location
            start_id, destination_id = random.sample(location_ids, 2)
            passengers.append(Passenger(id, start_id, destination_id))

        return passengers

    def __str__(self):
        
        """
        Returns:
            string: Displays the summary of the environment
        """
        return environment_info(self)