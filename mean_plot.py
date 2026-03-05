import numpy as np
import os
import matplotlib.pyplot as plt
import json
# from data_analysis.read_json_file import read_json_file

def read_json_file(file_path):
    # print(f"Reading: {file_path}")
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
# data_folder_path = "/media/samsung-2TB/Collective_Shepherding_Pygame_Data/results/"
# data_folder_path = "/media/samsung-2TB/Collective_Shepherding_Pygame_Data/result_with_fence_reflections/"
# data_folder_path = "/media/samsung-2TB/Collective_Shepherding_Pygame_Data/result_without_fence_reflections/"
data_folder_path = "/mnt/data3/Yating_Data/results/basic/implicit"

for L3 in [0, 50, 100, 150]:
    plt.figure(figsize=(12, 8))
    for N_shepherd in range(1, 6):
        marker_style = combinations[N_shepherd - 1]

        # Calculate statistics
        x_values = []
        y_means = []
        y_stds = []
        for N_sheep in [60, 80, 120, 160]:
            ticks = []
            for rep in range(1, 6):
                file_path = f"{data_folder_path}/L3_{L3}/N_shepherd_{N_shepherd}/N_sheep_{N_sheep}/rep_{rep}/sheep_data.json"
                if os.path.exists(file_path):
                    sheep_data = read_json_file(file_path)
                    if sheep_data:
                        ticks.append(sheep_data[-1]["tick"])
            if ticks:
                x_values.append(N_sheep)
                y_means.append(np.mean(ticks))
                y_stds.append(np.std(ticks))

        # Use plt.errorbar which is designed for this
        plt.errorbar(x_values, y_means, #yerr=y_stds,
                     fmt=marker_style['marker'] + '-',  # Marker with line
                     color=marker_style['color'],
                     markersize=10,
                     capsize=5,
                     capthick=2,
                     elinewidth=2,
                     linewidth=2,
                     markeredgecolor='grey',
                     markeredgewidth=0.5,
                     label=f'{N_shepherd} Shepherd',
                     alpha=0.8)

    plt.xlabel('Number of Sheep', fontsize=14)
    plt.ylabel('Mean Final Tick ± Std Dev', fontsize=14)
    plt.title('Implicit_Strategies_L3='+ str(L3), fontsize=16)
    plt.xticks([60, 80, 120, 160])
    plt.grid(True, alpha=0.3)
    plt.legend(title='Number of Shepherds')
    plt.tight_layout()
    plt.savefig('Implicit_Time_and_Ns_Nh_L3='+str(L3)+'.png', dpi=300, bbox_inches='tight')
    # plt.show()
    plt.clf()