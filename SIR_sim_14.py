import numpy as np
import pickle
import argparse
import random
import EoN
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm   
import time

def process_network(G, beta, initial_I, cnt_G):
    infected_nodes = random.sample(list(G.nodes), initial_I)
    sim = EoN.Gillespie_SIR(G=G, tau=beta, gamma=1/14, initial_infecteds=infected_nodes,
                            return_full_data=True)

    trans_df = pd.DataFrame(sim.transmissions(), columns=['time', 'source', 'target'])
    req_dict = []
    for i in list(G.nodes):
        if 'R' in sim.node_history(i)[1]:
            req_dict.append([cnt_G, beta, i,
                             sim.node_history(i)[0][sim.node_history(i)[1].index('I')],
                             len(trans_df[trans_df['source'] == i]['target'])])
    return req_dict

def main(filename, st, end):
    gamma = 1/14
    initial_I = 100
    # st_time = time.time()
    with open(f'{filename}.pkl', 'rb') as f:
        networks_ls = pickle.load(f)[st:end]
    print(f"Read network file!")

    
    SIR_dict = []

    # with ThreadPoolExecutor() as executor:
        # futures = []
    # beta_time = time.time()
    for beta in np.arange(0, 1.1, 0.1):
        for cnt_G, G in enumerate(tqdm(networks_ls, total=len(networks_ls))):
            req_dict = process_network(G,beta,initial_I,cnt_G)
            SIR_dict.append(req_dict)
                # future = executor.submit(process_network, G, beta, initial_I, cnt_G)
                # futures.append(future)
    # print(f'beta loop done {time.time()-beta_time}')
        
        # for i, future in enumerate(tqdm(as_completed(futures), total=len(futures))):
        #     SIR_dict.append(future.result())
        #     if i % 10 == 0:
        #         print(f"Processed {i} networks")

    print("Starting to write pickle file!")
    # file_write_st = time.time()
    with open(f"{filename}_{st}_{end}_14_SIR.pkl", 'wb') as f:
        pickle.dump(SIR_dict, f)
    print(f"{filename} done!")

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('filename', type=str, help='Network file name')
parser.add_argument('st', type=int, help='starting index of network list')
parser.add_argument('end', type=int, help='ending index of network list')
args = parser.parse_args()
main(args.filename, args.st, args.end)
