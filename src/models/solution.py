from typing import Set
import igraph as ig

class TourNode:
    """The building block of a Solution object

    Attributes
    ----------
    location_id: int
        Bus station id
    arrival_time: float
        Timestamp at which the bus arrives at this station
    waiting_time: float
        Amount of time the bus remains stationary at this station
    departure_time: float
        Timestamp at which bus departs the station (arrival + waiting)
    pick_up: Set[Passenger]
        Set of Passengers that were picked up at this TourNode
    drop_off: Set[Passenger]
        Set of Passengers that were dropped off at this TourNode
    next: TourNode
        The next TourNode
    prev: TourNode
        The previous TourNode

    """

    def __init__(self, location_id: int, arrival_time: float, waiting_time: float) -> None:
        self.location_id = location_id
        self.arrival_time = arrival_time
        self.waiting_time = waiting_time
        self.departure_time = self.arrival_time + self.waiting_time

        self.pick_up = set()
        self.drop_off = set()

        self.next = None
        self.prev = None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.location_id}, {self.arrival_time}, {self.waiting_time})"

class Solution:
    """Model for Solution. Consists of a LinkedList of TourNodes

    Attributes
    ----------
    root: TourNode
        The starting point of the Solution
    tail: TourNode
        The ending point of the Solution
    waiting: Set[Passenger]
        Passengers that are currently waiting to board
    onboard: Set[Passenger]
        Passengers that are currently onboard
    serving: Set[Passenger]
        The set of onboard and waiting Passengers
    graph: igraph.Graph
        Graph object that is required to update the Solution object
    rider_schedule: Dict[str, Dict[int, float]]
        Records the departure and arrival time of each rider
    
    Methods
    ----------
    expand_tour(new_tour_node: TourNode, boarded: Set[Passenger], served: Set[Passenger])
        Grows the current Solution with a new TourNode. boarded and served are
        the new boarded and served Passengers after adding new_tour_node. These two
        sets will be used to update the state of the Solution object

    update_waiting_time(node: TourNode, new_waiting_time: float, boarded: Set[Passenger], served: Set[Passenger])
        Updates the waiting time at the given TourNode. boarded and served are
        the new boarded and served Passengers after updating the
        waiting time of node, These two sets will be used to update the 
        state of the Solution object

    stations_to_visit()
        Returns the set of location_ids from Passengers that have 
        not been completely served (waiting + onboard)

    get_current_node()
        Returns the most recent TourNode of the Solution (the tail)
    """
    

    def __init__(self, root_node: TourNode, riders: Set["Passenger"], graph: ig.Graph):
        self.root = root_node
        self.tail = root_node

        self.waiting = set(riders)
        self.serving = set(riders)
        self.onboard = set()

        self.graph = graph
        self.rider_schedule = {"departure": dict(), "arrival": dict()}

    def expand_tour(self, new_tour_node: TourNode, boarded: Set["Passenger"], served: Set["Passenger"]):
        self.__insert_after_tail(new_tour_node)
        self.__update_solution_state(new_tour_node, boarded, served)

    def update_waiting_time(self, node: TourNode, new_waiting_time: float, boarded: Set["Passenger"], served: Set["Passenger"]):
        node.waiting_time = new_waiting_time
        node.departure_time = node.arrival_time + node.waiting_time
        self.__update_solution_state(node, boarded, served)

    def stations_to_visit(self) -> Set[int]:
        stations_to_vist = set()

        for rider in self.waiting:
            stations_to_vist.add(rider.start_id)

        for rider in self.onboard:
            stations_to_vist.add(rider.destination_id)

        return stations_to_vist

    def get_current_node(self) -> TourNode:
        return self.tail

    def __insert_after_tail(self, new_node: TourNode):
        # Re-adjusts the LinkedList structure after the addition of a new TourNode
        self.tail.next = new_node
        new_node.prev = self.tail
        self.tail = new_node

    def __update_solution_state(self, tour_node: TourNode, new_onboard_riders, new_served_riders):
        # Updates the state of the Solution object (onboard, waiting, serving, rider_schedule)
        # This function is called when a new TourNode is added, or an existing TourNode is updated

        for rider in new_onboard_riders:
            self.rider_schedule["departure"][rider.id] = tour_node.departure_time
            tour_node.pick_up.add(rider)

        for rider in new_served_riders:
            self.rider_schedule["arrival"][rider.id] = tour_node.arrival_time
            tour_node.drop_off.add(rider)

        self.waiting = self.waiting - new_onboard_riders
        self.onboard = (self.onboard - new_served_riders).union(new_onboard_riders)
        self.serving = self.serving - new_served_riders

    def __str__(self) -> str:
        current_node = self.root
        tour_nodes = []
        while current_node:
            tour_nodes.append(current_node)
            current_node = current_node.next

        tour_repr = [f"({node.location_id}, {node.arrival_time}, {node.waiting_time}); P - {node.pick_up}; D - {node.drop_off})" for node in tour_nodes]
        return " -> \n".join(tour_repr)

    def __repr__(self) -> str:
        return self.__str__()
