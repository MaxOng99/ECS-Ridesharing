import yaml
from multiprocessing import Pool

from utils import output_writer
from simulation import Simulation
from config_validator import parse_config

def __run_simulation(config):
    new_simulation = Simulation(config)
    configuration, sol_outputs = new_simulation.run()
    return (configuration, sol_outputs)

if __name__ == "__main__":

    # Parses config.yaml and returns a list of configuration.
    # Number of unique configurations depend on the number of optimisers, 
    # and the number of variable parameters specified
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        config_list = parse_config(config)

    with Pool(processes=4) as pool:
        result_list = pool.map(__run_simulation, config_list)
    
    # Write CSV Output
    full_data_rows = output_writer.write_full_output(config, result_list)
    mean_data_rows = output_writer.write_mean_output(config, result_list)

    # Plot graphical results
    output_writer.plot_graph(config, mean_data_rows)


