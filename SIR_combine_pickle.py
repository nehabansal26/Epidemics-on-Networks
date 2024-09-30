import pickle
import numpy as np
from itertools import chain
import glob
import argparse
import networkx as nx
from tqdm import tqdm
import os

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('network_name', type=str, help='Network name')
args = parser.parse_args()

file_paths = glob.glob(f"/home/neha/{args.network_name}_*_SIR.pkl")

file_paths = [(int(filepath.split("/")[-1].split("_")[2]),filepath) for filepath in file_paths]

# Sort the list based on the extracted numerical ranges
sorted_file_paths = sorted(file_paths) 
combines_out = []
for st_idx,filepath in sorted_file_paths:
    print(filepath)
    sir_file = pickle.load(open(filepath,"rb"))
    sir_file_new = []
    for ls in sir_file:
        for sub_ls in ls:
            net_idx = sub_ls[0] + st_idx
            sub_ls[0] = net_idx
            sir_file_new.append(sub_ls)
    combines_out.extend(sir_file_new)
    os.remove(filepath)

with open(f"{args.network_name}_SIR.pkl","wb") as f:
    pickle.dump(combines_out,f)
