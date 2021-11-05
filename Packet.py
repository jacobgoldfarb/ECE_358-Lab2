
class Packet:
    
    def __repr__(self):
        return f"Arrival Time: {self.arrival_time}\nNode: {self.node} \
            \nTransmission Delay: {self.transmission_delay}\n"
    
    def __init__(self, arrival_time, node, length = 1000, transmission_rate=10**6):
        self.transmitted = False
        self.arrival_time = arrival_time
        self.length = length
        self.transmission_rate = transmission_rate
        self.transmission_delay = self.length / self.transmission_rate
        self.node = node
    
        
    def time_to_node(self, other_node):
        delay = self.transmission_delay
        if self.node == other_node:
            return delay
        else:
            return delay + self.node.prop_delay_lookup[other_node.id]

