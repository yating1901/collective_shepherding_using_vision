import numpy as np
import matplotlib.pyplot as plt
import json
import os

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

combinations = [
    {'marker': 'o', 'color': 'lightcoral', 'markersize': 10},
    {'marker': 's', 'color': 'skyblue', 'markersize': 10},
    {'marker': '^', 'color': 'lightgreen', 'markersize': 10},
    {'marker': 'D', 'color': 'gold', 'markersize': 10},
    {'marker': '*', 'color': 'grey', 'markersize': 10},
]

data_folder_path = "/mnt/DATA/yating/results/antagonistic/"

N_sheep = 60
index = 0
for N_shepherd in range(1,3):

    plt.figure(figsize=(12, 8))
    # Calculate statistics
    x_values = []
    y_means = []
    y_stds = []

    marker_style = combinations[index]
    for alpha in range(0, 10, 100):
        ticks = []
        alpha = round(alpha*3.14/180, 3)

        for rep in range(1, 6):
            file_path = f"{data_folder_path}Alpha_{alpha}/N_shepherd_{N_shepherd}/N_sheep_{N_sheep}/rep_{rep}/sheep_data.json"
            if os.path.exists(file_path):
                sheep_data = read_json_file(file_path)
                if sheep_data:
                    ticks.append(sheep_data[-1]["tick"])

        if ticks:
            x_values.append(alpha)
            y_means.append(np.mean(ticks))
            y_stds.append(np.std(ticks))

    # Use plt.errorbar which is designed for this
    plt.errorbar(x_values, y_means,
                 fmt=marker_style['marker'] + '-',  # Marker with line
                 color=marker_style['color'],
                 markersize=10,
                 capsize=5,
                 capthick=2,
                 elinewidth=2,
                 linewidth=2,
                 markeredgecolor='grey',
                 markeredgewidth=0.5,
                 label=f'{N_shepherd} N_shepherd',
                 alpha=0.8)
    index = index +1

    plt.xlabel('Alpha', fontsize=14)
    plt.ylabel('Mean Final Tick ± Std Dev', fontsize=14)
    plt.title('Antagonistic Sheep = '+str(N_sheep), fontsize=16)
    plt.xticks([index for index in range(0,10,100)])
    plt.grid(True, alpha=0.3)
    plt.legend(title='N(shepherd)', fontsize=14)
    plt.tight_layout()
    plt.savefig('Time_and_Alpha_NH_'+ str(N_shepherd)+'.png', dpi=300, bbox_inches='tight')
    # plt.show()
    plt.clf()