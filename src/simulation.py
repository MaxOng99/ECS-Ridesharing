from models.graph import DatasetGraphGenerator, SyntheticGraphGenerator
from models.passenger import PassengerGenerator
from algorithms.optimiser import Optimiser
import time
import yaml

from utils.output_writer import write_simulation_output

class Simulation:
    def __init__(self, config_file) -> None:

        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)
            self.seed_params = self.config['seeds']
            self.graph_params = self.config['graph_params']
            self.passenger_params = self.config['passenger_params']
            self.optimiser_params = self.config['optimiser_params']
            self.optimiser_params['algorithm_params']['service_hours'] = self.passenger_params['service_hours']
            self.experiment_params = self.config['experiment_params']

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
            graph = None
            try: 
                self.graph_params['dataset']
                generator = DatasetGraphGenerator(self.graph_params)
                graph = generator.graph
                graphs.append(graph)
            except:
                generator = SyntheticGraphGenerator(graph_seed, self.graph_params)
                graph = generator.graph
                graphs.append(graph)

            # Generate passengers
            pass_generator = PassengerGenerator(passenger_seeds[x], graph, self.passenger_params)
            passengers = pass_generator.passengers

            # Set up optimiser
            optimiser = Optimiser(optimiser_seed, graph, passengers)
            if self.graph_params['dataset']:
                self.optimiser_params['algorithm_params']['dataset'] = self.graph_params['dataset']
            t_start = time.perf_counter()
            solution = optimiser.optimise(self.optimiser_params)
            t_end = time.perf_counter()
            elapsed.append(t_end - t_start)
            solutions.append(solution)

        print(solutions[0])
        write_simulation_output(self.config, solutions, elapsed)




