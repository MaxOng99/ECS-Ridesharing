# ECS RideSharing Research

## Dependencies
- python-igraph
- numpy
- prettytable
- pyllist
- pyyaml

## Instructions
1. Navigate to the root folder of this project.
2. Run `./setup_env.sh`.
3. Run `source env/ride_sharing/bin/activate`
4. Specify different experiments in the `config.yaml` file with the following [format](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml)
5. Run `./run_simulation.sh`
6. View the output in the `simulation_output` folder. Each experiment will have a pair of configuration file and output file.

## Resources
- [igraph python library](https://igraph.org/python/)
- [pretty table library](https://pypi.org/project/prettytable/)
- [pyllist library (linked list implementation)](https://pythonhosted.org/pyllist/)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
