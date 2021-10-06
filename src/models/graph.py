import igraph as ig
import numpy as np
import math
from pandas.core import groupby
from poisson_disc import Bridson_sampling
import pandas as pd
from haversine import haversine, Unit


def to_custom_graph(igraph):
    time_matrix = dict()
    distance_matrix = dict()

    for edge in igraph.es:
        source_vertex = igraph.vs[edge.source]
        target_vertex = igraph.vs[edge.target]

        source_id = source_vertex["location_id"]
        target_id = target_vertex["location_id"]

        time_matrix[(source_id, target_id)] = edge["travel_time"]
        time_matrix[(source_id, source_id)] = 0
        time_matrix[(target_id, target_id)] = 0

        distance_matrix[(source_id, target_id)] = edge["distance"]
        distance_matrix[(source_id, source_id)] = 0
        distance_matrix[(target_id, target_id)] = 0
    
    location_vertices = igraph.vs.select(is_centroid_eq=False)
    location_ids = [location_vertex['location_id'] for location_vertex in location_vertices]

    # Cluster info
    centroids = igraph.vs.select(is_centroid_eq=True)
    cluster_info = dict()

    for centroid in centroids:
        cluster_info[centroid['location_id']] = [location['location_id'] for location in centroid['cluster']]

    return Graph(igraph, location_ids, cluster_info, time_matrix, distance_matrix)

# Graph Model. Any custom graph generators should produce a Graph object
class Graph:
    def __init__(self, igraph, location_ids, cluster_info, time_matrix, distance_matrix) -> None:
        self.igraph = igraph
        self.locations = location_ids
        self.time_matrix = time_matrix
        self.cluster_info = cluster_info
        self.distance_matrix = distance_matrix
        min_travel_time = min(igraph.es['travel_time'])
        max_travel_time = max(igraph.es['travel_time'])
        self.avg_travel_time = np.mean(igraph.es['travel_time'])
        self.location_mapping = dict()
        

        travel_times = list(self.time_matrix.values())
        non_zero_travel_times = [time for time in travel_times if time > 0 ]
        self.travel_time_data = {
            "max": max(non_zero_travel_times),
            "min": min(non_zero_travel_times),
            "avg": np.mean(non_zero_travel_times)
        }

        distances = list(self.distance_matrix.values())
        non_zero_distances = [distance for distance in distances if distance > 0]
        self.distance_data = {
            "max": max(non_zero_distances),
            "min": min(non_zero_distances),
            "avg": np.mean(non_zero_distances)
        }
        
    def travel_time(self, source_id, target_id):
        try:
            return self.time_matrix[(source_id, target_id)]
        except KeyError:
            pass
        try:
            return self.time_matrix[(target_id, source_id)]
        except KeyError:
            raise KeyError(f"Source({source_id}) and Target({target_id}) not found in time matrix")

    def distance(self, source_id, target_id):
        try:
            return self.distance_matrix[(source_id, target_id)]
        except KeyError:
            pass
        try:
            return self.distance_matrix[(source_id, target_id)]
        except KeyError:
            raise KeyError(f"Source({source_id}) and Target({target_id}) not found in distance matrix")
        
