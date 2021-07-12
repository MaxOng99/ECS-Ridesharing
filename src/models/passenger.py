import random

class Passenger:

    def __init__(self, id, start, destination):
        """
        Args:
            start (int): Node ID of start location
            destination (int): Node ID of destination
        """
        self.id = id
        self.start_id = start
        self.destination_id = destination
        self.beta = random.uniform(0, 1)
        self.optimal_departure = 0
        self.optimal_arrival = 0

    def rank_solutions(self, solutions):
        return sorted(solutions, key=lambda sol: self.get_utility(sol), reverse=True)
    
    def get_utility(self, solution):
        eligible_node_pairs = solution.eligible_node_pairs(self.start_id, self.destination_id)

        max_utility = 0
        for source_node, target_node in eligible_node_pairs:
            utility = self.__utility_function(source_node.timestamp, target_node.timestamp)
            if utility > max_utility:
                max_utility = utility
        return max_utility
        
    def __utility_function(self, departure_time, arrival_time):
        return self.beta**(abs(self.optimal_departure - departure_time)) + \
            self.beta**(abs(self.optimal_arrival - arrival_time))

    def __str__(self):
        return f"Passenger {self.id}: {{Start: {self.start_id} | End: {self.destination_id}}}"
    
    def __repr__(self) -> str:
        return self.__str__()