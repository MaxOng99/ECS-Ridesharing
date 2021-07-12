from models.environment import Environment
from algorithms.optimiser import Optimiser

env = Environment(num_locations=10, num_passengers=5, max_coordinates=(100, 100))
optimiser = Optimiser(env.graph, env.passengers)
optimal_solution = optimiser.optimise(solution_constructor="nearest_neighbour")

print("Passenger Utilities", "\n")
for index, passenger in enumerate(env.passengers):
    print(f"Passenger {index}:", passenger.get_utility(optimal_solution))