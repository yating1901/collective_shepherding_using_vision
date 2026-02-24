import numpy as np
import os
import matplotlib.pyplot as plt
import json




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



def save_data(data, file_name, data_path):
    json_file = file_name + ".json"
    json_file_path = os.path.join(data_path, json_file)

    with open(json_file_path, "a") as outfile:
        json.dump(data, outfile)
        outfile.write("\n")

    return


def transfer_data_to_json(Data_folder_path):
    for N_shepherd in [3]:
        for Is_explicit in [True, False]:
            for L3 in [0, 50, 100]:
                if Is_explicit:
                    data_folder_path = Data_folder_path + "explicit/"+"L3_" + str(L3)+"/"
                else:
                    data_folder_path = Data_folder_path + "implicit/"+"L3_" + str(L3)+"/"

                final_ticks = []
                for N_sheep in range(50, 250, 50):
                    ticks = []
                    for rep in range(1, 6):
                        file_path = f"{data_folder_path}N_shepherd_{N_shepherd}/N_sheep_{N_sheep}/rep_{rep}/sheep_data.json"
                        print(file_path)
                        if os.path.exists(file_path):
                            sheep_data = read_json_file(file_path)
                            if sheep_data:
                                ticks.append(sheep_data[-1]["tick"])
                    final_ticks.append(ticks)
                if Is_explicit:
                    json_file_name = "Nh" + str(N_shepherd) + "_Explicit_L3_" + str(L3)
                    save_data(final_ticks, json_file_name, Data_folder_path)  # raw: Ns=50, 100, 150, 200
                else:
                    json_file_name = "Nh" + str(N_shepherd) + "_Implicit_L3_" + str(L3)
                    save_data(final_ticks, json_file_name, Data_folder_path)  # raw: Ns=50, 100, 150, 200
    return


def plot_data(data_folder_path):
    combinations = [
        {'marker': 'o-', 'color': 'lightcoral', 'markersize': 5},
        {'marker': 'o', 'color': 'skyblue', 'markersize': 5},
        {'marker': 's-', 'color': 'lightgreen', 'markersize': 5},
        {'marker': 's', 'color': 'gold', 'markersize': 5},
        {'marker': 'D-', 'color': 'grey', 'markersize': 5},
        {'marker': 'D', 'color': 'gold', 'markersize': 5},
        {'marker': '*-', 'color': 'grey', 'markersize': 5},
        {'marker': '*', 'color': 'grey', 'markersize': 5},
    ]
    plt.figure(figsize=(12, 8))
    for N_shepherd in [2, 3]:
        marker_index = 0
        for Is_explicit in [True, False]:
            for L3 in [0, 50, 100]:
                if Is_explicit:
                    line_label = "Explicit_L3_" + str(L3)
                    json_file_name = "Nh" + str(N_shepherd) + "_Explicit_L3_" + str(L3)+".json"
                else:
                    line_label = "Implicit_L3_" + str(L3)
                    json_file_name = "Nh" + str(N_shepherd) + "_Implicit_L3_" + str(L3)+".json"
                x_values = []
                y_means = []
                y_stds = []
                data = read_json_file(f"{data_folder_path}/{json_file_name}")
                print(data)
                marker_style = combinations[marker_index]
    #             plt.errorbar(x_values, y_means, yerr=y_stds,
    #                          fmt=marker_style['marker'] + '-',  # Marker with line
    #                          color=marker_style['color'],
    #                          markersize=10,
    #                          capsize=5,
    #                          capthick=2,
    #                          elinewidth=2,
    #                          linewidth=2,
    #                          markeredgecolor='grey',
    #                          markeredgewidth=0.5,
    #                          label=line_label,
    #                          alpha=0.8)
    #             marker_index += 1
    #
    # plt.xlabel('Number of Sheep', fontsize=14)
    # plt.ylabel('Mean Final Tick ± Std Dev', fontsize=14)
    # plt.title('Different Strategies in Complex environment', fontsize=16)
    # plt.xticks([50, 100, 150, 200])
    # plt.grid(True, alpha=0.3)
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig('Obstacles_Ex_implicit_Nsh_'+ str(N_shepherd) + '_rep_'+str(5)+'.png', dpi=300, bbox_inches='tight')
    # # plt.show()
    # plt.clf()

    return

Data_folder_path = "/mnt/DATA/yating/results/obstacles/"
transfer_data_to_json(Data_folder_path)


# data_folder_path = "/home/yateng/Workspace/CAB/data_analysis/Data_obstacles/"
# plot_data(data_folder_path)


#scp -r zheng@gadus.itb.biologie.hu-berlin.de:/mnt/DATA/yating/results/obstacles/explicit/*.json .
