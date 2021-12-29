
from models.passenger import Passenger
from models.solution import TourNodeValue

# Evaluation Function for Solution
def solution_utility(rider, solution):
    departure_time = solution.rider_schedule.get("departure").get(rider.id)
    arrival_time = solution.rider_schedule.get("arrival").get(rider.id)
    return rider.utility(departure_time, arrival_time)

def node_utility(rider: Passenger, depart_node_val, arrival_node_val: TourNodeValue=None):
    if arrival_node_val is None:
        departure_time = depart_node_val.departure_time
        return rider.utility(departure_time=departure_time, arrival_time=None)
    else:
        departure_time = depart_node_val.departure_time
        arrival_time = arrival_node_val.arrival_time
        return rider.utility(departure_time=departure_time, arrival_time=arrival_time)
