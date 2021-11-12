
class Packet:
    
    def __repr__(self):
        return f"Arrival Time: {self.arrival_time}\nNode: {self.node}"
    
    def __init__(self, arrival_time, node, length = 1500, transmission_rate=10**6):
        self.transmitted = False
        self.arrival_time = arrival_time
        self.length = length
        self.transmission_rate = transmission_rate
        self.transmission_delay = self.length / self.transmission_rate
        self.node = node