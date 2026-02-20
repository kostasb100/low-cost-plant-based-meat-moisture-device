"""
Fixed-scale difference color map program for reflectance and transmittance water cell measurements (RAW format)

This program:
- Loads RAW(DNG format) water cell(with and without water) and noise images
- Subtracts noise from the water cell images (performs dark-mage correction)
- Computes the difference between different states of the water cell
- Plots these differences using color mapping, where red pixels indicate a decrease in
  light intensity, blue pixels indicate an increase in light intensity, and white pixels indicate no change

Purpose:
- Enables inspection and comparison of the effects (e.g., absorption) that different volumes of water in the cell have
  in reflectance and transmittance setups

Date: 2026-02
"""

import os
import numpy as np
import rawpy
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

root_dir = r"file_path" # Directory in which the images are saved in
main_folders = ["50000", "100000", "150000"] # Folders used, which were named based on the exposure times

# Read DNG images and convert their pixel values to float for subtraction
def read_dng_gray_float(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    with rawpy.imread(path) as raw:
        raw_img = raw.raw_image_visible.astype(np.float32)
    if raw_img.ndim == 3:
        raw_img = raw_img.mean(axis=2)
    return raw_img

# Perform dark-frame correction (illuminated image (w0) minus dark image (f0))
def corrected_image_dng(main_folder, vol_folder):
    inner_dir = os.path.join(root_dir, main_folder, vol_folder, main_folder)
    w_path = os.path.join(inner_dir, "w0.dng") # Path of the image of the cell with water
    f_path = os.path.join(inner_dir, "f0.dng") # Path of the noise image(non-illuminated image)

    w = read_dng_gray_float(w_path)
    f = read_dng_gray_float(f_path)

    return w - f

def compute_diff(main_folder):
    corr_0 = corrected_image_dng(main_folder, "0ml") # Image of the illuminated cell without water
    corr_48 = corrected_image_dng(main_folder, "48ml") # Image of the illuminated cell with 48 ml of water
    return corr_0 - corr_48  # 0ml - 48ml

# Determine fixed symmetric color scale using the highest exposure
diff_ref = compute_diff("150000") # Any other value can be set
max_abs_ref = float(np.max(np.abs(diff_ref)))
if max_abs_ref == 0:
    max_abs_ref = 1.0

# Same color scale for all images:
norm = TwoSlopeNorm(vmin=-max_abs_ref, vcenter=0.0, vmax=max_abs_ref)

# Generate difference plots using the same color scale
for mf in main_folders:
    diff = compute_diff(mf)

    plt.figure(figsize=(7, 5))

    # Use fixed symmetric color scale:
    # red = positive difference
    # blue = negative difference
    # white = no change
    im = plt.imshow(diff, cmap="bwr", norm=norm)
    plt.title(f"Exposure time {mf}[us]: (0ml (w-f)) - (48ml (w-f))")
    plt.axis("off")
    cbar = plt.colorbar(im)
    cbar.set_label("Raw-pixel Value Difference (a.u.)", fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    # Export plot to PNG
    out_png = os.path.join(root_dir, f"difference_map_{mf}.png")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()


    print(f"Difference plots saved in: {out_png}")

