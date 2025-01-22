import pickle  # Import pickle for serializing and deserializing Python objects
import numpy as np  # Import NumPy for numerical computations and handling arrays
import pandas as pd  # Import pandas for data manipulation and analysis
import argparse  # Import argparse for parsing command-line arguments
from tqdm import tqdm  # Import tqdm for creating progress bars in loops
import networkx as nx  # Import NetworkX for working with graph data structures

# Set up argument parsing for command-line execution
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('network', type=str, help='Network name')  # Argument for the network name
parser.add_argument('start', type=int, help='Network list starting index')  # Argument for the starting index of the network
parser.add_argument('end', type=int, help='Network list ending index')  # Argument for the ending index of the network
parser.add_argument('gamma', type=int, help='Recovery rate parameter')  # Argument for recovery rate
parser.add_argument('dup', type=str, help='Remove duplicates from sample')  # Argument to determine if duplicates should be removed
parser.add_argument('sir_dir', type=str, help='Location for fetching SIR simulation results')  # Directory for SIR results
parser.add_argument('net_dir', type=str, help='Location for fetching network files')  # Directory for network files
parser.add_argument('sample_dir', type=str, help='Location for fetching sample data')  # Directory for sample data
parser.add_argument('dest_dir', type=str, help='Location for saving results')  # Directory for saving results
args = parser.parse_args()  # Parse command-line arguments

def create_sample_df(net_idx, algo, sample_array_2d, sir_df0, rm_dup):
    """
    Create a sample DataFrame from the given parameters.

    Parameters:
    - net_idx: Index of the network
    - algo: Algorithm used for sampling
    - sample_array_2d: 2D array of sampled nodes
    - sir_df0: DataFrame containing SIR model results
    - rm_dup: Flag to remove duplicates

    Returns:
    - sample_df_1: DataFrame containing aggregated sample data
    """
    sample_array_1d = sample_array_2d.ravel()  # Flatten the 2D sample array to 1D
    row_indices = np.repeat(np.arange(sample_array_2d.shape[0]), sample_array_2d.shape[1])  # Create row indices for each sample
    sample_df = pd.DataFrame({  # Create a DataFrame to store the sampled nodes
                                'walk_idx': row_indices,
                                'node_idx': sample_array_1d
                            })
    sample_df['net_idx'] = net_idx  # Add the network index to the DataFrame
    sample_df['algo'] = algo  # Add the algorithm name to the DataFrame
    
    ## Removing duplicates if specified
    if rm_dup == 'True':
        sample_df = sample_df.drop_duplicates()  # Drop duplicate entries
    
    # Aggregate sample sizes for each network, algorithm, and walk index
    sample_size_df = sample_df.groupby(['net_idx', 'algo', 'walk_idx'])\
                             .agg({'node_idx': 'count'})\
                             .reset_index()  # Reset index for the grouped DataFrame
    
    # Rename columns for clarity
    sample_size_df.columns = ['net_idx', 'algo', 'walk_idx', 'sample_size']
    
    # Merge the sample DataFrame with the SIR DataFrame
    sir_sample_df = pd.merge(sample_df, sir_df0, how='left', on=['net_idx', 'node_idx'])
    # Filter out rows where the second infection information is missing
    sir_sample_df = sir_sample_df[~sir_sample_df['second_inf'].isnull()]

    # Aggregate the data for the final output
    sample_df_1 = sir_sample_df.groupby(['beta', 'net_idx', 'algo', 'walk_idx'])\
                               .agg({'node_idx': 'count',
                                     'second_inf': 'mean',
                                     'inf_time': 'mean'
                                    })\
                                .reset_index()
    
    # Merge with sample size DataFrame to include sample sizes in the final output
    sample_df_1 = pd.merge(sample_df_1, sample_size_df, how='left', on=['net_idx', 'algo', 'walk_idx'])

    return sample_df_1  # Return the final aggregated DataFrame

print("process starts!")  # Indicate that the processing has started
# Load SIR results from a pickle file
sir_files = pickle.load(open(f"{args.sir_dir}/{args.network}_{args.start}_{args.end}_{args.gamma}.pkl", "rb"))
sir_df = pd.DataFrame(sir_files, columns=['net_idx', 'beta', 'node_idx', 'inf_time', 'second_inf'])  # Convert loaded data to DataFrame
# Aggregate original SIR data to get means and counts
OG_df = sir_df.groupby(['beta', 'net_idx'])\
              .agg({'node_idx': 'count',
                    'second_inf': 'mean',
                    'inf_time': 'mean'
                    })\
              .reset_index()  # Reset index for the grouped DataFrame
OG_df['algo'] = 'OG'  # Add a column indicating the algorithm type
OG_df['walk_idx'] = -1  # Set walk index to -1 for original data

# Load network files from a pickle file
if args.network.find("bcms")>=0:
    network_files = [pickle.load(open(f"{args.net_dir}/{args.network}.pkl", "rb"))]
else:
    network_files = pickle.load(open(f"{args.net_dir}/{args.network}_{args.start}_{args.end}.pkl", "rb"))
# Create a DataFrame for original sample sizes
OG_sample_size = pd.DataFrame([(i, len(G.nodes())) for i, G in enumerate(network_files)],
                              columns=['net_idx', 'sample_size'])
del network_files  # Delete the network files variable to free up memory
# Merge the original aggregated DataFrame with sample sizes
OG_df = pd.merge(OG_df, OG_sample_size, how='inner', on=['net_idx'])

# Save the original aggregated results to a pickle file
with open(f"{args.dest_dir}/{args.network}_{args.start}_{args.end}_{args.gamma}_OG.pkl", "wb") as f:
    pickle.dump(OG_df, f)  # Serialize and save the DataFrame

# Load sampled data from a pickle file
sample_dict = pickle.load(open(f"{args.sample_dir}/{args.network}_{args.start}_{args.end}.pkl", "rb"))
# Iterate through each sample in the dictionary
for key, value in sample_dict.items():
    print(f"{key} starts")  # Print which key is currently being processed
    # Create a list of DataFrames for each sampled network
    df_ls = [create_sample_df(net_idx, key, sample_array, sir_df[sir_df['net_idx'] == net_idx], rm_dup=args.dup) 
             for net_idx, sample_array in tqdm(enumerate(value), total=len(value))]

    # Concatenate all DataFrames in the list into a single DataFrame
    df = pd.concat(df_ls, axis=0, ignore_index=True)

    # Save the concatenated DataFrame to a pickle file
    with open(f"{args.dest_dir}/{args.network}_{args.start}_{args.end}_{args.gamma}_{key}.pkl", "wb") as f:
        pickle.dump(df, f)  # Serialize and save the DataFrame
