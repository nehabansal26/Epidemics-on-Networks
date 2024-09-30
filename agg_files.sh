## for SIR files
for NETWORK in ER SF SW; do
    if [ "$NETWORK" == "ER" ]; then
        for IDX in 1 2 3; do
            echo "Moving files from SIREN ${NETWORK}_${IDX}"
            scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}_SIR/${NETWORK}_${IDX}_*_SIR.pkl /home/neha/
            echo "Running command : python3 SIR_combine_pickle.py ${NETWORK}_${IDX}"
            python3 SIR_combine_pickle.py ${NETWORK}_${IDX} 
            sleep 10
            echo "Moving combined file to SIREN ${NETWORK}_${IDX}"
            scp ${NETWORK}_${IDX}_SIR.pkl neha@siren.maths.cf.ac.uk:/home/neha/
            sleep 10
            echo "Removing sample files from HARPY ${NETWORK}_${IDX}"
            # rm -r ${NETWORK}_${IDX}_*_samples.pkl
            rm -r ${NETWORK}_${IDX}_SIR.pkl
        done
    else
        echo "Moving files from SIREN ${NETWORK}"
        scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}_SIR/${NETWORK}_combined_*_SIR.pkl /home/neha/
        echo "Running command : python3 SIR_combine_pickle.py ${NETWORK}_combined"
        python3 SIR_combine_pickle.py ${NETWORK}_combined
        sleep 10
        echo "Moving combined file to SIREN ${NETWORK}"
        scp ${NETWORK}_combined_SIR.pkl neha@siren.maths.cf.ac.uk:/home/neha/
        sleep 10
        echo "Removing sample files from HARPY ${NETWORK}"
        # rm -r ${NETWORK}_combined_*_samples.pkl
        rm -r ${NETWORK}_combined_SIR.pkl
    fi
done
## for sample file
# for NETWORK in SF SW; do
#     if [ "$NETWORK" == "ER" ]; then
#         for IDX in 1 2 3; do
#             echo "Moving files from SIREN ${NETWORK}_${IDX}"
#             scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}_samples/${NETWORK}_${IDX}_*_samples.pkl /home/neha/
#             echo "Running command : python3 combine_pickle.py ${NETWORK}_${IDX} samples"
#             python3 combine_pickle.py ${NETWORK}_${IDX} samples
#             sleep 10
#             echo "Moving combined file to SIREN ${NETWORK}_${IDX}"
#             scp ${NETWORK}_${IDX}_samples.pkl neha@siren.maths.cf.ac.uk:/home/neha/
#             sleep 10
#             echo "Removing sample files from HARPY ${NETWORK}_${IDX}"
#             # rm -r ${NETWORK}_${IDX}_*_samples.pkl
#             rm -r ${NETWORK}_${IDX}_samples.pkl
#         done
#     else
#         echo "Moving files from SIREN ${NETWORK}"
#         scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}_samples/${NETWORK}_combined_*_samples.pkl /home/neha/
#         echo "Running command : python3 combine_pickle.py ${NETWORK}_combined samples"
#         python3 combine_pickle.py ${NETWORK}_combined samples
#         sleep 10
#         echo "Moving combined file to SIREN ${NETWORK}"
#         scp ${NETWORK}_combined_samples.pkl neha@siren.maths.cf.ac.uk:/home/neha/
#         sleep 10
#         echo "Removing sample files from HARPY ${NETWORK}"
#         # rm -r ${NETWORK}_combined_*_samples.pkl
#         rm -r ${NETWORK}_combined_samples.pkl
#     fi
# done