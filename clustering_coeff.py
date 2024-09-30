import pickle
import numpy as np
from itertools import chain
import glob
import argparse
import networkx as nx
from tqdm import tqdm
import os

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('network_filename', type=str, help='Network  file name')
args = parser.parse_args()

network_ls = pickle.load(open(f"/home/neha/{args.network_filename}.pkl","rb"))
sample_dict = pickle.load(open(f"/home/neha/{args.network_filename}_samples.pkl","rb"))
print("Network and sample file loaded!")

os.remove(f"/home/neha/{args.network_filename}.pkl")
os.remove(f"/home/neha/{args.network_filename}_samples.pkl")

avg_clustering_coeff = {'RW':[],'MHRW':[],'net':[]}
global_clustering_coeff = {'RW':[],'MHRW':[],'net':[]}

avg_clustering_coeff['net'] = [nx.average_clustering(G) for G in network_ls]
global_clustering_coeff['net'] = [nx.transitivity(G) for G in network_ls]
print("Original network calculation is done")

for algo in ['RW','MHRW']:
    for net_idx,sample_array in tqdm(enumerate(sample_dict[algo]), total = len(sample_dict[algo])):    
        G = network_ls[net_idx]
        for node_ls in sample_array:
            avg_clustering_coeff[algo].append(nx.average_clustering(G.subgraph(node_ls)))
            global_clustering_coeff[algo].append(nx.transitivity(G.subgraph(node_ls)))
    print(f"Calculation complete for {algo}")
    
with open(f"{args.network_filename}_avg_clust_coeff.pkl","wb") as f:
    pickle.dump(avg_clustering_coeff,f)
with open(f"{args.network_filename}_global_clust_coeff.pkl","wb") as f:
    pickle.dump(global_clustering_coeff,f)
 
print(f"process complete for {args.network_filename}")
        