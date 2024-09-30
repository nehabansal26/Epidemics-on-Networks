import numpy as np
import pickle
import argparse
import random
import EoN
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm   
import time
import os
import subprocess
from numba import njit,jit, config
import networkx as nx
# config.DEBUG = True

@njit
def get_req_dict(cnt_G,beta,node_ls, trans_df):
    req_dict = np.empty((len(node_ls),5),dtype=np.float64)
    idx = 0
    for node in node_ls:
        if (node in trans_df[:,1]) or (node in trans_df[:,2]):
            req_dict[idx] = [cnt_G,beta,node,
                            np.max(trans_df[trans_df[:,2] == node,0]),
                            len(trans_df[trans_df[:,1] == node,1])]
            idx+=1
    return req_dict[:idx]

def process_network(G, beta, initial_I, cnt_G,gamma):
    infected_nodes = random.sample(list(G.nodes), initial_I)
    sim = EoN.Gillespie_SIR(G=G, tau=beta, gamma=gamma, initial_infecteds=infected_nodes,
                            return_full_data=True)

    trans_df = np.array(sim.transmissions(),dtype=np.float64) # columns=['time', 'source', 'target']
    trans_df[np.isnan(trans_df.astype(float))] = -1
    node_ls = np.array(list(G.nodes()))
    req_dict = get_req_dict(cnt_G,beta,node_ls,trans_df)

    return req_dict

def main(filename, st, end,gamma_):
    gamma = 1/gamma_
    initial_I = 100
    # st_time = time.time()
    if filename.find("bcms")>=0:
        with open(f'{filename}.pkl', 'rb') as f:
            G = pickle.load(f)
            node_idx = {node:i for i,node in enumerate(G.nodes())}
            net = nx.relabel_nodes(G, node_idx)
            networks_ls = [net]*end
    else :
        with open(f'{filename}.pkl', 'rb') as f:
            networks_ls = pickle.load(f)[st:end]
    
    print(f"Read network file!")
    SIR_dict = []

    for beta in np.arange(0, 1.1, 0.1):
        for cnt_G, G in enumerate(tqdm(networks_ls, total=len(networks_ls))):
            req_dict = process_network(G,beta,initial_I,cnt_G,gamma)
            SIR_dict.append(req_dict)
            
    print("Starting to write pickle file!")
    with open(f"{filename}_{st}_{end}_{gamma_}_SIR.pkl", 'wb') as f:
        pickle.dump(SIR_dict, f)
    print(f"{filename} done!")

    result = subprocess.run(f"scp /home/neha/{filename}_{st}_{end}_{gamma_}_SIR.pkl neha@siren.maths.cf.ac.uk:/home/neha/results/"
                            , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)

    if result.stderr:
        print("Error:")
        print(result.stderr)

    os.remove(f"/home/neha/{filename}_{st}_{end}_{gamma_}_SIR.pkl")


parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('filename', type=str, help='Network file name')
parser.add_argument('st', type=int, help='starting index of network list')
parser.add_argument('end', type=int, help='ending index of network list')
parser.add_argument('gamma', type=int, help='recovery rate parameter')
args = parser.parse_args()
main(args.filename, args.st, args.end,args.gamma)
