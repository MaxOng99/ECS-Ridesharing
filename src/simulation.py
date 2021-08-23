from models.environment import Environment
from algorithms.optimiser import Optimiser
import numpy as np

np.random.seed(42)
env = Environment(num_locations=10, num_passengers=25, max_coordinates=(1000, 1000))
optimiser = Optimiser(env.graph, env.passengers)


options = dict()

# Greedy Insert
options["algorithm"] = 'greedy_insert'
options["parameters"] = {'iterations': 5}

# # Iterative Voting
# options["algorithm"] = "iterative_voting"
# options["parameters"] = {"voting_rule": "borda_count"}

optimal_solution = optimiser.optimise(options)
print(optimal_solution)
