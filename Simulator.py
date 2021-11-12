from Node import Node
from Packet import Packet
from Utility import Utility

C = 3 * 10**8
PROP_TIME_BITS = 512.0
RETRY_MAX = 10

class Simulator:

    def __init__(self, num_nodes, arrival_rate, simulation_time):
        self.simulation_time = simulation_time
        self.arrival_rate = arrival_rate
        self.prop_speed = C * (2.0/3.0)
        self.retry_max = RETRY_MAX

        self.collision_count = 0
        self.total_transmitted = 0
        self.total_packets = 0
        
        self.dropped_packets = []
        self.successfully_transmitted_packets = []
        self.efficiency = 0.0
        
        self.init_nodes(num_nodes)
    
    def init_nodes(self, num_nodes):
        first_node = Node(Utility.generate_id(), self.prop_speed)
        self.nodes = [first_node]
        for i in range(1, num_nodes):
            new_node = Node(Utility.generate_id(), self.prop_speed)
            prev_node = self.nodes[i - 1]
            prev_node.right_node = new_node
            new_node.left_node = prev_node
            self.nodes.append(new_node)
        for node in self.nodes:
            node.init_prop_delay_lookup(node.left_node, node.right_node)

    def run(self):
        self.generate_packets()
        self.poll_packets()
        self.calculate_metrics()
    
    def calculate_metrics(self):
        self.efficiency = float(self.total_packets - len(self.dropped_packets)) / float(self.total_packets)
    
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
        while self.at_least_one_node_has_packet():
            transmitting_node = self.get_node_with_next_packet()
            next_packet = transmitting_node.q[0]
            (carrier_failure, carrier_packet_time) = self.carrier_sense(next_packet)
            collided_packets = self.get_collisions(next_packet)
            collision_occurred = len(collided_packets) > 0
            
            if not collision_occurred and not carrier_failure:
                self.handle_transmittable_packet(transmitting_node)
                # transmitting_node.num_collisions = 0
            elif carrier_failure:
                self.handle_carrier_failure(transmitting_node, carrier_packet_time, next_packet)
            elif collision_occurred:
                num_collided = len(collided_packets) + 1
                self.total_transmitted += num_collided
                self.handle_collision(next_packet, collided_packets, transmitting_node)
                self.collision_count += num_collided

    def handle_carrier_failure(self, node, carrier_packet_time, packet, persistent=False):
        if persistent:
            backoff = self.get_backoff(packet.arrival_time, node.num_carrier_failures)
            node.apply_wait_to_packets(backoff)
        else:
            node.apply_wait_to_packets(carrier_packet_time - packet.arrival_time)
    
    def handle_collision(self, youngest_packet, involved_packets, node):
        max_collision_time = youngest_packet.arrival_time
        # Logic for other packet(s) involved in collision
        for packet in involved_packets:
            collider_source = packet.node
            collider_source.num_collisions += 1
            if collider_source.num_collisions > self.retry_max:
                self.drop_packet(collider_source)
                collider_source.num_collisions = 0
            else:
                backoff = self.get_backoff(packet, collider_source.num_collisions)
                collider_source.apply_wait_to_packets(backoff)
                max_collision_time = max(packet.arrival_time, max_collision_time)

        # Logic for youngest packet
        node.num_collisions += 1
        if node.num_collisions > self.retry_max:
            self.drop_packet(node)
            node.num_collisions = 0
        else:
            backoff = self.get_backoff(youngest_packet, node.num_collisions)
            node.apply_wait_to_packets(backoff, max_collision_time)
    
    def get_backoff(self, packet, fail_count):
        prop_time = PROP_TIME_BITS / float(packet.transmission_rate)
        return Utility.get_backoff(fail_count, prop_time)
    
    def drop_packet(self, node):
        self.dropped_packets.append(node.dequeue_packet())
        
    def at_least_one_node_has_packet(self):
        for node in self.nodes:
            if not node.empty():
                return True
        return False
    
    def handle_transmittable_packet(self, node):
        self.total_transmitted += 1
        self.successfully_transmitted_packets.append(node.dequeue_packet())
        
    def get_node_with_next_packet(self):
        non_empty_nodes = [node for node in self.nodes if not node.empty()]
        next_node = min(non_empty_nodes, key=lambda node: node.q[0].arrival_time )
        return next_node
    
    def get_collisions(self, packet):
        collided_packets = []
        sender = packet.node
        for node in self.nodes:
            if node == sender or node.empty(): continue
            packet_candidate = node.q[0]
            prop_delay_to_node = sender.prop_delay_lookup[node.id]
            if packet_candidate.arrival_time <= packet.arrival_time + prop_delay_to_node:
                collided_packets.append(packet_candidate)
        return collided_packets
    
    def carrier_sense(self, packet) -> bool:
        # By the threshold time, any packets that were transmitted will no longer be considered in the carrier 
        # since these packets cannot possible meet the carrier sense failure requirements.
        threshold = packet.arrival_time - max(packet.node.prop_delay_lookup.values()) - packet.transmission_delay
        sender = packet.node
        for transmitted_packet in self.successfully_transmitted_packets[::-1]:
            if transmitted_packet.arrival_time <= threshold:
                break
            if transmitted_packet.node == sender:
                continue
            transmitted_packet_node = transmitted_packet.node
            prop_delay_to_node = sender.prop_delay_lookup[transmitted_packet_node.id]
            first_bit_arrival_time = transmitted_packet.arrival_time + prop_delay_to_node
            last_bit_arrival_time = first_bit_arrival_time + transmitted_packet.transmission_delay
            if first_bit_arrival_time < packet.arrival_time < last_bit_arrival_time:
                return (True, last_bit_arrival_time)
        return (False, None)

            
        