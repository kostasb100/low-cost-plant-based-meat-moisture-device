"""
Metadata extractor program

This program:
- Loads .json files from each experiment cycle
- Extracts metadata for user-selected parameters
- Saves the extracted data to .csv files

Purpose:
- Enables inspection and comparison of capture metadata
  across multiple experiment cycles

Date: 2026-02
"""

import os
import json
import csv

# Metadata(.json) file path
root_dir = r"file_path"
json_names = ["f0.json", "l0.json", "n0.json"]

# Save CSV files inside root_dir
output_files = {
    "f0.json": os.path.join(root_dir, "f0_metadata.csv"),
    "l0.json": os.path.join(root_dir, "l0_metadata.csv"),
    "n0.json": os.path.join(root_dir, "n0_metadata.csv"),
}

# Save these fields inside CSV files
fields = [
    "time", "shutter_speed",
    "ExposureTime", "FocusFoM", "DigitalGain",
    "SensorTemperature",
    "LensPosition", "ColourTemperature", "Lux", "AnalogueGain"
]

# Initialize CSV writers
writers = {}
files = {}
for j in json_names:
    f = open(output_files[j], "w", newline="")
    writer = csv.writer(f)
    writer.writerow(fields)
    writers[j] = writer
    files[j] = f

# Find all of the existing time-labeled directories inside root_dir
time_dirs = []
for t in os.listdir(root_dir):
    path = os.path.join(root_dir, t)
    if os.path.isdir(path):
        try:
            float(t)
            time_dirs.append(t)
        except:
            pass

# Sort the time-labeled directories numerically (0.0, 20.0,...)
time_dirs = sorted(time_dirs, key=lambda x: float(x))

# Loop through sorted folders
for time_dir in time_dirs:
    time_path = os.path.join(root_dir, time_dir)
    time_value = float(time_dir)

    # Check whether time_path exists. If not, continue
    if not os.path.isdir(time_path):
        continue
    try:
        time_value = float(time_dir)
    except ValueError:
        continue

    for shutter_dir in os.listdir(time_path):
        shutter_path = os.path.join(time_path, shutter_dir)

        # Check whether shutter_path exists. If not, continue
        if not os.path.isdir(shutter_path):
            continue
        try:
            shutter_value = int(shutter_dir)
        except ValueError:
            continue

        for json_name in json_names:
            json_path = os.path.join(shutter_path, json_name)

            # Data extraction for .json files that exist
            if not os.path.isfile(json_path):
                continue

            with open(json_path) as file:
                data = json.load(file)

            m = data.get("metadata", {})

            row = [
                time_value,
                shutter_value,
                m.get("ExposureTime"),
                m.get("FocusFoM"),
                m.get("DigitalGain"),
                m.get("SensorTemperature", ""),
                m.get("LensPosition"),
                m.get("ColourTemperature"),
                m.get("Lux"),
                m.get("AnalogueGain"),
            ]

            writers[json_name].writerow(row)


# Finish writing inside CSV files and close them
for f in files.values():
    f.close()

print("Metadata files saved in:", root_dir)