import numpy as np
import os
import matplotlib.pyplot as plt
import read_json_file

combinations = [
    {'marker': 'o', 'color': 'lightcoral', 'markersize': 10},
    {'marker': 's', 'color': 'skyblue', 'markersize': 10},
    {'marker': '^', 'color': 'lightgreen', 'markersize': 10},
    {'marker': 'D', 'color': 'gold', 'markersize': 10},
    {'marker': '*', 'color': 'grey', 'markersize': 10},
]

data_folder_path = "/mnt/DATA/yating/results/antagonistic/"




for N_shepherd in range(1, 2):

    alphas = [0.523, 0.628, 0.785, 1.047]
    plt.figure(figsize=(12, 8))
    marker_style = combinations[N_shepherd - 1]

    # Calculate statistics
    x_values = []
    y_means = []
    y_stds = []
    for alpha in alphas:
        for N_sheep in [20, 40, 60, 80, 100]:
            ticks = []
            for rep in range(1, 5):
                file_path = f"{data_folder_path}Alpha_{alpha}/N_shepherd_{N_shepherd}/N_sheep_{N_sheep}/rep_{rep}/sheep_data.json"
                if os.path.exists(file_path):
                    sheep_data = read_json_file(file_path)
                    if sheep_data:
                        ticks.append(sheep_data[-1]["tick"])

            if ticks:
                x_values.append(N_sheep)
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
                     label=f'{alpha} Alpha',
                     alpha=0.8)

    plt.xlabel('Number of Sheep', fontsize=14)
    plt.ylabel('Mean Final Tick ± Std Dev', fontsize=14)
    plt.title('Antagonistic Sheep', fontsize=16)
    plt.xticks([20, 40, 60, 80, 100])
    plt.grid(True, alpha=0.3)
    plt.legend(title='Alpha', fontsize=14)
    plt.tight_layout()
    plt.savefig('Time_and_N_sheep_NH_'+ str(N_shepherd)+'.png', dpi=300, bbox_inches='tight')
    # plt.show()