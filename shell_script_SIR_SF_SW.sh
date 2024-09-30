#!/bin/bash

# Define the base command and the initial start and end values
COMMAND="python3 SIR_sim_numba.py bcms_network"
INTERVAL=500
START=0
GAMMA=1

# Loop to run the command with increasing intervals
while true; do
  END=$((START + INTERVAL))
  
  # Check if END exceeds , if so, break the loop
  if [ "$END" -gt 10000 ]; then
    echo "Reached END value greater than 10000. Stopping the loop."
    break
  fi
  
  # Run the command with the current start and end interval values
  # echo "Running command: $COMMAND $START $END $GAMMA"
  # $COMMAND $START $END $GAMMA

  ## only for bcms network
  echo "Running command: $COMMAND $START $END $GAMMA"
  $COMMAND $START $END $GAMMA
  
  # Update the start value for the next iteration
  START=$END
  
  # Optional: Sleep if you want a delay between runs, e.g., sleep 10 for a 10-second pause
  sleep 10
done


# Define the base command and the initial start and end values
# COMMAND="python3 SIR_sim.py SW_combined"
# INTERVAL=1000
# START=0

# # Loop to run the command with increasing intervals
# while true; do
#   END=$((START + INTERVAL))
  
#   # Check if END exceeds , if so, break the loop
#   if [ "$END" -gt 10000 ]; then
#     echo "Reached END value greater than 10000. Stopping the loop."
#     break
#   fi
  
#   # Run the command with the current start and end interval values
#   echo "Running command: $COMMAND $START $END"
#   $COMMAND $START $END
  
#   # Update the start value for the next iteration
#   START=$END
  
#   # Optional: Sleep if you want a delay between runs, e.g., sleep 10 for a 10-second pause
#   sleep 10
# done
