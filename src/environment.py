import random
import numpy as np
import igraph as ig
from prettytable import PrettyTable

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
        for edge in g.es:
            source_index = edge.source
            target_index = edge.target

            source_coordinate = np.array(g.vs[source_index]["coordinate"])
            target_coordinate = np.array(g.vs[target_index]["coordinate"])

            distance = round(np.linalg.norm(source_coordinate - target_coordinate), 2)
            travel_time = round(distance / avg_speed, 0)

            edge["distance"] = distance
            edge["time"] = travel_time

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

    def __str__(self):
        
        """
        Returns:
            string: Displays the summary of the environment
        """
        # Display Environment Properties
        environment_properties = PrettyTable()
        environment_properties.field_names = ["Properties", "Value"]
        environment_properties.add_rows([["num_locations", self.num_locations],
        ["num_passengers", self.num_passengers],
        ["vehicle speed", f"{self.avg_speed} km/min"]])

        # Display Passenger Details
        passengers = [[p.id, p.start_id, p.destination_id] for p in self.passengers]
        passenger_list = PrettyTable()
        passenger_list.add_rows(passengers)
        passenger_list.field_names = ["Passenger ID", "Start Location ID", "Destination ID"]

        # Display Graph Details
        graph_properties = PrettyTable()
        graph_properties_row = []
        for location_1, location_2 in self.graph.get_edgelist():

            edge_id = self.graph.get_eid(location_1, location_2)
            row_data = [edge_id, location_1, location_2, self.graph.es[edge_id]['time']]
            graph_properties_row.append(row_data)
        
        graph_properties.add_rows(graph_properties_row)
        graph_properties.field_names = ["Edge ID", "Location 1", "Location 2", "Time Taken (min)"]
        
        return "\n".join(["Environment Properties:",
        f"{environment_properties.get_string()} \n",
        "Passengers:",
        f"{passenger_list.get_string()} \n",
        "Graph:",
        graph_properties.get_string()])

env = Environment(num_locations=10, num_passengers=5)
print(env)