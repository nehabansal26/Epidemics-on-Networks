import random
import numpy as np
import pickle
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

def get_samples(G,algo,num_samples=5000,num_walks=30):
    ## Graph information : nodes and edges
    N = len(G.nodes())
    edges = G.edges()

    ## Transition rate matrix
    T = np.zeros((N,N))
    for (i,j) in edges:
        if algo == 'MHRW':
            if i!=j and (i,j) in edges : 
                T[i,j] =  min([1,G.degree[i]/G.degree[j] ])
                T[j,i] =  min([1,G.degree[j]/G.degree[i] ])
        if algo == 'RW':
            if i!=j and (i,j) in edges  : 
                T[i,j] =  1/G.degree[i]
                T[j,i] =  1/G.degree[j]

    ## extra params required 
    if algo == 'RW':
        T_non_zero = [np.nonzero(T[i,:])[0] for i in range(N)]
    if algo == 'MHRW':
        random_probs = np.random.rand(num_walks,num_samples)

    ## generate dummy sample array
    sample_array = np.zeros((num_walks,num_samples))
    sample_array[:,0] = random.sample(list(G.nodes()),num_walks)

    ## fill dummy sample array
    for  itr in range(num_samples-1):
        if algo == 'RW':
            ## current node taking all of them as starting node for parallel computation 
            next_node = [np.random.choice(T_non_zero[int(i)]) for i in sample_array[:,itr]]
            sample_array[:,itr+1] = next_node
        if algo == 'MHRW':
            ## current node taking all of them as starting node for parallel computation 
            choices = [np.where(T[int(i),:]>random_probs[cnt,itr])[0] for cnt,i in enumerate(sample_array[:,itr])]
            next_node = [np.random.choice(choices[i]) if len(choices[i])>0 else sample_array[i,itr]  for i in range(num_walks)]
            sample_array[:,itr+1] = next_node
    return sample_array



def process_network(net_type, num_cores,net_ls_st,net_ls_end):
    st = time.time()
    print("reading network pickle")
    network_ls = pickle.load(open(f"{net_type}_combined.pkl", "rb"))
    print(f"network pickle load complete : {time.time()-st}")
    network_ls = network_ls[net_ls_st:net_ls_end]

    samples_dict = {'RW': [], 'MHRW': [], 'RW_deg': [], 'MHRW_deg': [], 'net_deg': []}

    def process_net(net):
        OG_degree = [net.degree(node) for node in net.nodes()]
        samples_dict['net_deg'].append(OG_degree)
        for algo in ['RW', 'MHRW']:
            sample_array = get_samples(G=net, algo=algo, num_samples=1000, num_walks=100)[:, 500:]
            degree_ls = [net.degree(node) for i in range(sample_array.shape[0]) for node in set(sample_array[i, :])]
            samples_dict[algo].append(sample_array)
            samples_dict[f"{algo}_deg"].append(degree_ls)

    # Use a ThreadPoolExecutor to parallelize network processing
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(process_net, net) for net in network_ls]
        # Use tqdm to wrap the futures for a progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {net_type} networks"):
            future.result() 

    
    pickle.dump(samples_dict, open(f"{net_type}_{net_ls_st}_{net_ls_end}_samples.pkl", 'wb'))
    print(f"{net_type} done!")


# Create the parser
parser = argparse.ArgumentParser(description="Process some integers.")

# Define arguments
parser.add_argument('network_type', type=str, help='Name of the network')
parser.add_argument('num_cores', type=int, help='number of cores for threading')
parser.add_argument('net_ls_st', type=int, help='network ls starting index')
parser.add_argument('net_ls_end', type=int, help='network ls end index')

args = parser.parse_args()

# Parse the arguments
process_network(args.network_type, args.num_cores,args.net_ls_st,args.net_ls_end)
