from typing import List, Callable
from dataclasses import replace

from models.passenger import Passenger
from models.graph import Graph
from models.solution import Solution, TourNodeValue
from models.utility_functions import node_utility
from algorithms.greedy_insert import GreedyInsert, NewValidTourNode
from algorithms.voting_system import BordaCount, Popularity

class IterativeVoting2:
    def __init__(self, riders: List[Passenger], graph: Graph, params) -> None:
        self.riders = riders
        self.graph = graph
        self.params = params
        self.iterative_voting_rule = self.__voting_rule(params.get("iterative_voting_rule"))
        self.final_voting_rule = self.__voting_rule(params.get("final_voting_rule"))

    def __voting_rule(self, rule: str) -> Callable:
        if rule == "borda_count":
            return BordaCount
        elif rule == 'popularity':
            return Popularity

    def optimise(self):

        #Init sol
        sol: Solution = Solution(self.riders, self.graph)
        unallocated = self.riders
        rider_depart_node_dict = dict.fromkeys(unallocated, None)
        greedy_insert_algo = GreedyInsert(self.riders, self.graph, None)
        candidate_nodes = []
        candidate_voter_map = dict()

        for rider in self.riders:
            node_val = TourNodeValue(rider.start_id, rider.optimal_departure, 0)
            candidate_node = NewValidTourNode(node_val, None, None)
            candidate_voter_map[candidate_node] = rider
            candidate_nodes.append(candidate_node)

        vote_system = self.iterative_voting_rule(self.riders, candidate_nodes, additional_info=rider_depart_node_dict)
        winner_candidate = vote_system.winner
        allocated_rider = candidate_voter_map.get(winner_candidate)
        depart_node = rider_depart_node_dict.get(allocated_rider, None)

        updated_val = replace(winner_candidate.value, pick_ups=tuple([allocated_rider]))
        allocated_node = sol.llist.append(updated_val)

        if depart_node is None:
            rider_depart_node_dict[allocated_rider] = allocated_node
        else:
            unallocated.remove(allocated_rider)

        # Rest of allocation
        while unallocated:
            candidate_voter_map = dict()
            candidates = []
            for rider in unallocated:
                if rider_depart_node_dict.get(rider, None) is None:
                    valid_nodes = greedy_insert_algo.valid_tour_nodes(
                        rider.start_id,
                        rider.optimal_departure,
                        sol.llist.first,
                        "before"
                    )
                    best_node = max(valid_nodes, key=lambda node: node_utility(rider, node, additional_info=rider_depart_node_dict))
                    candidates.append(best_node)
                    candidate_voter_map[best_node] = rider
                else:
                    depart_node = rider_depart_node_dict.get(rider)
                    valid_nodes = greedy_insert_algo.valid_tour_nodes(
                        rider.destination_id,
                        rider.optimal_arrival,
                        depart_node,
                        "after"
                    )
                    best_node = max(valid_nodes, key=lambda node: node_utility(rider, node, additional_info=rider_depart_node_dict))
                    candidates.append(best_node)
                    candidate_voter_map[best_node] = rider

            vote_system = self.iterative_voting_rule(unallocated, candidates, additional_info=rider_depart_node_dict)
            winner_candidate = vote_system.winner
            allocated_rider = candidate_voter_map.get(winner_candidate)
            depart_node = rider_depart_node_dict.get(allocated_rider, None)
            allocated_node = greedy_insert_algo.update_sol(allocated_rider, sol, winner_candidate, depart_node)

            if depart_node is None:
                rider_depart_node_dict[allocated_rider] = allocated_node
            else:
                unallocated.remove(allocated_rider)

        # sol.check_constraint(complete=True)
        sol.create_rider_schedule()
        sol.calculate_objectives()
        return sol