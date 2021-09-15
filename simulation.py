import yaml
import numpy as np
from src.models.graph import SyntheticGraphGenerator
from src.models.passenger import PassengerGenerator
from src.algorithms.optimiser import Optimiser

class Simulation:
    def __init__(self, seed_config, exp_config) -> None:
        self.seed_config = seed_config
        self.graph_params = exp_config['graph_params']
        self.passenger_params = exp_config['passenger_params']
        self.optimiser_params = exp_config['optimiser_params']
        self.experiment_params = exp_config['experiment_params']

    def run(self):
        
        runs = self.experiment_params['runs']
        for _ in range(runs):
            # Generate graph
            np.random.seed(self.seed_config['graph'])
            graph_generator = SyntheticGraphGenerator(self.graph_params)
            graph = graph_generator.graph

            # Generate passengers
            np.random.seed(self.seed_config['passengers'])
            pass_generator = PassengerGenerator(graph, self.passenger_params)
            passengers = pass_generator.passengers

            # Set up optimiser
            optimiser = Optimiser(graph, passengers)
            solution = optimiser.optimise(self.optimiser_params)
            print(solution)
            
with open("config.yaml", "r") as file:
    try:
        config = yaml.safe_load(file)
        seed_config = config['seeds']
        experiment_configs = config['experiments']

        for config in experiment_configs:
            simulation = Simulation(seed_config, config)
            simulation.run()
    except yaml.YAMLError as exc:
        print(exc)
