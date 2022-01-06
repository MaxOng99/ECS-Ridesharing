from os import closerange
from prettytable import PrettyTable
from pathlib import Path
import yaml
import csv
import re
import numpy as np

def environment_info(env: 'Environment') -> str:
    """
    Returns:
        string: Displays the summary of the environment
    """
    # Display Environment Properties
    environment_properties = PrettyTable()
    environment_properties.field_names = ["Properties", "Value"]
    environment_properties.add_rows([["num_locations", env.num_locations],
    ["num_passengers", env.num_passengers],
    ["vehicle speed", f"{env.avg_speed} km/min"]])

    # Display Passenger Details
    passengers = [[p.id, p.start_id, p.destination_id] for p in env.passengers]
    passenger_list = PrettyTable()
    passenger_list.add_rows(passengers)
    passenger_list.field_names = ["Passenger ID", "Start Location ID", "Destination ID"]

    # Display Graph Details
    graph_properties = PrettyTable()
    graph_properties_row = []
    for location_1, location_2 in env.graph.get_edgelist():

        edge_id = env.graph.get_eid(location_1, location_2)
        row_data = [edge_id, location_1, location_2, env.graph.es[edge_id]['travel_time']]
        graph_properties_row.append(row_data)
    
    graph_properties.add_rows(graph_properties_row)
    graph_properties.field_names = ["Edge ID", "Location 1", "Location 2", "Time Taken (min)"]
    
    return "\n".join(["Environment Properties:",
    f"{environment_properties.get_string()} \n",
    "Passengers:",
    f"{passenger_list.get_string()} \n",
    "Graph:",
    graph_properties.get_string()])

def solution_info(solution: "Solution") -> str:

    schedule = PrettyTable()
    schedule.field_names = ['Visit Order', 'Location ID', 'Pick Ups', 'Drop Offs', 'Arrival', 'Wait Time', 'Departure Time']

    rider_sched = PrettyTable()
    rider_sched.field_names = ['Passenger', 'Travel Locations', 'Departure', 'Actual Departure', 'Arrival', 'Actual Arrival', 'Utility']

    for index, tour_node in enumerate(solution.llist.iternodes()):
        row_data = [index, tour_node.value.location_id, list(tour_node.value.pick_ups), list(tour_node.value.drop_offs), tour_node.value.arrival_time, tour_node.value.waiting_time, tour_node.value.departure_time]
        schedule.add_row(row_data)

    for rider in solution.riders:
        departure_time = solution.rider_schedule['departure'][rider.id]
        arrival_time = solution.rider_schedule['arrival'][rider.id]
        utility = rider.utility(departure_time, arrival_time)
        row_data = [f'P:{rider.id}', f'{rider.start_id} - {rider.destination_id}', rider.optimal_departure, departure_time, rider.optimal_arrival, arrival_time, utility]
        rider_sched.add_row(row_data)
    
    return "\n".join(['Schedule', f'{schedule.get_string()}', 'Rider Utils', rider_sched.get_string()]) 
    
def strategy_info(strat_obj):
    info = []

    if strat_obj.strat['action'] == 'stay':
        info = [
            f'Action: Wait',
            f"allocated_node: {strat_obj.strat['allocated_node']}",
            f"agent: {strat_obj.strat['agent']}"
        ]
        return "\n".join(info)
    
    elif strat_obj.strat['action'] == 'insert_before':
        info = [
            f'Action: Insert Before',
            f'Ref_Node: {strat_obj.strat["ref_node"]}',
            f"allocated_node: {strat_obj.strat['allocated_node']}",
            f"agent: {strat_obj.strat['agent']}"
        ]
        return "\n".join(info)

    elif strat_obj.strat['action'] == 'insert_after':
        info = [
            f'Action: Insert After',
            f'Ref_Node: {strat_obj.strat["ref_node"]}',
            f"allocated_node: {strat_obj.strat['allocated_node']}",
            f"agent: {strat_obj.strat['agent']}"
        ]
        return "\n".join(info)
    
    return ""
