import sys
import os
import yaml
import numpy as np
import math
from tqdm import tqdm
sys.path.insert(0, f"{os.getcwd()}")
sys.path.insert(0, f"{os.getcwd()}/ridesharing/")

from multiprocessing import Pool, Process, Manager

import output_writer
from scripts.simulation import Simulation
from config_validator import parse_config

def __run_simulation(args):
    config = args['config']
    queue = args['queue']

    new_simulation = Simulation(config)
    sim_config, sim_output = new_simulation.run()
    queue_item = {"config": sim_config, "output": sim_output}
    queue.put(queue_item)
    return queue_item
    
def __listener(queue):
    while True:
        item = queue.get()
        if item == "kill":
            break
        else:
            output_writer.write_single_experiment(item['config'], item['output'])

if __name__ == "__main__":

    # Parses config.yaml and returns a list of configuration.
    # Number of unique configurations = no. runs * no. optimisers * no. variable parameter specified
    config: dict
    with open('./scripts/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        config_list = parse_config(config)
        output_writer.create_csv_file(config)

    queue = Manager().Queue()
    listener = Process(target=__listener, args=(queue,))
    listener.start()


    # May need to find an optimized maxtasksperchild argument for Pool() and 
    # 'chunksize' argument for imap_unordered function to speed up simulation runs
    arg_list = [{"config": config, "queue": queue} for config in config_list]
    with Pool(maxtasksperchild=1) as simulation_pool:
        list(tqdm(simulation_pool.imap_unordered(__run_simulation, arg_list), total=len(config_list))) # Blocks until all experiments ran
    
    queue.put("kill")
    listener.join()
    listener.close()

    output_writer.write_config_output(config)
    output_writer.write_mean_experiment(config)
    output_writer.plot_graph(config)
