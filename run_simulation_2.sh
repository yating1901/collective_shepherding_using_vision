#!/bin/bash
BASE_OUTPUT="results"
mkdir -p "$BASE_OUTPUT"

JOBS_FILE="jobs.txt"
> "$JOBS_FILE"  # Clear jobs file

Iterations=10
L3=50
N_shepherd=1

# -----------------------------
# Generate job commands file
# -----------------------------
for N_sheep in $(seq 100 100 200)
do
  for Repetition in $(seq 1 1 15)  # 100 total jobs (2×50)
  do
    OUTPUT_FOLDER="$BASE_OUTPUT/N_sheep_$N_sheep/rep_$Repetition"
    mkdir -p "$OUTPUT_FOLDER"

    # Write job command to file
    echo "OUTPUT_DIR='$OUTPUT_FOLDER' python main_2.py $N_sheep $N_shepherd $Iterations $L3 $Repetition > '$OUTPUT_FOLDER/output.txt' 2>&1" >> "$JOBS_FILE"
  done
done

# Run with job control (max 64 parallel jobs)
parallel -j 64 --joblog "$BASE_OUTPUT/joblog.txt" < "$JOBS_FILE"

echo "All jobs completed"