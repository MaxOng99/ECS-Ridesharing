import copy
from pathlib import Path
import ridesharing.utils.config as config_utils
from cerberus import Validator

# Passengers
passengers_schema = {
    "type": "dict",
    "schema": {
        "num_passengers": {"type": "integer", "min": 1},
        "alpha": {"type": "number"},
        "beta": {"type": "number"},
        "peak_probability": {"type": "number"},
        "num_hotspots": {"type": "integer", "min": 0}
    }
}

# Graph
graph_schema = {
    "type": "dict",
    "schema": {
        'num_locations': {
            'type': 'number'
        },
        'avg_vehicle_speed': {
            'type': 'number'
        },
        'locality': {
            "type": "string",
            "allowed": ["Westminster", "Hackney"]
        }
    }
}

# Optimiser
RGA_schema = {
    "algorithm":{
        "type": "string",
        "allowed": ["RGA", "RGA ++"]
    },
    "algorithm_params": {
        "type": "dict",
        "schema": {
            "objective": {
                "type": "string",
                "allowed": [
                    'utilitarian',
                    'gini_index'
                ]
            },
            "multiple_iterations": {
                "type": "boolean"
            }
        }
    }
}

RGVA_schema = {
    "algorithm": {
        "type": "string",
        "allowed": ["RGVA"]
    },
    "algorithm_params": {
        "type": "dict",
        "schema": {
            "final_voting_rule": {
                "type": "string",
                "allowed": [
                    "borda_count",
                    "popularity",
                    "harmonic",
                    "instant_runoff"
                ]
            }
        }
    }
}

IV1_schema = {
    "algorithm": {
        "type": "string",
        "allowed": ["IV1"]
    },
    "algorithm_params": {
        "type": "dict",
        "schema": {
            "iterative_voting_rule": {
                "type": "string",
                "allowed": ["borda_count", "popularity", "harmonic", "instant_runoff"]
            },
            "final_voting_rule": {
                "type": "string",
                "allowed": ["borda_count", "popularity", "harmonic", "instant_runoff"]
            }
        }

    }
}

IV2_schema = {
    "algorithm": {
        "type": "string",
        "allowed": ["IV2"]
    },
    "algorithm_params": {
        "type": "dict",
        "schema": {
            "iterative_voting_rule": {
                "type": "string",
                "allowed": ["borda_count", "popularity", "harmonic", "instant_runoff"]
            },
            "multiple_iterations": {
                "type": "boolean"
            }
        }
    }
}

tsp_heuristic_schema = {
    "algorithm": {
        "type": "string",
        "allowed": ["tsp algorithms"]
    },
    "algorithm_params": {
        "type": "dict",
        "schema": {
            "driver": {
                "type": "string",
                "allowed": ["2_opt", "simulated_annealing"]
            },
            "max_processing_time": {"type": "number"}
        }
    }
}

optimiser_schema = {
    'type': 'dict', 
    'oneof_schema': [
        RGA_schema,
        RGVA_schema,
        IV1_schema,
        IV2_schema,
        tsp_heuristic_schema
    ]
}

# Experiment
experiment_schema = {
    'type': 'dict',
    'schema': {
        'runs': {
            'type': 'integer',
            'min': 1
        },
        "name": {
            "type": "string"
        },
        "initial_passenger_seed": {
            "type": "integer"
        },
        "initial_algorithm_seed": {
            "type": "integer"
        }
    }
}


graph_var_param_schema = {
    "type": "dict",
    "oneof_schema": [{key: {"type": "list", "schema": val}} for key, val in graph_schema['schema'].items()]
}

passenger_var_param_schema = {
    "type": "dict",
    "oneof_schema": [{key: {"type": "list", "schema": val}} for key, val in passengers_schema['schema'].items()]
}

config_schema = {
    "experiment_params": experiment_schema,
    "optimiser_params": {
        "type": "list",
        "schema": optimiser_schema,
    },
    "const_params": {
        "type" : "dict",
        "schema": {
            "passenger_params": passengers_schema,
            "graph_params": graph_schema
        }
    },
    "var_params": {
        "type": "dict",
        "oneof_schema": [
            {"passenger_params": passenger_var_param_schema},
            {"graph_params": graph_var_param_schema}
        ]
    } 
}


class ConfigException(Exception):
    pass

def __validate_yaml(config_dict):
    v = Validator(config_schema)
    if not v.validate(config_dict):
        raise ConfigException(v.errors)

def __build_configs(config_dict):
    runs = config_dict['experiment_params']['runs']
    current_algorithm_seed = config_dict['experiment_params']['initial_algorithm_seed']
    current_passenger_seed = config_dict['experiment_params']['initial_passenger_seed']
    var_param_type, var_param_key, var_param_values = config_utils.get_variable_param(config_dict)

    config_list = []
    for val in var_param_values:
        # current_params = const_params + current var_param
        temp_params = copy.deepcopy(config_dict['const_params'])
        temp_params[var_param_type][var_param_key] = val
        temp_params['var_param'] = {var_param_key: val}

        # Assign current_params to each optimiser
        optimiser_and_parameters = []
        for optimiser in config_dict['optimiser_params']:
            temp_optimiser_params = copy.deepcopy(temp_params)
            temp_optimiser_params['optimiser_params'] = optimiser
            optimiser_and_parameters.append(temp_optimiser_params)

        # 1. Create experiment_params['runs'] number of config for each optimiser, for the current var_param
        # 2. Set the seed for each config
        for i in range(runs):
            for optimiser_and_param_dict in optimiser_and_parameters:
                temp = copy.deepcopy(optimiser_and_param_dict)
                temp['optimiser_params']['algorithm_seed'] = current_algorithm_seed + i
                temp['passenger_params']['passenger_seed'] = current_passenger_seed + i
                temp['experiment_params'] = {"id": f"{temp['optimiser_params']}_{val}_{i}"}
                temp['experiment_params']['name'] = config_dict['experiment_params']['name']
                config_list.append(temp)

        current_algorithm_seed = current_algorithm_seed + runs
        current_passenger_seed = current_passenger_seed + runs
    
    return config_list

def parse_config(config_dict):

    # Check if experiment already exist by name
    exp_name = config_dict['experiment_params']['name']
    output_path = Path(f"./simulation_output/{exp_name}")

    if output_path.is_dir():
        msg = f"Experiment {exp_name} already exists. If you are " + \
            "creating a new experiment, supply a new value for the experiment " + \
                "name parameter"
        raise Exception(msg)

    # Validate then build individual configs to run simulation in parallel
    __validate_yaml(config_dict)
    configs = __build_configs(config_dict)
    return configs