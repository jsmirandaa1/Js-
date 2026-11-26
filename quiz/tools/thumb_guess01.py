"""Thumbnail colorida: GUESS 100 ANIMALS BY THEIR SHADOW"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brgfx import *
W, H = 1280, 720
im = starfield(W, H, 11).copy()
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 640) / W) ** 2 + ((yy - 200) / H) ** 2)
g = Image.new("RGBA", (W, H), (255, 180, 50, 0)); g.putalpha(Image.fromarray((np.clip(1 - r * 1.7, 0, 1) ** 2 * 110).astype(np.uint8))); im.alpha_composite(g)
paste_c(im, gold_text("GUESS 100 ANIMALS", F("anton", 128), stroke=3), W / 2, 105)
paste_c(im, text_img("BY THEIR SHADOW", F("anton", 74), fill=WHITE, stroke=5), W / 2, 215)
cards = [("lion", (80, 200, 120), False), ("panda", (240, 200, 60), True), ("elephant", (255, 140, 50), False), ("octopus", (240, 60, 70), True)]
for k, (e, col, sil) in enumerate(cards):
    x = 165 + k * 317; card = rrect((290, 380), 34, col + (255,), (255, 255, 255, 255), 6)
    em = Image.open(A + f"e_{e}_3d.png").convert("RGBA").resize((250, 250), Image.LANCZOS)
    if sil:
        s = Image.new("RGBA", em.size, (10, 10, 12, 255)); s.putalpha(em.getchannel("A")); em = s
    card.alpha_composite(em, (20, 50))
    if sil: ImageDraw.Draw(card).text((230, 70), "?", font=F("anton", 110), anchor="mm", fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
    paste_c(im, card.rotate((-4, 3, -3, 4)[k], resample=Image.BICUBIC, expand=True), x, 500)
ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=GOLD, width=10)
im.convert("RGB").save(sys.argv[1], quality=95)
