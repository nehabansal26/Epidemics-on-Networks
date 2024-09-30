#!/bin/bash

for NETWORK in ER_2 ER_3 SF_combined SW_combined
do 
    echo "Moving files from siren: $NETWORK"
    scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}.pkl /home/neha/

    # Define the base command and the initial start and end values
    COMMAND="python3 sample_gen_inorder.py ${NETWORK}"
    INTERVAL=1000
    START=0

    # Loop to run the command with increasing intervals
    while true; do
        END=$((START + INTERVAL))
        
        # Check if END exceeds , if so, break the loop
        if [ "$END" -gt 10000 ]; then
            echo "Reached END value greater than 10000. Stopping the loop."
            break
        fi
        
        # Run the command with the current start and end interval values
        echo "Running command: $COMMAND $START $END"
        $COMMAND $START $END
        
        echo "Moving files to siren: $NETWORK"
        scp ${NETWORK}_${START}_${END}_samples.pkl neha@siren.maths.cf.ac.uk:/home/neha/
        sleep 10

        echo "Removing files from harpy: $NETWORK"
        rm -r ${NETWORK}_${START}_${END}_samples.pkl
    
        # Update the start value for the next iteration
        START=$END
        
        # Optional: Sleep if you want a delay between runs, e.g., sleep 10 for a 10-second pause
        sleep 10
    done
    
    rm -r ${NETWORK}.pkl
    
done