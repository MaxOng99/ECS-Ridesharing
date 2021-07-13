from prettytable import PrettyTable

from models.environment import Environment

def environment_info(env: Environment) -> str:
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