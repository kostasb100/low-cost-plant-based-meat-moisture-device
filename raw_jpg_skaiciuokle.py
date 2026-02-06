import os
import cv2
import rawpy
import numpy as np
import pandas as pd

# Edge and shrinkage detection parameters
GAUSSIAN_KERNEL = (3, 3)
SIGMA = 0
THRESH_VALUE = 45
THRESH_MAX = 255
EDGE_KERNEL = (3, 3)
AREA_MIN = 147762
AREA_MAX = 9000000
BLACK_LEVEL = 64

ROOT_DIR = r"C:\Users\kbalc\Desktop\uni\bachelor_project\measurements\12.22-12.25\12-24\eksperimentas"

def get_mask(img, noise):
    if noise is not None:
        img = cv2.subtract(img, noise)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, GAUSSIAN_KERNEL, SIGMA)

    _, thresh = cv2.threshold(gray, THRESH_VALUE, THRESH_MAX, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, EDGE_KERNEL)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    valid = [c for c in contours if AREA_MIN < cv2.contourArea(c) < AREA_MAX]

    if not valid:
        return None

    contour = max(valid, key=cv2.contourArea)
    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    return mask.astype(bool)

def build_region_masks(mask_t, mask0):
    shrinkage = mask0 & (~mask_t)
    inside = mask_t
    outside = (~mask0) & (~shrinkage)
    full = (~shrinkage)
    return inside, outside, full

def raw_stats_with_mask(dng_path, mask, noise_path=None):
    with rawpy.imread(dng_path) as raw:
        img = raw.raw_image_visible.astype(np.float32)

    img -= BLACK_LEVEL
    img = np.clip(img, 0, None)

    if noise_path and os.path.exists(noise_path):
        with rawpy.imread(noise_path) as raw_f:
            noise = raw_f.raw_image_visible.astype(np.float32)
        noise -= BLACK_LEVEL
        img = np.clip(img - noise, 0, None)

    assert img.shape == mask.shape, "RAW/JPG size mismatch"

    h, w = img.shape

    R  = img[0:h:2, 0:w:2][mask[0:h:2, 0:w:2]]
    G1 = img[0:h:2, 1:w:2][mask[0:h:2, 1:w:2]]
    G2 = img[1:h:2, 0:w:2][mask[1:h:2, 0:w:2]]
    B  = img[1:h:2, 1:w:2][mask[1:h:2, 1:w:2]]

    return {
        "mean_raw": img[mask].mean(),
        "R_mean": R.mean(),
        "G1_mean": G1.mean(),
        "G2_mean": G2.mean(),
        "G_mean": np.mean([G1.mean(), G2.mean()]),
        "B_mean": B.mean()
    }

time_folders = sorted(
    [f for f in os.listdir(ROOT_DIR)
     if os.path.isdir(os.path.join(ROOT_DIR, f)) and f.replace('.', '', 1).isdigit()],
    key=lambda x: float(x)
)

shutters = sorted(
    {s for t in time_folders
     for s in os.listdir(os.path.join(ROOT_DIR, t))
     if os.path.isdir(os.path.join(ROOT_DIR, t, s)) and s.isdigit()},
    key=int
)

rows = []

# for shutter in shutters:
#     print(f"\nProcessing shutter {shutter}")
#     mask0 = None
#
#     # Mask
#     for t in time_folders:
#         n0_jpg = os.path.join(ROOT_DIR, t, shutter, "n0.jpg")
#         f0_jpg = os.path.join(ROOT_DIR, t, shutter, "f0.jpg")
#
#         if os.path.exists(n0_jpg):
#             img_n = cv2.imread(n0_jpg)
#             img_f = cv2.imread(f0_jpg)
#             mask0 = get_mask(img_n, img_f)
#
#     for t in time_folders:
#         n0_jpg = os.path.join(ROOT_DIR, t, shutter, "n0.jpg")
#         f0_jpg = os.path.join(ROOT_DIR, t, shutter, "f0.jpg")
#         n0_dng = os.path.join(ROOT_DIR, t, shutter, "n0.dng")
#         f0_dng = os.path.join(ROOT_DIR, t, shutter, "f0.dng")
#
#         img_n = cv2.imread(n0_jpg)
#         img_f = cv2.imread(f0_jpg) if os.path.exists(f0_jpg) else None
#         mask_t = get_mask(img_n, img_f)
#
#         inside, outside, full = build_region_masks(mask_t, mask0)
#
#         inside_stats = raw_stats_with_mask(n0_dng, inside,  f0_dng)
#         outside_stats = raw_stats_with_mask(n0_dng, outside, f0_dng)
#         full_stats = raw_stats_with_mask(n0_dng, full,    f0_dng)
#
#         row = {
#             "Time_min": float(t),
#             "Shutter_us": int(shutter)
#         }
#
#         for k, v in inside_stats.items():
#             row[f"inside_{k}"] = v
#         for k, v in outside_stats.items():
#             row[f"outside_{k}"] = v
#         for k, v in full_stats.items():
#             row[f"full_{k}"] = v
#
#         rows.append(row)


for shutter in shutters:
    print(f"\nProcessing shutter {shutter}")

    # --- 1. Build reference mask from the first time point ---
    t0 = time_folders[0]

    n0_jpg_0 = os.path.join(ROOT_DIR, t0, shutter, "n0.jpg")
    f0_jpg_0 = os.path.join(ROOT_DIR, t0, shutter, "f0.jpg")

    if not os.path.exists(n0_jpg_0):
        print(f"Skipping shutter {shutter}: no reference image")
        continue

    img_n0 = cv2.imread(n0_jpg_0)
    img_f0 = cv2.imread(f0_jpg_0) if os.path.exists(f0_jpg_0) else None
    mask0 = get_mask(img_n0, img_f0)

    if mask0 is None:
        print(f"Skipping shutter {shutter}: reference mask not found")
        continue

    # --- 2. Process each time point using the reference mask ---
    for t in time_folders:
        n0_jpg = os.path.join(ROOT_DIR, t, shutter, "n0.jpg")
        f0_jpg = os.path.join(ROOT_DIR, t, shutter, "f0.jpg")
        n0_dng = os.path.join(ROOT_DIR, t, shutter, "n0.dng")
        f0_dng = os.path.join(ROOT_DIR, t, shutter, "f0.dng")

        if not os.path.exists(n0_jpg):
            continue

        img_n = cv2.imread(n0_jpg)
        img_f = cv2.imread(f0_jpg) if os.path.exists(f0_jpg) else None
        mask_t = get_mask(img_n, img_f)

        if mask_t is None:
            continue

        inside, outside, full = build_region_masks(mask_t, mask0)

        inside_stats  = raw_stats_with_mask(n0_dng, inside,  f0_dng)
        outside_stats = raw_stats_with_mask(n0_dng, outside, f0_dng)
        full_stats    = raw_stats_with_mask(n0_dng, full,    f0_dng)

        row = {
            "Time_min": float(t),
            "Shutter_us": int(shutter)
        }

        for k, v in inside_stats.items():
            row[f"inside_{k}"] = v
        for k, v in outside_stats.items():
            row[f"outside_{k}"] = v
        for k, v in full_stats.items():
            row[f"full_{k}"] = v

        rows.append(row)

df = pd.DataFrame(rows)
df = df.sort_values(["Shutter_us", "Time_min"])

out_csv = os.path.join(ROOT_DIR, "raw_stats_with_shrinkage(new)_45.csv")
df.to_csv(out_csv, index=False)

print("Saved to:", out_csv)
