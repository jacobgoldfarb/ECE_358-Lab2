from Simulator import Simulator 
import matplotlib.pyplot as plt
from multiprocessing import Process

def main():
    nodes = [i for i in range(20, 120, 20)]
    arrival_rates = [5, 12]
    efficiencies = {}
    for rate in arrival_rates:
        es = []
        for num_node in nodes:
            e = run_sim(rate, num_node)
            es.append(e)
        efficiencies[rate] = es
        
    for rate in efficiencies:
        plt.plot(nodes, efficiencies[rate])
    plt.show()

def main_multi_processed():
    p1 = Process(target=run_sims, args=(5,))
    p2 = Process(target=run_sims, args=(12,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    plt.show()

def run_sims(arg):
    arrival_rate = arg
    nodes = [i for i in range(20, 120, 20)]
    processses = []
    for num_nodes in nodes:
        new_p = Process(target=run_sim, args=(arrival_rate, num_nodes))
        processses.append(new_p)
    for p in processses:
        p.start()
    for p in processses:
        p.join()
    
def run_sim(arrival_rate, nodes):
    sim = Simulator(num_nodes=nodes, arrival_rate=arrival_rate, simulation_time=10)
    sim.run()
    print(f"{sim.efficiency}, {arrival_rate}, {nodes}")
    return sim.efficiency

def debug():
    sim = Simulator(num_nodes=4, arrival_rate=5, simulation_time=3)
    sim.run()
    
    
    
if __name__ == "__main__":
    main()