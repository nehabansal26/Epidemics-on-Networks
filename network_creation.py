import networkx as nx
import pickle
import argparse
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_single_network(network_type, N, p, alpha, mean_k):
    if network_type=='ER':
        p_ER = mean_k / (N - 1)
        G = nx.gnp_random_graph(N, p_ER)
        G.remove_nodes_from([i for i in G.nodes() if G.degree[i]==0])
        G = nx.convert_node_labels_to_integers(G, first_label=0)
        return G
    if network_type == 'SF':
        sequence = np.random.zipf(alpha, N)
        int_sequence = np.round(sequence).astype(int)
        if np.sum(int_sequence)%2!=0: int_sequence[0]+=1
        G = nx.configuration_model(int_sequence)
        G = nx.Graph(G)
        G.remove_edges_from(nx.selfloop_edges(G))
        G.remove_nodes_from([i for i in G.nodes() if G.degree[i]==0])
        G = nx.convert_node_labels_to_integers(G, first_label=0)
        return G
    if network_type == 'SW':
        G = nx.watts_strogatz_graph(N,mean_k,p)
        G.remove_nodes_from([i for i in G.nodes() if G.degree[i]==0])
        G = nx.convert_node_labels_to_integers(G, first_label=0)
        return G
    

    
def create_networks(network_type, epochs, file_pre,num_cores, N=10000, p=0.5, alpha=3, mean_k=5):
    network_ls = []
    
    # Use ThreadPoolExecutor to parallelize network creation
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(create_single_network, network_type, N, p, alpha, mean_k) for _ in range(epochs)]
        for epoch, future in enumerate(as_completed(futures)):
            if epoch % 100 == 0:
                print(f"Epoch {epoch}/{epochs}")
            network_ls.append(future.result())
    
    print(f"Completed network creation for {network_type}")

    filename = f"{network_type}_{file_pre}.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(network_ls, f)

# Create the parser
parser = argparse.ArgumentParser(description="Process some integers.")

# Define arguments
parser.add_argument('network_type', type=str, help='Name of the network')
parser.add_argument('epochs', type=int, help='The number of epochs for network creation')
parser.add_argument('file_pre', type=str, help='The file prefix for saving the networks')
parser.add_argument('num_cores', type=int, help='number of cores for threading')

# Parse the arguments
args = parser.parse_args()
create_networks(args.network_type, args.epochs, args.file_pre,args.num_cores)
