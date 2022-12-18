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

    def run(self):

        # Generate Graph
        graph_generator = DatasetGraphGenerator(self.graph_params)
        graph = graph_generator.graph

        # Generate Passengers
        passenger_seed = self.passenger_params['passenger_seed']
        pass_generator = PassengerGenerator(passenger_seed, graph, self.passenger_params) # Need to get passenger_seeds
        passengers = pass_generator.passengers

        # Set up optimiser
        algorithm_seed = self.optimiser_params['algorithm_seed']
        algorithm = create_algorithm(algorithm_seed, self.optimiser_params, graph, passengers)
        t_start = time.perf_counter()
        solution = algorithm.optimise()
        t_end = time.perf_counter()
        return self.config, solution.objectives
