"""
GIF generator program

This program:
- Reads .jpg images from a folder
- Sorts the images by filename
- Combines them into a GIF

Purpose:
- Allows visual inspection of time-dependent changes in a plant-based sample
  without manually browsing individual images
- Applicable to LED-illuminated images, NIR-illuminated images,
  and blue/red mapped (contrast-enhanced) images

Date: 2026-02
"""


from PIL import Image, ImageDraw, ImageFont
import glob
import os

# Image(.jpg) file path (change to desired directory)
root_dir = r"C:\Users\folder_with_images"

# Image(.jpg) sort
img_files = sorted(
    glob.glob(os.path.join(root_dir, "*.jpg")),
    key=lambda x: float(os.path.basename(x).split("_")[0])
)

frames = []

# Time stamp font
font_path = "arial.ttf"
font_size = 150
font = ImageFont.truetype(font_path, font_size)

# Time stamps for every frame
for f in img_files:
    img = Image.open(f).convert("RGB")
    draw = ImageDraw.Draw(img)

    time_value = float(os.path.basename(f).split("_")[0])
    time_text = f"t = {int(time_value)} [min]"

    # Location of the time stamps inside of the image
    x = 3650
    y = 2300

    draw.text((x, y), time_text, fill="white", font=font)
    frames.append(img)

# Save as GIF
gif_path = os.path.join(root_dir, "gif_name.gif")
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=400,  # [ms] per frame (0.4 s)
    loop=0
)

print(f"GIF saved as: {gif_path}")