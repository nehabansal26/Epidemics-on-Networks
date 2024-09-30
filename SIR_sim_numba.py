import numpy as np  # Import NumPy for numerical computations and handling arrays
import pickle  # Import pickle for serializing and deserializing Python objects
import argparse  # Import argparse for parsing command-line arguments
import random  # Import random for generating random numbers
import EoN  # Import EoN for epidemic modeling functions
import pandas as pd  # Import pandas for data manipulation and analysis
from tqdm import tqdm  # Import tqdm for creating progress bars in loops
import os  # Import os for interacting with the operating system
import subprocess  # Import subprocess for executing shell commands
from numba import njit, config  # Import Numba for JIT compilation to optimize functions
import networkx as nx  # Import NetworkX for working with graph data structures

# config.DEBUG = True  # Uncomment to enable debugging mode in Numba

@njit  # JIT compile the function for performance
def get_req_dict(cnt_G, beta, node_ls, trans_df):
    """
    Create a request dictionary that holds transmission details for each node.

    Parameters:
    - cnt_G: Count of the current graph/network index
    - beta: Transmission rate parameter
    - node_ls: List of nodes in the graph
    - trans_df: DataFrame containing transmission details

    Returns:
    - req_dict: An array of required data for each node
    """
    req_dict = np.empty((len(node_ls), 5), dtype=np.float64)  # Initialize an empty array for the results
    idx = 0  # Index to keep track of filled entries
    for node in node_ls:
        # Check if the node is involved in any transmission
        if (node in trans_df[:, 1]) or (node in trans_df[:, 2]):
            req_dict[idx] = [cnt_G, beta, node,  # Store the current graph count, beta, and node
                             np.max(trans_df[trans_df[:, 2] == node, 0]),  # Max time of transmission for the node
                             len(trans_df[trans_df[:, 1] == node, 1])]  # Number of transmissions from the node
            idx += 1  # Increment index
    return req_dict[:idx]  # Return the filled portion of req_dict

def process_network(G, beta, initial_I, cnt_G, gamma):
    """
    Simulate the SIR model on a given network.

    Parameters:
    - G: The graph/network to simulate
    - beta: The transmission rate
    - initial_I: The number of initially infected nodes
    - cnt_G: Count of the current graph/network index
    - gamma: The recovery rate

    Returns:
    - req_dict: A dictionary of transmission details for the nodes
    """
    infected_nodes = random.sample(list(G.nodes), initial_I)  # Randomly select initial infected nodes
    # Run the SIR simulation using the Gillespie algorithm
    sim = EoN.Gillespie_SIR(G=G, tau=beta, gamma=gamma, initial_infecteds=infected_nodes,
                            return_full_data=True)

    # Convert transmission data into a NumPy array
    trans_df = np.array(sim.transmissions(), dtype=np.float64)  # Columns: ['time', 'source', 'target']
    trans_df[np.isnan(trans_df.astype(float))] = -1  # Replace NaN values with -1
    node_ls = np.array(list(G.nodes()))  # Convert the list of nodes into a NumPy array
    req_dict = get_req_dict(cnt_G, beta, node_ls, trans_df)  # Generate the request dictionary

    return req_dict  # Return the request dictionary

def main(filename, st, end, gamma_, source_dir, dest_dir):
    """
    Main function to read a network file and run the SIR simulation.

    Parameters:
    - filename: The name of the network file
    - st: Starting index for the network list
    - end: Ending index for the network list
    - gamma_: Recovery rate parameter
    - source_dir: Directory to source the network files
    - dest_dir: Directory to save the results
    """
    gamma = 1 / gamma_  # Convert recovery rate parameter
    initial_I = 100  # Set the number of initially infected nodes
    if filename.find("bcms") >= 0:  # Check if the filename contains "bcms"
        with open(f'{source_dir}/{filename}.pkl', 'rb') as f:  # Load the network data
            G = pickle.load(f)
            # Create a mapping from node to index for relabeling
            node_idx = {node: i for i, node in enumerate(G.nodes())}
            net = nx.relabel_nodes(G, node_idx)  # Relabel nodes in the graph
            networks_ls = [net] * end  # Create a list of the same network repeated 'end' times
    else:
        # Load networks based on the given filename and indices
        with open(f'{source_dir}/{filename}_{st}_{end}.pkl', 'rb') as f:
            networks_ls = pickle.load(f)
    
    print(f"Read network file!")  # Inform user that the network file has been read
    SIR_dict = []  # Initialize a list to hold results

    # Iterate over beta values from 0 to 1 in steps of 0.1
    for beta in np.arange(0, 1.1, 0.1):
        # Process each network in the list with a progress bar
        for cnt_G, G in enumerate(tqdm(networks_ls, total=len(networks_ls))):
            req_dict = process_network(G, beta, initial_I, cnt_G, gamma)  # Process the network
            SIR_dict.append(req_dict)  # Append the results to the SIR_dict list
            
    print("Starting to write pickle file!")  # Inform user that results are being saved
    # Save the SIR results to a pickle file
    with open(f"{dest_dir}/{filename}_{st}_{end}_{gamma_}.pkl", 'wb') as f:
        pickle.dump(SIR_dict, f)  # Serialize and save the results
    print(f"{filename} done!")  # Notify that processing for the filename is complete

    # Uncomment below to send the file to a remote server using SCP
    # result = subprocess.run(f"scp /home/neha/{filename}_{st}_{end}_{gamma_}_SIR.pkl neha@siren.maths.cf.ac.uk:/home/neha/results/"
    #                         , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # print(result.stdout)  # Print standard output of the SCP command

    # if result.stderr:  # Check for errors during the SCP operation
    #     print("Error:")
    #     print(result.stderr)

    # os.remove(f"/home/neha/{filename}_{st}_{end}_{gamma_}_SIR.pkl")  # Uncomment to remove the local file

# Set up argument parsing for command-line execution
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('filename', type=str, help='Network file name')  # Argument for the network file name
parser.add_argument('st', type=int, help='Starting index of network list')  # Argument for starting index
parser.add_argument('end', type=int, help='Ending index of network list')  # Argument for ending index
parser.add_argument('gamma', type=int, help='Recovery rate parameter')  # Argument for recovery rate
parser.add_argument('source_dir', type=str, help="Source directory")  # Argument for source directory
parser.add_argument('dest_dir', type=str, help="Destination directory")  # Argument for destination directory

args = parser.parse_args()  # Parse the command-line arguments
# Call the main function with parsed arguments
main(args.filename, args.st, args.end, args.gamma, args.source_dir, args.dest_dir)
