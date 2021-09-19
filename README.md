# ECS RideSharing Research

## Instructions

#### Running on ECS's linux server
*Windows users: Consider installing [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to ssh into the server.*
1. `ssh` into `linuxproj.ecs.soton.ac.uk` with your university username and password.
2. Clone the repository. <br/>


#### Running on personal machine
*Windows users: [Set up](https://docs.microsoft.com/en-us/windows/wsl/install-win10) WSL so that bash scripts can be run.*
1. Ensure that Python 3.4.x or above is already installed.
2. Clone the repository.
3. In the `setup_env.sh` and `run_simulation.sh` files, change `python3` to `<path/to/python_interpreter>`, or `<python_interpreter>` if your python interpreter was added to `PATH` variable. </br>


#### Running the simulation
1. Navigate to the root folder of this project.
3. Run `./setup_env.sh`.
4. Specify different experiments in the `config.yaml` file with the following [format](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml).
5. Run `./run_simulation.sh`.
6. Repeat steps 3-4 with different experiments.
7. View the outputs in the `simulation_output` folder. Each experiment contains a configuration file and an output file.

## Packages used in this project
- [numpy](https://numpy.org/)
- [python-igraph](https://igraph.org/python/)
- [prettytable](https://pypi.org/project/prettytable/)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [pyllist](https://pythonhosted.org/pyllist/)
