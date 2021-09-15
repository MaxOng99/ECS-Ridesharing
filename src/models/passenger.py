import numpy as np
from typing import List

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
    def __init__(self, id: int, start: int, destination: int, optimal_departure: int, optimal_arrival: int):
        self.id = id
        self.start_id = start
        self.destination_id = destination
        self.beta = np.random.uniform(0.1, 1)
        self.optimal_departure = optimal_departure
        self.optimal_arrival = optimal_arrival

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
    def __init__(self, graph, passenger_params) -> None:
        self.graph = graph
        self.passenger_params = passenger_params
        self.passengers = self.generate_passengers()
    
    def generate_passengers(self) -> List[Passenger]:
        
        num_passengers = self.passenger_params['num_passengers']
        cluster_info = self.graph.cluster_info
        location_ids = self.graph.locations
        passengers = []

        for id in range(num_passengers):
            # Sample 2 elements w/o replacement - avoids having same start and end location
            start_target_ids = np.random.choice(location_ids, size=2, replace=False)
            start_id, destination_id = start_target_ids[0], start_target_ids[1]
            optimal_departure, optimal_arrival = self.__generate_preferences(start_id, destination_id)
            passengers.append(Passenger(id, start_id, destination_id, optimal_departure, optimal_arrival))

        return passengers

    def __generate_preferences(self, source: int, destination: int):
        service_hours = self.passenger_params['service_hours']
        service_minutes = service_hours * 60
        travel_time = self.graph.travel_time(source, destination)
        optimum_departure = int(np.random.uniform(0, service_minutes - travel_time))
        optimum_arrival = optimum_departure + travel_time

        return (optimum_departure, optimum_arrival)