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
parser.add_argument('file_suffix', type=str, help='Suffix to writing files')
args = parser.parse_args()

def create_sample_df(net_idx,algo,sample_array_2d,sir_df0,rm_dup = False):
    sample_array_1d = sample_array_2d.ravel()
    row_indices = np.repeat(np.arange(sample_array_2d.shape[0]), sample_array_2d.shape[1])
    sample_df = pd.DataFrame({
        'walk_idx': row_indices,
        'node_idx': sample_array_1d
    })
    sample_df['net_idx'] = net_idx
    sample_df['algo'] = algo
    
    ## removing duplicates
    if rm_dup : 
        sample_df = sample_df.drop_duplicates()
    
    sample_size_df = sample_df.groupby(['net_idx','algo','walk_idx']).agg({'node_idx':'count'}).reset_index()
    sample_size_df.columns = ['net_idx','algo','walk_idx','sample_size']
    
    sir_sample_df = pd.merge(sample_df,sir_df0,how='left',on=['net_idx','node_idx'])
    # sir_sample_df = sir_sample_df[~sir_sample_df['second_inf'].isnull()]

    sample_df_1 = sir_sample_df.groupby(['beta','net_idx','algo','walk_idx']).agg({'node_idx':'count',
                                                                    'second_inf': 'mean',
                                                                    'inf_time' : 'mean'
                                                                    }).reset_index()
    
    sample_df_1 = pd.merge(sample_df_1,sample_size_df,how='left',on=['net_idx','algo','walk_idx'])

    return sample_df_1

print("process starts!")
result = subprocess.run(f"scp neha@siren.maths.cf.ac.uk:/home/neha/results/{args.network_filename}_SIR.pkl /home/neha/"
                        , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)

if result.stderr:
    print("Error:")
    print(result.stderr)

sir_files = pickle.load(open(f"/home/neha/{args.network_filename}_SIR.pkl","rb"))
sir_files = [pd.DataFrame(ls,columns = ['net_idx','beta','node_idx','inf_time','second_inf']) for ls in sir_files]
sir_df = pd.concat(sir_files,axis=0)
print(sir_df.head())

os.remove(f"/home/neha/{args.network_filename}_SIR.pkl")

result = subprocess.run(f"scp neha@siren.maths.cf.ac.uk:/home/neha/{args.network_filename}_samples.pkl /home/neha/"
                        , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)

if result.stderr:
    print("Error:")
    print(result.stderr)

sample_dict = pickle.load(open(f"{args.network_filename}_samples.pkl","rb"))
os.remove(f"/home/neha/{args.network_filename}_samples.pkl")

print("Files loaded")

OG_df = sir_df.groupby(['beta','net_idx']).agg({'node_idx':'count',
                                                'second_inf': 'mean',
                                                'inf_time' : 'mean'
                                                }).reset_index()
OG_df['algo'] = 'OG'
OG_df['walk_idx'] = -1
print(OG_df.head())
print("OG created, writing it")

with open(f"/home/neha/{args.network_filename}_OG_SIR_agg_{args.file_suffix}.pkl","wb") as f:
    pickle.dump(OG_df,f)
print("Sending OG to SIREN")

result = subprocess.run(f"scp /home/neha/{args.network_filename}_OG_SIR_agg_{args.file_suffix}.pkl neha@siren.maths.cf.ac.uk:/home/neha/results/"
                        , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)

if result.stderr:
    print("Error:")
    print(result.stderr)

print("Removing OG from HARPY")
os.remove(f"/home/neha/{args.network_filename}_OG_SIR_agg_{args.file_suffix}.pkl")


for key, value in sample_dict.items():
    print(f"{key} starts")
    df_ls = [create_sample_df(net_idx,key,sample_array,sir_df[sir_df['net_idx']==net_idx]) 
                for net_idx,sample_array in tqdm(enumerate(value),total = len(value))]

    df = pd.concat(df_ls, axis=0, ignore_index=True)
    print(df.head())
    print(f"{key} done, writing it")
    with open(f"/home/neha/{args.network_filename}_{key}_SIR_agg_{args.file_suffix}.pkl","wb") as f:
        pickle.dump(df,f)

    print(f"{key} sending to SIREN")
    result = subprocess.run(f"scp /home/neha/{args.network_filename}_{key}_SIR_agg_{args.file_suffix}.pkl neha@siren.maths.cf.ac.uk:/home/neha/results/"
                            , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                            )
    print(result.stdout)
    print(f"{key} removing from HARPY")
    os.remove(f"/home/neha/{args.network_filename}_{key}_SIR_agg_{args.file_suffix}.pkl")

    
