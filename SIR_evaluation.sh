#!/bin/bash
## use when files are not in combined form
for gamma in 7 14;
do
    # for network in SW SF ER;
    for network in SW ER;
    do
        if [ "$network" = "SF" ] || [ "$network" = "SW" ];
            then
            python3 SIR_evaluation_multipart.py ${network}_combined False results/${network}/${gamma} results/${gamma} ${gamma}
        else
            for idx in 1 2 3;
            do
            python3 SIR_evaluation_multipart.py ${network}_${idx} False results/${network}/${gamma} results/${gamma} ${gamma}
            done
        fi
    done
done
exit

## use when all the files are in combined form
for network in SW_combined SF_combined ER_1 ER_2 ER_3;
do
python3 SIR_evaluation.py ${network} False right results_right
done
exit 