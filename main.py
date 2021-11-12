from Simulator import Simulator 
from Utility import Utility

def main():
    nodes = [i for i in range(20, 120, 20)]
    efficiencies = []
    for num_nodes in nodes:
        sim = Simulator(num_nodes=num_nodes, arrival_rate=5, simulation_time=50)
        sim.run()
        efficiencies.append(sim.efficiency)
        print(sim.efficiency)
    
    
if __name__ == "__main__":
    main()