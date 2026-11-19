import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

D = os.path.dirname(os.path.abspath(__file__))
ANTON = f"{D}/../v/Anton.ttf"
def F(s): return ImageFont.truetype(ANTON, s)
PINK, CYAN, ORANGE, YEL, PURP = (255, 46, 160), (40, 230, 255), (255, 140, 40), (255, 222, 60), (120, 40, 200)

# ---------- person: stylized cutout ----------
cut = Image.open(f"{D}/cut_isnet-general-use.png").convert("RGBA")
rgb = np.array(cut.convert("RGB"))
sty = cv2.edgePreservingFilter(rgb[:, :, ::-1], flags=1, sigma_s=30, sigma_r=0.25)
sty = cv2.detailEnhance(sty, sigma_s=8, sigma_r=0.12)[:, :, ::-1]
p = Image.fromarray(sty).convert("RGB")
# punchier color: contrast + saturation + slight warm skin, cool shadows
from PIL import ImageEnhance
p = ImageEnhance.Contrast(p).enhance(1.15); p = ImageEnhance.Color(p).enhance(1.2); p = ImageEnhance.Brightness(p).enhance(1.08)
alpha = cut.split()[3]
# rim light: pink on left edge, cyan on right edge
a = np.array(alpha).astype(np.float32) / 255
er = cv2.erode(a, np.ones((25, 25), np.uint8)); rim = np.clip(a - er, 0, 1)
rim = cv2.GaussianBlur(rim, (0, 0), 6)
h, w = a.shape; xs = np.linspace(0, 1, w)[None, :]
col = (1 - xs)[..., None] * np.array(PINK) + xs[..., None] * np.array(CYAN)
pa = np.array(p).astype(np.float32)
pa = pa * (1 - 0.7 * rim[..., None]) + col * 0.7 * rim[..., None]
person = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8)).convert("RGBA"); person.putalpha(alpha)

def fade(img, bottom=(0.5, 0.9), side=0.12, **_):
    a = np.array(img.split()[3]).astype(np.float32)
    h, w = a.shape
    sm = lambda t: t * t * (3 - 2 * t)
    yv = sm(np.clip((np.linspace(0, 1, h) - bottom[0]) / (bottom[1] - bottom[0]), 0, 1))[:, None]
    xl = np.linspace(0, 1, w)
    xv = sm(np.clip(np.minimum(xl, 1 - xl) / side, 0, 1))[None, :]
    a = a * (1 - yv) * xv
    out = img.copy(); out.putalpha(Image.fromarray(a.astype(np.uint8))); return out

def sticker(img, stroke=22, glow=PINK, glow_r=40, stroke_end=(0.38, 0.6)):
    al = np.array(img.split()[3])
    pad = stroke + glow_r * 2
    W2, H2 = img.width + pad * 2, img.height + pad * 2
    big = np.zeros((H2, W2), np.uint8); big[pad:pad + img.height, pad:pad + img.width] = (al > 128) * 255
    st = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (stroke * 2 + 1, stroke * 2 + 1))).astype(np.float32)
    yr = (np.arange(H2) - pad) / img.height
    g = np.clip((stroke_end[1] - yr) / (stroke_end[1] - stroke_end[0]), 0, 1)[:, None]
    st = cv2.GaussianBlur(st * g, (0, 0), 1.5)
    stI = Image.fromarray(np.clip(st, 0, 255).astype(np.uint8))
    gl = stI.filter(ImageFilter.GaussianBlur(glow_r))
    base = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    base.paste(Image.new("RGBA", (W2, H2), glow + (255,)), (0, 0), gl.point(lambda v: min(255, int(v * 1.6))))
    base.paste(Image.new("RGBA", (W2, H2), (255, 255, 255, 255)), (0, 0), stI)
    base.alpha_composite(img, (pad, pad))
    return base, pad

