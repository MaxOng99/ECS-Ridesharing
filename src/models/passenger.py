import numpy as np
from typing import List, Tuple

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
    def __init__(self, seed, graph, passenger_params) -> None:
        self.seed = seed
        self.graph = graph
        self.passenger_params = passenger_params

        self.beta = self.passenger_params['beta_distribution']['beta']
        self.alpha = self.passenger_params['beta_distribution']['alpha']
        self.inter_cluster_travelling = self.passenger_params['preference_distribution']['inter_cluster_travelling']
        self.peak_probabilities = self.passenger_params['preference_distribution']['peak_probabilities']
        self.service_hours = self.passenger_params['service_hours']
        self.num_passengers = self.passenger_params['num_passengers']
        self.time_step = self.passenger_params['preference_distribution']['time_step']
        self.preference_distribution = None


        np.random.seed(seed)
        self.passengers = self.generate_passengers()
    
    def generate_passengers(self) -> List[Passenger]:
        passengers = []
        beta_distribution = self.__beta_distribution(self.alpha, self.beta)
        self.beta_distribution = beta_distribution 
        preferences, location_pairs = self.__generate_preferences()
        self.preference_distribution = preferences

        for id, beta, location_pair, preference in \
            zip(
                range(self.passenger_params['num_passengers']),
                beta_distribution,
                location_pairs,
                preferences
            ):
            p = Passenger(id, beta, location_pair, preference)
            passengers.append(p)
            self.graph.location_mapping[location_pair[0]] = p
            self.graph.location_mapping[location_pair[1]] = p

        return passengers
    
    def __beta_distribution(self, alpha, beta):
        return np.random.beta(alpha, beta, self.passenger_params['num_passengers'])            
    
    def __generate_preferences(self):
        
        service_minutes = self.service_hours * 60
        preferences = []
        locations = []

        if self.inter_cluster_travelling:
            clusters = list(self.graph.cluster_info.keys())
            cluster_info = self.graph.cluster_info
            morning_start, morning_end = np.random.choice(clusters, size=2, replace=False)
            evening_start, evening_end = morning_end, morning_start

            morning_frame = (420, 560)
            evening_frame = (1020, 1140)
            normal_frames = [(0, 420), (560, 1020), (1140, 1440)]

            time_frames = ["morning", "evening", "normal"]

            probabilities = [0.35, 0.35, 0.3]

            for _ in range(self.num_passengers):
                label_to_range = {
                    "morning": morning_frame,
                    "evening": evening_frame,
                    "normal": normal_frames[np.random.choice(len(normal_frames))]
                }

                range_to_location = {
                    (0, 420): np.random.choice(cluster_info[morning_start], size=2, replace=False),
                    (420, 560): (morning_start, morning_end),
                    (560, 1020): np.random.choice(cluster_info[evening_start], size=2, replace=False),
                    (1020, 1140): (evening_start, evening_end),
                    (1140, 1440): np.random.choice(cluster_info[morning_start], size=2, replace=False)
                }

                selected_time_frame = np.random.choice(time_frames, p=probabilities)
                start_time, end_time = label_to_range[selected_time_frame]
                start_location, end_location = range_to_location[(start_time, end_time)]
                optimum_departure = np.random.choice(np.arange(start_time, end_time, self.time_step))
                optimal_arrival = optimum_departure + self.graph.travel_time(start_location, end_location)
                preferences.append((optimum_departure, optimal_arrival))
                locations.append((start_location, end_location))

        else:
            for _ in range(self.passenger_params['num_passengers']):
                start, end = np.random.choice(self.graph.locations, size=2, replace=False)
                travel_time = self.graph.travel_time(start, end)
                optimum_departure = np.random.choice(np.arange(0, service_minutes, self.time_step))
                optimum_arrival = optimum_departure + travel_time
                preferences.append((optimum_departure, optimum_arrival))
                locations.append((start, end))

        return preferences, locations  