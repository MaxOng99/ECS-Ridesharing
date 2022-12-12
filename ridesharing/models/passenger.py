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
        
        np.random.seed(seed)
        self.passengers = self.generate_passengers()

    def generate_passengers(self) -> List[Passenger]:
        passengers = []
        beta_dist = self.__beta_distribution(self.alpha, self.beta)
        self.beta_distribution = beta_dist

        # New way of generating preferences with hotspots
        if self.passenger_params.get('num_hotspots', None):
            passengers = []
            beta_dist = self.__beta_distribution(self.alpha, self.beta)
            self.beta_distribution = beta_dist
            preferences = self.__generate_preferences()

            for id, beta, preference in zip(
                range(self.num_passengers),
                beta_dist,
                preferences,
            ):
                p = Passenger(id, beta, [preference['departure_location'], preference['arrival_location']], [preference['optimum_departure'], preference['optimum_arrival']])
                passengers.append(p)

            return passengers

        # Old way of generating preferences
        else:
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
        location_pairs = []
        location_ids = self.graph.locations()

        for _ in range(self.num_passengers):    
            start_loc, end_loc = \
                np.random.choice(location_ids, size=2, replace=False)
            location_pairs.append((start_loc, end_loc))
        
        return location_pairs

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

    # New preference generator that includes hotspots
    def __generate_preferences(self):
        locations = self.graph.locations()
        num_hotspots: int = self.passenger_params['num_hotspots']

        hotspot_locations = np.random.choice(locations, size=num_hotspots, replace=False)
        morning_hotspots = np.random.choice(hotspot_locations, size=num_hotspots // 2, replace=False)
        evening_hotspots = np.random.choice([location for location in hotspot_locations if location not in morning_hotspots], size=len(hotspot_locations) - len(morning_hotspots), replace=False)

        preferences = {
            'peak': {
                'config': [((420, 560), morning_hotspots), ((1020, 1140), evening_hotspots)]
            },
            'non_peak': {
                'config': [((0, 1440), locations)]
            }
        }

        preferences_type = \
            np.random.choice(['peak', 'non_peak'], size=self.num_passengers, p=[self.peak_probability, 1-self.peak_probability])
        
        generated_preferences = []
        for preference_type in preferences_type:
            configs = preferences[preference_type]['config']
            config_index = np.random.choice(len(configs))
            selected_config = configs[config_index]
            time_frame, locations = selected_config

            departure_location, arrival_location = np.random.choice(locations, size=2, replace=False)
            optimum_departure = np.random.randint(time_frame[0], time_frame[1] + 1)
            optimum_arrival = optimum_departure + self.graph.travel_time(departure_location, arrival_location)

            generated_preferences.append({
                'optimum_departure': optimum_departure,
                'optimum_arrival': optimum_arrival,
                'departure_location': departure_location,
                'arrival_location': arrival_location,
            })

        return generated_preferences