import yaml
import numpy as np
from models.graph import SyntheticGraphGenerator
from models.passenger import PassengerGenerator
from algorithms.optimiser import Optimiser
from utils.info_utils import write_simulation_output

class Simulation:
    def __init__(self, seed_config, exp_config) -> None:
        self.seed_config = seed_config
        self.graph_params = exp_config['graph_params']
        self.passenger_params = exp_config['passenger_params']
        self.optimiser_params = exp_config['optimiser_params']
        self.experiment_params = exp_config['experiment_params']

    def run(self):
        
        runs = self.experiment_params['runs']
        graph_seed = self.seed_config['graph']
        passenger_seeds = [self.seed_config['passengers'] + x for x in range(runs)]
        solutions = []
        for x in range(runs):
            # Generate graph
            np.random.seed(graph_seed)
            graph_generator = SyntheticGraphGenerator(self.graph_params)
            graph = graph_generator.graph

            # Generate passengers
            np.random.seed(passenger_seeds[x])
            pass_generator = PassengerGenerator(graph, self.passenger_params)
            passengers = pass_generator.passengers

            # Set up optimiser
            np.random.seed(self.seed_config['algorithm'])
            optimiser = Optimiser(graph, passengers)
            solution = optimiser.optimise(self.optimiser_params)
            solutions.append(solution)

        return solutions
        

def config_param_checker(config):
    passenger_params = config['passenger_params']

    if passenger_params['service_hours'] != 24 and\
        passenger_params['preference_distribution'] == "peak_hours":
        passenger_params['preference_distribution'] = "uniform"
    
    return config
    
with open("config.yaml", "r") as file:
    try:
        config = yaml.safe_load(file)
        seed_config = config['seeds']
        experiment_configs = config['experiments']
    
        for config in experiment_configs:
            checked_config = config_param_checker(config)
            simulation = Simulation(seed_config, checked_config)
            solutions = simulation.run()
            write_simulation_output(config, solutions)

    except yaml.YAMLError as exc:
        print(exc)
