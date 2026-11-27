"""Thumbnail colorida: GUESS 100 FLAGS"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brgfx import *
W, H = 1280, 720
im = starfield(W, H, 13).copy()
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 640) / W) ** 2 + ((yy - 200) / H) ** 2)
g = Image.new("RGBA", (W, H), (255, 180, 50, 0)); g.putalpha(Image.fromarray((np.clip(1 - r * 1.7, 0, 1) ** 2 * 110).astype(np.uint8))); im.alpha_composite(g)
paste_c(im, gold_text("GUESS 100 FLAGS", F("anton", 140), stroke=3), W / 2, 110)
paste_c(im, text_img("EASY → IMPOSSIBLE".replace("→", "TO"), F("anton", 70), fill=WHITE, stroke=5), W / 2, 225)
codes = [("br", 0), ("jp", 0), ("td", 1), ("ro", 1)]
for k, (c, q) in enumerate(codes):
    fl = Image.open(A + f"flags/{c}.png").convert("RGBA").resize((270, 202), Image.LANCZOS); fl.putalpha(rrect((270, 202), 18, (255, 255, 255, 255)).getchannel("A"))
    card = rrect((300, 232), 26, (255, 255, 255, 255)); card.alpha_composite(fl, (15, 15))
    if q: ImageDraw.Draw(card).text((150, 116), "?", font=F("anton", 150), anchor="mm", fill=WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
    paste_c(im, card.rotate((-5, 4, -3, 5)[k], resample=Image.BICUBIC, expand=True), 170 + k * 313, 500)
paste_c(im, text_img("CHAD OR ROMANIA?", F("anton", 54), fill=(255, 230, 120), stroke=4), 960, 665)
ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=GOLD, width=10)
im.convert("RGB").save(sys.argv[1], quality=95)
