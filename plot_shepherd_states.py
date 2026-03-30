import math
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import math

is_explicit = True

if is_explicit:
    data_folder_path = "/mnt/data3/Yating_Data/results/basic/explicit/"
else:
    data_folder_path = "/mnt/data3/Yating_Data/results/basic/implicit/"

def read_json_file(file_path):
    print(f"Reading: {file_path}")
    all_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read line by line
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        # Each line should be a JSON array
                        tick_data = json.loads(line)
                        all_data.extend(tick_data)
                        #print(f"Line {line_num}: Added {len(tick_data)} records from tick {tick_data[0]['tick']}")
                    except json.JSONDecodeError:
                        print(f"✗ Could not parse line {line_num}: {line[:50]}...")
        print(f"✓ Data covers ticks: {min(d['tick'] for d in all_data)} to {max(d['tick'] for d in all_data)}")
        f.close()
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")

    return all_data


def Caculte_coordination(shepherd_data):
    states = []
    Final_tick = int(shepherd_data[-1]["tick"])
    N_shepherd = int(shepherd_data[-1]["ID"]) + 1
    for tick_index in range(0, Final_tick):
        tick_states = 0
        for shepherd_index in range(0, N_shepherd):
            tick_states = tick_states + float(shepherd_data[tick_index * N_shepherd + shepherd_index]["MODE"])
        if (tick_states == 0) or (tick_states == N_shepherd):   # shepherd state: 1.0 --> drive_mode = true
            states.append(0)  # non-coorperation
        else:
            states.append(1)  # functional-coorperation
    # print(np.sum(states), Final_tick)
    coordination_percentage = np.sum(states)/Final_tick
    return coordination_percentage

# Create scatter plot
combinations = [
    {'marker': 'o', 'color': 'lightcoral', 'markersize': 10},
    {'marker': 's', 'color': 'skyblue', 'markersize': 10},
    {'marker': '^', 'color': 'lightgreen', 'markersize': 10},
    {'marker': 'D', 'color': 'gold', 'markersize': 10},
    {'marker': '*', 'color': 'grey', 'markersize': 10},
]
plt.figure(figsize=(12, 10))
for N_shepherd in range(2, 6):
    marker_style = combinations[N_shepherd - 1]
    Coordination = []
    for N_sheep in [40, 80, 120, 160]:
        coordinate_states = []
        for rep in range(1, 11):
            shepherd_file_path = f"{data_folder_path}N_shepherd_{N_shepherd}/N_sheep_{N_sheep}/rep_{rep}/shepherd_data.json"
            print(shepherd_file_path)
            shepherd_data = read_json_file(shepherd_file_path)
            final_tick = int(shepherd_data[-1]["tick"])
            coordinate_states.append(Caculte_coordination(shepherd_data))
        # print(N_shepherd, N_sheep, rep, coordination)
        Coordination.append(np.mean(coordinate_states))

    X = [40, 80, 120, 160]
    plt.plot(X, Coordination,
             marker_style['marker'] + '-',  # Marker with line
             color=marker_style['color'],
             markersize=10,
             linewidth=2,
             markeredgecolor='grey',
             markeredgewidth=0.5,
             label=f'N_shepherd = {N_shepherd}',
             alpha=0.8)
    plt.grid(True, alpha=0.3)
    plt.ylim(0.2, 0.8)

    if is_explicit:
        title_name = "Labor Division with Improved Rules"

    else:
        title_name = "Labor Division with Implicit Rules"

    plt.title(title_name, fontsize=14)
    plt.xlabel('Number of sheep', fontsize=12)
    plt.ylabel('Division Rate', fontsize=12)
    plt.legend()


plt.savefig(title_name + ".png", dpi=300, bbox_inches='tight')
plt.show()