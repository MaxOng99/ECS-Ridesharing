from typing import Callable, Set

class VotingRules:

    def borda_count(candidates: Set[object], ranking_functions: Set[Callable]):
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

        for ranking_function in ranking_functions:
            ranked_candidates = ranking_function(candidates)
            for rank_index, candidate in enumerate(ranked_candidates):
                scores[candidate] += (num_of_candidates - 1) - rank_index
        
        return ranked_candidates[0]