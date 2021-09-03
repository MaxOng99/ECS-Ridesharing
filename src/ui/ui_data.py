ui_data = dict()

ui_data["passenger"] = {
    "preferenceDistributionComboBox": ["uniform"],
    "betaDistributionComboBox": ["uniform"]
}

ui_data["graph"] = {
    "inter_cluster_distributions": ["normal", "uniform"],
    "intra_cluster_distributions": ["normal", "uniform"]
}

ui_data["optimiser"] = {
    "objectives": ["utilitarian", "egalitarian"],
    "algorithms": ["iterative voting", "greedy insert"],
    "greedy_params": {
        "final_voting_rules": ["borda", "majority"],
        "iterations": 0
    },
    "iterative_params": {
        "final_voting_rules": ["borda", "majority"],
        "iterative_voting_rules": ["borda", "majority"]
    }
}