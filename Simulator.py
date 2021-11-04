from Node import Node
from Utility import Utility

C = 3 * 10**8

class Simulator:

    def __init__(self, num_nodes, arrival_rate, simulation_time):
        self.simulation_time = simulation_time
        self.arrival_rate = arrival_rate
        self.prop_speed = C * (2.0/3.0)
        self.transmission_speed = 

        self.collision_count = 0
        self.total_transmitted = 0
        self.total_packets = 0
        
        self.transmitted_packets = []
        
        self.init_nodes(num_nodes)
    
    def init_nodes(self, num_nodes):
        A_int_rep = 65
        first_node = Node(chr(A_int_rep), self.prop_speed)
        self.nodes = [first_node]
        for i in range(1, num_nodes):
            new_node = Node(node_id=chr(i + A_int_rep), prop_speed = C * (2.0/3.0) )
            prev_node = self.nodes[i - 1]
            prev_node.right_node = new_node
            new_node.left_node = prev_node
            self.nodes.append(new_node)
        for node in self.nodes:
            node.init_prop_delay_lookup(node.left_node, node.right_node)

    def run(self):
        self.generate_packets()
        self.poll_packets()
    
    def generate_packets(self):
        for node in self.nodes:
            self.generate_packets_for_node(node)
    
    def generate_packets_for_node(self, node):
        cur_packet = Utility.poisson(self.arrival_rate)
        node.add_packet(cur_packet)
        while(cur_packet < self.simulation_time):
            cur_packet += Utility.poisson(self.arrival_rate)
            node.add_packet(cur_packet)
            
    def poll_packets(self):
        self.get_next_packet()
        self.check_collisions()
        
    def get_next_packet(self):
        next_node = min(self.nodes, key=lambda node: node.q[0] )
        return next_node
    
    def check_collisions(self):
        pass
    
    def carrier_sense(self) -> bool:
        threshold = len(self.nodes) *
        for packet in self.transmitted_packets:
            
        