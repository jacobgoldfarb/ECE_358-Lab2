from collections import deque

class Node:
    
    def __repr__(self):
        return self.id
    
    def __init__(self, node_id, prop_speed, distance=10):
        self.id = node_id
        self.distance = distance
        self.prop_speed = prop_speed

        self.q = deque()
        self.left_node = None
        self.right_node = None
        self.num_collisions = 0
        self.prop_delay_lookup = {}
        
    def add_packet(self, packet):
        self.q.append(packet)
    
    def init_prop_delay_lookup(self, left, right, level=1):
        if not left and not right:
            return
        if left:
            self.prop_delay_lookup[left.id] = self.distance * level / self.prop_speed
        if right:
            self.prop_delay_lookup[right.id] = self.distance * level / self.prop_speed
        next_left = None if not left else left.left_node
        next_right = None if not right else right.right_node
        self.init_prop_delay_lookup(next_left, next_right, level + 1)
    
        