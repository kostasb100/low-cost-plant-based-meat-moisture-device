"""
Color-mapped difference image generator program for experiments with the plant-based meat sample

This program:
- Loads all of the illuminated (n0) and noise (f0) JPEG images from the directory in which they are stored in
- Performs noise reduction (subtracts f0.jpeg from n0.jpeg)
- Sets the initial(t=0) noise reduced(clean) image as a reference image and then subtracts the clean images from
  other states by this image.
- Plots these differences using color mapping, where red pixels indicate an increase in pixel intensity(brightening)
  and blue pixels indicate a decrease in pixel intensity(darkening).
- The results can be converted into GIFs with gif_generator.py

Purpose:
- Let's the user visualize which areas of the plant-based meat sample brigther or darken over time.

Date 2026-03
"""

import os
import cv2
import numpy as np

root_dir = r"C:\path\to\images"          # Directory where input images are stored
output_dir_red = r"C:\path\to\red"      # Output path for brightened (red) area images
output_dir_blue = r"C:\path\to\blue"    # Output path for darkened (blue) area images

clean_images = {}

# Sort and remove noise from the experiment result images
for time_name in sorted(os.listdir(root_dir), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else float('inf')):
    time_path = os.path.join(root_dir, time_name)

    if not os.path.isdir(time_path):
        continue

    # Search inside shutter subfolders
    for shutter_name in os.listdir(time_path):
        shutter_path = os.path.join(time_path, shutter_name)
        if not os.path.isdir(shutter_path):
            continue

        f0_path = os.path.join(shutter_path, "f0.jpg")
        n0_path = os.path.join(shutter_path, "n0.jpg")

        if not (os.path.exists(f0_path) and os.path.exists(n0_path)):
            continue

        f0 = cv2.imread(f0_path)
        n0 = cv2.imread(n0_path)

        if f0 is None or n0 is None:
            print(f"Warning: Could not read images in {shutter_path}")
            continue

        # Convert to float for precision
        f0 = f0.astype(np.float32)
        n0 = n0.astype(np.float32)

        # Remove noise from illuminated images
        clean = np.clip(n0 - f0, 0, 255).astype(np.uint8)
        clean = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY)
        clean_images[float(time_name)] = clean

        break

# Set the reference image
if 0.0 not in clean_images:
    raise ValueError("Reference image (0.0 min) not found.")
ref_img = clean_images[0.0]

# Compute the difference between the clean images of individual states and the reference image
for time, img in sorted(clean_images.items()):
    if time == 0.0:
        continue

    # Difference
    diff = img.astype(np.int16) - ref_img.astype(np.int16)

    # Separate the brightened(red) and darkenbed(blue) area into different images
    pos = diff > 0
    neg = diff < 0

    red_map = np.zeros((ref_img.shape[0], ref_img.shape[1], 3), dtype=np.uint8)
    blue_map = np.zeros_like(red_map)

    red_map[pos] = [0, 0, 255]
    blue_map[neg] = [255, 0, 0]

    # Save the color-mapped images
    cv2.imwrite(os.path.join(output_dir_red, f"{time}_red.jpg"), red_map)
    cv2.imwrite(os.path.join(output_dir_blue, f"{time}_blue.jpg"), blue_map)

cv2.waitKey(0)
cv2.destroyAllWindows()
