
class Packet:
    
    def __repr__(self):
        return f"Arrival Time: {self.arrival_time}\nNode: {self.node}"
    
    def __init__(self, arrival_time, node):
        self.transmitted = False
        self.arrival_time = arrival_time
        self.node = node