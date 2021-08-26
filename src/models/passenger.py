import random

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
        self.beta = random.uniform(0.1, 1)
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
