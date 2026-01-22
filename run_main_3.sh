#!/bin/bash
BASE_OUTPUT="/mnt/DATA/yating/results"
mkdir -p "$BASE_OUTPUT"

JOBS=()
Iterations=100000

# Angle thresholds setup
# Angle_Threshold_Collection: from pi*2/3 to 1/4*pi (10 steps)
# Angle_Threshold_Drive: from pi/10 to pi/2 (10 steps)
COLLECTION_START=$(echo "scale=10; 2*3.14/3" | bc)
COLLECTION_END=$(echo "scale=10; 3.14/4" | bc)
DRIVE_START=$(echo "scale=10; 3.14/20" | bc)
DRIVE_END=$(echo "scale=10; 3.14/2" | bc)
STEPS=10

# Generate linear steps
coll_steps=()
drive_steps=()

# Calculate collection angle steps
for i in $(seq 0 $((STEPS-1))); do
    t=$(echo "scale=10; $COLLECTION_START + ($COLLECTION_END - $COLLECTION_START) * $i / ($STEPS - 1)" | bc)
    coll_steps+=($t)
done

# Calculate drive angle steps
for i in $(seq 0 $((STEPS-1))); do
    t=$(echo "scale=10; $DRIVE_START + ($DRIVE_END - $DRIVE_START) * $i / ($STEPS - 1)" | bc)
    drive_steps+=($t)
done

# -----------------------------
# Generate JOBS
# -----------------------------
L3=100
N_shepherd=1
N_sheep=100
for coll_angle in "${coll_steps[@]}"
do
  for drive_angle in "${drive_steps[@]}"
  do
    for Repetition in $(seq 1 1 1)
    do
      # Create unique output folder with angle parameters
      OUTPUT_FOLDER="$BASE_OUTPUT/L3_$L3/N_shepherd_$N_shepherd/N_sheep_$N_sheep/coll_$coll_angle/drive_$drive_angle/rep_$Repetition"
      mkdir -p "$OUTPUT_FOLDER"
      # Store job parameters: N_sheep N_shepherd Iterations L3 coll_angle drive_angle Repetition OUTPUT_FOLDER
      JOBS+=("$N_sheep $N_shepherd $Iterations $L3 $coll_angle $drive_angle $Repetition $OUTPUT_FOLDER")
    done
  done
done

#########################

echo "Total jobs to run: ${#JOBS[@]}"

i=0
for JOB in "${JOBS[@]}"; do
    # Parse fields: $N_sheep $N_shepherd $Iterations $L3 $coll_angle $drive_angle $Repetition $OUTPUT_FOLDER
    set -- $JOB
    N_sheep=$1
    N_shepherd=$2
    Iterations=$3
    L3=$4
    coll_angle=$5
    drive_angle=$6
    Repetition=$7
    OUTPUT_FOLDER=$8

    mkdir -p "$OUTPUT_FOLDER"

    echo "Launching job $((i+1))/${#JOBS[@]}: N_sheep=$N_sheep, coll_angle=$coll_angle, drive_angle=$drive_angle, rep=$Repetition"

    export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib:$LD_LIBRARY_PATH"

    # Pass angle parameters to the Python script
    nohup env OUTPUT_DIR="$OUTPUT_FOLDER" python main_3.py $N_sheep $N_shepherd $Iterations $L3 $coll_angle $drive_angle $Repetition > "$OUTPUT_FOLDER/output.txt" 2>&1 < /dev/null &

    i=$((i+1))

    # Optional: Add a small delay or limit concurrent processes
    # sleep 0.1

    # Optional: Limit number of parallel jobs
    # if (( i % 10 == 0 )); then
    #     wait
    # fi
done

echo "Number of total runs: $i"
echo "All jobs submitted!"