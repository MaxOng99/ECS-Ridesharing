# ECS RideSharing Research

## Dependencies
- python-igraph==0.9.6
- numpy==1.20.2
- prettytable==2.1.0
- pyllist==0.3
- pyyaml==5.4.1

## Instructions
1. Create a python virtual environment and activate it.
2. Run `python -m pip install -r requirements.txt`
3. Navigate to the root folder of this project.
4. Specify different experiments in the `config.yaml` file with the following [format](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml)
5. Run `python simulation.py`
6. View the output in the `simulation_output` folder. Each experiment will have a pair of configuration file and output file.

## Resources
- [igraph python library](https://igraph.org/python/)
- [pretty table library](https://pypi.org/project/prettytable/)
- [pyllist library (linked list implementation)](https://pythonhosted.org/pyllist/)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
