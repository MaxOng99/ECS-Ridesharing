from typing import Callable, Union, Tuple, Set, List
from models.passenger import Passenger
from models.solution import Solution, TourNode
from utils.graph_utils import travel_time
from copy import deepcopy
import igraph as ig
import random


class IterativeVoting:
    """Voting algorithm to find sub-optimal Solution

    Attributes
    ----------
    riders: Set[Passenger]
        Set of Passengers for this simulation instance
    graph: igraph.Graph
        Pruned graph that only consists of start and end location of Passengers
    voting_rule: Callable
        Voting rule can either be majority or borda_count
    
    Methods
    ----------
    optimise()
        Constructs n solutions based on the iterative voting procedure,
        and then vote on these solutions
    """

    def __init__(self, riders: Set[Passenger], graph: ig.Graph, params) -> None:
        self.riders = riders
        self.graph = graph
        self.voting_rule = self.__voting_rule(params.get("voting_rule"))
    
    def optimise(self):

        candidate_solutions = []

        for location_id in set(self.graph.vs["location_id"]):
            candidate_solutions.append(self.__initiate_voting(location_id))

        # List of solution ranking function from each Passenger
        solution_ranking_functions = [rider.rank_solutions for rider in self.riders]
        return self.voting_rule(candidate_solutions, solution_ranking_functions)

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return VotingRules.borda_count
        else:
            # TO-DO: Implement majority voting
            pass

    def __initiate_voting(self, start_location: int):
        
        # Initialise Solution object
        root_node = TourNode(location_id=start_location, arrival_time=0, waiting_time=0)
        new_solution = Solution(root_node, deepcopy(self.riders), self.graph)

        # Repeat voting process until all Passengers are served
        while len(new_solution.serving) > 0:

            current_node = new_solution.get_current_node()
            candidate_locations = new_solution.stations_to_visit()

            # Supply candidate locations AND riders' location ranking function to the voting rule
            location_ranking_functions = [rider.rank_locations for rider in new_solution.serving]
            additional_arguments = {"solution": new_solution}
            voted_location = self.voting_rule(candidate_locations, location_ranking_functions, additional_arguments)

            # Grow the Solution if the voted location is different
            # than the current location
            if voted_location != current_node.location_id:
                time_taken = travel_time(current_node.location_id, voted_location, new_solution.graph)
                new_node = TourNode(voted_location, current_node.departure_time + time_taken, 0)
                boarded_riders, served_riders = self.__get_affected_riders(new_node, new_solution)
                new_solution.expand_tour(new_node, boarded_riders, served_riders)

            # Increase the waiting time at the current location if riders
            # vote for the same location id as the previous iteration
            else:
                boarded, served = self.__get_affected_riders(TourNode(current_node.location_id, current_node.arrival_time, current_node.waiting_time + 50), new_solution)
                new_solution.update_waiting_time(current_node, current_node.waiting_time + 50, boarded, served)

        return new_solution

    def __get_affected_riders(self, tour_node: TourNode, solution: Solution) -> Tuple[Set[Passenger], Set[Passenger]]:
        # Returns the set of Passengers that will board or disembark the bus when
        # 1. This TourNode is added to the solution (new TourNode)
        # 2. This TourNode is updated (existing TourNode)

        boarded = set()
        served = set()

        for rider in solution.waiting:
            if rider.choose_to_board(tour_node.location_id, tour_node.departure_time, solution):
                rider.status = "onboard"
                boarded.add(rider)
        
        for rider in solution.onboard:
            if rider.choose_to_disembark(tour_node.location_id):
                rider.status = "served"
                served.add(rider)
        
        return (boarded, served) 

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
