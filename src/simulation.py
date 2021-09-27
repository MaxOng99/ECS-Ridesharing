import yaml
from models.graph import SyntheticGraphGenerator
from models.passenger import PassengerGenerator
from algorithms.optimiser import Optimiser
from utils.output_writer import write_simulation_output
from config_validator import validate_yaml
import time

class Simulation:
    def __init__(self, seed_config, exp_config) -> None:
        self.seed_params = seed_config
        self.graph_params = exp_config['graph_params']
        self.passenger_params = exp_config['passenger_params']
        self.optimiser_params = exp_config['optimiser_params']
        self.experiment_params = exp_config['experiment_params']

    def run(self):
        
        runs = self.experiment_params['runs']
        graph_seed = self.seed_params['graph']
        passenger_seeds = [self.seed_params['passengers'] + x for x in range(runs)]
        optimiser_seed = self.seed_params['algorithm']

        solutions = []
        elapsed = []
        graphs = []
        for x in range(runs):
            # Generate graph
            graph_generator = SyntheticGraphGenerator(graph_seed, self.graph_params)
            graph = graph_generator.graph
            graphs.append(graph)

            # Generate passengers
            pass_generator = PassengerGenerator(passenger_seeds[x], graph, self.passenger_params)
            passengers = pass_generator.passengers

            # Set up optimiser
            optimiser = Optimiser(optimiser_seed, graph, passengers)
            t_start = time.perf_counter()
            solution = optimiser.optimise(self.optimiser_params)
            t_end = time.perf_counter()
            elapsed.append(t_end - t_start)
            solutions.append(solution)

        return solutions, elapsed

with open("config.yaml", "r") as file:

    try:
        config = yaml.safe_load(file)
        validate_yaml(config)
        
        seed_config = config['seeds']
        experiment_configs = config['experiments']

        for config in experiment_configs:
            simulation = Simulation(seed_config, config)
            solutions, elapsed = simulation.run()
            write_simulation_output(config, solutions, elapsed)

    except yaml.YAMLError as exc:
        print(exc)



