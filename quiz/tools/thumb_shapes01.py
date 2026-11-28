"""Thumbnail: GUESS 100 COUNTRIES BY THEIR SHAPE"""
import sys, os
sys.argv = [sys.argv[0], "shapes01"] + sys.argv[1:]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_guess as G
from brgfx import *
W, H = 1280, 720
im = starfield(W, H, 17).copy()
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 640) / W) ** 2 + ((yy - 200) / H) ** 2)
g = Image.new("RGBA", (W, H), (255, 180, 50, 0)); g.putalpha(Image.fromarray((np.clip(1 - r * 1.7, 0, 1) ** 2 * 110).astype(np.uint8))); im.alpha_composite(g)
paste_c(im, gold_text("GUESS 100 COUNTRIES", F("anton", 112), stroke=3), W / 2, 100)
paste_c(im, text_img("BY THEIR SHAPE", F("anton", 72), fill=WHITE, stroke=5), W / 2, 205)
cards = [("380|it", (80, 200, 120), False), ("036|au", (240, 200, 60), True), ("076|br", (255, 140, 50), False), ("392|jp", (240, 60, 70), True)]
for k, (key, col, sil) in enumerate(cards):
    card = rrect((290, 380), 34, col + (255,), (255, 255, 255, 255), 6)
    c = G.country_img(key, 250, sil); card.alpha_composite(c, ((290 - c.width) // 2, (380 - c.height) // 2))
    if sil: ImageDraw.Draw(card).text((235, 60), "?", font=F("anton", 110), anchor="mm", fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
    paste_c(im, card.rotate((-4, 3, -3, 4)[k], resample=Image.BICUBIC, expand=True), 165 + k * 317, 500)
ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=GOLD, width=10)
im.convert("RGB").save(sys.argv[2], quality=95)
