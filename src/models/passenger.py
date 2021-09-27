from os import replace
import numpy as np
from typing import List, Tuple

from numpy.core.fromnumeric import size

class Passenger:

    """Model for Passenger

    Attributes
    ----------
    id: int
        Identifier for this Passenger
    start_id: int
        ID of this Passenger's origin station
    destination_id: int
        ID of this Passenger's destination station
    beta: float
        Convenience parameter. Higher beta means that this
        Passenger is less affected by temporal deviation,
        and vice versa
    optimal_departure: int
        Most preferred departure time
    optimal_arrival: int
        Most preferred arrival time

    Methods
    ----------
    get_utility_by_time(departure_time, arrival_time)
        Obtain rider's utility by directly supplying their
        departure and arrival time

    """
    def __init__(self, id: int, beta: float, location_pair: Tuple[int, int], temporal_preferences: Tuple[int, int]):
        self.id = id
        self.start_id = location_pair[0]
        self.destination_id = location_pair[1]
        self.beta = beta
        self.optimal_departure = temporal_preferences[0]
        self.optimal_arrival = temporal_preferences[1]

    def __utility_function(self, departure_time: int, arrival_time: int) -> float:
        utility = (self.beta**(abs(self.optimal_departure - departure_time)) + \
            self.beta**(abs(self.optimal_arrival - arrival_time))) / 2

        return utility
        
    def utility(self, departure_time: int, arrival_time: int) -> float:
        return self.__utility_function(departure_time, arrival_time)
    
    def __str__(self) -> str:
        return f"P:{self.id}"
    
    def __repr__(self) -> str:
        return self.__str__()

class PassengerGenerator:
    def __init__(self, seed, graph, passenger_params) -> None:
        self.seed = seed
        self.graph = graph
        self.passenger_params = passenger_params

        self.beta_distribution = None
        self.preference_distribution = None

        np.random.seed(seed)
        self.passengers = self.generate_passengers()
    
    def generate_passengers(self) -> List[Passenger]:
        
        passengers = []
        beta_distribution = self.__beta_distribution()
        self.beta_distribution = beta_distribution 
        location_pairs = self.__generate_locations()
        preferences = self.__generate_preferences(location_pairs)
        self.preference_distribution = preferences

        for id, beta, location_pair, preference in \
            zip(
                range(self.passenger_params['num_passengers']),
                beta_distribution,
                location_pairs,
                preferences
            ):
            passengers.append(Passenger(id, beta, location_pair, preference))

        return passengers

    def __generate_locations(self):
        num_passengers = self.passenger_params['num_passengers']
        cluster_travelling = self.passenger_params['inter_cluster_travelling']
        location_pairs = []

        if cluster_travelling:
            choices = ["cluster", "normal"]
            probability = [0.6, 0.4]

            for _ in range(num_passengers):
                option = np.random.choice(choices, p=probability)
                if option == "cluster":
                    cluster_info = self.graph.cluster_info
                    start, destination = \
                        np.random.choice(list(cluster_info.keys()), size=2, replace=False)
                    location_pairs.append((start, destination))
                else:
                    location_ids = self.graph.locations
                    location_pair = np.random.choice(location_ids, size=2, replace=False)
                    location_pairs.append(tuple(location_pair))

    
        else:
            location_ids = self.graph.locations
            for _ in range(num_passengers):
                location_pair = np.random.choice(location_ids, size=2, replace=False)
                location_pairs.append(tuple(location_pair))
        
        return location_pairs
    
    def __beta_distribution(self):
        beta_dist = self.passenger_params['beta_distribution']

        if beta_dist == "truncated_normal":
            return self.__truncated_normal_dist(0.5, 0.15, 0, 1)
        elif beta_dist == "uniform":
            return self.__uniform_dist()
        
        elif beta_dist == "sensitive":
            return np.random.beta(20, 65, self.passenger_params['num_passengers'])
        
        elif beta_dist == "non_sensitive":
            return np.random.beta(65, 20, self.passenger_params['num_passengers'])
            

    def __uniform_dist(self):
        n_samples = self.passenger_params['num_passengers']
        return np.random.uniform(0, 1, n_samples)
    
    def __truncated_normal_dist(self, loc, scale, min, max):
        n_samples = self.passenger_params['num_passengers']
        samples = np.zeros((0,))
        while samples.shape[0] < n_samples: 
            s = np.random.normal(loc, scale, size=(n_samples,))
            accepted = s[(s >= min) & (s <= max)]
            samples = np.concatenate((samples, accepted), axis=0)
        samples = samples[:n_samples]
        return samples

    def __generate_preferences(self, location_pairs):
        preference_dist = self.passenger_params['preference_distribution']
        service_hours = self.passenger_params['service_hours']
        service_minutes = service_hours * 60
    
        preferences = []

        if preference_dist == "peak_hours":
            morning_time_frame = (420, 560)
            evening_time_frame = (1020, 1140)

            time_frames = [morning_time_frame, evening_time_frame]
            probabilities = [0.4, 0.4, 0.2]

            for start, destination in location_pairs:
                travel_time = self.graph.travel_time(start, destination)
                normal_frame = (0, 1440 - travel_time)

                time_frames.append(normal_frame)
                idx = np.random.choice(len(time_frames), p=probabilities)
                selected_time_frame = time_frames[idx]
                
    
                start, end = selected_time_frame[0], selected_time_frame[1]
                optimal_departure = np.random.uniform(start, end)
                optimal_arrival = optimal_departure + travel_time

                time_frames.remove(normal_frame)
                preferences.append((optimal_departure, optimal_arrival))

        elif preference_dist == "uniform" or \
            preference_dist == None:
            for start, destination in location_pairs:
                travel_time = self.graph.travel_time(start, destination)
                optimum_departure = int(np.random.uniform(0, service_minutes - travel_time))
                optimum_arrival = optimum_departure + travel_time
                preferences.append((optimum_departure, optimum_arrival))

        return preferences