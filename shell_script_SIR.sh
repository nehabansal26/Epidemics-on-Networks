#!/bin/bash
GAMMA=3
SRC_DIR="/home/neha"
DEST_DIR="/home/neha"
# Define the base command and the initial start and end values
for NETWORK in ER_1 ER_2 ER_3 SW_combined;
do
  scp neha@siren.maths.cf.ac.uk:/home/neha/${NETWORK}.pkl ${SRC_DIR}
  COMMAND="python3 SIR_sim_numba.py"
  INTERVAL=1000
  START=0

  # Loop to run the command with increasing intervals
  while true; do
    END=$((START + INTERVAL))
    
    # Check if END exceeds , if so, break the loop
    if [ "$END" -gt 10000 ]; then
      echo "Reached END value greater than 100. Stopping the loop."
      break
    fi
    
    # Run the command with the current start and end interval values
    echo "Running command: $COMMAND $START $END $GAMMA $SRC_DIR $DEST_DIR"
    $COMMAND $NETWORK $START $END $GAMMA $SRC_DIR $DEST_DIR
    
    # Update the start value for the next iteration
    START=$END
    
    # Optional: Sleep if you want a delay between runs, e.g., sleep 10 for a 10-second pause
    # sleep 10
    done
    rm -r ${SRC_DIR}/${NETWORK}.pkl
done
