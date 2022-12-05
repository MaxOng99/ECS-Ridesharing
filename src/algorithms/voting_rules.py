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
        best_score = scores[best_candidate]
        indifferent_candidates = \
            [candidate for candidate in candidates if scores[candidate] == best_score]
            
        return np.random.choice(indifferent_candidates)

    def harmonic(candidates: Set[object], ranking_functions: List[Callable], weights: List[float]):
        scores = {candidate: 0 for candidate in candidates}

        for ranking_function, weight in zip(ranking_functions, weights):
            ranked_candidates = ranking_function(candidates)
            for rank_index, candidate in enumerate(ranked_candidates):
                scores[candidate] += weight * (1/(rank_index+1)) # practically the main change between harmonic and borda

        # Use np.random to account for the fact that there could be ties
        best_candidate = max(scores, key=scores.get)
        best_score = scores[best_candidate]
        indifferent_candidates = \
            [candidate for candidate in candidates if scores[candidate] == best_score]

        return np.random.choice(indifferent_candidates)

    def instant_runoff(candidates: Set[object], ranking_functions: List[Callable], weights: List[float]):
        """
        the voting rule runs in |candidates| rounds. At each round, the least supported candidate is eliminated
        I have not implemented a weighted version, as I cannot see how do we use them.
        :param ranking_functions:
        :param
        :return:
        """

        Eliminated = set([])
        ranked_candidates = []

        for ranking_function in ranking_functions:
            ranked_candidates.append(ranking_function(candidates))

        while len(Eliminated) < len(candidates) - 1:
            scores = {candidate: 0 for candidate in candidates if candidate not in Eliminated}
            for ordering, weight in zip(ranked_candidates, weights):
                not_eliminated_ordering = [i for i in ordering if i not in Eliminated]
                first_choice = not_eliminated_ordering[0]
                scores[first_choice] += 1 * weight
            worst_candidate = min(scores, key=scores.get)
            worst_score = scores[worst_candidate]

            indifferent_candidates = [candidate for candidate in candidates.difference(Eliminated) if scores[candidate] == worst_score]
            # choose randomly one of the candidates with the lowest score to be eliminated
            Eliminated.add(np.random.choice(indifferent_candidates))
        return candidates.difference(Eliminated).pop()