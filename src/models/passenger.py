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
    
    def __str__(self):
        return f"Passenger {self.id}: {{Start: {self.start_id} | End: {self.destination_id}}}"
    
    def __repr__(self) -> str:
        return self.__str__()