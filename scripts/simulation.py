import time

from ridesharing.models.graph import DatasetGraphGenerator
from ridesharing.models.passenger import PassengerGenerator
from ridesharing.algorithms.optimiser import create_algorithm



class Simulation:
    def __init__(self, config) -> None:

        self.config = config
        self.graph_params = self.config['graph_params']
        self.passenger_params = self.config['passenger_params']
        self.optimiser_params = self.config['optimiser_params']
        self.experiment_params = self.config['experiment_params']

    def run(self):
        
        runs = self.experiment_params['runs']
        graph_seed = self.experiment_params['graph_seed']
        passenger_seeds = [self.experiment_params['passenger_seed'] + x for x in range(runs)]
        optimiser_seed = self.experiment_params['algorithm_seed']

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
        
        



