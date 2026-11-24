"""Thumbnail do vídeo 01 (1280x720): ONLY 1% GET 15/15!"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brgfx import *
from planets import sphere, saturn
W, H = 1280, 720
im = starfield(W, H, 3).copy()
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 380) / W) ** 2 + ((yy - 360) / H) ** 2)
glow = Image.fromarray((np.clip(1 - r * 1.8, 0, 1) ** 2 * 120).astype(np.uint8)); g = Image.new("RGBA", (W, H), (255, 180, 50, 0)); g.putalpha(glow); im.alpha_composite(g)
m = sphere("mars.jpg", 300, lon0=40, atmo=(0.6, 0.25, 0.1)); paste_c(im, halo(m, 30, (255, 120, 60), 0.4), 1090, 150); paste_c(im, m, 1090, 150)
s = saturn(260); paste_c(im, s.resize((s.width // 2 * 2 // 2, s.height // 2)), 1080, 610)
br = emoji("brain", 256); paste_c(im, halo(br, 40, (255, 150, 180), 0.5), 250, 470); paste_c(im, br, 250, 470, scale=1.35)
paste_c(im, emoji("high_voltage", 256), 120, 330, scale=0.55)
t1 = text_img("ONLY", F("anton", 120), fill=WHITE, stroke=6); paste_c(im, t1, 560, 120)
t2 = gold_text("1%", F("anton", 300), stroke=4); paste_c(im, t2, 650, 330)
t3 = text_img("GET 15/15!", F("anton", 150), fill=WHITE, stroke=8); paste_c(im, t3, 690, 590)
d = ImageDraw.Draw(im); d.rectangle((0, 0, W - 1, H - 1), outline=GOLD, width=10)
im.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/br01/thumb.jpg", quality=95)
