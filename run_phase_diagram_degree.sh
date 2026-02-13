#!/bin/bash
BASE_OUTPUT=/media/yating/results_phase_diagram #samsung-2TB/CAB_Visual_Data  #"results" #"/mnt/DATA/yating/results_phase_diagram"
mkdir -p "$BASE_OUTPUT"
export LC_NUMERIC=C  # Force C locale (uses dot as decimal separator)

JOBS=()
Iterations=50000
N_shepherd=1 #2 3
N_sheep=60 #80 100
#Repetition=5

# -----------------------------
# Generate JOBS
# -----------------------------
for coll_angle in $(seq 40 20 120)
do
  for drive_angle in $(seq 0 10 90)
  do
    for Repetition in $(seq 1 1 1)
    do
    # Create unique output folder with angle parameters
    OUTPUT_FOLDER="$BASE_OUTPUT/N_shepherd_$N_shepherd/N_sheep_$N_sheep/coll_$coll_angle/drive_$drive_angle/rep_$Repetition"
    mkdir -p "$OUTPUT_FOLDER"
    JOBS+=("$N_shepherd $N_sheep $Iterations $Repetition $coll_angle $drive_angle $OUTPUT_FOLDER")
    done
  done
done

#########################

echo "Total jobs to run: ${#JOBS[@]}"

i=0
for JOB in "${JOBS[@]}"; do
    # Parse fields: $N_sheep $N_shepherd $Iterations $L3 $coll_angle $drive_angle $Repetition $OUTPUT_FOLDER
    set -- $JOB
    N_shepherd=$1
    N_sheep=$2
    Iterations=$3
    Repetition=$4
    coll_angle=$5
    drive_angle=$6
    OUTPUT_FOLDER=$7

    mkdir -p "$OUTPUT_FOLDER"

    echo "Launching job $((i+1))/${#JOBS[@]}: N_shepherd=$N_shepherd, N_sheep=$N_sheep, Iterations=$Iterations, rep=$Repetition, coll_angle=$coll_angle, drive_angle=$drive_angle"

    export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib:$LD_LIBRARY_PATH"

    # Pass angle parameters to the Python script
    nohup env OUTPUT_DIR="$OUTPUT_FOLDER" python main_phase_diagram_degree.py $N_shepherd $N_sheep $Iterations $Repetition $coll_angle $drive_angle> "$OUTPUT_FOLDER/output.txt" 2>&1 < /dev/null &

    i=$((i+1))
done

echo "Number of total runs: $i"
echo "All jobs submitted!"