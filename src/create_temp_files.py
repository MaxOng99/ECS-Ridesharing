from config_validator import validate_yaml
import yaml
from pathlib import Path

with open("config.yaml", "r") as file:

    try:
        config = yaml.safe_load(file)
        validate_yaml(config)
        
        seed_config = config['seeds']
        experiment_configs = config['experiments']

        for id, config in enumerate(experiment_configs):
            
            config_file = Path(f"./temp") / f"config_{id+1}.yaml"

            with config_file.open("w") as f:
                config['seeds'] = seed_config
                yaml.safe_dump(config, f)

    except yaml.YAMLError as exc:
        print(exc)