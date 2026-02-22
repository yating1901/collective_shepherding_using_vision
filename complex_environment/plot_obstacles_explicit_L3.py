import numpy as np
import os
import matplotlib.pyplot as plt
from data_analysis.read_json_file import read_json_file

Data_folder_path = "/home/yateng/Workspace/CAB/data_analysis/Data_obstacles/"

combinations = [
    {'marker': 'o', 'color': 'lightcoral', 'markersize': 5},
    {'marker': 's', 'color': 'skyblue', 'markersize': 5},
    {'marker': '^', 'color': 'lightgreen', 'markersize': 5},
    {'marker': 'D', 'color': 'gold', 'markersize': 5},
    {'marker': '*', 'color': 'grey', 'markersize': 5},
]


for N_shepherd in [1, 3]:
    plt.figure(figsize=(12, 8))
    marker_index = 0
    for Is_explicit in [True, False]:
        for L3 in [0, 100]:
            if Is_explicit:
                data_folder_path = Data_folder_path + "explicit/"+"L3_" + str(L3)+"/"
            else:
                data_folder_path = Data_folder_path + "implicit/"+"L3_" + str(L3)+"/"

            x_values = []
            y_means = []
            y_stds = []
            for N_sheep in range(50, 250, 50):
                ticks = []
                for rep in range(1, 6):
                    file_path = f"{data_folder_path}N_shepherd_{N_shepherd}/N_sheep_{N_sheep}/rep_{rep}/sheep_data.json"
                    print(file_path)
                    if os.path.exists(file_path):
                        sheep_data = read_json_file(file_path)
                        if sheep_data:
                            ticks.append(sheep_data[-1]["tick"])

                if ticks:
                    x_values.append(N_sheep)
                    y_means.append(np.mean(ticks))
                    y_stds.append(np.std(ticks))
            if Is_explicit:
                line_label = "Explicit_L3_" + str(L3)
            else:
                line_label = "Implicit_L3_" + str(L3)

            marker_style = combinations[marker_index]
            marker_index += 1

            # Use plt.errorbar which is designed for this
            plt.errorbar(x_values, y_means, yerr=y_stds,
                         fmt=marker_style['marker'] + '-',  # Marker with line
                         color=marker_style['color'],
                         markersize=10,
                         capsize=5,
                         capthick=2,
                         elinewidth=2,
                         linewidth=2,
                         markeredgecolor='grey',
                         markeredgewidth=0.5,
                         label=line_label,
                         alpha=0.8)

    plt.xlabel('Number of Sheep', fontsize=14)
    plt.ylabel('Mean Final Tick ± Std Dev', fontsize=14)
    plt.title('Different Strategies in Complex environment', fontsize=16)
    plt.xticks([50, 100, 150, 200])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('Obstacles_Ex_implicit_Nsh_'+ str(N_shepherd) + '_rep_'+str(5)+'.png', dpi=300, bbox_inches='tight')
    # plt.show()
    plt.clf()