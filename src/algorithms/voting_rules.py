from typing import Callable, Set, List
import numpy as np

class VotingRules:

    def borda_count(candidates: Set[object], ranking_functions: List[Callable], weights: List[float]):
        """Borda count implementation

        Args:
            candidates (Union[List[Solution], List[int]]): Either List of Solutions or List of location_ids
            ranking_functions (List[Callable]): Either solution ranking functions or location ranking functions from each rider
            kwargs: Additional arguments that is supplied to the runtime ranking functions

        Returns:
            winner [Solution | int]: Winner candidate (either a Solution or location_id) according to voting rule
        """
        num_of_candidates = len(candidates)
        scores = {candidate: 0 for candidate in candidates}

        for ranking_function, weight in zip(ranking_functions, weights):
            ranked_candidates = ranking_function(candidates)
            for rank_index, candidate in enumerate(ranked_candidates):
                scores[candidate] += weight*((num_of_candidates - 1) - rank_index)
        
        # Use np.random to account for the fact that there could be ties
        best_candidate = max(scores, key=scores.get)
        best_score = scores[best_candidate]
        indifferent_candidates = \
            [candidate for candidate in candidates if scores[candidate] == best_score]

        return np.random.choice(indifferent_candidates)

    def popularity(candidates: Set[object], ranking_functions: List[Callable], weights: List[float]):

        scores = {candidate: 0 for candidate in candidates}
    
        for ranking_function, weight in zip(ranking_functions, weights):
            ranked_candidates = ranking_function(candidates)
            first_choice = ranked_candidates[0]
            scores[first_choice] += 1*weight
        # Use np.random to account for ties
        best_candidate = max(scores, key=scores.get)
        best_score =scores[best_candidate]
        indifferent_candidates = \
            [candidate for candidate in candidates if scores[candidate] == best_score]
            
        return np.random.choice(indifferent_candidates)

    # def borda_count(candidates: Set[object], ranking_functions: Set[Callable]):
    #     """Borda count implementation

    #     Args:
    #         candidates (Union[List[Solution], List[int]]): Either List of Solutions or List of location_ids
    #         ranking_functions (List[Callable]): Either solution ranking functions or location ranking functions from each rider
    #         kwargs: Additional arguments that is supplied to the runtime ranking functions

    #     Returns:
    #         winner [Solution | int]: Winner candidate (either a Solution or location_id) according to voting rule
    #     """
    #     num_of_candidates = len(candidates)
    #     scores = {candidate: 0 for candidate in candidates}

    #     for ranking_function in ranking_functions:
    #         ranked_candidates = ranking_function(candidates)
    #         for rank_index, candidate in enumerate(ranked_candidates):
    #             scores[candidate] += (num_of_candidates - 1) - rank_index
        
    #     # Use np.random to account for the fact that there could be ties
    #     best_candidate = ranked_candidates[0]
    #     best_score = scores[best_candidate]
    #     indifferent_candidates = \
    #         [candidate for candidate in candidates if scores[candidate] == best_score]

    #     return np.random.choice(indifferent_candidates)
    
    # def majority(candidates: Set[object], ranking_functions: Set[Callable]):

    #     scores = {candidate: 0 for candidate in candidates}

    #     for ranking_function in ranking_functions:
    #         ranked_candidates = ranking_function(candidates)
    #         first_choice = ranked_candidates[0]
    #         scores[first_choice] += 1
        
    #     # Use np.random to account for ties
    #     best_candidate = max(scores, key=scores.get)
    #     best_score =scores[best_candidate]
    #     indifferent_candidates = \
    #         [candidate for candidate in candidates if scores[candidate] == best_score]
            
    #     return np.random.choice(indifferent_candidates)
