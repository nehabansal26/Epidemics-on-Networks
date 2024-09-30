import pickle
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm
import os
import subprocess
import networkx as nx

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('network_filename', type=str, help='Network  file name')
parser.add_argument('dup', type=str, help='Remove duplicates from sample')
parser.add_argument('source_dir', type=str, help='location for fetching SIR files')
parser.add_argument('dest_dir',type=str,help='location for saving results')
parser.add_argument('gamma',type=int,help='recovery rate param')
args = parser.parse_args()

def transfer_read_del_file(network_filename,file_type,source_dir='NA'):
    if file_type=='': filename = f"{network_filename}.pkl"
    else : filename = f"{network_filename}_{file_type}.pkl"

    print(f"transfer {filename} from HARPY")
    if file_type == 'SIR':    
        result = subprocess.run(f"scp neha@siren.maths.cf.ac.uk:/home/neha/{source_dir}/{filename} /home/neha/"
                            , shell=True
                            , stdout=subprocess.PIPE
                            , stderr=subprocess.PIPE
                            , text=True)
    else :
        result = subprocess.run(f"scp neha@siren.maths.cf.ac.uk:/home/neha/{filename} /home/neha/"
                            , shell=True
                            , stdout=subprocess.PIPE
                            , stderr=subprocess.PIPE
                            , text=True)
    print(result.stdout)

    if result.stderr:
        print("Error:")
        print(result.stderr)

    req_file = pickle.load(open(f"/home/neha/{filename}","rb"))

    print(f"removing {filename} from disk")
    os.remove(f"/home/neha/{filename}")

    return req_file

def write_transfer_del_file(df,network_filename,file_suffix,dest_dir):
    print(f"writing {file_suffix}")
    with open(f"/home/neha/{network_filename}_{file_suffix}.pkl","wb") as f:
        pickle.dump(df,f)
    
    print("Sending OG to SIREN")
    result = subprocess.run(f"scp /home/neha/{network_filename}_{file_suffix}.pkl neha@siren.maths.cf.ac.uk:/home/neha/{dest_dir}/"
                            , shell=True
                            , stdout=subprocess.PIPE
                            , stderr=subprocess.PIPE
                            , text=True)
    print(result.stdout)

    if result.stderr:
        print("Error:")
        print(result.stderr)

    print("Removing OG from HARPY")
    os.remove(f"/home/neha/{network_filename}_{file_suffix}.pkl")

def create_sample_df(net_idx,algo,sample_array_2d,sir_df0,rm_dup,join_type):
    sample_array_1d = sample_array_2d.ravel()
    row_indices = np.repeat(np.arange(sample_array_2d.shape[0]), sample_array_2d.shape[1])
    sample_df = pd.DataFrame({
                                'walk_idx': row_indices,
                                'node_idx': sample_array_1d
                            })
    sample_df['net_idx'] = net_idx
    sample_df['algo'] = algo
    
    ## removing duplicates
    if rm_dup == 'True' : 
        sample_df = sample_df.drop_duplicates()
    
    sample_size_df = sample_df.groupby(['net_idx','algo','walk_idx'])\
                             .agg({'node_idx':'count'})\
                             .reset_index()
    
    sample_size_df.columns = ['net_idx','algo','walk_idx','sample_size']
    
    sir_sample_df = pd.merge(sample_df
                             ,sir_df0
                             ,how='left'
                             ,on=['net_idx','node_idx'])
    sir_sample_df = sir_sample_df[~sir_sample_df['second_inf'].isnull()]

    sample_df_1 = sir_sample_df.groupby(['beta','net_idx','algo','walk_idx'])\
                               .agg({'node_idx':'count',
                                    'second_inf': 'mean',
                                    'inf_time' : 'mean'
                                    })\
                                .reset_index()
    
    sample_df_1 = pd.merge(sample_df_1
                           ,sample_size_df
                           ,how='left'
                           ,on=['net_idx','algo','walk_idx'])

    return sample_df_1


print("process starts!")

for cnt in range(0,10000,1000):
    end = cnt+1000
    net_filename = f"{args.network_filename}_{cnt}_{end}_{args.gamma}"

    sir_files =  transfer_read_del_file(net_filename,'SIR',args.source_dir)
    sir_df =  pd.DataFrame(sir_files
                        ,columns = ['net_idx','beta','node_idx','inf_time','second_inf'])
    OG_df = sir_df.groupby(['beta','net_idx'])\
                .agg({'node_idx':'count',
                        'second_inf': 'mean',
                        'inf_time' : 'mean'
                        })\
                .reset_index()
    OG_df['algo'] = 'OG'
    OG_df['walk_idx'] = -1

    network_files =  transfer_read_del_file(args.network_filename,'')
    OG_sample_size = pd.DataFrame([(i,len(G.nodes())) for i,G in enumerate(network_files)],
                                columns=['net_idx','sample_size']
                                )
    del network_files
    OG_df = pd.merge(OG_df,OG_sample_size,how='inner',on=['net_idx'])
    write_transfer_del_file(OG_df,args.network_filename,f"{cnt}_{end}_OG_SIR_agg",args.dest_dir)

    sample_dict = transfer_read_del_file(args.network_filename,'samples')
    for key, value in sample_dict.items():
        req_samples = value[cnt:end]
        print(f"{key} starts")
        df_ls = [create_sample_df(net_idx+cnt ## shifting the start point
                                ,key
                                ,sample_array
                                ,sir_df[sir_df['net_idx']==net_idx+cnt] ## shifting the start point
                                ,rm_dup=args.dup 
                                ,join_type=args.join_type
                                ) 
                for net_idx,sample_array in tqdm(enumerate(req_samples),total = len(req_samples))]

        df = pd.concat(df_ls, axis=0, ignore_index=True)

        write_transfer_del_file(df,args.network_filename,f"{cnt}_{end}_{key}_SIR_agg",args.dest_dir)

        





