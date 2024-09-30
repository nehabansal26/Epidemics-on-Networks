for NETWORK in ER_1 ER_2 ER_3 SF_combined SW_combined; do 
    echo "Moving ${NETWORK} file from SIREN"
    scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}.pkl /home/neha/
    
    echo "Moving ${NETWORK} sample file from SIREN"
    scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}_samples.pkl /home/neha/

    echo "Running command: python3 clustering_coeff.py ${NETWORK}"
    python3 clustering_coeff.py ${NETWORK}

    echo "Moving results to SIREN"
    scp /home/neha/${NETWORK}_avg_clust_coeff.pkl neha@siren.maths.cf.ac.uk:/home/neha/results/
    scp /home/neha/${NETWORK}_global_clust_coeff.pkl neha@siren.maths.cf.ac.uk:/home/neha/results/

    sleep 10
    
done