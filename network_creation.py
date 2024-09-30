import networkx as nx  # Importing the NetworkX library for network creation and analysis
import pickle  # Importing pickle for saving and loading Python objects
import argparse  # Importing argparse for command-line argument parsing
import numpy as np  # Importing NumPy for numerical operations
from concurrent.futures import ThreadPoolExecutor, as_completed  # Importing ThreadPoolExecutor for parallel execution of tasks

def create_single_network(network_type, N, p, alpha, mean_k):
    # Function to create a single network based on the specified type
    if network_type == 'ER':
        # Generate an Erdős-Rényi random graph
        p_ER = mean_k / (N - 1)  # Calculate edge probability based on mean degree
        G = nx.gnp_random_graph(N, p_ER)  # Create the random graph
        # Remove isolated nodes (nodes with degree 0)
        G.remove_nodes_from([i for i in G.nodes() if G.degree[i] == 0])
        # Convert node labels to integers starting from 0
        G = nx.convert_node_labels_to_integers(G, first_label=0)
        return G  # Return the generated graph

    if network_type == 'SF':
        # Generate a Scale-Free network using the configuration model
        sequence = np.random.zipf(alpha, N)  # Draw from a Zipf distribution
        int_sequence = np.round(sequence).astype(int)  # Round to nearest integer
        if np.sum(int_sequence) % 2 != 0:
            int_sequence[0] += 1  # Ensure the sum is even for configuration model
        G = nx.configuration_model(int_sequence)  # Create the configuration model graph
        G = nx.Graph(G)  # Convert to a simple graph (removes self-loops)
        G.remove_edges_from(nx.selfloop_edges(G))  # Remove self-loops
        # Remove isolated nodes
        G.remove_nodes_from([i for i in G.nodes() if G.degree[i] == 0])
        # Convert node labels to integers starting from 0
        G = nx.convert_node_labels_to_integers(G, first_label=0)
        return G  # Return the generated graph

    if network_type == 'SW':
        # Generate a Small-World network using the Watts-Strogatz model
        G = nx.watts_strogatz_graph(N, mean_k, p)  # Create the small-world graph
        # Remove isolated nodes
        G.remove_nodes_from([i for i in G.nodes() if G.degree[i] == 0])
        # Convert node labels to integers starting from 0
        G = nx.convert_node_labels_to_integers(G, first_label=0)
        return G  # Return the generated graph

def create_networks(network_type, epochs, dest_dir, num_cores,start,end,N=10000, p=0.5, alpha=3, mean_k=5):
    # Function to create multiple networks in parallel and save them to a file
    network_ls = []  # List to hold generated networks
    
    # Use ThreadPoolExecutor to parallelize network creation
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        # Submit tasks to create networks in parallel
        futures = [executor.submit(create_single_network, network_type, N, p, alpha, mean_k) for _ in range(epochs)]
        
        # Iterate over completed futures
        for epoch, future in enumerate(as_completed(futures)):
            if epoch % 100 == 0:  # Print progress every 100 epochs
                print(f"Epoch {epoch}/{epochs}")
            network_ls.append(future.result())  # Append the result to the list
    
    print(f"Completed network creation for {network_type}")

    # Save the generated networks to a pickle file
    with open(f"{dest_dir}/{network_type}_{start}_{end}.pkl", 'wb') as f:
        pickle.dump(network_ls, f)  # Dump the list of networks to a file

# Create the parser for command-line arguments
parser = argparse.ArgumentParser(description="Process some integers.")

# Define command-line arguments
parser.add_argument('network_type', type=str, help='Name of the network')
parser.add_argument('epochs', type=int, help='The number of epochs for network creation')
parser.add_argument('dest_dir', type=str, help='Directory for storing results')
parser.add_argument('num_cores', type=int, help='number of cores for threading')
parser.add_argument('start', type=int, help='network start idx')
parser.add_argument('end', type=int, help='network end idx')

# Parse the command-line arguments
args = parser.parse_args()
# Call the function to create networks with the provided arguments
create_networks(args.network_type, args.epochs, args.dest_dir, args.num_cores,args.start,args.end)
