from Node import Node
from Packet import Packet
from Utility import Utility

C = 3 * 10**8
PROP_TIME_BITS = 512.0
RETRY_MAX = 10

class Simulator:

    def __init__(self, num_nodes, arrival_rate, simulation_time, persistent):
        self.simulation_time = simulation_time
        self.arrival_rate = arrival_rate
        self.prop_speed = C * (2.0/3.0)
        self.retry_max = RETRY_MAX
        self.persistent = persistent

        self.total_transmitted = 0
        self.total_packets = 0
        
        self.dropped_packets = []
        self.successfully_transmitted_packets = []
        self.efficiency = 0.0
        self.transmission_rate = 10**6
        self.transmission_delay = 1500 / self.transmission_rate
        
        self.init_nodes(num_nodes)
    
    def init_nodes(self, num_nodes):
        first_node = Node(0, self.prop_speed)
        self.nodes = [first_node]
        for i in range(1, num_nodes):
            new_node = Node(i, self.prop_speed)
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
        num_success = len(self.successfully_transmitted_packets)
        self.efficiency = num_success / self.total_transmitted
        num_bytes_transmitted = num_success * 1500
        MEGA_BIT = 10**6 
        self.throughput = (num_bytes_transmitted / self.max_sim_time) / MEGA_BIT
    
    def generate_packets(self):
        for node in self.nodes:
            self.generate_packets_for_node(node)
    
    def generate_packets_for_node(self, node):
        packet_arrival_time = Utility.poisson(self.arrival_rate)
        new_packet = Packet(packet_arrival_time, node)
        node.add_packet(new_packet)
        self.total_packets += 1
        self.max_sim_time = self.simulation_time
        while(packet_arrival_time < self.simulation_time):
            packet_arrival_time += Utility.poisson(self.arrival_rate)
            new_packet = Packet(packet_arrival_time, node)
            node.add_packet(new_packet)
            self.total_packets += 1
            self.max_sim_time = max(self.max_sim_time, packet_arrival_time)
    
    def poll_packets(self):
        while self.at_least_one_node_has_packet():
            transmitting_node = self.get_node_with_next_packet()
            next_packet = transmitting_node.next_packet()
            if next_packet.arrival_time > self.simulation_time:
                break
            (carrier_failure, carrier_packet_time) = self.carrier_sense(next_packet)
            collided_packets = self.get_collisions(next_packet)
            collision_occurred = len(collided_packets) > 0
            
            if not collision_occurred and not carrier_failure:
                self.handle_transmittable_packet(transmitting_node)
            elif carrier_failure:
                self.handle_carrier_failure(transmitting_node, carrier_packet_time, next_packet)
            elif collision_occurred:
                num_collided = len(collided_packets) + 1
                self.total_transmitted += num_collided
                self.handle_collision(next_packet, collided_packets, transmitting_node)

    def handle_carrier_failure(self, node, carrier_packet_time, packet):
        if not self.persistent:
            backoff = self.get_backoff(node.num_carrier_failures)
            node.apply_wait_to_packets(backoff)
        else:
            node.apply_wait_to_packets(carrier_packet_time - packet.arrival_time)
    
    def handle_collision(self, youngest_packet, involved_packets, node):
        max_collision_time = max([youngest_packet.arrival_time] + [p.arrival_time for p in involved_packets])
        involved_node_ids = set([packet.node.id for packet in involved_packets + [youngest_packet]])
        for packet in involved_packets:
            collider_source = packet.node
            furthest_prop_delay = max([collider_source.prop_delay_lookup[node.id] for node in self.nodes if node.id in involved_node_ids and node.id != collider_source.id])
            self.handle_collision_for_packet(collider_source, None, 0)
        self.handle_collision_for_packet(node, max_collision_time)
            
    def handle_collision_for_packet(self, node, collision_time=None, prop_delay=0):
        node.num_collisions += 1
        if node.num_collisions > self.retry_max:
            self.drop_packet(node)
            node.num_collisions = 0
        else:
            backoff = self.get_backoff(node.num_collisions) + prop_delay
            if collision_time:
                node.apply_wait_to_packets(backoff, collision_time)
            else:
                node.apply_wait_to_packets(backoff)
    
    def get_backoff(self, fail_count):
        prop_time = PROP_TIME_BITS / float(self.transmission_rate)
        backoff = Utility.get_backoff(fail_count, prop_time)
        return backoff
    
    def drop_packet(self, node):
        self.dropped_packets.append(node.dequeue_packet())
        
    def at_least_one_node_has_packet(self):
        for node in self.nodes:
            if not node.empty():
                return True
        return False
    
    def handle_transmittable_packet(self, node):
        node.num_collisions = 0
        self.total_transmitted += 1
        transmittable_packet = node.dequeue_packet()
        # Change packet arrival time of all nodes that have packets with arrival times
        # less than this packets arrival time + transmission delay + propagation delay
        if not node.empty():
            node.apply_wait_to_packets(self.transmission_delay)
        self.successfully_transmitted_packets.append(transmittable_packet)
    
    def get_node_with_next_packet(self):
        non_empty_nodes = [node for node in self.nodes if not node.empty()]
        next_node = min(non_empty_nodes, key=lambda node: node.next_packet().arrival_time )
        return next_node
    
    def get_collisions(self, packet):
        collided_packets = []
        sender = packet.node
        for node in self.nodes:
            if node == sender or node.empty(): continue
            packet_candidate = node.next_packet()
            prop_delay_to_node = sender.prop_delay_lookup[node.id]
            first_bit_arrival_time = packet.arrival_time + prop_delay_to_node
            if packet_candidate.arrival_time <= first_bit_arrival_time:
                collided_packets.append(packet_candidate)
        return collided_packets
    
    def carrier_sense(self, packet) -> bool:
        # By the threshold time, any packets that were transmitted will no longer be considered in the carrier 
        # since these packets cannot possible meet the carrier sense failure requirements.
        threshold = packet.arrival_time - max(packet.node.prop_delay_lookup.values()) - self.transmission_delay
        sender = packet.node
        for transmitted_packet in self.successfully_transmitted_packets[::-1]:
            if transmitted_packet.arrival_time <= threshold: break
            if transmitted_packet.node == sender: continue
            transmitted_packet_node = transmitted_packet.node
            prop_delay_to_node = sender.prop_delay_lookup[transmitted_packet_node.id]
            first_bit_arrival_time = transmitted_packet.arrival_time + prop_delay_to_node
            last_bit_arrival_time = first_bit_arrival_time + self.transmission_delay
            if first_bit_arrival_time < packet.arrival_time < last_bit_arrival_time:
                return (True, last_bit_arrival_time)
        return (False, None)
        