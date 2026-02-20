import json
import re
import numpy as np
import os
import matplotlib.pyplot as plt
from  read_json_file import read_json_file
import json
import seaborn as sns
import pandas as pd

def parse_mixed_file(filename):
    """Parse file with mixed JSON and non-JSON content."""
    with open(filename, 'r') as f:
        content = f.read()

    result = {
        'matrix': [],
        'raw': [],
        'line': [],
        'n_sheep': 0
    }

    # Split by lines
    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. Parse JSON arrays (matrix rows)
        if line.startswith('[') and line.endswith(']'):
            try:
                row = json.loads(line)
                result['matrix'].append(row)
            except:
                # Try to fix common JSON issues
                fixed_line = line.replace('99999,', '"99999",')  # Convert numbers to strings if needed
                try:
                    row = json.loads(fixed_line)
                    result['matrix'].append(row)
                except:
                    print(f"Could not parse: {line[:50]}...")

        # 2. Parse "Raw:" line
        if '"Raw:"' in line:
            # Use regex to extract JSON array
            match = re.search(r'"Raw:"\s*(\[.*?\])', line)

            result['raw'] = json.loads(match.group(1))

        # 3. Parse "Line:" line
        if '"Line:"' in line:
            match = re.search(r'"Line:"\s*(\[.*?\])', line)
            result['line'] = json.loads(match.group(1))

        # 4. Parse N_sheep
        if 'N_sheep=' in line:
            match = re.search(r'N_sheep=(\d+)', line)
            if match:
                result['n_sheep'] = int(match.group(1))

    return result


# Usage

N_sheep = 120
json_file_name = "map_data_Nh_1_Ns_"+str(N_sheep)+"_rep_3"
data = parse_mixed_file(json_file_name + '.json')

# print(f"Matrix size: {len(data['matrix'])}x{len(data['matrix'][0])}")
# print(f"Number of sheep: {data['n_sheep']}")
map_data = data['matrix']
map_data = map_data[::-1]
# print(map_data)

# Create DataFrame
df = pd.DataFrame(map_data)
plt.figure(figsize=(10, 6))
ax=sns.heatmap(df, annot=False, fmt='.2f', cmap='coolwarm', vmin=0, vmax=50000)
# ax.set_ylim(0, len(df))
x_ticks = [round(x,2) for x in data["raw"]]
y_ticks = [round(y,2) for y in data["line"]][::-1]
# print(x_ticks, y_ticks)
ax.set_xticklabels(x_ticks)
ax.set_yticklabels(y_ticks)

# Add axis labels
ax.set_xlabel('Driving Threshold')
ax.set_ylabel('Collecting Threshold')
plt.title('N_sheep = '+ str(N_sheep), fontsize=14)
# plt.savefig('Map_N_sheep=' + str(N_sheep) + '.png', dpi=300, bbox_inches='tight')
plt.savefig(json_file_name + '.png', dpi=300, bbox_inches='tight')
# plt.show()