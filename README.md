# ECS RideSharing Research

## Instructions
*Ensure that Python 3.X, pip and virtualenv is already installed*
1. Navigate to the root folder of this project.
2. Run `./setup_env.sh`.
3. Specify different experiments in the `config.yaml` file with the following [format](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml).
4. Run `./run_simulation.sh`.
5. Repeat steps 3-4 with different experiments.
6. View the outputs in the `simulation_output` folder. Each experiment will have a pair of configuration file and output file.

## Dependencies
- numpy
- [python-igraph](https://igraph.org/python/)
- [prettytable](https://pypi.org/project/prettytable/)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [pyllist](https://pythonhosted.org/pyllist/)
