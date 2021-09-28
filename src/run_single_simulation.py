from simulation import Simulation
from utils.output_writer import write_simulation_output
import sys

config_file_path = sys.argv[1]
new_simulation = Simulation(config_file_path)
new_simulation.run()
print(f"{config_file_path} Done")