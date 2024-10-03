#!/bin/bash

mkdir networks
net_dir='networks'
mkdir samples
sample_dir='samples'
mkdir sir
sir_dir='sir'
mkdir sir_feat
agg_results='sir_feat'

start=0
num_nets=10
max_nets=10
sample_size=10
walks=10
gamma=1
dup='True' ## to remove duplicated from sample, use dup='False'
while true;
do
    end=$((start + num_nets))
    # Check if END exceeds , if so, break the loop
    if [ "$end" -gt "$max_nets" ]; then
        echo "Reached END value greater than 10000. Stopping the loop."
    break
    fi

    num_cores=40 #cores for parallel execution
    for network in ER SW SF;
    do
        ##1 create networks
        python3 network_creation.py ${network} ${num_nets} ${net_dir} ${num_cores} ${start} ${end} ##if needed change the network params in .py script

        ##2 sample generation
        python3 sample_gen_inorder.py ${network} ${start} ${end} ${sample_size} ${walks} ${net_dir} ${sample_dir}

        ##3 SIR simulation
        python3 SIR_sim_numba_pipeline.py ${network} ${start} ${end} ${gamma} ${net_dir} ${sir_dir}

        #4 Disease feature calculation
        python3 SIR_evaluation_pipeline.py ${network} ${start} ${end} ${gamma} ${dup} ${sir_dir} ${net_dir} ${sample_dir} ${agg_results}

        #5 Degree distribution and clustering coefficient calculation
        python3 degree_cluster_coeff.py ${network} ${start} ${end} ${net_dir} ${sample_dir} ${agg_results}

    done
    start=$end
done

