from Simulator import Simulator 
from Utility import Utility

def main():
    sim = Simulator(num_nodes=5, arrival_rate=20, simulation_time=10)
    sim.run()
    
    
if __name__ == "__main__":
    main()