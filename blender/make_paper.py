# Paper sign texture: colorful "adversarial" squiggles + big DOG (Snowmoon ch. 30).
# Not a real adversarial patch - a hand-made visual stand-in. Deterministic via SEED.
# Usage: python make_paper.py  ->  tex/paper_dog.png
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 30
W, H = 1024, 640
OUT = os.path.join(os.path.dirname(__file__), "tex", "paper_dog.png")
FONT = r"C:\Windows\Fonts\arialbd.ttf"  # any heavy sans works
COLORS = [(214, 60, 52), (40, 110, 200), (242, 180, 30), (30, 150, 90), (140, 70, 170), (20, 20, 20)]

rnd = random.Random(SEED)
img = Image.new("RGB", (W, H), (238, 234, 222))
d = ImageDraw.Draw(img)

for _ in range(70):  # squiggles: random smooth polylines
    x, y = rnd.uniform(0, W), rnd.uniform(0, H)
    a, step = rnd.uniform(0, 2 * math.pi), rnd.uniform(6, 14)
    pts = []
    for _ in range(rnd.randint(12, 40)):
        a += rnd.uniform(-0.9, 0.9)
        x, y = x + math.cos(a) * step, y + math.sin(a) * step
        pts.append((x, y))
    d.line(pts, fill=rnd.choice(COLORS), width=rnd.randint(3, 9), joint="curve")

font = ImageFont.truetype(FONT, 330)
bx = d.textbbox((0, 0), "DOG", font=font)
tx, ty = (W - (bx[2] - bx[0])) // 2 - bx[0], (H - (bx[3] - bx[1])) // 2 - bx[1]
d.text((tx, ty), "DOG", font=font, fill=(16, 16, 16), stroke_width=10, stroke_fill=(238, 234, 222))

img = img.filter(ImageFilter.GaussianBlur(0.6))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT)
print("OK", OUT)
