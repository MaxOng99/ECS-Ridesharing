from pathlib import Path

from numpy.lib.function_base import percentile
from numpy.random.mtrand import beta
import utils.graph_utils as graph_utils
import numpy as np
import csv
import yaml
import re

def write_illustration_output(graphs, beta_dists, preference_dists):
    output_path = Path("./illustrations")
    output_path.mkdir(parents=True, exist_ok=True)
    
    for id, (graph, beta_dist, preference_dist) in \
        enumerate(zip(graphs, beta_dists, preference_dists)):

        # Paths
        new_dir = Path(f"./illustrations/experiment_{id+1}")
        new_dir.mkdir(parents=True, exist_ok=True)
        graph_file = new_dir / "graph.png"
        beta_dist_file = new_dir / "beta_distribution.png"
        pref_dist_file = new_dir / "preference_distribution.png"

        graph_utils.plot_graph(graph, path=str(graph_file))
        graph_utils.plot_beta_distribution(beta_dist, path=str(beta_dist_file))
        graph_utils.plot_preference_distribution(preference_dist, path=str(pref_dist_file))

def write_simulation_output(config, solutions, elapsed):
    
    output_path = Path("./simulation_output")
    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
    regex = re.compile('experiment_\d+$')
    experiment_folders = []
    for file in Path(output_path).iterdir():
        if regex.match(file.name):
            experiment_folders.append(file.name)

    if experiment_folders:
        id = len(experiment_folders) + 1
    else:
        id = 1

    new_dir = Path(output_path, f"experiment_{id}")
    new_dir.mkdir(parents=True, exist_ok=True)
    config_file = new_dir / 'config.yaml'
    full_csv_file = new_dir / 'full_output.csv'
    local_summary_csv_file = new_dir / 'summary_output.csv'
    global_summary_csv_file = output_path / "summary_output.csv"
    fieldnames = None
    try:
        config['graph_params']['dataset']
        fieldnames = [
            'num_passengers',
            "alpha",
            "beta",
            "inter_cluster_travelling",
            "peak_probabilities",
            "time_step", 
            'service_hours',
            'num_locations',
            'centroid_codes',
            'dataset',
            'short_avg_vehicle_speed',
            'long_avg_vehicle_speed',
            'algorithm',
            'utilitarian',
            'egalitarian',
            'proportionality',
            'avg_utility',
            'gini_index',
            'percentile',
            'elapsed_time'
        ]
    except:

        fieldnames = [
            'num_passengers',
            "alpha",
            "beta",
            "inter_cluster_travelling",
            "peak_probabilities",
            "time_step",
            'service_hours',
            'num_locations',
            'clusters',
            'min_location_distance',
            'grid_size',
            'short_avg_vehicle_speed',
            'long_avg_vehicle_speed',
            'algorithm',
            'algorithm_params',
            'utilitarian',
            'egalitarian',
            'proportionality',
            'avg_utility',
            'gini_index',
            'percentile',
            'elapsed_time'
        ]

    # Flatten config dict
    passenger_params = config['passenger_params']
    beta_dist = passenger_params.pop("beta_distribution")
    preference_dist = passenger_params.pop("preference_distribution")
    passenger_params['beta'] = beta_dist['beta']
    passenger_params['alpha'] = beta_dist['alpha']
    passenger_params['inter_cluster_travelling'] = preference_dist['inter_cluster_travelling']
    passenger_params['peak_probabilities'] = preference_dist['peak_probabilities']

    graph_params = config['graph_params']
    optimiser_params = config['optimiser_params']
    algo_params = {
        'algorithm': f"{optimiser_params['algorithm']} ({optimiser_params['algorithm_params']})"
    }

    # Dump config parameters
    with config_file.open('w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    
    # Dump full csv 

    utilitarian = []
    egalitarian = []
    proportional = []
    utilities = []
    elapsed_times = []
    ginis = []
    percentiles = []
    with full_csv_file.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for solution, elapsed_time in zip(solutions, elapsed):
            objective_dict = solution.objectives
            utilitarian.append(objective_dict['utilitarian'])
            egalitarian.append(objective_dict['egalitarian'])
            proportional.append(objective_dict['proportionality'])
            utilities.append(objective_dict['avg_utility'])
            ginis.append(objective_dict['gini_index'])
            percentiles.append(objective_dict['percentile'])

            elapsed_times.append(elapsed_time)
            elapsed_dict = {"elapsed_time": elapsed_time}
            row = {**passenger_params, **graph_params, **algo_params, **objective_dict, **elapsed_dict}
            writer.writerow(row)
    
    # Dump summary csv
    summary_fieldnames = None

    try:
        config['graph_params']['dataset']
        summary_fieldnames = [
            'num_passengers',
            "alpha",
            "beta",
            "inter_cluster_travelling",
            "peak_probabilities",
            "time_step", 
            'service_hours',
            'num_locations',
            'centroid_codes',
            'dataset',
            'short_avg_vehicle_speed',
            'long_avg_vehicle_speed',
            'algorithm',
            'avg_utilitarian',
            'avg_egalitarian',
            'avg_proportionality',
            'avg_utility',
            'avg_gini_index',
            'avg_percentile',
            'avg_elapsed_time'
        ]

    except:
        summary_fieldnames = [
            'num_passengers',
            "alpha",
            "beta",
            "inter_cluster_travelling",
            "peak_probabilities",
            "time_step",
            'service_hours',
            'num_locations',
            'clusters',
            'min_location_distance',
            'grid_size',
            'short_avg_vehicle_speed',
            'long_avg_vehicle_speed',
            'algorithm',
            'algorithm_params',
            'avg_utilitarian',
            'avg_egalitarian',
            'avg_proportionality',
            'avg_utility',
            'avg_gini_index',
            'avg_percentile',
            'avg_elapsed_time'
        ]

    
    global_summary_csv_file.touch(exist_ok=True)
    id_dict = dict()
    with global_summary_csv_file.open("r") as f:
        global_reader = csv.DictReader(f)
        id_dict["id"] = len(list(global_reader))
    
    with local_summary_csv_file.open('w') as local_f, global_summary_csv_file.open("a") as global_f:
        objective_dict = {
            "avg_utilitarian": np.mean(utilitarian),
            "avg_egalitarian": np.mean(egalitarian),
            "avg_proportionality": np.mean(proportional),
            'avg_utility': np.mean(utilities),
            'avg_gini_index': np.mean(ginis),
            'avg_percentile': np.mean(percentiles)
        }

        local_writer = csv.DictWriter(local_f, fieldnames=summary_fieldnames)
        local_writer.writeheader()
        elapsed_dict = {"avg_elapsed_time": np.mean(elapsed_times)}
        local_row = {**passenger_params, **graph_params, **algo_params, **objective_dict, **elapsed_dict}
        local_writer.writerow(local_row)


        global_fieldnames = [field for field in summary_fieldnames]
        global_fieldnames.insert(0, "id")
        global_writer = csv.DictWriter(global_f, fieldnames=global_fieldnames)
        global_reader = csv.DictReader(global_f)

        if id_dict["id"] == 0:
            global_writer.writeheader()
        
        id_dict = {"id": id}
        global_row = {**local_row, **id_dict, **elapsed_dict}
        global_writer.writerow(global_row)
