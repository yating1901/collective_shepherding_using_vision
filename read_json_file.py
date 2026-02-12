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

# data_folder_path = "/media/samsung-2TB/Collective_Shepherding_Pygame_Data/results/"
# for N_shepherd in range(1, 5):
#     for N_sheep in [50, 100, 150, 200]:
#         for rep in range(1, 5):
#             local_folder_path = "N_shepherd_"+ str(N_shepherd) + "/N_sheep_" + str(N_sheep) + "/rep_" + str(rep)+"/"
#             # print(local_folder_path)
#             folder_path = data_folder_path + local_folder_path
#             file_path = os.path.join(folder_path, "sheep_data.json")
#             # Add error handling
#             if not os.path.exists(file_path):
#                 print(f"  File not found: {file_path}")
#                 continue
#
#             sheep_data = read_json_file(file_path)
#
#             if not sheep_data:
#                 print(f"  No data loaded from {file_path}")
#                 continue
#
#             final_tick = sheep_data[-1]["tick"]
#             num_sheep = int(sheep_data[-1]["ID"])+1
#             state = sheep_data[-1]["state:"]
#             print(N_shepherd, num_sheep, final_tick)