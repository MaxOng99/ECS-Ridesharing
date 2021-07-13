from models.passenger import Passenger
from models.solution import Solution

def borda_count(solutions: Solution, passengers: Passenger) -> Solution:

    num_of_candidates = len(solutions)
    scores = {solution_index: 0 for solution_index, _ in enumerate(solutions)}

    for passenger in passengers:
        ranked_solutions = passenger.rank_solutions(solutions)
        for rank_index, solution in enumerate(ranked_solutions):
            solution_id = solutions.index(solution)
            scores[solution_id] += (num_of_candidates - 1) - rank_index
    
    winner_solution_id = max(scores, key=scores.get)
    return solutions[winner_solution_id]









            
        






