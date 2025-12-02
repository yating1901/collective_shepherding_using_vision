#!/bin/bash
BASE_OUTPUT="results"
mkdir -p "BASE_OUTPUT"

Repetition=1
JOBS=()
for N_sheep in $(seq 100 100 200)   # Sheep numbers
do
  for N_shepherd in $(seq 1 1 2)    # Shepherd numbers
  do
    for Iterations in 100        # Simulation steps
    do
      for L3 in 50                   # L3 distance
      do
        JOBS+=("python "main_2.py" $N_sheep $N_shepherd $Iterations $L3 $Repetition")
      done
    done
  done
done

i=0
for JOB_CMD in "${JOBS[@]}"; do
    OUTPUT_FOLDER="$BASE_OUTPUT/run_$i"
    mkdir -p "$OUTPUT_FOLDER"

    echo "Launching job $i -> $JOB_CMD"

    OUTPUT_DIR="$OUTPUT_FOLDER" $JOB_CMD &
    i=$((i+1))
done

wait
echo "Number of total runs: $i"
