import random  # Import the random library for random number generation
import numpy as np  # Import NumPy for numerical operations and array handling
import pickle  # Import pickle for saving and loading Python objects to and from files
import argparse  # Import argparse for command-line argument parsing
from tqdm import tqdm  # Import tqdm for progress bar functionality
import networkx as nx  # Import NetworkX for the creation and manipulation of complex networks

def get_samples(G, algo, num_samples=5000, num_walks=30):
    """
    Generate random samples from the graph G using the specified algorithm.
    
    :param G: The input graph (NetworkX graph)
    :param algo: The sampling algorithm ('RW' for Random Walk, 'MHRW' for Metropolis-Hastings Random Walk)
    :param num_samples: Total number of samples to generate
    :param num_walks: Number of walks to initiate in parallel
    :return: An array of sampled nodes
    """
    ## Graph information: number of nodes and edges
    N = len(G.nodes())  # Get the number of nodes in the graph
    edges = G.edges()  # Get the list of edges in the graph
    
    ## Transition rate matrix (T) initialization
    T = np.zeros((N, N))  # Create an NxN matrix initialized to zero
    for (i, j) in edges:  # Iterate through each edge in the graph
        if algo == 'MHRW':
            # For Metropolis-Hastings Random Walk
            if i != j and (i, j) in edges:
                T[i, j] = min([1, G.degree[i] / G.degree[j]])  # Transition probability based on node degrees
                T[j, i] = min([1, G.degree[j] / G.degree[i]])  # Symmetric transition probability
        if algo == 'RW':
            # For standard Random Walk
            if i != j and (i, j) in edges:
                T[i, j] = 1 / G.degree[i]  # Transition probability based on the degree of node i
                T[j, i] = 1 / G.degree[j]  # Transition probability based on the degree of node j

    ## Additional parameters required for sampling
    if algo == 'RW':
        # Get non-zero transitions for Random Walk
        T_non_zero = [np.nonzero(T[i, :])[0] for i in range(N)]  # Find non-zero transition nodes for each node
    if algo == 'MHRW':
        # Generate random probabilities for the Metropolis-Hastings algorithm
        random_probs = np.random.rand(num_walks, num_samples)

    ## Initialize dummy sample array to store samples
    sample_array = np.zeros((num_walks, num_samples))  # Create an array for sampled nodes
    sample_array[:, 0] = random.sample(list(G.nodes()), num_walks)  # Randomly select initial nodes for walks

    ## Fill the sample array with sampled nodes
    for itr in range(num_samples - 1):  # Loop over the number of samples
        if algo == 'RW':
            ## For each current node, select the next node based on transition probabilities
            next_node = [
                np.random.choice(T_non_zero[int(i)]) if len(T_non_zero[int(i)]) > 0 else int(i)
                for i in sample_array[:, itr]
            ]
            sample_array[:, itr + 1] = next_node  # Update the sample array with the next nodes
        if algo == 'MHRW':
            ## For Metropolis-Hastings, select the next node based on probabilities
            choices = [np.where(T[int(i), :] > random_probs[cnt, itr])[0] for cnt, i in enumerate(sample_array[:, itr])]
            next_node = [
                np.random.choice(choices[i]) if len(choices[i]) > 0 else sample_array[i, itr]
                for i in range(num_walks)
            ]
            sample_array[:, itr + 1] = next_node  # Update the sample array with the next nodes
    return sample_array  # Return the filled sample array

def process_network(net_type, net_ls_st, net_ls_end, sample_size, walks, source_dir, dest_dir):
    """
    Process the network by reading it from a file, sampling, and saving the results.
    
    :param net_type: Type of the network (for file naming)
    :param net_ls_st: Starting index for network list
    :param net_ls_end: Ending index for network list
    :param sample_size: Size of the samples to be generated
    :param walks: Number of walks to be initiated
    :param source_dir: Directory to read network files from
    :param dest_dir: Directory to save the sampled results
    """
    print("Reading network pickle...")  # Inform user that network reading is starting
    if net_type.find("bcms") >= 0:
        # Load the BCMS data network
        network_ls = [pickle.load(open(f"{source_dir}/{net_type}.pkl", "rb"))]  # Load from a single BCMS pickle file
    else:
        # Load the general network data
        network_ls = pickle.load(open(f"{source_dir}/{net_type}_{net_ls_st}_{net_ls_end}.pkl", "rb"))

    # Dictionary to hold samples for different algorithms
    samples_dict = {'RW': [], 'MHRW': []} 

    # Iterate over each network and perform sampling
    for net in tqdm(network_ls, total=len(network_ls)):
        for algo in ['RW', 'MHRW']:
            # Generate samples for each algorithm and store them
            sample_array = get_samples(G=net, algo=algo, num_samples=sample_size + 500, num_walks=walks)[:, 500:]
            samples_dict[algo].append(sample_array)  # Append the samples for the current algorithm

    # Save the generated samples to a pickle file
    pickle.dump(samples_dict, open(f"{dest_dir}/{net_type}_{net_ls_st}_{net_ls_end}.pkl", 'wb'))
    print(f"{net_type} done!")  # Inform user that processing for the network type is complete

# Create the argument parser for command-line execution
parser = argparse.ArgumentParser(description="Sample generation process.")

# Define command-line arguments
parser.add_argument('network_type', type=str, help='Name of the network')  # Network type
parser.add_argument('net_ls_st', type=int, help='Network list starting index')  # Starting index
parser.add_argument('net_ls_end', type=int, help='Network list ending index')  # Ending index
parser.add_argument('sample_size', type=int, help='Sample size')  # Desired sample size
parser.add_argument('walks', type=int, help="Number of different walks/samples")  # Number of walks
parser.add_argument('source_dir', type=str, help="Source directory to pick network files")  # Source directory for input
parser.add_argument('dest_dir', type=str, help="Directory for saving results")  # Destination directory for output
args = parser.parse_args()  # Parse the command-line arguments

# Call the process_network function with the parsed arguments
process_network(args.network_type, args.net_ls_st, args.net_ls_end, args.sample_size, args.walks, args.source_dir, args.dest_dir)
