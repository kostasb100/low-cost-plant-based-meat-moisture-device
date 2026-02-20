"""
Light source average pixel value drift capture and analysis program

This program:
- Captures images of a given area illuminated by a light source(halogen lamp) at given intervals over time
- Calculates the average pixel values (APV) of the images and outputs this data into a CSV file
- Can perform capture and analysis separately

Purpose:
- Used to test the APV drift properties of the light source used in the experiments
- This data can then be used to calculate the light source pre-heat time

Date: 2026-02
"""

import time
# import RPi.GPIO as GPIO
# from picamera2 import Picamera2
import os
import re
import rawpy
import numpy as np
import pandas as pd
import cv2

base_dir = os.getcwd()
dng_output_folder = os.path.join(base_dir, "light_source_drift_images")
os.makedirs(dng_output_folder, exist_ok=True)

# Make the user select the program mode
print("Select program mode:")
print("1 - Capture and Analysis")
print("2 - Capture only")
print("3 - Analysis only")

mode = input("Enter 1, 2, or 3: ").strip()

# Set GPIO settings of the light source
light_source_pin = 4 # GPIO pin which is used to turn on the light source(halogen lamp, LED and etc.)
GPIO.setmode(GPIO.BCM)
GPIO.setup(light_source_pin, GPIO.OUT)

# Capture with these settings
total_time = 240 # Total time for the experiment
interval = 5 # Interval at which capture will happen
num_pics = total_time // interval

# Use try/finally to prevent hardware crashes
def perform_capture():
    try:
        # Turn off the camera in case it is turned on
        picam2 = None
        GPIO.output(light_source_pin, GPIO.HIGH)

        # Initialize the camera
        picam2 = Picamera2()

        sensor_width, sensor_height = picam2.sensor_resolution

        config = picam2.create_still_configuration(
            raw={"size": (sensor_width, sensor_height)},
            buffer_count=2,
            controls={
                "AeEnable": False,
                "AwbEnable": False,
                "Brightness": 0.0,
                "Contrast": 1.0,
                "Saturation": 1.0,
                "Sharpness": 1.0,
                "NoiseReductionMode": 0,
                "ExposureTime": 150000, # [us]
                "AnalogueGain": 1.0,
                "ColourGains": (1.0, 1.0),
                "LensPosition": 10.0
            }
        )

        picam2.configure(config)
        picam2.start()
        time.sleep(1.0)  # Allow camera to stabilise

        # Start time count
        start_time = time.time()

        for i in range(num_pics):
            timestamp = time.time() - start_time

            # Save RAW(DNG) images based on their time stamp
            filename = os.path.join(dng_output_folder, f"image_{timestamp:.1f}s.dng")

            # Capture  images
            picam2.capture_file(filename, name="raw")
            print(f"Captured RAW {filename}")
            time.sleep(interval)

    # Turn the camera off
    finally:
        if picam2:
            picam2.stop()
            picam2.close()

        GPIO.output(light_source_pin, GPIO.LOW) # Turn of the light source
        GPIO.cleanup()
        print("Capture finished.")

def perform_analysis():
    print("Starting analysis...")

    black_level = 64  # Adjust if camera-specific value differs

    output_csv = os.path.join(dng_output_folder, "raw_vs_time.csv")
    # Extract time from the time-stamped images names
    time_pattern = re.compile(r"image_([0-9]+(?:\.[0-9]+)?)s\.dng", re.IGNORECASE)

    results = []

    for filename in os.listdir(dng_output_folder):
        match = time_pattern.match(filename)
        if not match:
            continue

        time_s = float(match.group(1))
        dng_path = os.path.join(dng_output_folder, filename)

        # Calculate the average pixel values of the individual DNG images
        try:
            with rawpy.imread(dng_path) as raw:
                raw_img = raw.raw_image_visible.astype(np.float32)
                raw_img -= black_level
                raw_img = np.clip(raw_img, 0, None)
                raw_mean = raw_img.mean()

        except Exception as e:
            print(f"Skipping {filename}: {e}")
            continue

        results.append((time_s, raw_mean))

    if not results:
        print("No DNG files found for analysis.")
        return

    # Sort results by time
    results.sort(key=lambda x: x[0])

    # Save data to CSV
    df = pd.DataFrame(results, columns=["Time", "MeanRaw"])
    df.to_csv(output_csv, index=False)

    print(f"Saved CSV to {output_csv}")

# Conditions for every mode
if mode == "1":
    perform_capture()
    perform_analysis()

elif mode == "2":
    perform_capture()

elif mode == "3":
    perform_analysis()

else:
    print("Invalid mode selected.")
