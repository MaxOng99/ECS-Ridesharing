import csv
from pathlib import Path
import yaml
import numpy as np
import seaborn as sns
import glob
import shutil
import os
import pandas as pd
from matplotlib import pyplot as plt
from itertools import groupby
from multiprocessing import Queue
from ridesharing.utils.data_structure import flatten_dict
import ridesharing.utils.config as config_utils

FINAL_OUTPUT_PATH = "./simulation_output"

def write_config_output(main_config):
    path = Path(f"{FINAL_OUTPUT_PATH}/{main_config['experiment_params']['name']}/config.yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(main_config, f)

def create_csv_file(main_config):
    path = Path(f"{FINAL_OUTPUT_PATH}/{main_config['experiment_params']['name']}/full_output.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as temp_csv_file:
        var_type, var_param_key, var_param_value = config_utils.get_variable_param(main_config)
        fieldnames = [var_param_key, 'utilitarian', 'gini_index', 'algorithm']
        writer = csv.DictWriter(temp_csv_file, fieldnames=fieldnames)
        writer.writeheader()

def write_single_experiment(sim_config, sim_output):
    csv_file_path = Path(f"{FINAL_OUTPUT_PATH}/{sim_config['experiment_params']['name']}/full_output.csv")
    csv_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_file_path, "a") as csv_file:
        row_data = {
            **sim_config['var_param'],
            'utilitarian': sim_output['utilitarian'], 
            'gini_index': sim_output['gini_index'],
            'algorithm': f"{sim_config['optimiser_params']['algorithm']} ({sim_config['optimiser_params']['algorithm_params']})",
        }

        writer = csv.DictWriter(csv_file, fieldnames=[list(sim_config['var_param'].keys())[0], 'utilitarian', 'gini_index', 'algorithm'])
        writer.writerow(row_data)
    
def write_mean_experiment(main_config):
    exp_name = main_config['experiment_params']['name']
    var_type, var_key, var_value = config_utils.get_variable_param(main_config)

    full_output_path = f"{FINAL_OUTPUT_PATH}/{exp_name}/full_output.csv" 
    df = pd.read_csv(full_output_path)
    grouped_df = df.groupby([var_key, 'algorithm']).mean()

    mean_output_path = f"{FINAL_OUTPUT_PATH}/{exp_name}/mean_output.csv"
    grouped_df.to_csv(mean_output_path)

def plot_graph(main_config):
    exp_name = main_config['experiment_params']['name']
    var_type, var_key, var_value = config_utils.get_variable_param(main_config)
    output_path = Path(f"{FINAL_OUTPUT_PATH}/{exp_name}")

    df = pd.read_csv(f"{output_path}/full_output.csv")
    keys = df.columns.tolist()
    keys.remove("algorithm")
    keys.remove(var_key)
    for key in keys:
        _, ax = plt.subplots()
        sns.lineplot(data=df, ax=ax, x=var_key, y=key, hue="algorithm", err_style="bars", ci=95)
        plt.legend(fontsize="xx-small")
        plt.ylim(bottom=0)
        plt.savefig(f"{output_path}/{key}_vs_{var_key}.pdf", format='pdf')
        plt.savefig(f"{output_path}/{key}_vs_{var_key}.png", format='png')
