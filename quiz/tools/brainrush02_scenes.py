# Cenas do palco do vídeo 02 (Science & Nature). Executado dentro do namespace do build_brainrush01.py
# (tem acesso a SW, SH, kb, stars, sphere, halo, emoji, pill, label, periodic, tile, australia, etc.)

@functools.lru_cache(maxsize=512)
def _sph(texn, size, lon, amb=0.06, atmo=None):
    return sphere(texn, size, lon0=lon, ambient=amb, atmo=atmo)

@functools.lru_cache(None)
def _sun(size):
    s = sphere("sunmap.jpg", size, ambient=0.55, light=(0, 0, 1)); s = Image.fromarray(np.clip(np.asarray(s).astype(np.float32) * np.array([1.15, 0.92, 0.6, 1.0]), 0, 255).astype(np.uint8), "RGBA")
    out = halo(s, max(20, size // 8), (255, 150, 40), 0.9); paste_c(out, s, out.width / 2, out.height / 2); return out

def _bg(top, bot):
    return grad(SW, SH, top, bot).convert("RGBA")

def _hue(im, shift):
    a = im.getchannel("A"); h, s_, v = im.convert("RGB").convert("HSV").split()
    h = h.point(lambda x: (x + int(shift)) % 256)
    out = Image.merge("HSV", (h, s_, v)).convert("RGBA"); out.putalpha(a); return out

PLAN = [("mercurymap.jpg", 230, 26, 1.6), ("venusmap.jpg", 330, 40, 1.15), ("earth.jpg", 440, 42, 0.9), ("mars.jpg", 550, 32, 0.7)]
def solar(t, hi=None, arrows=0.0, speed=1.0):
    im = kb(stars(), t, 1.0, 1.04, 20); cx, cy = 60, SH / 2
    d = ImageDraw.Draw(im)
    for _, r, _, _ in PLAN: d.ellipse((cx - r, cy - r * 0.36, cx + r, cy + r * 0.36), outline=(120, 100, 60, 160), width=2)
    paste_c(im, _sun(330), cx, cy)
    for k, (tx, r, sz, sp) in enumerate(PLAN):
        a = t * 0.35 * sp * speed + k * 1.7; x, y = cx + r * math.cos(a), cy + r * 0.36 * math.sin(a)
        if hi == k:
            rr = sz + 14 + 4 * math.sin(t * 6); d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=GOLD_L + (255,), width=4)
        if arrows > 0:
            ax, ay = x + (cx - x) * 0.35 * arrows, y + (cy - y) * 0.35 * arrows
            d.line((x, y, ax, ay), fill=GOLD_L + (255,), width=5)
            ang = math.atan2(cy - y, cx - x)
            d.polygon([(ax + 14 * math.cos(ang), ay + 14 * math.sin(ang)), (ax + 12 * math.cos(ang + 2.4), ay + 12 * math.sin(ang + 2.4)), (ax + 12 * math.cos(ang - 2.4), ay + 12 * math.sin(ang - 2.4))], fill=GOLD_L + (255,))
        paste_c(im, _sph(tx, sz * 2, int(t * 10) % 360, 0.15), x, y)
    return im

def _row(im, names, t, size=170, y=None, bob=12):
    n = len(names); y = SH / 2 if y is None else y
    for k, e in enumerate(names):
        x = SW * (k + 0.5) / n
        if e == "?":
            c = rrect((size, size), 28, (40, 32, 12, 255), GOLD + (255,), 4); ImageDraw.Draw(c).text((size / 2, size / 2 + 6), "?", font=F("anton", int(size * 0.7)), anchor="mm", fill=GOLD_L)
            paste_c(im, c, x, y + bob * math.sin(t * 2 + k))
        else:
            paste_c(im, emoji(e, size), x, y + bob * math.sin(t * 2 + k))

def _pills_seq(im, items, te, t0=0.6, gap=0.7, y=None, size=38):
    y = SH - 60 if y is None else y; n = len(items)
    for k, it in enumerate(items):
        if te > t0 + k * gap: paste_c(im, pill(it, size), SW * (k + 0.5) / n, y, scale=eback((te - t0 - k * gap) / 0.4))

@functools.lru_cache(None)
def _lake():
    im = _bg((70, 110, 170), (250, 190, 120)); d = ImageDraw.Draw(im)
    d.ellipse((SW * 0.62, 40, SW * 0.62 + 120, 160), fill=(255, 236, 170))
    d.polygon([(0, 270), (180, 150), (330, 250), (520, 120), (720, 260), (900, 170), (SW, 250), (SW, 290), (0, 290)], fill=(60, 70, 90))
    d.rectangle((0, 285, SW, SH), fill=(30, 80, 120))
    for k in range(14):
        y = 300 + k * 11; d.line((40 + 37 * k % 300, y, 300 + 51 * k % 700, y), fill=(140, 190, 220), width=2)
    return im

def _brain_side(te, glow):
    im = Image.new("RGBA", (SW * 2, SH * 2), (8, 7, 6, 255)); d = ImageDraw.Draw(im)
    cx, cy = SW * 0.85, SH * 0.95
    d.ellipse((cx - 470, cy - 330, cx + 430, cy + 250), fill=(235, 160, 175))
    for k in range(9):
        a0 = 200 + k * 16; d.arc((cx - 420 + k * 18, cy - 300 + k * 10, cx + 380 - k * 22, cy + 220 - k * 12), a0, a0 + 70, fill=(190, 110, 130), width=10)
    c = tuple(int(200 + (v - 200) * glow) for v in (170, 120, 140))
    col = tuple(int(a + (b - a) * glow) for a, b in zip((200, 120, 140), GOLD_L))
    d.ellipse((cx + 120, cy + 90, cx + 470, cy + 330), fill=col)
    for k in range(6): d.arc((cx + 140, cy + 110 + k * 20, cx + 450, cy + 310 - k * 4), 200, 340, fill=(120, 80, 40) if glow > 0.5 else (170, 100, 120), width=6)
    d.rounded_rectangle((cx + 40, cy + 150, cx + 140, cy + 470), 40, fill=(210, 140, 150))
    return im.resize((SW, SH), Image.LANCZOS)

def stage_ask(qi, tl):
    if qi == 0: return solar(tl)
    if qi == 1:
        im = _bg((20, 60, 30), (4, 12, 6)); paste_c(im, emoji("sun", 150), SW - 140, 110, scale=1 + 0.05 * math.sin(tl * 2))
        paste_c(im, emoji("potted_plant", 260), SW / 2, SH / 2 + 30 + 6 * math.sin(tl * 1.5))
        for k in range(5): paste_c(im, emoji("leaf_fluttering_in_wind", 80), (tl * 60 + k * 230) % (SW + 160) - 80, 80 + (k * 97) % 300 + 15 * math.sin(tl + k))
        return im
    if qi == 2:
        im = _bg((24, 14, 18), (6, 5, 6)); _row(im, ["brain", "lungs", "anatomical_heart", "raised_hand"], tl, 180); return im
    if qi == 3:
        im = kb(stars(), tl, 1.0, 1.04, 20)
        for k, tx in enumerate(["neptunemap.jpg", "saturn.jpg", "jupitermap.jpg", "uranusmap.jpg"]):
            paste_c(im, _sph(tx, 190, int(tl * 12) % 360), SW * (k + 0.5) / 4, SH / 2 + 10 * math.sin(tl + k))
        d = ImageDraw.Draw(im)
        for k in range(14):
            x = (tl * 380 + k * 157) % (SW + 300) - 150; y = 40 + (k * 61) % (SH - 80)
            d.line((x, y, x + 120, y), fill=(200, 220, 255, 90), width=2)
        return im
    if qi == 4: return kb(periodic(None, 0), tl, 1.0, 1.08, 16)
    if qi == 5:
        im = _bg((30, 60, 20), (8, 16, 6)); _row(im, ["leopard", "lizard", "kangaroo", "zebra"], tl, 180); return im
    if qi == 6:
        im = _bg((30, 6, 10), (6, 4, 5)); d = ImageDraw.Draw(im)
        ph = (tl * 1.2) % 1; beat = math.exp(-((ph - 0.1) / 0.05) ** 2) + 0.6 * math.exp(-((ph - 0.28) / 0.05) ** 2)
        pts = []
        for x in range(0, SW, 6):
            u = ((x / SW) - tl * 0.5) % 1; y = SH * 0.78 - (60 * math.exp(-((u - 0.5) / 0.015) ** 2) - 25 * math.exp(-((u - 0.56) / 0.02) ** 2))
            pts.append((x, y))
        d.line(pts, fill=(255, 90, 90, 200), width=4)
        paste_c(im, emoji("anatomical_heart", 260), SW / 2, SH * 0.42, scale=1 + 0.08 * beat); return im
    if qi == 7:
        im = _bg((14, 12, 20), (5, 5, 7)); _row(im, ["crystal_ball", "gem_stone", "rock", "chains"], tl, 170)
        for k in range(8):
            ph = (tl * 0.8 + k * 0.37) % 1
            paste_c(im, emoji("sparkles", 50), (k * 131) % SW, 60 + (k * 89) % (SH - 120), alpha=math.sin(ph * math.pi))
        return im
    if qi == 8:
        im = kb(stars(), tl, 1.0, 1.05, 20); p = _sph("earth.jpg", 360, int(-60 + tl * 3), 0.06, (0.3, 0.55, 1.0))
        paste_c(im, halo(p, 40, (90, 150, 255), 0.6), SW / 2, SH / 2 + 4); paste_c(im, p, SW / 2, SH / 2 + 4); return im
    if qi == 9:
        im = _bg((18, 10, 20), (5, 4, 6))
        for k in range(10):
            ph = (tl * 0.6 + k * 0.29) % 1; paste_c(im, emoji("sparkles", 46), SW / 2 + 260 * math.cos(k * 0.63 + tl * 0.3), SH / 2 + 170 * math.sin(k * 0.63 + tl * 0.3), alpha=math.sin(ph * math.pi))
        paste_c(im, emoji("brain", 260), SW / 2, SH / 2, scale=1 + 0.04 * math.sin(tl * 3)); return im
    if qi == 10:
        im = underwater(SW, SH).copy(); bubbles(im, tl, 21); _row(im, ["dolphin", "?", "penguin", "seal"], tl, 170); return im
    if qi == 11: return solar(tl, speed=1.6)
    if qi == 12:
        im = _bg((110, 60, 20), (20, 10, 4)); d = ImageDraw.Draw(im)
        for k in range(12):
            a = tl * 0.2 + k * math.pi / 6; d.line((150, 110, 150 + 900 * math.cos(a), 110 + 900 * math.sin(a)), fill=(255, 210, 120, 40), width=30)
        paste_c(im, emoji("sun", 200), 150, 110); paste_c(im, emoji("flexed_biceps", 260), SW * 0.62, SH * 0.58 + 8 * math.sin(tl * 2)); return im
    if qi == 13:
        im = _lake().copy(); d = ImageDraw.Draw(im)
        for k in range(10):
            x = (k * 113 + tl * 20) % SW; d.line((x, 330 + k * 9, x + 60, 330 + k * 9), fill=(220, 240, 255, 140), width=2)
        return im
    if qi == 14:
        im = kb(stars(), tl, 1.0, 1.06, 20); d = ImageDraw.Draw(im)
        for k, (x, y, c) in enumerate([(0.2, 0.35, (200, 220, 255)), (0.45, 0.7, (255, 255, 255)), (0.7, 0.3, (255, 230, 200)), (0.85, 0.65, (210, 230, 255)), (0.33, 0.62, (255, 210, 170))]):
            tw = 0.7 + 0.3 * math.sin(tl * 3 + k * 2); X, Y = SW * x, SH * y; L = 60 * tw
            d.line((X - L, Y, X + L, Y), fill=c + (180,), width=3); d.line((X, Y - L, X, Y + L), fill=c + (180,), width=3)
            r = 10 * tw; d.ellipse((X - r, Y - r, X + r, Y + r), fill=c + (255,))
        return im.filter(ImageFilter.GaussianBlur(0.6))

def stage_exp(qi, te, sc):
    if qi == 0:
        im = solar(te + 20, hi=0)
        if te > 0.4: paste_c(im, pill("MERCURY", 44), SW * 0.62, 70, scale=eback((te - 0.4) / 0.4))
        if te > 1.6: paste_c(im, pill("1 ORBIT = 88 DAYS", 40), SW * 0.62, SH - 60, scale=eback((te - 1.6) / 0.4))
        return im
    if qi == 1:
        im = stage_ask(1, te + 10); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 150)))
        if te > 0.3: paste_c(im, pill("CARBON DIOXIDE (CO2)", 46), SW / 2, 110, scale=eback((te - 0.3) / 0.4))
        if te > 1.4: paste_c(im, text_img("CO2 + WATER + SUNLIGHT  =  SUGAR + O2", F("mont", 40), fill=WHITE), SW / 2, SH / 2 + 30, alpha=ease((te - 1.4) / 0.5))
        if te > 2.4: paste_c(im, emoji("potted_plant", 110), SW / 2, SH - 80, scale=eback((te - 2.4) / 0.4))
        return im
    if qi == 2:
        im = _bg((30, 18, 14), (8, 6, 6)); paste_c(im, emoji("raised_hand", 270), SW * 0.25, SH / 2 - 20, scale=eback(te / 0.5))
        if te > 0.4: paste_c(im, gold_text_cached("SKIN", 150, 1.0), SW * 0.66, SH * 0.36, scale=eback((te - 0.4) / 0.4))
        if te > 0.9: label(im, "THE LARGEST ORGAN", SW * 0.66, SH * 0.6, 36)
        _pills_seq(im, ["PROTECTION", "TEMPERATURE", "TOUCH"], te, 1.8, 0.8); return im
    if qi == 3:
        im = kb(stars(), te, 1.0, 1.06, 10); p = _sph("neptunemap.jpg", 420, int(te * 20) % 360, 0.05, (0.2, 0.4, 1.0))
        paste_c(im, halo(p, 40, (60, 110, 255), 0.6), SW * 0.32, SH / 2); paste_c(im, p, SW * 0.32, SH / 2)
        d = ImageDraw.Draw(im)
        for k in range(18):
            x = (te * 700 + k * 97) % (SW + 300) - 150; y = 40 + (k * 41) % (SH - 80)
            d.line((x, y, x + 180, y - 10), fill=(190, 220, 255, 130), width=3)
        if te > 0.3: paste_c(im, pill("NEPTUNE", 44), SW * 0.74, SH * 0.3, scale=eback((te - 0.3) / 0.4))
        if te > 1.2: paste_c(im, pill("2,000+ KM/H WINDS", 42), SW * 0.74, SH * 0.62, scale=eback((te - 1.2) / 0.4))
        return im
    if qi == 4:
        im = kb(periodic(8, int(min(10, te * 10))), te, 1.0, 1.0, 8)
        if te > 1.0:
            im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, int(160 * ease((te - 1.0) / 0.4)))))
            paste_c(im, tile(8, "O", "Oxygen", 250), SW / 2 - 220, SH / 2, scale=eback((te - 1.0) / 0.5))
        if te > 1.8: paste_c(im, emoji("lungs", 110), SW / 2 + 120, SH / 2 - 70, scale=eback((te - 1.8) / 0.4)); label(im, "RESPIRATION", SW / 2 + 300, SH / 2 - 70, 34)
        if te > 2.6: paste_c(im, emoji("fire", 110), SW / 2 + 120, SH / 2 + 80, scale=eback((te - 2.6) / 0.4)); label(im, "COMBUSTION", SW / 2 + 300, SH / 2 + 80, 34)
        return im
    if qi == 5:
        sh = te * 40; im = _hue(_bg((30, 90, 20), (8, 30, 6)), sh)
        paste_c(im, _hue(emoji("lizard", 300), sh), SW / 2, SH / 2 - 40, scale=eback(te / 0.5))
        _pills_seq(im, ["COMMUNICATION", "TEMPERATURE", "CAMOUFLAGE"], te, 1.2, 0.9, size=34)
        if te > 0.4: paste_c(im, pill("CHAMELEON", 40), SW / 2, 60, scale=eback((te - 0.4) / 0.4))
        return im
    if qi == 6:
        im = _bg((30, 6, 10), (6, 4, 5)); paste_c(im, emoji("anatomical_heart", 260), SW * 0.24, SH / 2, scale=1 + 0.06 * abs(math.sin(te * 4)))
        names = ["RIGHT ATRIUM", "LEFT ATRIUM", "RIGHT VENTRICLE", "LEFT VENTRICLE"]
        for k, nm in enumerate(names):
            tk = te - 0.4 - k * 0.5
            if tk <= 0: continue
            x = SW * 0.5 + (k % 2) * 250; y = 90 + (k // 2) * 170
            box = rrect((230, 140), 22, (60, 14, 20, 255) if k < 2 else (110, 20, 30, 255), GOLD + (255,), 3)
            ImageDraw.Draw(box).multiline_text((115, 70), nm.replace(" ", "\n"), font=F("mont", 26), anchor="mm", align="center", fill=WHITE)
            paste_c(im, box, x + 115, y + 70, scale=eback(tk / 0.4))
        if te > 2.6: paste_c(im, pill("4 CHAMBERS", 40), SW * 0.24, SH - 50, scale=eback((te - 2.6) / 0.4))
        return im
    if qi == 7:
        im = _bg((14, 12, 20), (5, 5, 7)); paste_c(im, halo(emoji("gem_stone", 220), 30, (150, 220, 255), 0.7), SW / 2, 150)
        paste_c(im, emoji("gem_stone", 220), SW / 2, 150, scale=eback(te / 0.5) * (1 + 0.04 * math.sin(te * 3)))
        d = ImageDraw.Draw(im); x0, x1, y = 90, SW - 90, SH - 110; p = ease((te - 0.8) / 1.2)
        d.rounded_rectangle((x0, y - 10, x0 + (x1 - x0) * p, y + 10), 10, fill=GOLD)
        for k in range(1, 11):
            x = x0 + (x1 - x0) * (k - 1) / 9
            if p >= (k - 1) / 9: d.text((x, y + 40), str(k), font=F("anton", 34), anchor="mm", fill=GOLD_L if k == 10 else WHITE)
        if te > 1.6: label(im, "QUARTZ 7", x0 + (x1 - x0) * 6 / 9, y - 45, 26, (200, 200, 200))
        if te > 2.1: paste_c(im, pill("DIAMOND 10", 34), x0 + (x1 - x0) - 40, y - 55, scale=eback((te - 2.1) / 0.4))
        if te > 0.8: label(im, "MOHS HARDNESS SCALE", SW / 2, SH - 25, 24, (190, 190, 190))
        return im
    if qi == 8:
        im = kb(stars(), te, 1.0, 1.04, 10); p = _sph("earth.jpg", 280, int(-60 + te * 3), 0.06, (0.3, 0.55, 1.0))
        paste_c(im, halo(p, 30, (90, 150, 255), 0.6), 190, SH / 2); paste_c(im, p, 190, SH / 2)
        cx, cy, R = SW * 0.62, SH / 2, 160; p_ = eout(te / 1.4)
        ring = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(ring); b = (0, 0, R * 4 - 1, R * 4 - 1)
        segs = [(0.78, GOLD), (0.21, (230, 230, 235)), (0.01, (120, 120, 120))]; a = -90
        for frac, c in segs:
            e = a + 360 * frac * p_; d.pieslice(b, a, e, fill=c + (255,)); a = a + 360 * frac
        d.ellipse((R * 2 - R * 1.1, R * 2 - R * 1.1, R * 2 + R * 1.1, R * 2 + R * 1.1), fill=(8, 8, 12, 255))
        ring = ring.resize((R * 2, R * 2), Image.LANCZOS); paste_c(im, ring, cx, cy)
        paste_c(im, gold_text_cached("78%", 90, 1.0), cx, cy - 8, alpha=ease((te - 0.6) / 0.4))
        if te > 1.2: label(im, "NITROGEN", cx + 300, cy - 60, 36, GOLD_L); label(im, "OXYGEN 21%", cx + 300, cy, 30); label(im, "OTHER 1%", cx + 300, cy + 50, 26, (170, 170, 170))
        return im
    if qi == 9:
        g = ease((te - 0.3) / 0.5) * (0.75 + 0.25 * math.sin(te * 4)); im = _brain_side(te, g)
        if te > 0.6: paste_c(im, pill("CEREBELLUM", 42), SW * 0.8, SH * 0.2, scale=eback((te - 0.6) / 0.4))
        _pills_seq(im, ["BALANCE", "COORDINATION", "POSTURE"], te, 1.6, 0.7, size=34)
        return im
    if qi == 10:
        base, box = australia(); im = kb(base, te, 1.0, 1.05, 10); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 120)))
        if te > 0.3: paste_c(im, pill("PLATYPUS", 54), SW / 2, 90, scale=eback((te - 0.3) / 0.4))
        for k in range(3):
            if te > 1.0 + k * 0.3: paste_c(im, emoji("egg", 110), SW / 2 - 140 + k * 140, SH / 2 + 20, scale=eback((te - 1.0 - k * 0.3) / 0.4))
        if te > 2.2: paste_c(im, pill("A MAMMAL THAT LAYS EGGS", 34), SW / 2, SH - 110, scale=eback((te - 2.2) / 0.4))
        if te > 3.0: label(im, "NATIVE TO AUSTRALIA", SW / 2, SH - 40, 28)
        return im
    if qi == 11:
        im = solar(te + 5, arrows=ease((te - 0.3) / 0.8), speed=1.6)
        if te > 0.8: paste_c(im, pill("GRAVITY", 54), SW * 0.68, 80, scale=eback((te - 0.8) / 0.4))
        return im
    if qi == 12:
        im = _bg((110, 60, 20), (20, 10, 4)); im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 90)))
        steps = [("sun", "UVB LIGHT"), ("flexed_biceps", "SKIN"), (None, "VITAMIN D"), ("bone", "CALCIUM")]
        for k, (e, nm) in enumerate(steps):
            tk = te - 0.3 - k * 0.6
            if tk <= 0: continue
            x = SW * (k + 0.5) / 4
            if e: paste_c(im, emoji(e, 140), x, SH / 2 - 50, scale=eback(tk / 0.4)); label(im, nm, x, SH / 2 + 60, 30)
            else: paste_c(im, pill("VITAMIN D", 40), x, SH / 2 - 20, scale=eback(tk / 0.4))
            if k:
                d = ImageDraw.Draw(im); ax = SW * k / 4; ay = SH / 2 - 40
                d.line((ax - 26, ay, ax + 14, ay), fill=GOLD_L, width=7); d.polygon([(ax + 28, ay), (ax + 10, ay - 14), (ax + 10, ay + 14)], fill=GOLD_L)
        return im
    if qi == 13:
        im = _lake().copy(); vap = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(vap)
        for k in range(9):
            x0 = 80 + k * 110; ph = (te * 0.5 + k * 0.17) % 1; pts = []
            for j in range(20):
                y = 300 - ph * 220 - j * 6; pts.append((x0 + 12 * math.sin(j * 0.5 + te * 3 + k), y))
            d.line(pts, fill=(255, 255, 255, int(150 * math.sin(ph * math.pi))), width=6)
        im.alpha_composite(vap.filter(ImageFilter.GaussianBlur(3)))
        paste_c(im, emoji("cloud", 150), SW * 0.3 + 20 * math.sin(te), 70, scale=eback((te - 1.0) / 0.5) if te > 1.0 else 0.01)
        if te > 0.4: paste_c(im, pill("EVAPORATION", 46), SW * 0.68, SH * 0.45, scale=eback((te - 0.4) / 0.4))
        if te > 2.0: label(im, "PART OF THE WATER CYCLE", SW * 0.68, SH * 0.62, 30)
        return im
    if qi == 14:
        im = kb(stars(), te, 1.0, 1.04, 10); paste_c(im, _sun(380), 120, SH / 2, scale=1 + 0.02 * math.sin(te * 2))
        p = _sph("earth.jpg", 90, 0, 0.1); paste_c(im, p, SW - 130, SH / 2)
        d = ImageDraw.Draw(im); pr = ease((te - 0.4) / 1.0); x0, x1 = 330, SW - 190
        for x in range(int(x0), int(x0 + (x1 - x0) * pr), 30): d.line((x, SH / 2, x + 16, SH / 2), fill=GOLD_L, width=4)
        if te > 1.2: paste_c(im, pill("150 MILLION KM", 46), (x0 + x1) / 2, SH / 2 - 70, scale=eback((te - 1.2) / 0.4))
        if te > 2.4: label(im, "NEXT CLOSEST STAR: PROXIMA CENTAURI", SW * 0.64, SH - 70, 24, (200, 200, 200)); label(im, "(4.2 LIGHT-YEARS AWAY)", SW * 0.64, SH - 38, 22, (170, 170, 170))
        if te > 0.3: paste_c(im, pill("THE SUN", 40), 220, 60, scale=eback((te - 0.3) / 0.4))
        return im

MONT = [(0, 3), (3, 3, "exp"), (6, 2), (8, 4, "exp"), (10, 2), (14, 3, "exp"), (1, 2), (9, 3, "exp")]
