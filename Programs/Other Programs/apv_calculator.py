"""
Average Pixel Value (APV) calculator

This program:
- Reads .jpg and .dng images (noise and illuminated) acquired from experiments conducted with capture.py
- Computes a reference mask from the .jpg images
- Applies this reference mask to divide both .jpg and .dng images into three regions 
  (inside the sample, outside the sample, and the total area without shrinkage)
- Calculates the APV of the individual regions and outputs the results in CSV format

Purpose:
- Allows the user to observe the optical changes of the plant-based meat sample over time
- Enables batch analysis of experimental results

Date: 2026-03
"""

import os
import cv2
import rawpy
import numpy as np
import pandas as pd

# Edge and shrinkage detection parameters taken from image.py

GAUSSIAN_KERNEL = (3, 3)     # Kernel size for Gaussian blur
SIGMA = 0                    # Gaussian sigma (0 = auto)
THRESH_VALUE = 31            # Threshold value for binary segmentation
THRESH_MAX = 255             # Maximum value for thresholding
EDGE_KERNEL = (3, 3)         # Kernel size for morphological gradient
AREA_MIN = 700000            # Minimum contour area to be considered valid
AREA_MAX = 9000000           # Maximum contour area to be considered valid
BLACK_LEVEL = 64             # Sensor black level offset (RAW calibration)

root_dir = r"C:\Users\kbalc\Desktop\uni\bachelor_project\measurements\3.2-3-6\3-1"


# Create a binary mask of the detected sample region and subtract noise before processing with JPEG files.
def get_mask(img, noise):

    # Subtract background/noise image if provided
    if noise is not None:
        img = cv2.subtract(img, noise)

    # Convert to grayscale for processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Smooth image to reduce noise before thresholding
    gray = cv2.GaussianBlur(gray, GAUSSIAN_KERNEL, SIGMA)

    # Apply binary threshold to segment object from background
    _, thresh = cv2.threshold(gray, THRESH_VALUE, THRESH_MAX, cv2.THRESH_BINARY)

    # Create rectangular structuring element for edge detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, EDGE_KERNEL)

    # Use morphological gradient to highlight edges
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)

    # Find contours in the processed binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Keep only contours within valid area range
    valid = [c for c in contours if AREA_MIN < cv2.contourArea(c) < AREA_MAX]

    # If no valid contour found, return None
    if not valid:
        return None

    # Select the largest valid contour
    contour = max(valid, key=cv2.contourArea)

    # Create empty mask
    mask = np.zeros(gray.shape, np.uint8)

    # Fill selected contour into mask
    cv2.drawContours(mask, [contour], -1, 255, -1)

    # Return boolean mask
    return mask.astype(bool)

# Build logical region masks: inside (current sample area), outside (outside the sample area)
# and full (everything except shrinkage region)

def build_region_masks(mask_t, mask0):

    # Shrinkage = area present in the reference mask but missing in current mask
    shrinkage = mask0 & (~mask_t)

    # Current detected region
    inside = mask_t

    # True background (excluding shrinkage)
    outside = (~mask0) & (~shrinkage)

    # Full region excluding shrinkage
    full = (~shrinkage)

    return inside, outside, full

