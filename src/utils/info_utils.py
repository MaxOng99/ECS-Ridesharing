from prettytable import PrettyTable

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
        row_data = [index, tour_node.value.location_id, list(tour_node.value.pick_up), list(tour_node.value.drop_off), tour_node.value.arrival_time, tour_node.value.waiting_time, tour_node.value.departure_time]
        schedule.add_row(row_data)

    for agent in solution.agents:
        departure_time = agent.departure_node.value.departure_time
        arrival_time = agent.arrival_node.value.arrival_time
        utility = agent.rider.utility(departure_time, arrival_time)
        row_data = [f'P:{agent.rider.id}', f'{agent.rider.start_id} - {agent.rider.destination_id}', agent.rider.optimal_departure, departure_time, agent.rider.optimal_arrival, arrival_time, utility]
        rider_sched.add_row(row_data)
    
    return "\n".join(['Schedule', f'{schedule.get_string()}', 'Rider Utils', rider_sched.get_string()]) 
    
def strategy_info(strat_obj):
    info = []

    if strat_obj.strat['action'] == 'wait':
        info = [
            f'{strat_obj.__class__.__name__}, Wait',
            f'Ref_Node: {strat_obj.strat["ref_node"]}',
            f'Ref_Node_Old_Value {strat_obj.strat["ref_node_old_value"]}',
            f'Ref_Node_New_Value{strat_obj.strat["ref_node_new_value"]}',
            f'Next_Node: {strat_obj.strat["next_node"]}',
            f'Next_Node_Old_Value: {strat_obj.strat["next_node_old_value"]}',
            f'Next_Node_New_Value: {strat_obj.strat["next_node_new_value"]}'
        ]
        return "\n".join(info)
    
    elif strat_obj.strat['action'] == 'insert_before':
        info = [
            f'{strat_obj.__class__.__name__}, Insert Before',
            f'Ref_Node: {strat_obj.strat["ref_node"]}',
            f'Next_Node: {strat_obj.strat["next_node"]}',
            f'Next_Node_Old_Value: {strat_obj.strat["next_node_old_value"]}',
            f'Next_Node_New_Value: {strat_obj.strat["next_node_new_value"]}',
            f'New_Node_Value: {strat_obj.strat["new_node_value"]}',
        ]
        return "\n".join(info)

    elif strat_obj.strat['action'] == 'insert_after':
        info = [
            f'{strat_obj.__class__.__name__}, Insert After',
            f'Ref_Node: {strat_obj.strat["ref_node"]}',
            f'Next_Node: {strat_obj.strat["next_node"]}',
            f'Next_Node_Old_Value: {strat_obj.strat["next_node_old_value"]}',
            f'Next_Node_New_Value: {strat_obj.strat["next_node_new_value"]}',
            f'New_Node_Value: {strat_obj.strat["new_node_value"]}'
        ]
        return "\n".join(info)