# ---------- background ----------
def sunset_bg(W, H, sun=(0.5, 0.62), sun_r=0.28, grid=True, stars=True):
    y = np.linspace(0, 1, H)[:, None]
    stops = [(0, (14, 4, 40)), (0.45, (90, 20, 120)), (0.7, (230, 40, 130)), (0.85, (255, 120, 60)), (1, (255, 170, 70))]
    img = np.zeros((H, W, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = ((y >= p0) & (y <= p1)).astype(np.float32); u = np.clip((y - p0) / (p1 - p0), 0, 1)
        for c in range(3): img[:, :, c] += m[:, 0:1] * (c0[c] + (c1[c] - c0[c]) * u)
    bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(bg, "RGBA")
    if stars:
        rng = np.random.default_rng(3)
        for _ in range(int(W * H / 9000)):
            x, yy = rng.integers(0, W), rng.integers(0, int(H * 0.5)); r = rng.choice([1, 1, 2])
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, int(rng.integers(80, 220))))
    cx, cy, r = int(W * sun[0]), int(H * sun[1]), int(min(W, H) * sun_r)
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
    for yy in range(cy - r, cy + r):
        f = (yy - (cy - r)) / (2 * r); half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
        if yy > cy and (yy - cy) % max(8, r // 7) < 3 + (yy - cy) * 10 // r: continue
        sd.line([(cx - half, yy), (cx + half, yy)], fill=(255, int(235 - 130 * f), int(110 - 60 * f), 235))
    glow = s.filter(ImageFilter.GaussianBlur(r * 0.25)); bg.alpha_composite(glow); bg.alpha_composite(s)
    if grid:
        hz = int(H * 0.8); g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.rectangle([0, hz, W, H], fill=(25, 5, 45, 255))
        for k in range(-30, 31):
            gd.line([(W / 2 + k * W / 60, hz), (W / 2 + k * W / 10, H)], fill=PINK + (200,), width=max(2, W // 800))
        yy, step = hz, max(4, H // 120)
        while yy < H:
            gd.line([(0, yy), (W, yy)], fill=PINK + (200,), width=max(2, W // 800)); step *= 1.3; yy += int(step)
        gl = g.filter(ImageFilter.GaussianBlur(3)); bg.alpha_composite(gl); bg.alpha_composite(g)
    return bg

def palm(d, x, y, s, col=(10, 2, 25, 255)):
    pts = [(x + math.sin(t / 20) * s * 0.15 + t * s * 0.004, y - t * s / 100) for t in range(0, 100, 5)]
    d.line(pts, fill=col, width=max(3, int(s * 0.035)))
    tx, ty = pts[-1]
    for ang in range(0, 360, 40):
        a = math.radians(ang); L = s * 0.45
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.55 + L * 0.25
        mx, my = tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.3 - L * 0.08
        d.line([(tx, ty), (mx, my), (ex, ey)], fill=col, width=max(3, int(s * 0.05)), joint="curve")

def neon_text(canvas, xy, text, size, fill, glow, anchor="lm", stroke=0, blur=None):
    blur = blur or size // 8
    g = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text(xy, text, font=F(size), fill=glow + (255,), anchor=anchor, stroke_width=max(4, size // 18), stroke_fill=glow + (255,))
    canvas.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur))); canvas.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur // 3)))
    ImageDraw.Draw(canvas).text(xy, text, font=F(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(20, 0, 40))

def logo(canvas, x, y, size, anchor="l"):
    """JHON (white/cyan glow) + LIVES (pink neon) on one line, italic-ish via shear."""
    tmp = Image.new("RGBA", (int(size * 5.2), int(size * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp); f = F(size)
    w1 = d.textlength("JHON", font=f); gap = size * 0.12
    neon_text(tmp, (size * 0.2, size * 0.8), "JHON", size, (255, 255, 255), CYAN, "lm")
    neon_text(tmp, (size * 0.2 + w1 + gap, size * 0.8), "LIVES", size, (255, 235, 250), PINK, "lm")
    tmp = tmp.crop(tmp.getbbox())
    sh = 0.18; tmp = tmp.transform((int(tmp.width + tmp.height * sh), tmp.height), Image.AFFINE, (1, sh, -tmp.height * sh, 0, 1, 0), Image.BICUBIC)
    ox = x if anchor == "l" else x - tmp.width // 2
    canvas.alpha_composite(tmp, (int(ox), int(y - tmp.height / 2)))
    return tmp.size

ICON = {"YOUTUBE": (255, 40, 40), "TWITCH": (150, 80, 255), "TIKTOK": (40, 230, 255)}
def handle_chip(canvas, x, y, plat, handle, size):
    d = ImageDraw.Draw(canvas, "RGBA"); f1, f2 = F(int(size * 0.62)), F(size)
    w = d.textlength(plat, font=f1) + d.textlength(handle, font=f2) + size * 1.6
    hgt = size * 1.55
    d.rounded_rectangle([x, y, x + w, y + hgt], radius=hgt / 2, fill=(10, 0, 30, 200), outline=ICON[plat] + (255,), width=max(3, size // 12))
    d.text((x + size * 0.6, y + hgt / 2), plat, font=f1, fill=ICON[plat], anchor="lm")
    d.text((x + size * 0.6 + d.textlength(plat, font=f1) + size * 0.4, y + hgt / 2), handle, font=f2, fill=(255, 255, 255), anchor="lm")
    return w

# person crops
bb = person.getbbox()
head_box = (380, 780, 1320, 2346)   # head + shoulders (full-res coords)

os.makedirs(f"{D}/out", exist_ok=True)

# ---------- 1. PROFILE 1080x1080 ----------
S = 1080
pf = sunset_bg(S, S, sun=(0.5, 0.58), sun_r=0.36, grid=False)
crop = fade(person.crop((300, 700, 1320, 2346)), bottom=(0.6, 0.98), side=0.16)
sc = 1180 / crop.height; crop = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
st, pad = sticker(crop, stroke=14, glow=CYAN, glow_r=30, stroke_end=(0.36, 0.56))
pf.alpha_composite(st, (int(S / 2 - (pad + 790 * sc - 300 * sc)) , int(170 - pad)))
ring = Image.new("RGBA", (S, S), (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
rd.ellipse([18, 18, S - 18, S - 18], outline=PINK + (255,), width=16)
pf.alpha_composite(ring.filter(ImageFilter.GaussianBlur(10))); pf.alpha_composite(ring)
pf.convert("RGB").save(f"{D}/out/perfil_1080.png")
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S, S], fill=255)
pc = pf.copy(); pc.putalpha(m); pc.save(f"{D}/out/perfil_preview_circular.png")

# ---------- 2. YOUTUBE 2560x1440 (safe area 1546x423 centered) ----------
W, H = 2560, 1440
yt = sunset_bg(W, H, sun=(0.66, 0.53), sun_r=0.17)
sx0, sy0, sx1, sy1 = (W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2
crop = fade(person.crop((330, 740, 1320, 1900)), bottom=(0.55, 0.92)); sc = 0.5
crop = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
st, pad = sticker(crop, stroke=12, glow=PINK, glow_r=26)
px = int(sx1 - 230 - (pad + 460 * sc)); py = int(sy0 + 30 - pad - 40 * sc)
yt.alpha_composite(st, (px, py))
lw, lh = logo(yt, sx0 + 10, sy0 + 105, 190)
neon_text(yt, (sx0 + 40, sy0 + 262), "GTA 6  •  ZOEIRA  •  GAMEPLAY", 64, YEL, ORANGE, "lm")
x = sx0 + 40; y = sy0 + 320
for plat, hd in [("YOUTUBE", "@jhonlivesx"), ("TWITCH", "@jhonlivesx"), ("TIKTOK", "@jhonexlives")]:
    x += handle_chip(yt, x, y, plat, hd, 44) + 22
yt.convert("RGB").save(f"{D}/out/capa_youtube_2560x1440.png")
# preview with safe-area guides
pv = yt.copy(); dd = ImageDraw.Draw(pv)
dd.rectangle([sx0, sy0, sx1, sy1], outline=(0, 255, 0), width=6)
dd.rectangle([(W - 2560) // 2, (H - 423) // 2, (W + 2560) // 2, (H + 423) // 2], outline=(255, 255, 0), width=4)
pv.convert("RGB").resize((1280, 720)).save(f"{D}/out/guia_youtube_areas.jpg", quality=85)

# ---------- 3. TWITCH 1200x480 ----------
W, H = 1200, 480
tw = sunset_bg(W, H, sun=(0.72, 0.62), sun_r=0.42)
crop = fade(person.crop((330, 700, 1320, 2050))); sc = 560 / crop.height
crop = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
st, pad = sticker(crop, stroke=9, glow=PINK, glow_r=18)
tw.alpha_composite(st, (W - st.width + pad - 30, H - st.height + pad + 90))
logo(tw, 60, 175, 120)
neon_text(tw, (75, 285), "GTA 6  •  ZOEIRA  •  GAMEPLAY", 40, YEL, ORANGE, "lm")
x = 75
for plat, hd in [("YOUTUBE", "@jhonlivesx"), ("TIKTOK", "@jhonexlives")]:
    x += handle_chip(tw, x, 340, plat, hd, 30) + 16
tw.convert("RGB").save(f"{D}/out/capa_twitch_1200x480.png")
print("ok")
