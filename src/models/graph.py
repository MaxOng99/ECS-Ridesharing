import igraph as ig
import numpy as np
import math

# Graph Model. Any custom graph generators should produce a Graph object
class Graph:
    def __init__(self, num_locations, num_centroids, location_ids, cluster_info, time_matrix, distance_matrix) -> None:
        self.num_locations = num_locations
        self.num_centroids = num_centroids
        self.locations = location_ids
        self.time_matrix = time_matrix
        self.cluster_info = cluster_info
        self.distance_matrix = distance_matrix
        
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
    def __init__(self, graph_params) -> None:
        self.graph_params = graph_params
        self.__igraph = None
        self.__centroid_distance = None
        self.__num_centroids_per_axis = None
        self.__intra_cluster_min_distance = None
        self.__total_vertices = None

        self.graph: Graph = self.generate_graph()
        
    def generate_graph(self) -> Graph:
        self.__calculate_graph_properties()
        self.__generate_centroids()
        self.__generate_locations()
        return self.__to_custom_graph()

    def __calculate_graph_properties(self):

        # Graph Parameters
        num_locations = self.graph_params['num_locations']
        num_centroids = self.graph_params['clusters']
        grid_size = self.graph_params['grid_size']

        self.__total_vertices = num_locations + num_centroids
        self.__num_centroids_per_axis = math.ceil(np.sqrt(num_centroids))
        self.__centroid_distance = grid_size / self.__num_centroids_per_axis
        self.__intra_cluster_min_distance = \
            self.__centroid_distance / (num_locations / num_centroids)
        
        
        self.__igraph = ig.Graph.Full(n=self.__total_vertices)
        self.__igraph.vs['is_centroid'] = [False for _ in range(self.__total_vertices)]
        self.__igraph.vs['coordinate'] = [None for _ in range(self.__total_vertices)]
        self.__igraph.vs['location_id'] = [id for id in range(self.__total_vertices)]

    def __generate_centroids(self):
        
        # Graph parameters
        num_centroids = self.graph_params['clusters']
        grid_size = self.graph_params['grid_size']

        x_coordinates = np.arange(self.__centroid_distance/2, grid_size, self.__centroid_distance)
        y_coordinates = np.arange(self.__centroid_distance/2, grid_size, self.__centroid_distance)

        X, Y = np.meshgrid(x_coordinates, y_coordinates)
        centroid_coordinates = map(tuple, np.stack([X.ravel(), Y.ravel()]).T)

        for centroid_id, coordinate in zip(range(num_centroids), centroid_coordinates):
            self.__igraph.vs[centroid_id]['coordinate'] = coordinate
            self.__igraph.vs[centroid_id]['is_centroid'] = True
            self.__igraph.vs[centroid_id]['cluster'] = []
    
    def __generate_locations(self):
        centroids = self.__igraph.vs.select(is_centroid_eq=True)
        locations = self.__igraph.vs.select(is_centroid_eq=False)
        locations_per_centroid = \
            np.array_split(locations, len(centroids))
        
        for centroid, locations in zip(centroids, locations_per_centroid):
            centroid_x, centroid_y = centroid['coordinate']

            theta = np.random.uniform(0,2*np.pi, len(locations))
            radius = np.random.uniform(0, self.__centroid_distance/2, len(locations))
            x = centroid_x + radius * np.cos(theta)
            y = centroid_y + radius * np.sin(theta)

            location_coordinates = zip(x, y)
            
            for location, coordinate in zip(locations, location_coordinates):
                location['coordinate'] = coordinate
                centroid['cluster'].append(location)
        
        # Compute time and distance matrix
        avg_speed = self.graph_params['avg_vehicle_speed'] * 1000 / 60

        for edge in self.__igraph.es:
            source_index = edge.source
            target_index = edge.target

            source_coordinate = np.array(self.__igraph.vs[source_index]["coordinate"])
            target_coordinate = np.array(self.__igraph.vs[target_index]["coordinate"])
            distance = round(np.linalg.norm(source_coordinate - target_coordinate), 2)
            travel_time = round(distance / avg_speed, 0)

            edge["distance"] = distance
            edge["travel_time"] = travel_time
    
    def __to_custom_graph(self):
        time_matrix = dict()
        distance_matrix = dict()

        for edge in self.__igraph.es:
            source_vertex = self.__igraph.vs[edge.source]
            target_vertex = self.__igraph.vs[edge.target]

            source_id = source_vertex["location_id"]
            target_id = target_vertex["location_id"]

            time_matrix[(source_id, target_id)] = edge["travel_time"]
            time_matrix[(source_id, source_id)] = 0
            time_matrix[(target_id, target_id)] = 0

            distance_matrix[(source_id, target_id)] = edge["distance"]
            distance_matrix[(source_id, source_id)] = 0
            distance_matrix[(target_id, target_id)] = 0
        
        location_vertices = self.__igraph.vs.select(is_centroid_eq=False)
        location_ids = [location_vertex['location_id'] for location_vertex in location_vertices]

        # Cluster info
        centroids = self.__igraph.vs.select(is_centroid_eq=True)
        cluster_info = dict()

        for centroid in centroids:
            cluster_info[centroid['location_id']] = [location['location_id'] for location in centroid['cluster']]

        return Graph(self.graph_params['num_locations'], self.graph_params['clusters'], location_ids, cluster_info, time_matrix, distance_matrix)


# Might be useful
# dims = np.array([self.__centroid_distance, self.__centroid_distance])
# sampled_coordinates = \
#     pd.Bridson_sampling(num_samples=len(locations)+1, dims=dims, radius=self.__intra_cluster_min_distance)
# offset = [centroid_x - dims[0]/2, centroid_y - dims[1]/2]
# location_coordinates = \
#     [coor for coor in map(tuple, sampled_coordinates + offset)]

# if centroid['coordinate'] in location_coordinates:
#     location_coordinates.remove(centroid['coordinate'])