"""
Weight measurement extractor program

This program:
- Loads .json files containing weight measurements from each experiment cycle
- Extracts this data and saves it to .csv files

Purpose:
- Enables inspection and comparison of weight changes of the sample

Date: 2026-02
"""

import os
import json
import csv

# Root directory
root_dir = r"root_dir_path"

# Output CSV file
output_csv = os.path.join(root_dir, "weight_data.csv")

# CSV header
fields = ["Time", "Weight(g)"]

# Initialize CSV writer
f = open(output_csv, "w", newline="", encoding="utf-8")
writer = csv.writer(f)
writer.writerow(fields)

# Find numeric time directories
time_dirs = []
for t in os.listdir(root_dir):
    path = os.path.join(root_dir, t)
    if os.path.isdir(path):
        try:
            float(t)
            time_dirs.append(t)
        except ValueError:
            continue

# Sort numerically (0.0, 20.0, ...)
time_dirs = sorted(time_dirs, key=lambda x: float(x))

# Loop through sorted folders
for time_dir in time_dirs:
    folder_path = os.path.join(root_dir, time_dir)
    time_value = float(time_dir)

    json_path = os.path.join(folder_path, "weight.json")

    if not os.path.isfile(json_path):
        continue

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    weight = data.get("Weight(g)", "")

    row = [time_value, weight]

    writer.writerow(row)

f.close()

print("Weight data saved in:", output_csv)