# Separate Bayer channels (R, G1, G2, B) and compute average pixel values (APV) of the individual regions.
def raw_stats_with_mask(dng_path, mask, noise_path=None):

    # Load RAW image
    with rawpy.imread(dng_path) as raw:
        img = raw.raw_image_visible.astype(np.float32)

    # Subtract black level calibration offset
    img -= BLACK_LEVEL

    # Clip negative values
    img = np.clip(img, 0, None)

    # Subtract RAW noise
    if noise_path and os.path.exists(noise_path):
        with rawpy.imread(noise_path) as raw_f:
            noise = raw_f.raw_image_visible.astype(np.float32)
        noise -= BLACK_LEVEL
        img = np.clip(img - noise, 0, None)

    h, w = img.shape

    # Extract Bayer channels
    R  = img[0:h:2, 0:w:2][mask[0:h:2, 0:w:2]]
    G1 = img[0:h:2, 1:w:2][mask[0:h:2, 1:w:2]]
    G2 = img[1:h:2, 0:w:2][mask[1:h:2, 0:w:2]]
    B  = img[1:h:2, 1:w:2][mask[1:h:2, 1:w:2]]

    # Return dictionary of mean intensities
    return {
        "mean_raw": img[mask].mean(),                 # Mean over all masked pixels
        "R_mean": R.mean(),                           # Red channel mean
        "G1_mean": G1.mean(),                         # Green channel 1 mean
        "G2_mean": G2.mean(),                         # Green channel 2 mean
        "G_mean": np.mean([G1.mean(), G2.mean()]),    # Combined green mean
        "B_mean": B.mean()                            # Blue channel mean
    }

# Collect all time folders
time_folders = sorted(
    [f for f in os.listdir(root_dir)
     if os.path.isdir(os.path.join(root_dir, f)) and f.replace('.', '', 1).isdigit()],
    key=lambda x: float(x)   # Sort numerically
)

# Collect all shutter subfolders across time folders
shutters = sorted(
    {s for t in time_folders
     for s in os.listdir(os.path.join(root_dir, t))
     if os.path.isdir(os.path.join(root_dir, t, s)) and s.isdigit()},
    key=int  # Sort numerically
)

rows = []

for shutter in shutters:
    print(f"\nProcessing shutter {shutter}")
	
	# Build reference mask from the first time point
    t0 = time_folders[0]

    n0_jpg_0 = os.path.join(root_dir, t0, shutter, "n0.jpg")
    f0_jpg_0 = os.path.join(root_dir, t0, shutter, "f0.jpg")

    # Load reference JPG images
    img_n0 = cv2.imread(n0_jpg_0)
    img_f0 = cv2.imread(f0_jpg_0) if os.path.exists(f0_jpg_0) else None

    # Generate reference mask from JPEG images.
    mask0 = get_mask(img_n0, img_f0)

    # Process each time point using the reference mask
    for t in time_folders:

        # Build file paths
        n0_jpg = os.path.join(root_dir, t, shutter, "n0.jpg")
        f0_jpg = os.path.join(root_dir, t, shutter, "f0.jpg")
        n0_dng = os.path.join(root_dir, t, shutter, "n0.dng")
        f0_dng = os.path.join(root_dir, t, shutter, "f0.dng")

        # Skip if main image does not exist
        if not os.path.exists(n0_jpg):
            continue

        # Load images for mask computation
        img_n = cv2.imread(n0_jpg)
        img_f = cv2.imread(f0_jpg) if os.path.exists(f0_jpg) else None

        # Build mask for current time point
        mask_t = get_mask(img_n, img_f)

        if mask_t is None:
            continue

        # Build logical regions (inside, outside, full)
        inside, outside, full = build_region_masks(mask_t, mask0)

        # Compute RAW statistics for each region
        inside_stats  = raw_stats_with_mask(n0_dng, inside,  f0_dng)
        outside_stats = raw_stats_with_mask(n0_dng, outside, f0_dng)
        full_stats    = raw_stats_with_mask(n0_dng, full,    f0_dng)

        # Create row entry
        row = {
            "Time_min": float(t),         # Time in minutes
            "Shutter_us": int(shutter)    # Shutter speed in microseconds
        }

        # Append region statistics to row dictionary
        for k, v in inside_stats.items():
            row[f"inside_{k}"] = v
        for k, v in outside_stats.items():
            row[f"outside_{k}"] = v
        for k, v in full_stats.items():
            row[f"full_{k}"] = v

        rows.append(row)


# Sort and save results to CSV
df = pd.DataFrame(rows)

df = df.sort_values(["Shutter_us", "Time_min"])

out_csv = os.path.join(root_dir, "raw_stats.csv")
df.to_csv(out_csv, index=False)


print("Saved to:", out_csv)
