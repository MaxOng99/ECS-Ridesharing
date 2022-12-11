
from numpy import add
from models.passenger import Passenger
from models.solution import TourNodeValue

# Evaluation Function for Solution
def solution_utility(rider, solution, additional_info=None):
    departure_time = solution.rider_schedule.get("departure").get(rider.id)
    arrival_time = solution.rider_schedule.get("arrival").get(rider.id)
    return rider.utility(departure_time, arrival_time)

def node_utility(rider: Passenger, node, additional_info=None):
    graph = additional_info['graph']
    departure_node = additional_info['rider_depart_node_dict'].get(rider, None)
    node_val = node.value

    if departure_node is None:
        if node_val.location_id == rider.start_id:
            departure_time = node_val.departure_time
            return rider.utility(departure_time=departure_time, arrival_time=None)
        else:
            potential_departure_time = node_val.departure_time + graph.travel_time(node_val.location_id, rider.start_id)
            return rider.utility(departure_time=potential_departure_time, arrival_time=None)

    else:
        if node_val.location_id == rider.destination_id:
            departure_time = departure_node.value.departure_time
            arrival_time = node_val.arrival_time
            return rider.utility(departure_time=departure_time, arrival_time=arrival_time)
        else:
            departure_time = departure_node.value.departure_time
            potential_arrival_time = node_val.departure_time + graph.travel_time(node_val.location_id, rider.destination_id)
            return rider.utility(departure_time=departure_time, arrival_time=potential_arrival_time)
        
def location_utility(rider, new_location, additional_info=None) -> float:
    graph = additional_info['graph']
    current_node = additional_info['current_node']
    departure_node = additional_info['rider_depart_node_dict'].get(rider, None)

    travel_time = graph.travel_time(current_node.value.location_id, new_location)
    new_location_arrival_time = current_node.value.departure_time + travel_time
    
    # Make sure node exist in the linked list solution
    if departure_node is None:
        potential_departure_time = new_location_arrival_time + graph.travel_time(new_location, rider.start_id)
        potential_arrival_time = potential_departure_time + graph.travel_time(rider.start_id, rider.destination_id)
        return rider.utility(potential_departure_time, potential_arrival_time)
    else:
        departure_time = departure_node.value.departure_time
        potential_arrival_time = new_location_arrival_time + graph.travel_time(rider.start_id, rider.destination_id)
        return rider.utility(departure_time, potential_arrival_time)
