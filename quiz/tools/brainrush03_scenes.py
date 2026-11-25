# Cenas do vídeo 03 (30 perguntas). Executado no namespace do build_brainrush01.py.
# Reaproveita as cenas dos vídeos 01 (V1_*) e 02 (V2_*) nas perguntas repetidas.
V1_ASK, V1_EXP = stage_ask, stage_exp
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "brainrush02_scenes.py")).read(), globals())
V2_ASK, V2_EXP = stage_ask, stage_exp
CITIES = [("SYDNEY", 151.2, -33.87), ("MELBOURNE", 144.96, -37.81), ("BRISBANE", 153.03, -27.47), ("CANBERRA", 149.13, -35.28)]

@functools.lru_cache(None)
def _map(name, hi=None):
    boxes = {"asia": (60, 150, 5, 56), "europe": (-12, 36, 34, 60), "world": (-170, 190, -58, 80), "africa": (-22, 62, -38, 40)}
    b = boxes[name]; w = 1100; h = int(w * (b[3] - b[2]) / (b[1] - b[0]))
    if name == "world": h = 520
    return map_img(*b, w, h, hi=set(hi) if hi else None, sea=(8, 16, 30), land=(52, 50, 56), edge=(130, 108, 60)), b

@functools.lru_cache(None)
def _sahara():
    base, b = _map("africa"); im = base.copy(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    x0, y0 = lonlat_px(-16, 33, *b, *im.size); x1, y1 = lonlat_px(34, 15, *b, *im.size)
    d.ellipse((x0, y0, x1, y1), fill=(240, 190, 80, 150)); im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(25))); return im

def _gauge(im, cx, cy, r, frac, ticks, unit):
    d = ImageDraw.Draw(im)
    d.arc((cx - r, cy - r, cx + r, cy + r), 150, 390, fill=(70, 62, 44), width=18)
    d.arc((cx - r, cy - r, cx + r, cy + r), 150, 150 + 240 * frac, fill=GOLD, width=18)
    for k, tk in enumerate(ticks):
        a = math.radians(150 + 240 * k / (len(ticks) - 1)); d.text((cx + (r - 45) * math.cos(a), cy + (r - 45) * math.sin(a)), str(tk), font=F("mont", 22), anchor="mm", fill=(200, 200, 200))
    a = math.radians(150 + 240 * frac); d.line((cx, cy, cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a)), fill=GOLD_L, width=8)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=GOLD_L); d.text((cx, cy + r * 0.5), unit, font=F("bebas", 34), anchor="mm", fill=(200, 200, 200))

def _floating_nums(nums, tl, seed=5):
    im = Image.new("RGBA", (SW, SH), (8, 7, 6, 255))
    for k, n in enumerate(nums): paste_c(im, gold_text_cached(n, 130, 1.0), SW * (0.2 + 0.6 * k / max(1, len(nums) - 1)), SH / 2 + 20 * math.sin(tl * 1.2 + k))
    return im

def _bars(im, items, te, horizontal=True, unit=""):
    d = ImageDraw.Draw(im); n = len(items); mx = max(v for _, v, _ in items)
    for k, (nm, v, lab) in enumerate(items):
        p = eout((te - 0.3 - k * 0.35) / 0.8)
        if p <= 0: continue
        col = GOLD if k == 0 else (120, 130, 150)
        if horizontal:
            y = 70 + k * (SH - 120) / n; L = (SW - 420) * v / mx * p
            d.rounded_rectangle((300, y - 22, 300 + L, y + 22), 20, fill=col); label(im, nm, 150, y, 28, GOLD_L if k == 0 else WHITE)
        else:
            x = SW * (k + 0.5) / n; Hh = (SH - 150) * v / mx * p
            d.rounded_rectangle((x - 70, SH - 60 - Hh, x + 70, SH - 60), 14, fill=col); label(im, nm, x, SH - 30, 24, GOLD_L if k == 0 else WHITE)
            if p >= 1 and lab: label(im, lab, x, SH - 85 - Hh, 26, WHITE)

def _helix(te):
    im = Image.new("RGBA", (SW * 2, SH * 2), (8, 7, 10, 255)); d = ImageDraw.Draw(im); pts1, pts2 = [], []
    for x in range(0, SW * 2, 8):
        a = x / 110 + te * 2.2; y1 = SH + 230 * math.sin(a); y2 = SH + 230 * math.sin(a + math.pi); pts1.append((x, y1)); pts2.append((x, y2))
        if x % 48 == 0: d.line((x, y1, x, y2), fill=(150, 130, 90), width=6)
    d.line(pts1, fill=GOLD_L, width=16); d.line(pts2, fill=(235, 235, 240), width=16)
    return im.resize((SW, SH), Image.LANCZOS)

