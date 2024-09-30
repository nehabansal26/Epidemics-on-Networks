#!/bin/bash
## use when all the files are in combined form
for network in SW_combined SF_combined ER_1 ER_2 ER_3;
do
python3 SIR_evaluation.py ${network} False right results_right
done
exit 

## use when files are not in combined form
gamma=7
for network in SW SF ER;
do
    if [ "$network" = "SF" ] || [ "$network" = "SW" ];
        then
        python3 SIR_evaluation_multipart.py ${network}_combined True results/${network}/${gamma} results_right
    else
        for idx in 1 2 3;
        do
        python3 SIR_evaluation_multipart.py ${network}_${idx} True results/${network}/${gamma} results_right
        done
    fi
done

