import time

from models.graph import DatasetGraphGenerator
from models.passenger import PassengerGenerator
from algorithms.optimiser import create_algorithm



class Simulation:
    def __init__(self, config) -> None:

        self.config = config
        self.seed_params = self.config['seeds']
        self.graph_params = self.config['graph_params']
        self.passenger_params = self.config['passenger_params']
        self.optimiser_params = self.config['optimiser_params']
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
            generator = DatasetGraphGenerator(graph_seed, self.graph_params)
            graph = generator.graph
            graphs.append(graph)

            # Generate passengers
            pass_generator = PassengerGenerator(passenger_seeds[x], graph, self.passenger_params)
            passengers = pass_generator.passengers

            # Set up optimiser
            algorithm = create_algorithm(optimiser_seed, self.optimiser_params, graph, passengers)
            t_start = time.perf_counter()
            solution = algorithm.optimise()
            t_end = time.perf_counter()
            elapsed.append(t_end - t_start)
            solutions.append(solution.objectives)
        
        return (self.config, solutions)
        
        




