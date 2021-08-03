from models.environment import Environment
from algorithms.optimiser import Optimiser

env = Environment(num_locations=15, num_passengers=20, max_coordinates=(800, 800))
optimiser = Optimiser(env.graph, env.passengers)

options = {"algorithm": "iterative_voting", 
            "parameters": {"voting_rule": "borda_count"}
            }
optimal_solution = optimiser.optimise(options)

print("Solution:", "\n")
print(optimal_solution, "\n")
print("Passenger Utilities: ", "\n")
for index, passenger in enumerate(env.passengers):
    print(f"Passenger {index}:", f"Start ({passenger.start_id})", f"End ({passenger.destination_id})", passenger.get_solution_utility(optimal_solution))