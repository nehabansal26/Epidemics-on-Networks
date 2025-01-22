import pickle  # Import pickle for serializing and deserializing Python objects
import numpy as np  # Import NumPy for numerical operations and handling arrays
import pandas as pd  # Import pandas for data manipulation and analysis
import argparse  # Import argparse for parsing command-line arguments
from tqdm import tqdm  # Import tqdm for displaying progress bars
import networkx as nx  # Import NetworkX for creating and analyzing complex networks

# Set up argument parsing to accept command-line arguments
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('network', type=str, help='Network file name')  # Argument for the network file name
parser.add_argument('start', type=int, help='Starting index for network file')  # Starting index of the network file
parser.add_argument('end', type=int, help='Ending index for network file')  # Ending index of the network filex
parser.add_argument('net_dir', type=str, help='Directory for network files')  # Directory containing network files
parser.add_argument('sample_dir', type=str, help='Directory for sample files')  # Directory containing sample files
parser.add_argument('dest_dir', type=str, help='Directory for saving results')  # Directory for saving output files
args = parser.parse_args()  # Parse the command-line arguments

print("process starts!")  # Print a message indicating that the processing has started


# Load network files from a pickle file
if args.network.find("bcms")>=0:
    network_files = [pickle.load(open(f"{args.net_dir}/{args.network}.pkl", "rb"))]
else:
    network_files = pickle.load(open(f"{args.net_dir}/{args.network}_{args.start}_{args.end}.pkl", "rb"))


# Load sample dictionary from a pickle file
sample_dict = pickle.load(open(f"{args.sample_dir}/{args.network}_{args.start}_{args.end}.pkl", "rb"))

## Degree Distributions
degree_dedup = {'OG': []}  # Initialize a dictionary to hold degree distributions without duplicates
for key, sample_dict_ in sample_dict.items():  # Iterate over each algorithm and its corresponding sample
    degree_dedup[key] = []  # Initialize a list for degree distributions for each algorithm
    for net_idx, sample_array in enumerate(sample_dict_):  # Iterate over each network index and its sample array
        G = network_files[net_idx]  # Retrieve the network corresponding to the current index
        # Extend the list with the degree of each node in the original graph
        degree_dedup['OG'].extend([G.degree(node) for node in G.nodes()])
        for sample_ls in sample_array:  # Iterate through each sample list
            temp_ls = [G.degree(node) for node in set(sample_ls)]  # Get the degree for unique nodes in the sample
            degree_dedup[key].extend(temp_ls)  # Add the degrees to the corresponding list for the algorithm
        
print("process completed, writing it")  # Indicate that the degree calculation is complete and results will be saved

# Save the degree distribution data to a pickle file
with open(f"{args.dest_dir}/{args.network}_{args.start}_{args.end}_deg.pkl", "wb") as f:
    pickle.dump(degree_dedup, f)  # Serialize and save the degree distributions

