import random
import math


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
