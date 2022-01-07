import numpy as np
from typing import Counter, List, Tuple

from models.graph import Graph

class Passenger:
    def __init__(self, id: int, beta: float, location_pair: Tuple[int, int], temporal_preferences: Tuple[int, int]):
        self.id = id
        self.start_id = location_pair[0]
        self.destination_id = location_pair[1]
        self.beta = beta
        self.optimal_departure = temporal_preferences[0]
        self.optimal_arrival = temporal_preferences[1]

    def __utility_function(self, departure_time: int, arrival_time: int) -> float:
        depart_utility = self.beta**(abs(self.optimal_departure - departure_time))
        arrival_utility = 0 if not arrival_time else self.beta**(abs(self.optimal_arrival - arrival_time))
        return (depart_utility + arrival_utility) / 2

    def utility(self, departure_time: int, arrival_time: int) -> float:
        return self.__utility_function(departure_time, arrival_time)
    
    def __str__(self) -> str:
        return f"P:{self.id}"
    
    def __repr__(self) -> str:
        return self.__str__()

class PassengerGenerator:
    def __init__(self, seed, graph: Graph, passenger_params) -> None:
        self.seed = seed
        self.graph = graph
        self.passenger_params = passenger_params

        self.beta = self.passenger_params['beta']
        self.alpha = self.passenger_params['alpha']
        self.peak_probability = self.passenger_params['peak_probability']
        self.num_passengers = self.passenger_params['num_passengers']
        self.centroid_likelihood = self.passenger_params['centroid_likelihood']
        self.inter_cluster_prob = self.passenger_params['inter_cluster_probability']

        np.random.seed(seed)
        self.passengers = self.generate_passengers()

    def generate_passengers(self) -> List[Passenger]:
        passengers = []
        beta_dist = self.__beta_distribution(self.alpha, self.beta)
        self.beta_distribution = beta_dist
        loc_pairs = self.__generate_loc_preferences()
        time_preferences = self.__generate_time_preferences(loc_pairs)

        for id, beta, loc_pair, time_pref in zip(
            range(self.num_passengers),
            beta_dist,
            loc_pairs,
            time_preferences
        ):
            p = Passenger(id, beta, loc_pair, time_pref)
            passengers.append(p)

        return passengers

    def __beta_distribution(self, alpha, beta):
        return np.random.beta(alpha, beta, self.passenger_params['num_passengers'])            
    
    def __generate_loc_preferences(self):

        if self.inter_cluster_prob > 0:
            inter_loc_preferences = self.__inter_cluster_loc_preference()
            intra_loc_preferences = self.__intra_cluster_loc_preference()
            return inter_loc_preferences + intra_loc_preferences
        else:
            return self.__intra_cluster_loc_preference()

    def __intra_cluster_loc_preference(self):
        intra_loc_pairs = []
        centroid_ids = self.graph.centroid_ids()

        for _ in range(self.num_passengers):    
            selected_centroid = np.random.choice(centroid_ids)
            locations_of_centroid = self.graph.locations_of_centroid(selected_centroid)
            start_loc, end_loc = \
                np.random.choice(locations_of_centroid, size=2, replace=False)
            intra_loc_pairs.append((start_loc, end_loc))
        
        return intra_loc_pairs

    def __inter_cluster_loc_preference(self):
        centroid_ids = self.graph.centroid_ids()
        travel_types = \
            np.random.choice(['inter', 'intra'], size=self.num_passengers, p=[self.inter_cluster_prob, 1 - self.inter_cluster_prob])
        centroid_likelihood = self.centroid_likelihood

        counter = Counter(travel_types)

        inter_loc_pairs = []
        for _ in range(counter['inter']):
            start_centroid, end_centroid = \
                np.random.choice(centroid_ids, size=2, replace=False)
            depart_from_centroid, arrive_at_centriod = \
                np.random.choice([True, False], size=2, p=[centroid_likelihood, 1 - centroid_likelihood])
            
            if depart_from_centroid:
                start_loc = start_centroid
            else:
                start_centroid_locations = self.graph.locations_of_centroid(start_centroid)
                start_loc = np.random.choice(start_centroid_locations)
            
            if arrive_at_centriod:
                end_loc = end_centroid
            else:
                end_centroid_locations = self.graph.locations_of_centroid(end_centroid)
                end_loc = np.random.choice(end_centroid_locations)
            inter_loc_pairs.append((start_loc, end_loc))
        
        return inter_loc_pairs

    def __generate_time_preferences(self, loc_pairs):
        time_preferences = []
        peak_frames = [(420, 560), (1020, 1140)]
        non_peak_frames = [(0, 420), (560, 1020), (1140, 1440)]
        frame_category_list = np.random.choice(
            ["peak", "non_peak"],
            size=self.num_passengers,
            p=[self.peak_probability, 1 - self.peak_probability]
        )

        counter = Counter(frame_category_list)
        peak_frame_indices = np.random.choice(len(peak_frames), size=counter['peak'])
        peak_frame_list = [peak_frames[index] for index in peak_frame_indices]
        non_peak_indices = np.random.choice(len(non_peak_frames), size=counter['non_peak'])
        non_peak_frame_list = [non_peak_frames[index] for index in non_peak_indices]
        for frame, loc_pair in zip(peak_frame_list + non_peak_frame_list, loc_pairs):
            start, end = frame
            start_loc, end_loc = loc_pair
            optimum_departure = np.random.randint(start, end+1)
            optimum_arrival = optimum_departure + self.graph.travel_time(start_loc, end_loc)

            time_preferences.append((optimum_departure, optimum_arrival))

        return time_preferences