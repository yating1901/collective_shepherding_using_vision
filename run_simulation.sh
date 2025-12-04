#!/bin/bash
BASE_OUTPUT="results"
mkdir -p "$BASE_OUTPUT"

JOBS=()
Iterations=100000
L3=50
# -----------------------------
# Generate JOBS
# -----------------------------
for N_shepherd in $(seq 1 1 5)
do
  for N_sheep in $(seq 50 50 200)   # Sheep numbers
  do
    for Repetition in $(seq 6 1 10)    # Shepherd numbers
    do
      OUTPUT_FOLDER="$BASE_OUTPUT/N_shepherd_$N_shepherd/N_sheep_$N_sheep/rep_$Repetition"
      mkdir -p "$OUTPUT_FOLDER"
      # Store the job as a string: "A REP OUTPUT_FOLDER"
      JOBS+=("$N_sheep $N_shepherd $Iterations $L3 $Repetition $OUTPUT_FOLDER")
      #JOBS+=("python "main_2.py" $N_sheep $N_shepherd $Iterations $L3 $Repetition")
    done
  done
done
i=0
for JOB in "${JOBS[@]}"; do
    # Parse fields: $A $REP $OUTPUT_FOLDER
    set -- $JOB
    N_sheep=$1
    N_shepherd=$2
    Iterations=$3
    L3=$4
    Repetition=$5
    OUTPUT_FOLDER=$6

    mkdir -p "$OUTPUT_FOLDER"

    echo "Launching job N_sheep=$N_sheep rep=$Repetition"
    # In your .sh file, before running python
    export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib:$LD_LIBRARY_PATH"
    nohup env OUTPUT_DIR="$OUTPUT_FOLDER" python main_2.py $N_sheep $N_shepherd $Iterations $L3 $Repetition > "$OUTPUT_FOLDER/output.txt" 2>&1 < /dev/null &
    i=$((i+1))
done

#wait
echo "Number of total runs: $i"

