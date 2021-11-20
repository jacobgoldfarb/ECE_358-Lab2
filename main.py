from Simulator import Simulator 
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
from numba import jit

def main():
    nodes = [i for i in range(20, 120, 20)]
    # arrival_rates = [5, 12]
    arrival_rates = [7, 10,  20]
    sim_times = [50, 60]
    calculate_efficiency = True
    for sim_time in sim_times:
        efficiencies = {}
        for rate in arrival_rates:
            es = []
            for num_node in nodes:
                e, t = run_sim(rate, num_node, sim_time)
                point = e if calculate_efficiency else t
                es.append(point)
            efficiencies[rate] = es
            
        for rate in efficiencies:
            plt.plot(nodes, efficiencies[rate])
    plt.xlabel("Number of Nodes")
    ylabel = "Efficiency" if calculate_efficiency else "Throughput"
    plt.ylabel(ylabel)
    title = "Efficiency vs Number of Nodes" if calculate_efficiency else "Throughput vs Number of Nodes"
    plt.title(title)
    legend = [f"Simulation time: 50, Arrival rate: {rate}" for rate in arrival_rates]
    legend += [f"Simulation time: 60, Arrival rate: {rate}" for rate in arrival_rates]
    plt.legend(legend)
    plt.show()

def main_mp():
    queue = Queue()
    p1 = Process(target=run_sims, args=(5,queue,))
    p2 = Process(target=run_sims, args=(12,queue))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    results = {}
    while( not queue.empty() ):
        efficiency, nodes, rate = queue.get()
        if not rate in results:
            results[rate] = [[efficiency], [nodes]]
        else:
            results[rate][0].append(efficiency)
            results[rate][1].append(nodes)
    print(results)
    for rate in results:
        plt.plot(results[rate][1].sort(), results[rate][0].sort())
    plt.show()


def run_sims(arrival_rate, queue=None):
    nodes = [i for i in range(20, 120, 20)]
    processses = []
    for num_nodes in nodes:
        new_p = Process(target=run_sim, args=(arrival_rate, num_nodes, queue))
        processses.append(new_p)
    for p in processses:
        p.start()
    for p in processses:
        p.join()
    
@jit
def run_sim(arrival_rate, nodes, sim_time=10, queue=None):
    sim = Simulator(num_nodes=nodes, arrival_rate=arrival_rate, simulation_time=sim_time, persistent=True)
    sim.run()
    if queue:
        queue.put((sim.efficiency, nodes, arrival_rate))
    print(f"Efficiency: {str(sim.efficiency)[:4]}, Throughput: {str(sim.throughput)[:4]}, Arrival: {arrival_rate}, #Nodes: {nodes}")
    return (sim.efficiency, sim.throughput)

def debug():
    sim = Simulator(num_nodes=4, arrival_rate=5, simulation_time=3)
    sim.run()
    
    
    
if __name__ == "__main__":
    main()