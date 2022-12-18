def get_variable_param(config_dict):
    var_type = list(config_dict['var_params'].keys())[0]
    var_param_key = list(config_dict['var_params'][var_type].keys())[0]
    var_param_value = config_dict['var_params'][var_type][var_param_key]
    return var_type, var_param_key, var_param_value