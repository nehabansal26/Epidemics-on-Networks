import pickle
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm
import os
import time
import subprocess

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('network_filename', type=str, help='Network  file name')
args = parser.parse_args()

print("process starts!")
result = subprocess.run(f"scp neha@siren.maths.cf.ac.uk:/home/neha/{args.network_filename}.pkl /home/neha/"
                        , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)

if result.stderr:
    print("Error:")
    print(result.stderr)

network_files = pickle.load(open(f"/home/neha/{args.network_filename}.pkl","rb"))
os.remove(f"/home/neha/{args.network_filename}.pkl")

result = subprocess.run(f"scp neha@siren.maths.cf.ac.uk:/home/neha/{args.network_filename}_samples.pkl /home/neha/"
                        , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)

if result.stderr:
    print("Error:")
    print(result.stderr)

sample_dict = pickle.load(open(f"{args.network_filename}_samples.pkl","rb"))
os.remove(f"/home/neha/{args.network_filename}_samples.pkl")


degree_dedup = {'OG':[]}
for key, sample_dict_ in sample_dict.items():
    degree_dedup[key] = []
    for net_idx, sample_array in enumerate(sample_dict_):
        G = network_files[net_idx]
        degree_dedup['OG'].extend([G.degree(node) for node in G.nodes()])
        for sample_ls in sample_array:
            temp_ls = [G.degree(node) for node in set(sample_ls)]
            degree_dedup[key].extend(temp_ls)
        
print("process completed, writing it")

with open(f"/home/neha/{args.network_filename}_deg_rm_dup.pkl","wb") as f:
    pickle.dump(degree_dedup,f)
print("Sending file to SIREN")

result = subprocess.run(f"scp /home/neha/{args.network_filename}_deg_rm_dup.pkl neha@siren.maths.cf.ac.uk:/home/neha/results_dup/"
                        , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)

if result.stderr:
    print("Error:")
    print(result.stderr)

print("Removing file from HARPY")
os.remove(f"/home/neha/{args.network_filename}_deg_rm_dup.pkl")

