import csv
from pathlib import Path

import yaml
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt

from ridesharing.utils.data_structure import flatten_dict

def write_mean_output(main_config, result_list):

    exp_name = main_config['experiment_params']['name']
    var_param = flatten_dict(main_config['var_params'])
    var_key = list(var_param.keys())[0]
    objective_keys = list(result_list[0][1][0].keys())

    output_path = Path(f"./simulation_output/{exp_name}")
    mean_csv = output_path / "mean_output.csv"
    mean_csv_fieldnames = [var_key] + \
    list(map(lambda obj_key: f"mean_{obj_key}", objective_keys)) + \
        ["algorithm"]

    data_rows = []

    for config, sol_objective_list in result_list:
        objective_dict = dict()
        optimiser_params = config['optimiser_params']
        for key in objective_keys:
            values = [objective[key] for objective in sol_objective_list]
            mean_val = np.mean(values)
            objective_dict[f"mean_{key}"] = mean_val

        optimiser_dict = {
            "algorithm": f"{optimiser_params['algorithm']} ({optimiser_params['algorithm_params']})"
        }
        data_row = {**objective_dict, **config['var_param'], **optimiser_dict}
        data_rows.append(data_row)

    with mean_csv.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=mean_csv_fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)
    
    return data_rows

def write_config_output(main_config, path):
    with path.open("w") as f:
        yaml.safe_dump(main_config, f)
        
def write_full_output(main_config, result_list):
    exp_name = main_config['experiment_params']['name']
    var_param = flatten_dict(main_config['var_params'])

    output_path = Path(f"./simulation_output/{exp_name}")
    output_path.mkdir(parents=True, exist_ok=True)

    full_csv = output_path / "full_output.csv"
    config_path = output_path / "config.yaml"
    write_config_output(main_config, config_path)
    
    var_key = list(var_param.keys())[0]
    objective_keys = list(result_list[0][1][0].keys())
    full_csv_fieldnames = [var_key] + objective_keys + ["algorithm"]

    data_rows = []
    for config, sol_objectives in result_list:
        var_param = config['var_param']
        optimiser_params = config['optimiser_params']
        for objective in sol_objectives:
            optimiser_dict = {
                "algorithm": f"{optimiser_params['algorithm']} ({optimiser_params['algorithm_params']})"
            }
            data_row = {**objective, **var_param, **optimiser_dict}
            data_rows.append(data_row)

    with full_csv.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=full_csv_fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)
    
    return data_rows
    

def plot_graph(main_config, mean_data_rows):
    exp_name = main_config['experiment_params']['name']
    var_key = list(flatten_dict(main_config["var_params"]).keys())[0]

    output_path = Path(f"./simulation_output/{exp_name}")
    keys = list(mean_data_rows[0].keys())
    keys.remove("algorithm")
    keys.remove(var_key)

    df = pd.read_csv(f"{output_path}/mean_output.csv", header=0)
    for key in keys:
        _, ax = plt.subplots()
        sns.lineplot(data=df, ax=ax, x=var_key, y=key, hue="algorithm")
        plt.legend(fontsize="xx-small")
        plt.savefig(f"{output_path}/{key}_vs_{var_key}.png")

