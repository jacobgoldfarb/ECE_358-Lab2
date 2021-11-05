from Simulator import Simulator 
from Utility import Utility

def main():
    sim = Simulator(num_nodes=5, arrival_rate=100, simulation_time=10)
    sim.run()
    for node in sim.nodes:
        Utility.print_node_info(node)
    
    
if __name__ == "__main__":
    main()