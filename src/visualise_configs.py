import yaml
from config_validator import validate_yaml
from models.graph import SyntheticGraphGenerator
from models.passenger import PassengerGenerator
import utils.output_writer as writer

with open("config.yaml", "r") as file:
    try:
        config = yaml.safe_load(file)
        validate_yaml(config)

        graphs = []
        beta_dists = []
        preference_dists = []

        seed_config = config['seeds']
        experiment_configs = config['experiments']

        for exp_config in experiment_configs:
            graph_generator = SyntheticGraphGenerator(seed_config['graph'], exp_config['graph_params'])
            graph = graph_generator.graph
            graphs.append(graph)

            passenger_generator = PassengerGenerator(seed_config['passengers'], graph, exp_config['passenger_params'])
            beta_dists.append(passenger_generator.beta_distribution)
            preference_dists.append(passenger_generator.preference_distribution)
        
        writer.write_illustration_output(graphs, beta_dists, preference_dists)

    except yaml.YAMLError as exc:
        print(exc)