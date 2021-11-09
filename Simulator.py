from Node import Node
from Packet import Packet
from Utility import Utility
import sys

C = 3 * 10**8
PROP_TIME_BITS = 512.0

class Simulator:

    def __init__(self, num_nodes, arrival_rate, simulation_time):
        self.simulation_time = simulation_time
        self.arrival_rate = arrival_rate
        self.prop_speed = C * (2.0/3.0)
        self.retry_max = 10
        self.transmission_speed = 5

        self.collision_count = 0
        self.total_transmitted = 0
        self.total_packets = 0
        
        self.dropped_packets = []
        self.transmitted_packets = []
        
        self.init_nodes(num_nodes)
    
    def init_nodes(self, num_nodes):
        first_node = Node(Utility.generate_id(), self.prop_speed)
        self.nodes = [first_node]
        for i in range(1, num_nodes):
            new_node = Node(node_id=Utility.generate_id(), prop_speed = C * (2.0/3.0) )
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
        packet_arrival_time = Utility.poisson(self.arrival_rate)
        new_packet = Packet(packet_arrival_time, node)
        node.add_packet(new_packet)
        self.total_packets += 1
        while(packet_arrival_time < self.simulation_time):
            packet_arrival_time += Utility.poisson(self.arrival_rate)
            new_packet = Packet(packet_arrival_time, node)
            node.add_packet(new_packet)
            self.total_packets += 1
            
    def poll_packets(self):
        # for i in range(5):
        while self.at_least_one_node_has_packet():
            transmitting_node = self.get_node_with_next_packet()
            next_packet = transmitting_node.q[0]
            carrier_success = self.carrier_sense(next_packet)
            collision_success = self.check_collisions(next_packet)
            if collision_success and carrier_success:
                self.handle_transmittable_packet(transmitting_node)
            elif not carrier_success:
                # print("CSMA Failure")
                self.handle_carrier_failure(next_packet, transmitting_node)
                # handle backoff incase of carrier failure
            if not collision_success:
                self.collision_count += 1
                print("Packet collided")
                # handle dropping in case of collision
    
    def handle_carrier_failure(self, packet, node):
        packet.carrier_failure_count += 1
        if packet.carrier_failure_count >= self.retry_max:
            self.drop_packet(node)
        else:
            node.apply_wait_to_packets(self.get_backoff(packet))
    
    def get_backoff(self, packet):
        prop_time = PROP_TIME_BITS / float(packet.transmission_rate)
        return Utility.get_backoff(packet.carrier_failure_count, prop_time)
    
    def drop_packet(self, node):
        self.dropped_packets.append(node.dequeue_packet())
        
    def at_least_one_node_has_packet(self):
        for node in self.nodes:
            if not node.empty():
                return True
        return False
    
    def handle_transmittable_packet(self, node):
        self.total_transmitted += 1
        self.transmitted_packets.append(node.dequeue_packet())
        
    def get_node_with_next_packet(self):
        non_empty_nodes = [node for node in self.nodes if not node.empty()]
        next_node = min(non_empty_nodes, key=lambda node: node.q[0].arrival_time )
        return next_node
    
    def check_collisions(self, packet):
        threshold = packet.arrival_time - max(packet.node.prop_delay_lookup.values()) - packet.transmission_delay
        sender = packet.node
        for transmitted_packet in self.transmitted_packets[::-1]:
            # if transmitted_packet.arrival_time <= threshold:
            #     break
            if transmitted_packet.node == sender:
                continue
            transmitted_packet_node = transmitted_packet.node
            prop_delay_to_node = sender.prop_delay_lookup[transmitted_packet_node.id]
            if packet.arrival_time <= transmitted_packet.arrival_time + prop_delay_to_node:
                return False
        return True
    
    def carrier_sense(self, packet) -> bool:
        # By this time, any packets that were transmitted will no longer be considered in the carrier 
        # since these packets cannot possible meet the carrier sense failure requirements.
        threshold = packet.arrival_time - max(packet.node.prop_delay_lookup.values()) - packet.transmission_delay
        sender = packet.node
        for transmitted_packet in self.transmitted_packets[::-1]:
            if transmitted_packet.arrival_time <= threshold:
                break
            elif transmitted_packet.node == sender:
                continue
            transmitted_packet_node = transmitted_packet.node
            prop_delay_to_node = sender.prop_delay_lookup[transmitted_packet_node.id]
            if packet.arrival_time > transmitted_packet.arrival_time + prop_delay_to_node \
                and packet.arrival_time < transmitted_packet.arrival_time + prop_delay_to_node + packet.transmission_delay:
                    return False
        return True

            
        