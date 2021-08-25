from typing import Union, List, Callable
from models.solution import Solution
import random

class VotingRules:

    def borda_count(candidates: Union[List[Solution], List[int]], ranking_functions: List[Callable], kwargs=None):
        """Borda count implementation

        Args:
            candidates (Union[List[Solution], List[int]]): Either List of Solutions or List of location_ids
            ranking_functions (List[Callable]): Either solution ranking functions or location ranking functions from each rider
            kwargs: Additional arguments that is supplied to the runtime ranking functions

        Returns:
            winner [Solution | int]: Winner candidate (either a Solution or location_id) according to voting rule
        """
        num_of_candidates = len(candidates)
        candidates = list(candidates)
        scores = {candidate_index: 0 for candidate_index, _ in enumerate(candidates)}

        for ranking_function in ranking_functions:
            ranked_candidates = ranking_function(candidates, kwargs=kwargs)
            for rank_index, candidate in enumerate(ranked_candidates):
                candidate_id = candidates.index(candidate)
                scores[candidate_id] += (num_of_candidates - 1) - rank_index
        
        # If there are ties, pick random candidate
        temp_scores = list(scores.values())
        if all([score == temp_scores[0] for score in temp_scores]):
            winner = random.choice(candidates)
        else:
            winner_id = max(scores, key=scores.get)
            winner = candidates[winner_id]
        return winner