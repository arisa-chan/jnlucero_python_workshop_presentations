"""One-off script to generate examples/sample.png for the demo slide."""
import math
from PIL import Image, ImageDraw

W, H = 300, 150
img = Image.new("RGB", (W, H))

# Soft blue-grey gradient background
for y in range(H):
    for x in range(W):
        r = int(220 + 35 * x / W)
        g = int(225 + 20 * y / H)
        b = int(255 - 40 * x / W)
        img.putpixel((x, y), (r, g, b))

# Blue sine wave
for x in range(W):
    yv = int(H / 2 + (H / 3) * math.sin(x * 2 * math.pi / W))
    for dy in range(-2, 3):
        yy = yv + dy
        if 0 <= yy < H:
            img.putpixel((x, yy), (20, 80, 200))

# Header bar
draw = ImageDraw.Draw(img)
draw.rectangle([(0, 0), (W - 1, 22)], fill=(30, 100, 180))
draw.text((6, 5), "pyxel-slides sample image", fill=(255, 255, 255))

# Coloured boxes
colors = [(220, 50, 50), (50, 200, 50), (50, 50, 220), (220, 180, 30)]
for i, c in enumerate(colors):
    bx, by = 20 + i * 65, 90
    draw.rectangle([(bx, by), (bx + 45, by + 40)], fill=c, outline=(0, 0, 0))

img.save("examples/sample.png")
print("examples/sample.png written.")
