"""Thumbnail do vídeo 03 (1280x720): CAN YOU SCORE 30/30?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brgfx import *
from planets import sphere
from build_brainrush01 import pill
W, H = 1280, 720
im = starfield(W, H, 5).copy()
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 640) / W) ** 2 + ((yy - 380) / H) ** 2)
g = Image.new("RGBA", (W, H), (255, 180, 50, 0)); g.putalpha(Image.fromarray((np.clip(1 - r * 1.8, 0, 1) ** 2 * 110).astype(np.uint8))); im.alpha_composite(g)
n = sphere("saturn.jpg", 1, lon0=0); n = Image.new("RGBA", (2, 2)); paste_c(im, halo(emoji("brain", 256), 40, (255, 150, 180), 0.5), 1160, 120); paste_c(im, emoji("brain", 256), 1160, 120, scale=0.72)
paste_c(im, halo(emoji("dna", 256), 30, (120, 200, 255), 0.5), 140, 170); paste_c(im, emoji("dna", 256), 140, 170, scale=0.9)
paste_c(im, emoji("stopwatch", 256), 170, 560, scale=0.95); paste_c(im, emoji("trophy", 256), 1110, 560, scale=0.85)
paste_c(im, emoji("lizard", 256), 1060, 600, scale=0.0001)
paste_c(im, text_img("CAN YOU SCORE", F("anton", 110), fill=WHITE, stroke=6), 640, 105)
paste_c(im, gold_text("30/30?", F("anton", 300), stroke=3), 640, 330)
paste_c(im, text_img("30 QUESTIONS • 7 SECONDS EACH", F("anton", 60), fill=GOLD_L, stroke=4), 640, 610)
ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=GOLD, width=10)
im.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/br03/thumb.jpg", quality=95)
