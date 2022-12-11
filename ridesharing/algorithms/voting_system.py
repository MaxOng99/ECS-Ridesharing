from typing import Any
import numpy as np
from collections import Counter
from pyllist import dllistnode
from algorithms.greedy_insert import ExistingValidTourNode, NewValidTourNode
from models import utility_functions
from models.solution import Solution

# There is an inherent dependency between evaluation function, and the candidate
def determine_utility_function(candidate):
    if isinstance(candidate, Solution):
        return utility_functions.solution_utility
    
    elif isinstance(candidate, ExistingValidTourNode) or \
        isinstance(candidate, NewValidTourNode):
        return utility_functions.node_utility
    
    else:
        return utility_functions.location_utility

class BordaCount:
    def __init__(self, voters, candidates, additional_info) -> None:
        self.voters = voters
        self.candidates = candidates
        self.additional_info = additional_info
        self.util_function = determine_utility_function(candidates[0])
        self.ballots = self.__prepare_ballots(voters, candidates)
        self.winner = self.__aggregate_votes(self.ballots)

    def __prepare_ballots(self, voters, candidates):

        # Ballot is the set of ordered candidate rankings from each voter
        ballots = []
        for voter in voters:
            ordering = \
                sorted(candidates, key=lambda cand: self.util_function(voter, cand, self.additional_info), reverse=True)
            ballots.append(ordering)
        return ballots
    
    def __aggregate_votes(self, ballots):         
        scores = dict.fromkeys(self.candidates, 0)
        num_candidates = len(self.voters)

        for ballot in ballots:
            for rank_index, candidate in enumerate(ballot):
                scores[candidate] += (num_candidates - 1) - rank_index
        
        highest_score = max(scores.values())
        tie_winning_candidates = \
            [candidate for candidate, score in scores.items() if score == highest_score]
        return np.random.choice(tie_winning_candidates)

class Popularity:
    def __init__(self, voters, candidates, additional_info) -> None:
        self.voters = voters
        self.candidates = candidates
        self.additional_info = additional_info
        self.util_function = determine_utility_function(candidates[0])
        self.ballots = self.__prepare_ballots(voters, candidates)
        self.winner = self.__aggregate_votes(self.ballots)

    def __prepare_ballots(self, voters, candidates):
        # top choice candidate from each voter
        ballots = []
        for voter in voters:
            winner = \
                max(candidates, key=lambda cand: self.util_function(voter, cand, self.additional_info))
            ballots.append(winner)

        return ballots
    
    def __aggregate_votes(self, ballots):
        scores = Counter(ballots)
        highest_score = max(scores.values())
        tie_winning_candidates = \
            [cand for cand, score in scores.items() if score == highest_score]
        return np.random.choice(tie_winning_candidates)

class Harmonic:
    def __init__(self, voters, candidates, additional_info) -> None:
        self.voters = voters
        self.candidates = candidates
        self.additional_info = additional_info
        self.util_function = determine_utility_function(candidates[0])
        self.ballots = self.__prepare_ballots(voters, candidates)
        self.winner = self.__aggregate_votes(self.ballots)

    def __prepare_ballots(self, voters, candidates):
        # Ballot is the set of ordered candidate rankings from each voter
        ballots = []
        for voter in voters:
            ordering = \
                sorted(candidates, key=lambda cand: self.util_function(voter, cand, self.additional_info), reverse=True)
            ballots.append(ordering)
        return ballots
    
    def __aggregate_votes(self, ballots):
        scores = dict.fromkeys(self.candidates, 0)

        for ballot in ballots:
            for rank_index, candidate in enumerate(ballot):
                scores[candidate] += (1/(rank_index+1))
        
        highest_score = max(scores.values())
        tie_winning_candidates = \
            [candidate for candidate, score in scores.items() if score == highest_score]
        return np.random.choice(tie_winning_candidates)

class InstantRunoff:
    def __init__(self, voters, candidates, additional_info) -> None:
        self.voters = voters
        self.candidates = set(candidates)
        self.additional_info = additional_info
        self.util_function = determine_utility_function(list(candidates)[0])
        self.ballots = self.__prepare_ballots(voters, list(candidates))
        self.winner = self.__aggregate_votes(self.ballots)

    def __prepare_ballots(self, voters, candidates):
        # Ballot is the set of ordered candidate rankings from each voter
        ballots = []
        for voter in voters:
            ordering = \
                sorted(candidates, key=lambda cand: self.util_function(voter, cand, self.additional_info), reverse=True)
            ballots.append(ordering)
        return ballots
    
    def __aggregate_votes(self, ballots):
        Eliminated = set([])

        while len(self.candidates) - len(Eliminated) > 2:
            scores = {candidate: 0 for candidate in self.candidates if candidate not in Eliminated}
            for ordering in ballots:
                not_eliminated_ordering = [i for i in ordering if i not in Eliminated]
                first_choice = not_eliminated_ordering[0]
                scores[first_choice] += 1 
            worst_candidate = min(scores, key=scores.get)
            worst_score = scores[worst_candidate]

            indifferent_candidates = [candidate for candidate in self.candidates.difference(Eliminated) if scores[candidate] == worst_score]
            # choose randomly one of the candidates with the lowest score to be eliminated
            Eliminated.add(np.random.choice(indifferent_candidates))

        return self.candidates.difference(Eliminated).pop()