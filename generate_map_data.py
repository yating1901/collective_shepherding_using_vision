import numpy as np
import os
import matplotlib.pyplot as plt
from fontTools.misc.cython import returns

import json
import seaborn as sns
import pandas as pd


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


def generate_map_data_in_order(N_sheep, N_shepherd, rep, data_folder_path):
    json_file_name = "map_data_"+"N_sheep_"+ str(N_sheep) +".json"
    coll_subfolders = [f.name for f in os.scandir(data_folder_path) if f.is_dir()]

    coll_thresholds = []
    drive_thresholds = []
    map = []
    for coll_subfolder in coll_subfolders:
        coll_thresholds.append(float(coll_subfolder[5:]))
    coll_thresholds.sort(reverse=True)

    coll_threshold_0 = coll_thresholds[0]
    subfolder = data_folder_path + "coll_"+str(coll_threshold_0)+"/"
    drive_subfolders = [f.name for f in os.scandir(subfolder) if f.is_dir()]
    for drive_subfolder in drive_subfolders:
        drive_thresholds.append(float(drive_subfolder[6:]))
    drive_thresholds.sort()

    print("coll_thresholds:",coll_thresholds)
    print("drive_thresholds:",drive_thresholds)

    for coll_threshold in coll_thresholds:
        map_data = []
        subfolder = data_folder_path + "coll_"+str(coll_threshold)+"/"
        for drive_threshold in drive_thresholds:
            file_path = subfolder + "drive_"+ str(drive_threshold) + "/" + "rep_1/"
            sheep_file_path = file_path + "sheep_data.json"
            sheep_data = read_json_file(sheep_file_path)
            Final_tick = sheep_data[-1]["tick"]
            map_data.append(Final_tick)
        map.append(map_data)

        with open(json_file_name, 'a') as f:
            json.dump(map_data, f)
            f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("Raw:", f)
        json.dump(drive_thresholds, f)
        f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("Line:", f)
        json.dump(coll_thresholds, f)
        f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("N_sheep=" + str(N_sheep), f)
        f.write("\n")

    return

def generate_map_data(N_sheep, N_shepherd, rep, data_folder_path):
    json_file_name = "map_data_"+"N_sheep_"+ str(N_sheep) +".json"
    coll_subfolders = [f.name for f in os.scandir(data_folder_path) if f.is_dir()]

    coll_thresholds = []
    drive_thresholds = []
    map = []
    for coll_subfolder in coll_subfolders:
        subfolder = data_folder_path + "/" + coll_subfolder
        drive_subfolders = [f.name for f in os.scandir(subfolder) if f.is_dir()]
        coll_thresholds.append(float(coll_subfolder[5:]))
        map_data = []
        for drive_subfolder in drive_subfolders:
            file_path = subfolder + "/" + drive_subfolder + "/" + "rep_1/"
            drive_thresholds.append(float(drive_subfolder[6:]))
            sheep_file_path = file_path + "sheep_data.json"
            sheep_data = read_json_file(sheep_file_path)
            Final_tick = sheep_data[-1]["tick"]
            map_data.append(Final_tick)
        map.append(map_data)
        with open(json_file_name, 'a') as f:
            json.dump(map_data, f)
            f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("Raw:", f)
        json.dump(drive_subfolders, f)
        f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("Line:", f)
        json.dump(coll_subfolders, f)
        f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("N_sheep=" + str(N_sheep), f)
        f.write("\n")

    return drive_subfolders, coll_subfolders

# drive_subfolders, coll_subfolders = generate_map_data(N_sheep, N_shepherd, rep, data_folder_path)

def generate_map_json_data(N_shepherd, N_sheep, rep, coll_angles, drive_angles, coll_folders, drive_folders, data_folder_path):
    json_file_name = "map_data_" + "Nh_"+str(N_shepherd)+"_Ns_" + str(N_sheep) +"_rep_"+str(rep)+ ".json"
    map = []
    for coll_folder in coll_folders:
        map_data = []
        for drive_folder in drive_folders:
            final_ticks = []
            for index in range(1, rep+1):
                file_path = data_folder_path + coll_folder +"/"+ drive_folder + "/" + "rep_"+str(index)+"/"
                print(file_path)
                sheep_file_path = file_path + "sheep_data.json"
                sheep_data = read_json_file(sheep_file_path)
                final_tick = sheep_data[-1]["tick"]
                final_ticks.append(final_tick)

            map_data.append(np.mean(final_ticks))
        map.append(map_data)

        with open(json_file_name, 'a') as f:
            json.dump(map_data, f)
            f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("Raw:", f)
        json.dump(drive_angles, f)
        f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("Line:", f)
        json.dump(coll_angles, f)
        f.write("\n")

    with open(json_file_name, 'a') as f:
        json.dump("N_sheep=" + str(N_sheep), f)
        f.write("\n")

    return


N_shepherd = 1
N_sheep = 100 #60 80 100
rep = 5
coll_angles=[angle for angle in range(40,121,20)]
drive_angles=[angle for angle in range(0,91,10)]
coll_folders = ["coll_"+str(coll_angle) for coll_angle in coll_angles]
drive_folders = ["drive_"+str(drive_angle) for drive_angle in drive_angles]


data_folder_path = "/media/samsung-2TB/results_phase_diagram/"+"N_shepherd_"+str(N_shepherd)+"/N_sheep_"+str(N_sheep)+"/"
print(data_folder_path)

generate_map_json_data(N_shepherd, N_sheep, rep, coll_angles, drive_angles, coll_folders, drive_folders, data_folder_path)
