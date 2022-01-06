import copy
from pathlib import Path

from cerberus import Validator

# Seeds
seeds_schema = {
    'type': 'dict',
    'schema': {
        'graph': {
            'type': 'integer',
        },
        'passengers': {
            'type': 'integer'
        },
        'algorithm': {
            'type': 'integer'
        }
    }
}

# Passengers
passengers_schema = {
    "type": "dict",
    "schema": {
        "num_passengers": {"type": "integer", "min": 1},
        "service_hours": {"type": "integer", "min": 1, "max": 24},
        "alpha": {"type": "number"},
        "beta": {"type": "number"},
        "peak_probability": {"type": "number"},
        "time_step": {"type": "number"},
        "inter_cluster_probability": {"type": "number", "min":0, "max":1},
        "centroid_likelihood": {"type": "number", "min": 0, "max": 1}
    }
}

# Graph

dataset_graph_schema = {
    'num_locations': {
        'type': 'list'
    },
    'short_avg_vehicle_speed': {
        'type': 'number'
    },
    'long_avg_vehicle_speed': {
        'type': 'number'
    },
    'localities': {
        'type': 'list'
    }
}

# synthetic_graph_schema = {
#     'num_locations': {
#         'type': 'integer',
#         'min': 2,
#     },
#     'clusters': {
#         'type': 'integer',
#         'min': 1
#     },
#     'grid_size': {
#         'type': 'number',
#     },
#     'min_location_distance': {
#         'type': 'number',
#         'min': 100
#     },
#     'short_avg_vehicle_speed': {
#         'type': 'number'
#     },
#     'long_avg_vehicle_speed': {
#         'type': 'number'
#     },
#     'dataset': {
#         'type': 'string'
#     }
# }

graph_schema = {
    'type': 'dict',
    'oneof_schema': [
        # synthetic_graph_schema,
        dataset_graph_schema
    ]
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
                    'egalitarian',
                    'utilitarian',
                    'proportionality',
                    'avg_utility',
                    'gini_index',
                    'percentile'
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
                    "popularity"
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
                "allowed": ["borda_count", "popularity"]
            },
            "final_voting_rule": {
                "type": "string",
                "allowed": ["borda_count", "popularity"]
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
                "allowed": ["borda_count", "poplarity"]
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
                "allowed": ["2_opt", "simulated_annealing", "dp"]
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
        "passenger_seed": {
            "type": "integer"
        },
        "algorithm_seed": {
            "type": "integer"
        },
        "graph_seed": {
            "type": "integer"
        }
    }
}

config_schema = {
    "seeds": seeds_schema,
    "optimiser_params": optimiser_schema,
    "passenger_params": passengers_schema,
    "graph_params": graph_schema,
    "experiment_params": experiment_schema,
    "var_param": {"type": "dict"}
}


class ConfigException(Exception):
    pass

def __validate_yaml(config_dict):
    v = Validator(config_schema)
    if not v.validate(config_dict):
        raise ConfigException(v.errors)

def __get_variable_param(config_dict):
    var_param = config_dict['var_params']
    param_type, param_dict = list(var_param.items())[0]
    param_key, param_list = list(param_dict.items())[0]

    if not isinstance(param_list, list):
        msg = "Variable parameters need to be supplied with " + \
            "a list of values."
        raise Exception(msg)

    return (param_type, param_key, param_list)

def __get_optimiser_params(config_dict):
    optimisers = config_dict['optimiser_params']
    if not isinstance(optimisers, list):
        raise Exception("Please supply list of optimisers")
    return optimisers

def parse_config(config_dict):

    # Check if experiment already exist by name
    exp_name = config_dict['experiment_params']['name']
    output_path = Path(f"./simulation_output/{exp_name}")

    if output_path.is_dir():
        msg = f"Experiment {exp_name} already exists. If you are " + \
            "creating a new experiment, supply a new value for the experiment " + \
                "name parameter"
        raise Exception(msg)

    # create params combination configuration
    params_config_list = []
    const_params = config_dict['const_params']
    param_type, param_key, param_list = __get_variable_param(config_dict)

    for value in param_list:
        temp_dict = copy.deepcopy(const_params)
        temp_dict[param_type][param_key] = value
        temp_dict['experiment_params'] = config_dict['experiment_params']
        temp_dict["var_param"] = {param_key: value}
        params_config_list.append(temp_dict)

    # For each param combination config, run all specified optimisers
    final_config_list = []
    optimisers = __get_optimiser_params(config_dict)
    for optimiser in optimisers:
        for config in params_config_list:
            temp = copy.deepcopy(config)
            temp['optimiser_params'] = optimiser
            __validate_yaml(temp)
            final_config_list.append(temp)
    return final_config_list