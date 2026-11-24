"""Thumbnail do vídeo 02 (1280x720): ONLY GENIUSES GET 15/15!"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brgfx import *
from planets import sphere
W, H = 1280, 720
im = starfield(W, H, 5).copy()
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 640) / W) ** 2 + ((yy - 380) / H) ** 2)
g = Image.new("RGBA", (W, H), (255, 180, 50, 0)); g.putalpha(Image.fromarray((np.clip(1 - r * 1.8, 0, 1) ** 2 * 110).astype(np.uint8))); im.alpha_composite(g)
n = sphere("neptunemap.jpg", 300, lon0=30, atmo=(0.2, 0.4, 1.0)); paste_c(im, halo(n, 30, (60, 110, 255), 0.6), 1120, 170); paste_c(im, n, 1120, 170)
paste_c(im, halo(emoji("dna", 256), 30, (120, 200, 255), 0.5), 140, 170); paste_c(im, emoji("dna", 256), 140, 170, scale=0.9)
paste_c(im, emoji("brain", 256), 170, 560, scale=1.0); paste_c(im, emoji("atom_symbol", 256), 1110, 560, scale=0.75)
paste_c(im, emoji("lizard", 256), 1060, 600, scale=0.0001)
paste_c(im, text_img("ONLY", F("anton", 110), fill=WHITE, stroke=6), 640, 105)
paste_c(im, gold_text("GENIUSES", F("anton", 190), stroke=3), 640, 290)
paste_c(im, text_img("GET 15/15!", F("anton", 150), fill=WHITE, stroke=8), 640, 520)
ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=GOLD, width=10)
im.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/br02/thumb.jpg", quality=95)
