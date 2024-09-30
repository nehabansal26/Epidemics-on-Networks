#!/bin/bash
dup=True
for NETWORK in SW_combined SF_combined ER_3 ER_2 ER_1; do 

    echo "Running command: python3 SIR_evaluation.py ${NETWORK}"
    python3 SIR_evaluation.py ${NETWORK} ${dup}
    sleep 10
    
done