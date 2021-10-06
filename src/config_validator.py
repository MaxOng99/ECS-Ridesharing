from cerberus import Validator
import numpy as np
import math

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
    'type': 'dict',
    'schema': {
        'num_passengers': {
            "type": "integer",
            "min": 1
        },
        'service_hours': {
            'type': 'integer',
            'min': 1,
            'max': 24,
        },
        'beta_distribution': {
            'type': 'dict',
            'schema': {
                'alpha': {'type': 'number'},
                'beta': {'type': 'number'}
            }
        },
        'preference_distribution':{
            'type': 'dict',
            'schema': {
                'inter_cluster_travelling': {'type': 'boolean'},
                'peak_probability': {'type': 'number'},
                'time_step': {'type': 'number'}
            }
        }
    },
    'check_with': 'compatible_passenger_params'
}

# Graph
synthetic_graph_schema = {
    'num_locations': {
        'type': 'integer',
        'min': 2,
    },
    'clusters': {
        'type': 'integer',
        'min': 1
    },
    'grid_size': {
        'type': 'number',
    },
    'min_location_distance': {
        'type': 'number',
        'min': 100
    },
    'short_avg_vehicle_speed': {
        'type': 'number'
    },
    'long_avg_vehicle_speed': {
        'type': 'number'
    },
    'dataset': {
        'type': 'string'
    }
}

dataset_graph_schema = {
    'dataset': {
        'type': 'string'
    },
    'num_locations': {
        'type': 'list'
    },
    'short_avg_vehicle_speed': {
        'type': 'number'
    },
    'long_avg_vehicle_speed': {
        'type': 'number'
    },
    'centroid_codes': {
        'type': 'list'
    }
}

graph_schema = {
    'type': 'dict',
    'oneof_schema': [
        synthetic_graph_schema,
        dataset_graph_schema
    ]
}

# Optimiser
greedy_insert_schema = {
    'algorithm': {
        'type': 'string',
        'allowed': ['greedy insert', 'greedy insert ++']
    },
    'algorithm_params': {
        'type': 'dict',
        'schema': {
            'iterations': {
                'type': 'integer',
                'min': 1
            },
            'final_voting_rule': {
                'type': 'string',
                'allowed': [
                    'borda_count',
                    'popularity',
                    'none'
                ]
            },
            "objective": {
                'type': 'string',
                "allowed": [
                    'egalitarian',
                    'utilitarian',
                    'proportionality',
                    'avg_utility',
                    'gini_index',
                    'percentile'
                ]
            }
        }

    }
}

iterative_voting_schema = {
    'algorithm': {
        'type': 'string',
        'allowed': ['iterative_voting_1', 'iterative_voting_2']
    },
    'algorithm_params': {
        'type': 'dict',
        'schema': {
            'iterative_voting_rule': {
                'type': 'string',
                'allowed': ['borda_count', 'popularity']
            },
            'final_voting_rule': {
                'type': 'string',
                'allowed': ['none', 'borda_count', 'popularity']
            },
            'iterations': {
                'type': 'number'
            },
            "objective": {
                'type': 'string',
                "allowed": [
                    'egalitarian',
                    'utilitarian',
                    'proportionality',
                    'avg_utility',
                    'gini_index',
                    'percentile'
                ]
            }
        }
    }
}


optimiser_schema = {
    'type': 'dict', 
    'oneof_schema': [
        greedy_insert_schema,
        iterative_voting_schema
    ]
}

# Experiment
experiment_schema = {
    'type': 'dict',
    'schema': {
        'runs': {
            'type': 'integer',
            'min': 1
        }
    }
}

config_schema = {
    'seeds': seeds_schema,
    'experiments': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'passenger_params': passengers_schema,
                'graph_params': graph_schema,
                'optimiser_params': optimiser_schema,
                'experiment_params': experiment_schema
            }
        }
    }
}

class CustomValidator(Validator):
    def _check_with_compatible_passenger_params(self, field, value):

        if field == "passenger_params":
            passenger_params = value

            inter_cluster_travelling = passenger_params['preference_distribution']['inter_cluster_travelling']
            peak_probability = passenger_params['preference_distribution']['peak_probability']

            if not inter_cluster_travelling and \
                peak_probability != 0:
                self._error(field, "peak probability must be 0; inter cluster travelling is disabled")

    def _check_with_compatible_graph_params(self, field, value):
        if field == "graph_params":
            graph_params = value
            num_locations = graph_params['num_locations']
            clusters = graph_params['clusters']
            grid_size = graph_params['grid_size']
            min_location_distance = graph_params['min_location_distance']

            locations_per_cluster = num_locations / clusters
            num_centroids_per_axis = math.ceil(np.sqrt(clusters))
            centroid_distance = grid_size / num_centroids_per_axis
            radius = centroid_distance / 2

            # Max possible locations
            utilised_locations = 0
            ring_index = 0
            max_ring_index = radius // min_location_distance

            while utilised_locations < locations_per_cluster:
                if ring_index > (max_ring_index // 2):
                    self._error(field, "num_locations value is too big")
                    break
                ring_index += 1
                utilised_locations += math.ceil(2 * np.pi * ring_index)

class ConfigException(Exception):
    pass

def validate_yaml(config_dict):
    v = CustomValidator(config_schema)
    if not v.validate(config_dict):
        raise ConfigException(v.errors)