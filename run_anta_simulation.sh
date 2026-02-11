#!/bin/bash
BASE_OUTPUT="results" #"/mnt/DATA/yating/results/antagonistic"
mkdir -p "$BASE_OUTPUT"

JOBS=()
Iterations=5

alphas=(0.523 0.628 0.785 1.047) #1/6pi 1/5pi 1/4pi 1/3pi

for alpha in "${alphas[@]}"
do
  Alpha=$(printf "%.3f" "$alpha")
  echo "Alpha = $Alpha"
  for N_shepherd in $(seq 1 1 1) # Shepherd numbers
  do
    for N_sheep in $(seq 40 20 400)   # Sheep numbers
    do
      for Repetition in $(seq 1 1 1)
      do
        OUTPUT_FOLDER="$BASE_OUTPUT/Alpha_$Alpha/N_shepherd_$N_shepherd/N_sheep_$N_sheep/rep_$Repetition"
        mkdir -p "$OUTPUT_FOLDER"
        # Store the job as a string: "A REP OUTPUT_FOLDER"
        JOBS+=("$N_sheep $N_shepherd $Iterations $Alpha $Repetition $OUTPUT_FOLDER")
      done
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
    Alpha=$4
    Repetition=$5
    OUTPUT_FOLDER=$6

    mkdir -p "$OUTPUT_FOLDER"

    echo "Launching job N_sheep=$N_sheep rep=$Repetition Iterations=$Iterations Alpha=$Alpha Repetition=$Repetition"
    # In your .sh file, before running python
    export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib:$LD_LIBRARY_PATH"
    nohup env OUTPUT_DIR="$OUTPUT_FOLDER" python main_anta.py $N_sheep $N_shepherd $Iterations $Alpha $Repetition > "$OUTPUT_FOLDER/output.txt" 2>&1 < /dev/null &
    i=$((i+1))
done

#wait
echo "Number of total runs: $i"