@functools.lru_cache(None)
def _mountains():
    im = grad(SW + 200, SH + 80, (30, 40, 70), (200, 140, 100)).convert("RGBA"); d = ImageDraw.Draw(im); W_ = SW + 200; H_ = SH + 80
    for k, (col, base, peaks) in enumerate([((70, 70, 95), 0.75, [(0.15, 0.35), (0.45, 0.2), (0.75, 0.4)]), ((40, 40, 60), 0.95, [(0.3, 0.45), (0.62, 0.3), (0.9, 0.5)])]):
        pts = [(0, H_ * base)] + [(W_ * x, H_ * y) for x, y in peaks] + [(W_, H_ * base), (W_, H_), (0, H_)]
        d.polygon(pts, fill=col)
        for x, y in peaks: d.polygon([(W_ * x, H_ * y), (W_ * x - 40, H_ * y + 50), (W_ * x + 40, H_ * y + 50)], fill=(240, 240, 250))
    return im

def stage_ask(qi, tl):
    if qi == 0: return V1_ASK(1, tl)
    if qi == 1: return V1_ASK(4, tl)
    if qi == 2: return V1_ASK(8, tl)
    if qi == 3: return V1_ASK(2, tl)
    if qi == 4: im = _bg((60, 10, 20), (10, 4, 6)); _row(im, ["performing_arts", "scroll", "open_book", "rose"], tl, 170); return im
    if qi == 5: return V1_ASK(11, tl)
    if qi == 6:
        im = _bg((70, 25, 35), (10, 5, 8)); paste_c(im, emoji("mount_fuji", 280), SW * 0.38, SH / 2 + 10); paste_c(im, emoji("japanese_castle", 200), SW * 0.72, SH / 2 + 30 + 6 * math.sin(tl * 2)); return im
    if qi == 7:
        im = _bg((14, 20, 34), (4, 6, 10))
        for k in range(6): paste_c(im, emoji("bone", 110), (k * 190 + tl * 30) % (SW + 100) - 50, 90 + (k * 113) % 260 + 15 * math.sin(tl + k))
        paste_c(im, emoji("skull", 220), SW / 2, SH / 2 + 8 * math.sin(tl * 1.5)); return im
    if qi == 8:
        im = _bg((30, 30, 40), (8, 8, 10)); d = ImageDraw.Draw(im)
        for k in range(4):
            pts = [(SW / 2 - 40 + k * 26 + 14 * math.sin(j * 0.6 + tl * 3 + k), 150 - j * 7) for j in range(18)]
            d.line(pts, fill=(230, 230, 240, 120), width=5)
        paste_c(im, emoji("teapot", 240), SW / 2, SH / 2 + 60); paste_c(im, emoji("thermometer", 150), SW * 0.8, SH / 2 + 20); return im
    if qi == 9: im = _bg((60, 45, 15), (12, 9, 4)); _row(im, ["lion", "?", "horse", "leopard"], tl, 170); return im
    if qi == 10: base, b = _map("asia"); return kb(base, tl, 1.0, 1.08, 16)
    if qi == 11: return V2_ASK(1, tl)
    if qi == 12:
        im = _bg((30, 24, 18), (6, 5, 4)); ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).polygon([(SW / 2 - 60, 0), (SW / 2 + 60, 0), (SW / 2 + 260, SH), (SW / 2 - 260, SH)], fill=(255, 230, 170, 45)); im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(20)))
        paste_c(im, emoji("framed_picture", 260), SW / 2, SH / 2 + 10, scale=1 + 0.02 * math.sin(tl * 2)); return im
    if qi == 13: return _floating_nums(["0", "1", "2", "3"], tl)
    if qi == 14:
        im = _bg((210, 130, 60), (90, 50, 20)); paste_c(im, emoji("desert", 280), SW / 2, SH / 2 + 10)
        paste_c(im, emoji("camel", 120), (tl * 45) % (SW + 200) - 100, SH * 0.8); return im
    if qi == 15:
        im = kb(stars(), tl, 1.0, 1.06, 20); paste_c(im, emoji("milky_way", 200), SW * 0.3, SH / 2)
        paste_c(im, emoji("comet", 130), (tl * 140) % (SW + 300) - 150, 90 + (tl * 40) % 200); return im
    if qi == 16:
        im = _bg((20, 22, 30), (6, 6, 8))
        for k, (z, s_, nm) in enumerate([(26, "Fe", "Iron"), (13, "Al", "Aluminum"), (80, "Hg", "Mercury"), (29, "Cu", "Copper")]):
            paste_c(im, tile(z, s_, nm, 190), SW * (k + 0.5) / 4, SH / 2 + 10 * math.sin(tl * 2 + k))
        return im
    if qi == 17: base, b = _map("europe"); return kb(base, tl, 1.0, 1.06, 16, py=0.55)
    if qi == 18: return V1_ASK(12, tl)
    if qi == 19: return V2_ASK(6, tl)
    if qi == 20:
        im = Image.new("RGBA", (SW, SH), (8, 7, 6, 255)); g = gold_text_cached("144", 230, 1.0)
        paste_c(im, g, SW / 2 + 60, SH / 2 + 10, scale=1 + 0.03 * math.sin(tl * 2)); d = ImageDraw.Draw(im)
        x0 = SW / 2 + 60 - g.width / 2 + 20; d.line([(x0 - 150, SH / 2 + 20), (x0 - 115, SH / 2 + 5), (x0 - 70, SH / 2 + 120), (x0 - 20, SH / 2 - 105), (x0 + g.width - 60, SH / 2 - 105)], fill=GOLD_L, width=16, joint="curve")
        return im
    if qi == 21: return V1_ASK(3, tl)
    if qi == 22:
        base, b = _map("europe"); im = kb(base, tl, 1.0, 1.06, 16, py=0.55); paste_c(im, emoji("money_bag", 140), SW - 120, SH - 100 + 6 * math.sin(tl * 2)); return im
    if qi == 23:
        im = _bg((10, 20, 40), (4, 6, 10)); e = emoji("dna", 280); sx = abs(math.cos(tl * 1.2)) * 0.7 + 0.3
        e = e.resize((max(1, int(280 * sx)), 280), Image.BICUBIC); paste_c(im, e, SW / 2, SH / 2); return im
    if qi == 24: base, b = _map("world"); return kb(base, tl, 1.0, 1.04, 20)
    if qi == 25:
        im = kb(_mountains(), tl, 1.0, 1.08, 14); paste_c(im, emoji("snow-capped_mountain", 140), SW - 120, 100); return im
    if qi == 26: im = _bg((20, 30, 50), (5, 7, 12)); _row(im, ["thermometer", "?", "droplet", "wind_face"], tl, 170); return im
    if qi == 27:
        im = kb(stars(), tl, 1.0, 1.05, 20); y = SH + 100 - (tl * 45) % (SH + 250)
        for k in range(4): paste_c(im, emoji("cloud", 120), SW / 2 - 90 + k * 60, min(SH - 20, y + 140 + 20 * k), alpha=0.8)
        paste_c(im, emoji("rocket", 170).rotate(45, resample=Image.BICUBIC), SW / 2, y); return im
    if qi == 28:
        im = Image.new("RGBA", (SW, SH), (3, 3, 8, 255)); d = ImageDraw.Draw(im); rng = random.Random(9)
        for k in range(70):
            a = rng.uniform(0, 6.283); r0 = (rng.uniform(0, 1) + tl * 0.6) % 1 * 600; r1 = r0 + 40 + r0 * 0.3
            d.line((SW / 2 + r0 * math.cos(a), SH / 2 + r0 * math.sin(a), SW / 2 + r1 * math.cos(a), SH / 2 + r1 * math.sin(a)), fill=(220, 230, 255, int(80 + r0 / 4)), width=2)
        paste_c(im, emoji("flashlight", 160), SW / 2, SH / 2); return im
    if qi == 29:
        im = _bg((12, 18, 30), (4, 5, 8)); paste_c(im, emoji("globe_showing_americas", 230), SW / 2, SH / 2)
        for k in range(5):
            a = tl * 0.5 + k * 1.256; paste_c(im, emoji("speech_balloon", 90), SW / 2 + 330 * math.cos(a), SH / 2 + 150 * math.sin(a))
        return im

