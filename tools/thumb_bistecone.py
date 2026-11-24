import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
D = sys.argv[1]
ANTON = f"{D}/../v/Anton.ttf"; EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H = 1280, 720; YEL = (255, 212, 0)
def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMO, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def outlined(img, w=10, col=(255, 255, 255), glow=YEL, gw=28):
    a = img.getchannel("A"); pad = w + gw * 2
    big = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    A = Image.new("L", big.size, 0); A.paste(a, (pad, pad))
    st = A.filter(ImageFilter.MaxFilter(2 * w + 1))
    gl = st.filter(ImageFilter.GaussianBlur(gw)).point(lambda v: min(255, v * 2))
    big.paste(Image.new("RGBA", big.size, glow + (255,)), (0, 0), gl)
    big.paste(Image.new("RGBA", big.size, col + (255,)), (0, 0), st)
    big.alpha_composite(img, (pad, pad)); return big, pad
def text(d, xy, s, size, fill, stroke=12, anchor="la"):
    x, y = xy
    d.text((x + 7, y + 9), s, font=F(size), fill=(0, 0, 0, 200), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    d.text((x, y), s, font=F(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
def rays(size, c, col, n=16):
    L = Image.new("L", size, 0); d = ImageDraw.Draw(L)
    for k in range(n):
        a = np.deg2rad(k * 360 / n)
        d.polygon([c, (c[0] + 2000 * np.cos(a - .07), c[1] + 2000 * np.sin(a - .07)), (c[0] + 2000 * np.cos(a + .07), c[1] + 2000 * np.sin(a + .07))], fill=90)
    return L.filter(ImageFilter.GaussianBlur(6))
def face(h):
    c = Image.open(f"{D}/th2/cut4.png"); s = h / c.height
    c = c.resize((int(c.width * s), h), Image.LANCZOS)
    c = ImageEnhance.Contrast(c).enhance(1.12); c = ImageEnhance.Color(c).enhance(1.15); c = ImageEnhance.Sharpness(c).enhance(1.6)
    return c

def gold_bg():
    bg = Image.new("RGB", (W, H), (40, 22, 0))
    g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse([700, -150, 1500, 650], fill=255); g = g.filter(ImageFilter.GaussianBlur(170))
    bg.paste((255, 170, 20), (0, 0), g)
    bg.paste((255, 220, 90), (0, 0), rays((W, H), (930, 260), None))
    return bg

# ---------- A: DO CAMINHÃO AO TOPO ----------
bg = gold_bg()
left = Image.open(f"{D}/th2/bg_crates.png").convert("RGB").crop((380, 180, 1180, 630)).resize((W, H)).filter(ImageFilter.GaussianBlur(3))
left = ImageEnhance.Color(left).enhance(0.15); left = ImageEnhance.Brightness(left).enhance(0.55)
left = Image.blend(left, Image.new("RGB", (W, H), (10, 25, 60)), 0.45)
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0), (560, 0), (430, H), (0, H)], fill=255)
bg.paste(left, (0, 0), mask)
d = ImageDraw.Draw(bg); d.line([(560, 0), (430, H)], fill=YEL, width=14)
im = bg.convert("RGBA")
fc = face(700); f, pad = outlined(fc); fx, fy = 1270 - fc.width, 30; im.alpha_composite(f, (fx - pad, fy - pad))
tro = emoji("🏆", 240); im.alpha_composite(tro, (fx + 5, fy + int(fc.height * 0.56)))
tr = ImageOps.grayscale(emoji("🚚", 250).convert("RGB")).convert("RGBA"); tr.putalpha(emoji("🚚", 250).getchannel("A"))
im.alpha_composite(tr, (60, 430))
d = ImageDraw.Draw(im)
# red arrow from truck to face
pts = [(330, 560), (420, 520), (500, 500)]
d.line(pts, fill=(235, 30, 30), width=24, joint="curve")
d.polygon([(560, 490), (490, 455), (500, 545)], fill=(235, 30, 30))
text(d, (40, 30), "DO CAMINHÃO", 108, (255, 255, 255))
text(d, (40, 150), "AO TOPO", 170, YEL, stroke=14)
im.convert("RGB").save(f"{D}/thumb_A.jpg", quality=95)

# ---------- B: 5 MILHÕES ----------
bg = Image.open(f"{D}/th2/bg_day.png").convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(6))
bg = ImageEnhance.Brightness(bg).enhance(0.6)
bg = Image.blend(bg, gold_bg(), 0.55)
im = bg.convert("RGBA")
fc = face(720); f, pad = outlined(fc); fx, fy = 1275 - fc.width, 20; im.alpha_composite(f, (fx - pad, fy - pad))
d = ImageDraw.Draw(im)
d.rounded_rectangle([36, 40, 560, 140], 18, fill=(230, 25, 35))
d.text((298, 90), "EX-DESCARREGADOR", font=F(64), fill=(255, 255, 255), anchor="mm")
text(d, (40, 165), "5", 330, YEL, stroke=16)
text(d, (245, 200), "MILHÕES", 140, (255, 255, 255))
text(d, (250, 360), "DE INSCRITOS", 70, YEL, stroke=8)
up = emoji("📈", 150); im.alpha_composite(up, (260, 480))
tro = emoji("🏆", 230); im.alpha_composite(tro, (fx + 5, fy + int(fc.height * 0.6)))
im.convert("RGB").save(f"{D}/thumb_B.jpg", quality=95)