class SyntheticGraphGenerator:
    def __init__(self, seed, graph_params) -> None:
        self.graph_params = graph_params
        self.seed = seed
        self.igraph = None
        self.__centroid_distance = None
        self.__num_centroids_per_axis = None
        self.__total_vertices = None

        np.random.seed(seed)
        self.graph: Graph = self.generate_graph()
        
    def generate_graph(self) -> Graph:
        self.__calculate_graph_properties()
        self.__generate_centroids()
        self.__generate_locations()
        return to_custom_graph(self.igraph)

    def __calculate_graph_properties(self):

        # Graph Parameters
        num_locations = self.graph_params['num_locations']
        num_centroids = self.graph_params['clusters']
        grid_size = self.graph_params['grid_size']

        self.__total_vertices = num_locations + num_centroids
        self.__num_centroids_per_axis = math.ceil(np.sqrt(num_centroids))
        self.__centroid_distance = grid_size / self.__num_centroids_per_axis

        self.igraph = ig.Graph.Full(n=self.__total_vertices)
        self.igraph.vs['is_centroid'] = [False for _ in range(self.__total_vertices)]
        self.igraph.vs['coordinate'] = [None for _ in range(self.__total_vertices)]
        self.igraph.vs['location_id'] = [id for id in range(self.__total_vertices)]
        self.igraph.vs['centroid'] = [None for _ in range(self.__total_vertices)]

    def __generate_centroids(self):
        
        # Graph parameters
        num_centroids = self.graph_params['clusters']
        grid_size = self.graph_params['grid_size']

        x_coordinates = np.arange(self.__centroid_distance/2, grid_size, self.__centroid_distance)
        y_coordinates = np.arange(self.__centroid_distance/2, grid_size, self.__centroid_distance)

        X, Y = np.meshgrid(x_coordinates, y_coordinates)
        centroid_coordinates = map(tuple, np.stack([X.ravel(), Y.ravel()]).T)

        for centroid_id, coordinate in zip(range(num_centroids), centroid_coordinates):
            self.igraph.vs[centroid_id]['coordinate'] = coordinate
            self.igraph.vs[centroid_id]['is_centroid'] = True
            self.igraph.vs[centroid_id]['cluster'] = []
            self.igraph.vs[centroid_id]['centroid'] = centroid_id
    
    def __generate_locations(self):
        centroids = self.igraph.vs.select(is_centroid_eq=True)
        locations = self.igraph.vs.select(is_centroid_eq=False)
        locations_per_centroid = \
            np.array_split(locations, len(centroids))
        
        # Bridson Sampling Parameters
        dims = np.array([self.__centroid_distance, self.__centroid_distance])
        radius = self.graph_params['min_location_distance']
        for centroid, locations in zip(centroids, locations_per_centroid):
            centroid_x, centroid_y = centroid['coordinate']
            offset = [centroid_x - dims[0]/2, centroid_y - dims[1]/2]
            samples = \
                Bridson_sampling(num_samples=len(locations), dims=dims, radius=radius)
            location_coordinates = \
                samples[(samples[:, 0] != dims[0]/2) & (samples[:, 1] != dims[1]/2)] + offset
            
            for location, coordinate in zip(locations, map(tuple, location_coordinates)):
                location['coordinate'] = coordinate
                location['centroid'] = centroid
                centroid['cluster'].append(location)
        
        # Compute time and distance matrix

        for edge in self.igraph.es:
            source_index = edge.source
            target_index = edge.target

            speed = None
            if self.igraph.vs[source_index]['centroid'] != self.igraph.vs[target_index]['centroid']:
                speed = self.graph_params['long_avg_vehicle_speed'] * 1000 / 60
            else:
                speed = self.graph_params['short_avg_vehicle_speed'] * 1000 / 60
                
            source_coordinate = np.array(self.igraph.vs[source_index]["coordinate"])
            target_coordinate = np.array(self.igraph.vs[target_index]["coordinate"])
            distance = round(np.linalg.norm(source_coordinate - target_coordinate), 2)
            travel_time = round(distance / speed, 0)

            edge["distance"] = distance
            edge["travel_time"] = travel_time

class DatasetGraphGenerator:

    def __init__(self, graph_params) -> None:
        self.dataset_path = graph_params['dataset']
        self.short_avg_vehicle_speed = graph_params['short_avg_vehicle_speed']
        self.long_avg_vehicle_speed = graph_params['long_avg_vehicle_speed']

        self.num_locations = graph_params['num_locations']
        self.centroid_codes = graph_params['centroid_codes']
        self.igraph = None
        self.graph = None
        self.generate_graph()

    def generate_graph(self) -> Graph:
        df = pd.read_csv(f"./dataset/{self.dataset_path}.csv", header=0)
        df.columns = df.columns.str.strip()
        filtered_df = df[["ATCOCode", "LocalityName", "Longitude", "Latitude"]]
        groups = dict()
        
        for code in self.centroid_codes:
            temp = filtered_df[filtered_df[filtered_df.columns[0]] == code]
            locality_name = temp['LocalityName'].iloc[0]
            groups[locality_name] = dict()
            groups[locality_name]["df"] = filtered_df[filtered_df["LocalityName"] == locality_name]
            groups[locality_name]['code'] = code

        curr_idx = 0
        igraph = ig.Graph.Full(n=sum(self.num_locations), loops=False)
        igraph.vs['is_centroid'] = False
        igraph.vs['cluster'] = None
        
        for index, (locality_name, info_dict) in enumerate(groups.items()):
            start = curr_idx
            df = info_dict['df']
            code = info_dict['code']
            end = curr_idx + self.num_locations[index]
            igraph.vs[start:end]['location_id'] = list(df[df.columns[0]])
            igraph.vs[start:end]['coordinate'] = list(zip(df['Latitude'], df['Longitude']))
            igraph.vs[start:end]['centroid'] = locality_name

            centroid_code = code
            centroid = igraph.vs[start:end].find(location_id_eq=centroid_code)
            centroid['is_centroid'] = True
            centroid['cluster'] = igraph.vs[start:end].select(location_id_ne=centroid_code)
            curr_idx += end
        
        for edge in igraph.es:
            source_vertex = igraph.vs[edge.source]
            target_vertex = igraph.vs[edge.target]
            
            source_coordinates = source_vertex["coordinate"]
            target_coordinate = target_vertex["coordinate"]
            distance = haversine(source_coordinates, target_coordinate, unit=Unit.METERS)

            speed = None
            if source_vertex['centroid'] != target_vertex['centroid']:
                speed = self.long_avg_vehicle_speed * 1000 / 60
            else:
                speed = self.short_avg_vehicle_speed * 1000 / 60

            travel_time = round(distance / speed, 2)
            edge["distance"] = distance
            edge["travel_time"] = travel_time
        
        self.igraph = igraph
        self.graph = to_custom_graph(self.igraph)