# ECS RideSharing Research

## Instructions

### Running on ECS's linux server
*Windows users: Consider installing [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to ssh into the server.*
1. `ssh` into `linuxproj.ecs.soton.ac.uk` with your university username and password.
2. Clone the repository. <br/>


### Running on personal machine
*Windows users: [Set up](https://docs.microsoft.com/en-us/windows/wsl/install-win10) WSL so that bash scripts can be run.*
1. Ensure that Python 3.4.x or above is already installed.
2. Clone the repository.
3. In the `setup_env.sh` and `run_simulation.sh` files, change `python3` to `<path/to/python_interpreter>`, or `<python_interpreter>` if your python interpreter was added to `PATH` variable. </br>


### Running the simulation
1. Navigate to the root folder of this project.
3. Run `./setup_env.sh`.
4. Specify different experiments in the `config.yaml` file with the following [format](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml).
5. Run `./run_simulation.sh`.
6. Repeat steps 3-4 with different experiments.
7. View the outputs in the `simulation_output` folder. Each experiment contains a configuration file and an output file.

### Specifying experiments

Refer to [config.yaml](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml) for examples.
#### Seeds
- `graph: int`
- `passengers: int`
- `algorithm: int`

*There are 3 seed parameters to set: `graph`, `passengers` and `algorithm`. For each experiment, each run will generate the same graph, but different passengers (different betas, start/end location and time). Different passengers are generated based on the `passengers` seed. For e.g., if `runs = 3` and the passenger seed `passengers = 67`, the list of passengers seeds to be used for each run of the experiment is [67, 68, 69]*

#### Passenger Parameters
- `num_passengers: int`
- `service_hours: int`

#### Graph Parameters
- `num_locations: int`
- `cluster: int`
- `grid_size`: int
- `avg_vehicle_speed: float`

*Note that 1. individual clusters are not part of the locations 2. The specified grid size is always nxn. For e.g., `grid_size=1200` equals to a 1200x1200 grid 3. `avg_vehicle_speed` is in km/h*

#### Optimiser Parameters
- `algorithm: 'greedy_insert' | 'iterative_voting'`
- `algorithm_params (greedy_insert): 'iterations': int, 'final_voting_rule': 'borda_count' | 'majority'`
- `algorithm_params (iterative_voting): 'iterative_voting_rule': 'borda_count' | 'majority', 'final_voting_rule': 'borda_count' | 'majority'`
 
## Packages used in this project
- [numpy](https://numpy.org/)
- [python-igraph](https://igraph.org/python/)
- [prettytable](https://pypi.org/project/prettytable/)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [pyllist](https://pythonhosted.org/pyllist/)
