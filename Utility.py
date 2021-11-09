import random
import math
import uuid


class Utility:

    @staticmethod
    def get_arrival_rate_from_rho(rho, transmission_rate=1_000_000, avg_packet_length=2000):
        return rho * transmission_rate / avg_packet_length

    @staticmethod
    # lambd is the rate parameter.
    def poisson(lambd=0.5):
        def ln(x): return math.log(x, math.e)

        U = random.random()
        return -(1 / lambd) * ln(1 - U)
    
    @staticmethod
    def print_node_info(node):
        print(f"Node: {node}\nPackets: {node.q[0].arrival_time}")
        print(f"Lookup: {node.prop_delay_lookup}\n")

    @staticmethod
    def generate_id(digits=4):
        id = str(uuid.uuid4())
        if digits > 16:
            return id
        else:
            return id[:digits]
        
    @staticmethod
    def get_backoff(i, prop_time):
        R = random.randint(0, 2**i - 1)
        return float(R) * prop_time