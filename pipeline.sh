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
num_nets=2 ## number of networks to be generated in each loop
max_nets=2 ## total number of networks to be generated
sample_size=10 ## number of nodes in a sample
walks=2 ## number of samples 
gamma=1 ## recovery rate
dup='True' ## to remove duplicated from sample, use dup='False'
while true;
do
    end=$((start + num_nets))
    # Check if END exceeds , if so, break the loop
    if [ "$end" -gt "$max_nets" ]; then
        echo "Reached END value greater than 10000. Stopping the loop."
    break
    fi

    num_cores=4 #cores for parallel execution
    for network in ER SW SF;
    do
        ##1 create networks
        python3 network_creation.py ${network} ${num_nets} ${net_dir} ${num_cores} ${start} ${end} ##if needed change the network params in .py script

        ##2 sample generation
        python3 sample_generation.py ${network} ${start} ${end} ${sample_size} ${walks} ${net_dir} ${sample_dir}

        ##3 SIR simulation
        python3 SIR_simulation.py ${network} ${start} ${end} ${gamma} ${net_dir} ${sir_dir}

        #4 Disease feature calculation
        python3 disease_metric_estimation.py ${network} ${start} ${end} ${gamma} ${dup} ${sir_dir} ${net_dir} ${sample_dir} ${agg_results}

        #5 Degree distribution and clustering coefficient calculation
        python3 degree_distribution.py ${network} ${start} ${end} ${net_dir} ${sample_dir} ${agg_results}

    done
    start=$end
done

