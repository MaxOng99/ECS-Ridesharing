import copy
from typing import List, Union
from dataclasses import dataclass, replace

import numpy as np
from pyllist.dllist import dllistnode

from models.graph import Graph
from models.passenger import Passenger
from models.solution import TourNodeValue, Solution
from models.utility_functions import node_utility

@dataclass(frozen=True)
class ExistingValidTourNode:
    ref_node: dllistnode
    value: TourNodeValue

@dataclass(frozen=True)
class NewValidTourNode:
    value: TourNodeValue
    ref_node: dllistnode
    insert_position: str

@dataclass(frozen=True)
class InsertionContext:
    ref_node: dllistnode
    position: str

class WaitTimeError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class CreateNodeError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class GreedyInsert:
    def __init__(self, riders, graph: Graph, params) -> None:
        self.riders = riders
        self.graph = graph
        self.params = params

    def optimise(self) -> Solution:
        np.random.shuffle(self.riders)

        if self.params['multiple_iterations']:
            solutions: List[Solution] = []
            for rider in self.riders:
                # Initialize solution by allocating first rider
                solution: Solution = self.initialise_solution(rider)
                temp_riders = copy.copy(self.riders)
                temp_riders.remove(rider)

                # Allocate n other riders
                for rider in temp_riders:
                    departure_node = self.allocate_rider(rider, solution, departure_node=None)
                    arrival_node = self.allocate_rider(rider, solution, departure_node=departure_node)

                solution.check_constraint(complete=True)
                solution.create_rider_schedule()
                solution.calculate_objectives()
                solutions.append(solution)
            
            return max(solutions, key=lambda sol: sol.objectives[self.params['objective']])
            
        else:
            solution: Solution = self.initialise_solution(self.riders[0])

            # Allocate n other riders
            for rider in self.riders[1:]:
                departure_node = self.allocate_rider(rider, solution, departure_node=None)
                arrival_node = self.allocate_rider(rider, solution, departure_node=departure_node)

            solution.check_constraint(complete=True)
            solution.create_rider_schedule()
            solution.calculate_objectives()
            return solution

    def initialise_solution(self, first_rider: Passenger) -> None:
        sol = Solution(self.riders, self.graph)
        optimal_depart = first_rider.optimal_departure
        depart_loc = first_rider.start_id
        optimal_arrival = first_rider.optimal_arrival
        arrival_loc = first_rider.destination_id

        depart_node_val = TourNodeValue(depart_loc, 0, optimal_depart, pick_ups=tuple([first_rider]))
        
        arrival_time = self.__calc_new_node_arrival_time(dllistnode(depart_node_val), arrival_loc)
        waiting_time = self.calc_wait_time(arrival_time, optimal_arrival, None, None)
        arrival_node_val = TourNodeValue(arrival_loc, arrival_time, waiting_time, drop_offs=tuple([first_rider]))
        sol.llist.append(depart_node_val)
        sol.llist.append(arrival_node_val)

        return sol
        
    def allocate_rider(self, rider, solution, departure_node=None):
        loc_id = rider.start_id if not departure_node else rider.destination_id
        pref_time = rider.optimal_departure if not departure_node else rider.optimal_arrival
        start_node = solution.llist.first if not departure_node else departure_node
        pos = "before" if not departure_node else "after"

        valid_tns = self.valid_tour_nodes(loc_id, pref_time, start_node, pos)
        best_tn = max(valid_tns, key=lambda node: node_utility(rider, node, additional_info={rider: departure_node}))
        allocated_node = self.update_sol(rider, solution, best_tn, departure_node)
        return allocated_node

    def update_sol(self, rider, sol, best_tn, departure_node):
        if departure_node is None:
            updated_val = replace(best_tn.value, pick_ups=best_tn.value.pick_ups + tuple([rider]))
        else:
            updated_val = replace(best_tn.value, drop_offs=best_tn.value.drop_offs + tuple([rider]))
        
        if type(best_tn) is NewValidTourNode:
            if best_tn.insert_position == "before":
                new_node = sol.llist.insert(updated_val, before=best_tn.ref_node)
                self.__update_next_node(new_node.next)
            elif best_tn.insert_position == "after":
                new_node = sol.llist.insert(updated_val, after=best_tn.ref_node)
                self.__update_next_node(new_node.next)
            sol.check_constraint()
            return new_node

        elif type(best_tn) is ExistingValidTourNode:
            best_tn.ref_node.value = updated_val
            return best_tn.ref_node

    def valid_tour_nodes(self, input_loc, pref_time, start_node, pos) -> List[Union[ExistingValidTourNode, NewValidTourNode]]:
        valid_existing_tour_nodes = self.__valid_existing_nodes(input_loc, start_node)
        valid_insert_contexts = self.__valid_insert_positions(input_loc, pos, start_node)
        valid_new_tour_nodes = list(map(lambda insert_ctx: self.__create_node(
            insert_ctx.ref_node,
            insert_ctx.position,
            input_loc,
            pref_time
        ), valid_insert_contexts))
        return valid_existing_tour_nodes + valid_new_tour_nodes
        
    def __valid_existing_nodes(self, input_loc, start_node) -> List[ExistingValidTourNode]:
        filtered = filter(lambda node: node.value.location_id == input_loc, start_node.iternext())
        valid_existing_nodes = list(map(
            lambda node: ExistingValidTourNode(node, node.value),
            filtered
        ))
        return valid_existing_nodes

    def __valid_insert_positions(self, input_loc, position: str, start_node: dllistnode) -> List[InsertionContext]:
        insert_positions = []
        for node in start_node.iternext():
            if self.insertion_constraint_satisfied(input_loc, node, position=position):
                insert_positions.append(InsertionContext(node, position))
            
            if node.next is None and position == "before":
                if self.insertion_constraint_satisfied(input_loc, node, position="after"):
                    insert_positions.append(InsertionContext(node, "after"))
        return insert_positions
    
    def __calc_new_node_arrival_time(self, prev_node, location_id):
        if prev_node:
            prev_location = prev_node.value.location_id
            prev_departure_time = prev_node.value.departure_time
            return prev_departure_time + self.graph.travel_time(prev_location, location_id)
        else:
            return 0
    
    def __calc_next_node_new_arrival_time(self, next_node, location_id):
        if next_node is None:
            raise ValueError("calc_next_node_new_arrival_time argument next_node cannot be None")
        
        input_to_next = self.graph.travel_time(location_id, next_node.value.location_id)

        if next_node.prev:
            prev_departure_time = next_node.prev.value.departure_time
            prev_location_id = next_node.prev.value.location_id

            prev_to_input = self.graph.travel_time(prev_location_id, location_id)
            return prev_departure_time + prev_to_input + input_to_next
        else:
            return input_to_next

    def calc_wait_time(self, rider_arrival, rider_preferred, next_arrival=None, next_departure=None):
        if next_arrival is None and next_departure is None:
            return max(rider_preferred - rider_arrival, 0)
        
        negative_nums = filter(
            lambda time: time < 0,
            [rider_arrival, rider_preferred, next_arrival, next_departure]
        )

        if len(list(negative_nums)) > 0:
            raise WaitTimeError("Unable to calculate wait time, some arguments are negative")
        elif next_departure < next_arrival:
            raise WaitTimeError("Next node's departure time must not be less than its arrival time")

        else:
            allowable_wait_time = next_departure - next_arrival
            preferred_wait_time = max(rider_preferred - rider_arrival, 0)
            return min(allowable_wait_time, preferred_wait_time)

    def __create_node(self, ref_node, pos, loc_id, pref_time) -> NewValidTourNode:
        if not self.insertion_constraint_satisfied(loc_id, ref_node, pos):
            raise CreateNodeError("Insertion constraint is not satisfied")

        prev_node, next_node = self.adjacent_nodes_after_insertion(ref_node, pos)
        new_node_arrival_time = self.__calc_new_node_arrival_time(prev_node, loc_id)

        if next_node:
            next_node_new_arrival_time = self.__calc_next_node_new_arrival_time(next_node, loc_id)
            new_node_wait_time = self.calc_wait_time(
                new_node_arrival_time,
                pref_time,
                next_node_new_arrival_time,
                next_node.value.departure_time
            )
            new_val = TourNodeValue(loc_id, new_node_arrival_time, new_node_wait_time)
            return NewValidTourNode(new_val, ref_node, pos)
        else:
            new_node_wait_time = self.calc_wait_time(new_node_arrival_time, pref_time, None, None)
            new_val = TourNodeValue(loc_id, new_node_arrival_time, new_node_wait_time)
            return NewValidTourNode(new_val, ref_node, pos)

    def __update_next_node(self, next_affected_node: dllistnode) -> None:
        if next_affected_node:
            prev_node_val = next_affected_node.prev.value
            travel_time = self.graph.travel_time(prev_node_val.location_id, next_affected_node.value.location_id)
            next_new_arrival_time = prev_node_val.departure_time + travel_time
            next_new_wait_time = next_affected_node.value.departure_time - next_new_arrival_time
            updated_val = replace(next_affected_node.value, arrival_time=next_new_arrival_time, waiting_time=next_new_wait_time)
            next_affected_node.value = updated_val

    def adjacent_nodes_after_insertion(self, ref_node: dllistnode, position: str):
        prev_node = ref_node.prev if position == "before" else ref_node
        next_node = ref_node if position == "before" else ref_node.next
        return prev_node, next_node

    def insertion_constraint_satisfied(self, location_id, ref_node: dllistnode, position: str) -> bool:
        if self.__adjacent_loc_constraint_satisfied(location_id, ref_node, position) and \
            self.__departure_constraint_satisfied(location_id, ref_node, position):
            return True
        else:
            return False
        
    def __adjacent_loc_constraint_satisfied(self, location_id, node: dllistnode, position: str) -> bool:
        prev_node, next_node = self.adjacent_nodes_after_insertion(node, position)

        if prev_node and prev_node.value.location_id == location_id or \
            next_node and next_node.value.location_id == location_id:
            return False
        else:
            return True
        
    def __departure_constraint_satisfied(self, location_id, ref_node: dllistnode, position: str) -> bool:
        prev_node, next_node = self.adjacent_nodes_after_insertion(ref_node, position)

        if next_node:
            next_node_val = next_node.value
            input_to_next = self.graph.travel_time(location_id, next_node_val.location_id)
            if prev_node:
                prev_node_val = prev_node.value
                prev_to_input = self.graph.travel_time(prev_node_val.location_id, location_id)
                return prev_node_val.departure_time + prev_to_input + input_to_next <= \
                    next_node_val.departure_time
            else:
                return input_to_next <= next_node_val.departure_time
        else:
            return True