def stage_exp(qi, te, sc):
    if qi == 0: return V1_EXP(1, te, sc)
    if qi == 1: return V1_EXP(4, te, sc)
    if qi == 2: return V1_EXP(8, te, sc)
    if qi == 3: return V1_EXP(2, te, sc)
    if qi == 4:
        im = _bg((60, 10, 20), (10, 4, 6)); paste_c(im, emoji("performing_arts", 230), SW * 0.2, SH / 2 - 10, scale=eback(te / 0.5))
        if te > 0.3: paste_c(im, gold_text_cached("SHAKESPEARE", 110, 1.0), SW * 0.62, SH * 0.36, scale=eback((te - 0.3) / 0.4))
        if te > 1.0: label(im, "WILLIAM SHAKESPEARE", SW * 0.62, SH * 0.56, 34)
        if te > 1.8: paste_c(im, pill("ROMEO & JULIET", 40), SW * 0.62, SH - 70, scale=eback((te - 1.8) / 0.4)); paste_c(im, emoji("rose", 90), SW * 0.92, SH - 70)
        return im
    if qi == 5: return V1_EXP(11, te, sc)
    if qi == 6:
        im = _bg((70, 25, 35), (10, 5, 8)); paste_c(im, emoji("yen_banknote", 260), SW * 0.28, SH / 2, scale=eback(te / 0.5))
        if te > 0.3: paste_c(im, gold_text_cached("YEN", 170, 1.0), SW * 0.68, SH * 0.4, scale=eback((te - 0.3) / 0.4))
        if te > 1.2: label(im, "JAPAN'S OFFICIAL CURRENCY", SW * 0.68, SH * 0.68, 32)
        if te > 1.8: paste_c(im, pill("JPY", 38), SW * 0.68, SH - 50, scale=eback((te - 1.8) / 0.4))
        return im
    if qi == 7:
        im = _bg((14, 20, 34), (4, 6, 10)); paste_c(im, gold_text_cached("206", 210, 1.0), SW * 0.3, SH * 0.42, scale=eback(te / 0.5))
        if te > 0.6: label(im, "BONES IN AN ADULT", SW * 0.3, SH * 0.78, 34)
        if te > 1.8: paste_c(im, emoji("baby", 170), SW * 0.74, SH * 0.4, scale=eback((te - 1.8) / 0.4))
        if te > 2.3: label(im, "BABIES: MORE BONES", SW * 0.74, SH * 0.72, 30, GOLD_L); label(im, "(THEY FUSE AS WE GROW)", SW * 0.74, SH * 0.84, 24, (190, 190, 190))
        return im
    if qi == 8:
        im = _bg((60, 20, 10), (10, 4, 3)); paste_c(im, emoji("thermometer", 230), SW * 0.2, SH / 2, scale=eback(te / 0.5))
        if te > 0.3: paste_c(im, gold_text_cached("100°C", 170, 1.0), SW * 0.6, SH * 0.4, scale=eback((te - 0.3) / 0.4))
        if te > 1.6: paste_c(im, pill("= 212°F", 44), SW * 0.6, SH * 0.75, scale=eback((te - 1.6) / 0.4))
        if te > 2.4: paste_c(im, emoji("hot_springs", 100), SW * 0.9, SH * 0.2)
        return im
    if qi == 9:
        im = _bg((60, 45, 15), (12, 9, 4)); _gauge(im, SW * 0.3, SH / 2 + 30, 170, min(1, ease((te - 0.2) / 1.2)) * 65 / 80, [0, 20, 40, 60, 80], "MPH")
        if te > 0.3: paste_c(im, pill("CHEETAH", 54), SW * 0.7, SH * 0.3, scale=eback((te - 0.3) / 0.4))
        if te > 1.4: paste_c(im, gold_text_cached("60-70 MPH", 90, 1.0), SW * 0.7, SH * 0.6, scale=eback((te - 1.4) / 0.4)); paste_c(im, emoji("dashing_away", 90), SW * 0.93, SH * 0.6)
        return im
    if qi == 10:
        base, b = _map("asia", ("156",)); im = kb(base, te, 1.0, 1.12, 8, px=0.6, py=0.45)
        if te > 0.4: paste_c(im, pill("CHINA", 54), SW * 0.62, SH * 0.45, scale=eback((te - 0.4) / 0.4))
        if te > 1.4: label(im, "THE GREAT WALL • NORTHERN CHINA", SW * 0.5, SH - 40, 30)
        return im
    if qi == 11: return V2_EXP(1, te, sc)
    if qi == 12:
        im = stage_ask(12, te); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 110)))
        paste_c(im, emoji("classical_building", 160), SW * 0.18, SH / 2, scale=eback(te / 0.5))
        if te > 0.3: paste_c(im, pill("LOUVRE MUSEUM", 52), SW * 0.66, SH * 0.38, scale=eback((te - 0.3) / 0.4))
        if te > 1.2: label(im, "PARIS, FRANCE", SW * 0.66, SH * 0.65, 36)
        return im
    if qi == 13: return V1_EXP(6, te, sc)
    if qi == 14:
        im = kb(_sahara(), te, 1.0, 1.15, 9, px=0.4, py=0.25)
        if te > 0.5: paste_c(im, pill("SAHARA DESERT", 50), SW * 0.5, SH * 0.55, scale=eback((te - 0.5) / 0.4))
        if te > 1.5: label(im, "LARGEST HOT DESERT • NORTH AFRICA", SW * 0.5, SH - 40, 28)
        return im
    if qi == 15:
        im = kb(stars(), te, 1.0, 1.04, 10); d = ImageDraw.Draw(im); p = ease((te - 0.3) / 1.6)
        paste_c(im, emoji("flashlight", 120).rotate(-45, resample=Image.BICUBIC), 90, SH / 2)
        d.line((160, SH / 2, 160 + (SW - 260) * p, SH / 2), fill=(255, 240, 180), width=10)
        if p >= 1: paste_c(im, emoji("glowing_star", 90), SW - 80, SH / 2)
        if te > 0.4: paste_c(im, pill("DISTANCE", 54), SW / 2, 90, scale=eback((te - 0.4) / 0.4))
        if te > 1.4: label(im, "HOW FAR LIGHT TRAVELS IN 1 YEAR", SW / 2, SH / 2 + 60, 30)
        if te > 2.4: paste_c(im, gold_text_cached("5.88 TRILLION MILES", 70, 1.0), SW / 2, SH - 70, scale=eback((te - 2.4) / 0.4))
        return im
    if qi == 16:
        im = _bg((20, 22, 30), (6, 6, 8)); paste_c(im, tile(80, "Hg", "Mercury", 240), SW * 0.24, SH / 2, scale=eback(te / 0.5)); d = ImageDraw.Draw(im)
        for k in range(6):
            x = SW * 0.55 + k * 70 + 10 * math.sin(te * 2 + k); y = SH * 0.36 + 18 * math.sin(te * 3 + k * 2); r = 22 + 6 * math.sin(k)
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=(190, 195, 205)); d.ellipse((x - r * 0.5, y - r * 0.6, x, y - r * 0.2), fill=(250, 250, 255))
        if te > 0.8: paste_c(im, pill("LIQUID AT ROOM TEMPERATURE", 34), SW * 0.68, SH * 0.68, scale=eback((te - 0.8) / 0.4))
        return im
    if qi == 17:
        base, b = _map("europe", ("380",)); im = kb(base, te, 1.0, 1.2, 8, px=0.5, py=0.72)
        if te > 0.4: paste_c(im, pill("ITALY", 54), SW * 0.25, SH * 0.3, scale=eback((te - 0.4) / 0.4))
        if te > 1.2: paste_c(im, emoji("pizza", 110), SW * 0.85, SH * 0.3, scale=eback((te - 1.2) / 0.4))
        return im
    if qi == 18:
        im = kb(stars(), te, 1.0, 1.05, 10); paste_c(im, moon_big(), SW / 2, SH + 260 - 30 * ease(te / 6))
        paste_c(im, emoji("astronaut", 170), SW * 0.78, SH * 0.55 + 6 * math.sin(te * 2), scale=eback(te / 0.5))
        if te > 0.3: paste_c(im, pill("NEIL ARMSTRONG", 52), SW * 0.4, 100, scale=eback((te - 0.3) / 0.4))
        if te > 1.4: label(im, "JULY 20, 1969  •  APOLLO 11", SW * 0.4, 200, 32)
        return im
    if qi == 19: return V2_EXP(6, te, sc)
    if qi == 20: return V1_EXP(14, te, sc)
    if qi == 21: return V1_EXP(3, te, sc)
    if qi == 22:
        base, b = _map("europe", ("756",)); im = kb(base, te, 1.0, 1.25, 8, px=0.42, py=0.6)
        if te > 0.4: paste_c(im, pill("SWISS FRANC (CHF)", 46), SW * 0.5, 80, scale=eback((te - 0.4) / 0.4))
        if te > 1.2: paste_c(im, emoji("coin", 110), SW * 0.85, SH * 0.7); paste_c(im, emoji("cheese_wedge", 100), SW * 0.15, SH * 0.7)
        return im
    if qi == 23:
        im = _helix(te)
        if te > 0.5: paste_c(im, pill("DOUBLE HELIX", 54), SW / 2, SH - 60, scale=eback((te - 0.5) / 0.4))
        if te > 1.4: label(im, "TWO STRANDS TWISTED TOGETHER", SW / 2, 50, 30)
        return im
    if qi == 24:
        base, b = _map("world"); im = kb(base, te, 1.0, 1.02, 20)
        conts = [("AFRICA", 20, 5), ("ANTARCTICA", 20, -52), ("ASIA", 95, 48), ("EUROPE", 15, 52), ("N. AMERICA", -100, 45), ("S. AMERICA", -60, -15), ("AUSTRALIA", 134, -25)]
        n = 0
        for k, (nm, lo, la) in enumerate(conts):
            tk = te - 0.3 - k * 0.45
            if tk <= 0: continue
            n = k + 1; x, y = lonlat_px(lo, la, *b, SW, SH)
            paste_c(im, pill(nm, 24), x, y, scale=eback(tk / 0.35))
        if n: paste_c(im, gold_text_cached(str(n), 120, 1.0), SW - 90, 90)
        return im
    if qi == 25:
        im = _bg((20, 26, 44), (6, 7, 12))
        _bars(im, [("EVEREST", 8849, "8,849 m"), ("K2", 8611, "8,611 m"), ("DENALI", 6190, "6,190 m"), ("KILIMANJARO", 5895, "5,895 m")], te, horizontal=False)
        if te > 2.2: paste_c(im, pill("MOUNT EVEREST", 40), SW * 0.72, 60, scale=eback((te - 2.2) / 0.4))
        return im
    if qi == 26:
        im = _bg((20, 30, 50), (5, 7, 12)); _gauge(im, SW * 0.28, SH / 2 + 20, 170, 0.35 + 0.3 * ease(te / 2) + 0.03 * math.sin(te * 3), ["LOW", "", "", "", "HIGH"], "PRESSURE")
        if te > 0.3: paste_c(im, pill("BAROMETER", 54), SW * 0.7, SH * 0.32, scale=eback((te - 0.3) / 0.4))
        if te > 1.4: paste_c(im, emoji("sun_behind_cloud", 1) if False else emoji("cloud", 110), SW * 0.62, SH * 0.68); paste_c(im, emoji("sun", 90), SW * 0.8, SH * 0.68)
        if te > 1.8: label(im, "WEATHER FORECASTING", SW * 0.7, SH - 30, 28)
        return im
    if qi == 27:
        im = kb(stars(), te, 1.0, 1.05, 10); paste_c(im, moon_big(), SW / 2, SH + 260)
        paste_c(im, emoji("rocket", 130).rotate(-135, resample=Image.BICUBIC), SW * 0.5, 120 + 60 * ease(te / 3))
        if te > 0.3: paste_c(im, pill("APOLLO 11", 56), SW * 0.22, 90, scale=eback((te - 0.3) / 0.4))
        if te > 1.4: label(im, "FIRST CREWED MOON LANDING • JULY 1969", SW / 2, SH - 40, 28)
        return im
    if qi == 28:
        im = stage_ask(28, te * 2); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 120)))
        paste_c(im, gold_text_cached("300,000 KM/S", 120, 1.0), SW / 2, SH * 0.42, scale=eback(te / 0.5))
        if te > 1.2: label(im, "EXACTLY: 299,792 KM PER SECOND", SW / 2, SH * 0.72, 32)
        return im
    if qi == 29:
        im = _bg((12, 18, 30), (4, 5, 8))
        _bars(im, [("MANDARIN", 10, ""), ("SPANISH", 5.2, ""), ("ENGLISH", 4.0, ""), ("HINDI", 3.6, "")], te)
        if te > 2.0: paste_c(im, pill("#1 MANDARIN CHINESE", 38), SW - 230, SH - 50, scale=eback((te - 2.0) / 0.4))
        if te > 1.0: label(im, "NATIVE SPEAKERS", SW - 160, 40, 24, (180, 180, 180))
        return im

MONT = [(0, 3), (5, 3), (9, 3, "exp"), (17, 3, "exp"), (24, 4, "exp"), (28, 2)]
