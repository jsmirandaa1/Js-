"""Monta o vídeo 01 do BrainRush Quiz (16:9, 1920x1080, 30fps).
Uso: python3 build_brainrush01.py [--frames t1,t2,...] [--range a b]
Precisa: narração em /tmp/claude-0/br01/voz (brainrush01_tts.py) e assets em /tmp/claude-0/quiz_assets.
"""
import json, math, os, re, subprocess, sys, difflib, functools, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brainrush01_data import QS, BANDS
from brgfx import *
from planets import sphere, saturn

W, H, FPS = 1920, 1080, 30
WORK = "/tmp/claude-0/br01"; VOZ = WORK + "/voz"
META = json.load(open(VOZ + "/meta.json"))

# ------------------------------------------------------------------ alinhamento texto x whisper
def norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def align(name):
    """Palavras do roteiro com tempos (do whisper, interpolando onde não bate)."""
    m = META[name]; sw = m["text"].split(); ww = m["words"]
    a = [norm(x) for x in sw]; b = [norm(x[2]) for x in ww]
    T = [None] * len(sw)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): T[blk.a + k] = (ww[blk.b + k][0], ww[blk.b + k][1])
    # interpola
    known = [i for i, x in enumerate(T) if x]
    for i in range(len(sw)):
        if T[i]: continue
        p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
        t0 = T[p][1] if p is not None else 0.0; t1 = T[n][0] if n is not None else m["dur"]
        lo = p if p is not None else -1; hi = n if n is not None else len(sw)
        f0 = (i - lo - 1) / (hi - lo - 1); f1 = (i - lo) / (hi - lo - 1)
        T[i] = (t0 + (t1 - t0) * f0, t0 + (t1 - t0) * f1)
    return [(T[i][0], T[i][1], sw[i]) for i in range(len(sw))]

# ------------------------------------------------------------------ linha do tempo
TL = []      # cenas: dict(kind, start, dur, ...)
AUD = []     # (abs_start, name)
SFX = []     # (abs_time, kind)
CAP_WORDS = []  # (abs_s, abs_e, word, chunk_id)
t = 0.0
def add_voice(name, at):
    AUD.append((at, name))
    for s, e, w in align(name): CAP_WORDS.append((at + s, at + e, w))
def scene(kind, dur, **kw):
    global t
    d = dict(kind=kind, start=t, dur=dur, **kw); TL.append(d); t += dur; return d

d1 = META["intro1"]["dur"]; s = scene("intro1", 1.0 + d1 + 0.7); add_voice("intro1", s["start"] + 1.0); SFX.append((s["start"] + 0.45, "impact"))
d2 = META["intro2"]["dur"]; s = scene("intro2", 0.5 + d2 + 0.6); add_voice("intro2", s["start"] + 0.5); SFX.append((s["start"], "whoosh")); SFX.append((s["start"] + 0.1, "impact"))
d3 = META["intro3"]["dur"]; s = scene("intro3", 0.3 + d3 + 0.9, words=align("intro3"), v0=0.3); add_voice("intro3", s["start"] + 0.3); SFX.append((s["start"], "whoosh"))
for i, q in enumerate(QS):
    ask, ans = f"q{i+1:02d}_ask", f"q{i+1:02d}_ans"
    A0 = 0.9; aw = align(ask)
    letters = [A0 + s_ for s_, e_, w in aw if re.fullmatch(r"[ABCD]:", w)]
    CS = A0 + META[ask]["dur"] + 0.45; R = CS + 7.0; AN = R + 1.0
    dur = AN + META[ans]["dur"] + 1.5
    s = scene("q", dur, qi=i, A0=A0, letters=letters, CS=CS, R=R, AN=AN, aw=align(ans))
    add_voice(ask, s["start"] + A0); add_voice(ans, s["start"] + AN)
    SFX += [(s["start"], "whoosh"), (s["start"] + 0.55, "qstart")]
    SFX += [(s["start"] + CS + k, "tick" if k < 4 else "tick2") for k in range(7)]
    SFX.append((s["start"] + R, "victory" if i == len(QS) - 1 else "correct"))
d = META["score"]["dur"]; s = scene("score", 0.8 + d + 1.2, words=align("score"), v0=0.8); add_voice("score", s["start"] + 0.8); SFX.append((s["start"], "whoosh"))
d = META["outro"]["dur"]; s = scene("outro", 0.6 + d + 2.6, v0=0.6, vd=d); add_voice("outro", s["start"] + 0.6); SFX.append((s["start"], "whoosh")); SFX.append((s["start"] + 0.6 + d + 0.5, "impact"))
TOTAL = t
for sc in TL:
    if sc["kind"] == "score":
        ws = sc["words"]; keys = ["zero", "six", "eleven", "fourteen", "perfect"]; ts = []
        for kk in keys:
            ts.append(next(s_ for s_, e_, w in ws if norm(w) == kk) + sc["v0"])
        sc["band_t"] = ts
        SFX += [(sc["start"] + x, "pluck") for x in ts]

# ------------------------------------------------------------------ legendas (chunks)
def build_chunks():
    ch = []; cur = []
    for w in CAP_WORDS:
        if cur and (w[0] - cur[-1][1] > 0.6): ch.append(cur); cur = []
        cur.append(w)
        txt = " ".join(x[2] for x in cur)
        if len(cur) >= 7 or len(txt) > 38 or re.search(r"[.!?]$", w[2]) or (re.search(r"[,:]$", w[2]) and len(cur) >= 3):
            ch.append(cur); cur = []
    if cur: ch.append(cur)
    return ch
CHUNKS = build_chunks()
CH_T = [(c[0][0], max(c[-1][1] + 0.25, c[-1][1])) for c in CHUNKS]
for k in range(len(CH_T) - 1):
    CH_T[k] = (CH_T[k][0], min(CH_T[k][1], CHUNKS[k + 1][0][0]))

def srt():
    def fmt(x):
        ms = int(round(x * 1000)); h_, ms = divmod(ms, 3600000); m_, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f"{h_:02d}:{m_:02d}:{s_:02d},{ms:03d}"
    out = []
    for k, (c, (a, b)) in enumerate(zip(CHUNKS, CH_T), 1):
        out.append(f"{k}\n{fmt(a)} --> {fmt(b)}\n{' '.join(x[2] for x in c)}\n")
    return "\n".join(out)

# ------------------------------------------------------------------ elementos fixos
@functools.lru_cache(None)
def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2)
    g = np.clip(1 - r * 1.6, 0, 1) ** 2
    base = np.array(BG, np.float32)
    img = base + g[..., None] * np.array([34, 24, 6], np.float32)
    im = Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")
    # grade hexagonal discreta
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rr = 46
    for j in range(-1, int(H / (rr * 1.5)) + 2):
        for i in range(-1, int(W / (rr * 1.732)) + 2):
            cx = i * rr * 1.732 + (j % 2) * rr * 0.866; cy = j * rr * 1.5
            d.polygon(hexagon_pts(cx, cy, rr - 2, math.pi / 6), outline=(212, 170, 60, 10))
    im.alpha_composite(ov)
    vg = np.clip((r - 0.35) * 1.6, 0, 1)[..., None] * 0.75
    arr = np.asarray(im).astype(np.float32); arr[..., :3] *= (1 - vg)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

PART = [(random.Random(k).uniform(0, W), random.Random(k + 99).uniform(0, H), random.Random(k + 7).uniform(8, 30), random.Random(k + 3).uniform(0.8, 2.6)) for k in range(70)]
def particles(img, t, alpha=1.0):
    d = ImageDraw.Draw(img)
    for x, y, sp, r in PART:
        yy = (y - t * sp) % H; xx = x + 12 * math.sin(t * 0.4 + y)
        a = int((90 + 80 * math.sin(t * 1.3 + x)) * alpha)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(230, 190, 90, max(0, a)))

@functools.lru_cache(None)
def logo(scale=1.0):
    br = gold_text("BRAIN", F("anton", int(150 * scale)), top=(255, 255, 255), bot=(200, 200, 205), glow=False)
    ru = gold_text("RUSH", F("anton", int(150 * scale)))
    qz = gold_text("Q U I Z", F("bebas", int(76 * scale)), glow=False)
    em = emoji("brain", int(190 * scale)); hv = emoji("high_voltage", int(110 * scale))
    w = em.width + br.width + ru.width - int(70 * scale); h = br.height + qz.height - int(40 * scale)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    im.alpha_composite(glow_of(em, 20, (255, 170, 190), 0.5), (0, int(20 * scale)))
    im.alpha_composite(em, (0, int(20 * scale)))
    im.alpha_composite(hv, (int(em.width * 0.55), int(em.height * 0.62)))
    x = em.width - int(20 * scale)
    im.alpha_composite(br, (x, 0)); im.alpha_composite(ru, (x + br.width - int(60 * scale), 0))
    qy = br.height - int(48 * scale); qx = x + (br.width + ru.width - int(60 * scale)) // 2 - qz.width // 2
    d = ImageDraw.Draw(im)
    for sgn in (-1, 1):
        x0 = qx + (qz.width // 2) + sgn * (qz.width // 2 + int(10 * scale)); x1 = x0 + sgn * int(150 * scale)
        d.line((x0, qy + qz.height // 2, x1, qy + qz.height // 2), fill=GOLD + (255,), width=max(2, int(4 * scale)))
    im.alpha_composite(qz, (qx, qy))
    return im.crop(im.getbbox())

@functools.lru_cache(None)
def small_logo():
    l = logo(1.0); return l.resize((int(l.width * 0.3), int(l.height * 0.3)), Image.LANCZOS)

# ------------------------------------------------------------------ UI da pergunta
SX, SY, SW, SH = 440, 140, 1040, 440
OPT_W, OPT_H = 830, 100
OPT_POS = [(115 + OPT_W / 2, 745 + OPT_H / 2), (975 + OPT_W / 2, 745 + OPT_H / 2), (115 + OPT_W / 2, 865 + OPT_H / 2), (975 + OPT_W / 2, 865 + OPT_H / 2)]

@functools.lru_cache(None)
def option_img(text, letter, state):
    im = Image.new("RGBA", (OPT_W + 40, OPT_H + 40), (0, 0, 0, 0))
    if state == "ok":
        g = grad(OPT_W, OPT_H, GOLD_L, GOLD_D).convert("RGBA"); g.putalpha(rrect((OPT_W, OPT_H), 22, (255, 255, 255, 255)).getchannel("A"))
        im.alpha_composite(glow_of(g, 16, (255, 200, 80), 1.0).resize(g.size), (20, 20)); im.alpha_composite(g, (20, 20))
    else:
        im.alpha_composite(rrect((OPT_W, OPT_H), 22, (20, 19, 24, 235), GOLD + (255,), 2), (20, 20))
    d = ImageDraw.Draw(im)
    cx, cy, r = 20 + 58, 20 + OPT_H / 2, 34
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(20, 14, 2) if state == "ok" else GOLD)
    d.text((cx, cy + 2), letter, font=F("anton", 44), anchor="mm", fill=GOLD_L if state == "ok" else (16, 12, 4))
    fnt = F("mont", 42 if F("mont", 42).getlength(text) < OPT_W - 200 else 34)
    d.text((20 + 118, cy + 1), text, font=fnt, anchor="lm", fill=(25, 16, 2) if state == "ok" else WHITE)
    if state == "ok":
        x0, y0 = 20 + OPT_W - 70, cy
        d.line([(x0 - 18, y0), (x0 - 4, y0 + 15), (x0 + 22, y0 - 16)], fill=(25, 16, 2), width=9, joint="curve")
    return im

@functools.lru_cache(None)
def question_img(txt):
    f = F("mont", 54); lines = wrap(txt, f, 1500)
    if len(lines) > 2: f = F("mont", 46); lines = wrap(txt, f, 1600)
    if len(lines) == 2: f = F("mont", 48); lines = wrap(txt, f, 1500)
    lh = int(f.size * 1.18); asc, desc = f.getmetrics()
    out = Image.new("RGBA", (1700, lh * len(lines) + desc + 20), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); d = ImageDraw.Draw(out)
    for k, l in enumerate(lines):
        ds.text((850, 10 + asc + k * lh + 3), l, font=f, anchor="ms", fill=(0, 0, 0, 170))
        d.text((850, 10 + asc + k * lh), l, font=f, anchor="ms", fill=WHITE)
    sh = sh.filter(ImageFilter.GaussianBlur(4)); sh.alpha_composite(out)
    return sh

@functools.lru_cache(None)
def chip(txt):
    t_ = text_img(txt, F("bebas", 40), fill=GOLD_L, spacing=4, shadow=False)
    im = rrect((t_.width + 50, 54), 27, (24, 20, 10, 230), GOLD + (255,), 2)
    im.alpha_composite(t_, ((im.width - t_.width) // 2, (im.height - t_.height) // 2 + 1)); return im

@functools.lru_cache(None)
def pill(txt, size=50):
    t_ = text_img(txt, F("anton", size), fill=(24, 16, 2), shadow=False)
    w_, h_ = t_.width + 70, t_.height + 34
    g = grad(w_, h_, GOLD_L, GOLD_D).convert("RGBA"); g.putalpha(rrect((w_, h_), h_ // 2, (255, 255, 255, 255)).getchannel("A"))
    out = Image.new("RGBA", (w_ + 60, h_ + 60), (0, 0, 0, 0)); out.alpha_composite(glow_of(g, 14, (255, 190, 60), 0.9), (30, 30))
    out.alpha_composite(g, (30, 30)); out.alpha_composite(t_, (30 + 35, 30 + (h_ - t_.height) // 2)); return out

@functools.lru_cache(None)
def stage_frame():
    im = Image.new("RGBA", (SW + 60, SH + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((30, 30, 30 + SW, 30 + SH), 26, outline=GOLD + (255,), width=4)
    g = glow_of(im, 12, (255, 190, 60), 0.6); g.alpha_composite(im); return g
@functools.lru_cache(None)
def stage_mask():
    return rrect((SW, SH), 26, (255, 255, 255, 255)).getchannel("A")

def timer(frac, num, pulse, done=False, urgent=False):
    S = 300; ss = 2; im = Image.new("RGBA", (S * ss, S * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pad = 30 * ss; box = (pad, pad, S * ss - pad, S * ss - pad)
    d.ellipse((pad - 18, pad - 18, S * ss - pad + 18, S * ss - pad + 18), fill=(14, 12, 10, 235))
    d.arc(box, 0, 360, fill=(60, 52, 36), width=22 * ss)
    col = (255, 120, 60) if urgent else GOLD
    if frac > 0: d.arc(box, -90, -90 + 360 * frac, fill=col, width=22 * ss)
    im = im.resize((S, S), Image.LANCZOS)
    g = glow_of(im, 10, (255, 180, 60), 0.35); g.alpha_composite(im); im = g
    if done:
        d = ImageDraw.Draw(im); c = S / 2
        d.line([(c - 48, c + 2), (c - 14, c + 36), (c + 52, c - 40)], fill=GOLD_L, width=20, joint="curve")
    else:
        n = text_img(str(num), F("anton", 120), fill=(255, 255, 255) if not urgent else (255, 200, 170))
        paste_c(im, n, S / 2, S / 2 + 6, scale=1 + 0.3 * pulse)
    return im

def progress_dots(img, qi, t):
    d = ImageDraw.Draw(img); n = 15; gap = 34; x0 = W / 2 - gap * (n - 1) / 2; y = 116
    for k in range(n):
        x = x0 + k * gap
        if k < qi: d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=GOLD)
        elif k == qi:
            r = 9 + 2 * math.sin(t * 5); d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD_L)
        else: d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(120, 100, 60), width=2)

# ------------------------------------------------------------------ cenas do palco (SW x SH)
def kb(img, tl, z0=1.0, z1=1.12, dur=12.0, px=0.5, py=0.5, dx=0.0):
    """Ken Burns: recorte animado de img para SW x SH."""
    p = ease(tl / dur); z = z0 + (z1 - z0) * p
    iw, ih = img.size; scale = max(SW / iw, SH / ih)
    cw, ch = SW / scale / z, SH / scale / z
    cx = iw * px + dx * p * iw; cy = ih * py
    x0 = min(max(cx - cw / 2, 0), iw - cw); y0 = min(max(cy - ch / 2, 0), ih - ch)
    return img.resize((SW, SH), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")

@functools.lru_cache(None)
def stars(): return starfield(1400, 600, 7)
@functools.lru_cache(None)
def mars_big(): return sphere("mars.jpg", 1500, lon0=60, light=(-0.75, -0.45, 0.5), atmo=(0.6, 0.25, 0.1))
@functools.lru_cache(None)
def saturn_img():
    s = saturn(760); return s.resize((s.width // 2, s.height // 2), Image.LANCZOS)
@functools.lru_cache(None)
def saturn_big():
    return saturn(1400)
@functools.lru_cache(None)
def world_pacific():
    w_, h_ = 1400, 600; lon0, lon1, lat0, lat1 = 20, 380, -62, 80
    im = map_img(lon0, lon1, lat0, lat1, w_, h_, wrap360=True, sea=(8, 16, 30), land=(44, 44, 50), edge=(120, 100, 55))
    arr = np.asarray(im).astype(np.int16)
    sea = (np.abs(arr[..., 0] - 8) < 6) & (np.abs(arr[..., 1] - 16) < 6) & (np.abs(arr[..., 2] - 30) < 6)
    yy, xx = np.mgrid[0:h_, 0:w_]; lon = lon0 + xx / w_ * (lon1 - lon0); lat = lat1 - yy / h_ * (lat1 - lat0)
    east = np.interp(lat, [-70, 8, 15, 20, 30, 40, 50, 58, 66], [292, 290, 265, 255, 245, 237, 234, 222, 200])
    west = np.where(lat < -10, 147, np.where(lat < 8, 128, 100))
    pac = sea & (lon >= west) & (lon <= east) & (lat > -60) & (lat < 66)
    m = Image.fromarray((pac * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    return im, m
@functools.lru_cache(None)
def africa():
    box = (-22, 62, -38, 40)
    return map_img(*box, 1040, int(1040 * 78 / 84), hi={"818"}, sea=(8, 16, 30), land=(48, 46, 52), edge=(120, 100, 55)), box
@functools.lru_cache(None)
def australia():
    box = (106, 162, -46, -8)
    im = map_img(*box, 1100, int(1100 * 38 / 56), sea=(8, 16, 30), land=(70, 56, 38), edge=(160, 130, 70))
    d = ImageDraw.Draw(im)
    for nm, lo, la in CITIES:
        x, y = lonlat_px(lo, la, *box, *im.size); d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=WHITE, outline=(0, 0, 0), width=2)
    return im, box

CITIES = [("SYDNEY", 151.2, -33.87), ("MELBOURNE", 144.96, -37.81), ("PERTH", 115.86, -31.95), ("CANBERRA", 149.13, -35.28)]

def label(img, txt, x, y, size=34, col=WHITE, anchor="mm"):
    paste_c(img, text_img(txt, F("mont", size), fill=col), x, y)

def stage_ask(qi, tl):
    if qi == 0:
        im = kb(stars(), tl, 1.0, 1.08, 20); p = sphere("mars.jpg", 360, lon0=30 + tl * 8, atmo=(0.6, 0.25, 0.1))
        paste_c(im, halo(p, 30, (255, 120, 60), 0.35), SW / 2, SH / 2 + 4); paste_c(im, p, SW / 2, SH / 2 + 4); return im
    if qi == 1:
        im = kb(stars(), tl, 1.0, 1.08, 20, px=0.3); p = sphere("earth.jpg", 380, lon0=-170 + tl * 1.5, atmo=(0.25, 0.45, 1.0))
        paste_c(im, halo(p, 30, (80, 140, 255), 0.4), SW / 2, SH / 2 + 4); paste_c(im, p, SW / 2, SH / 2 + 4); return im
    if qi == 2:
        ss = 2; im = Image.new("RGBA", (SW * ss, SH * ss), (8, 7, 6, 255)); d = ImageDraw.Draw(im)
        gl = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon(hexagon_pts(SW, SH, 400, tl * 0.5), fill=(255, 190, 60, 50))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
        pts = hexagon_pts(SW, SH, 370, tl * 0.5)
        d.polygon(pts, fill=(40, 30, 10), outline=GOLD_L, width=16)
        im = im.resize((SW, SH), Image.BILINEAR)
        return im
    if qi == 3:
        im = underwater(SW, SH).copy(); bubbles(im, tl)
        e = emoji("whale", 300); paste_c(im, e, SW / 2 + 160 * math.sin(tl * 0.25), SH / 2 + 18 * math.sin(tl * 1.1), scale=1.0)
        return im
    if qi == 4:
        return kb(gold_bars(SW + 200, SH + 90, tl), tl, 1.0, 1.1, 14)
    if qi == 5:
        im = kb(pyramids_scene(SW + 160, SH + 70, tl), tl, 1.0, 1.1, 14, px=0.45)
        paste_c(im, emoji("camel", 120), (tl * 45) % (SW + 200) - 100, SH * 0.78); return im
    if qi == 6:
        im = Image.new("RGBA", (SW, SH), (8, 7, 6, 255)); rng = random.Random(5)
        for k in range(26):
            n = str(rng.choice([3, 4, 6, 8, 10, 12, 14, 16, 18, 25, 27, 33, 35]))
            x = (rng.uniform(0, SW) + tl * rng.uniform(-20, 20)) % SW; y = (rng.uniform(0, SH) - tl * rng.uniform(8, 25)) % SH
            paste_c(im, gold_text_cached(n, 46, 0.35), x, y)
        for k, n in enumerate(["9", "15", "21", "2"]):
            paste_c(im, gold_text_cached(n, 120, 1.0), SW * (0.2 + 0.2 * k), SH / 2 + 20 * math.sin(tl * 1.2 + k))
        return im
    if qi == 7:
        return piano_scene(SW, SH, tl)
    if qi == 8:
        base, box = australia(); im = kb(base, tl, 1.0, 1.06, 16, py=0.5)
        paste_c(im, emoji("kangaroo", 150), 400, 230 + 6 * math.sin(tl * 3)); return im
    if qi == 9:
        return kb(periodic(None, 0), tl, 1.0, 1.08, 16)
    if qi == 10:
        im = underwater(SW, SH).copy(); bubbles(im, tl, 9)
        paste_c(im, emoji("octopus", 280), SW / 2 + 40 * math.sin(tl * 0.5), SH / 2 + 25 * math.sin(tl * 1.3), scale=1 + 0.03 * math.sin(tl * 2)); return im
    if qi == 11:
        im = kb(stars(), tl, 1.0, 1.08, 20, px=0.6); s_ = saturn_img()
        paste_c(im, s_, SW / 2, SH / 2, scale=1 + 0.06 * ease(tl / 14)); return im
    if qi == 12:
        im = kb(stars(), tl, 1.0, 1.08, 20); m = sphere("moon.jpg", 400, lon0=tl * 4, light=(-0.6, -0.3, 0.75), ambient=0.03)
        paste_c(im, halo(m, 30, (200, 200, 230), 0.3), SW / 2, SH / 2 + 4); paste_c(im, m, SW / 2, SH / 2 + 4)
        x = -150 + (tl * 120) % (SW + 300); paste_c(im, emoji("rocket", 110), x, SH * 0.75 - x * 0.25); return im
    if qi == 13:
        im = kb(stars(), tl, 1.0, 1.05, 20, px=0.4); m = sphere("moon.jpg", 170, lon0=20, ambient=0.2)
        paste_c(im, halo(m, 40, (230, 230, 255), 0.5), int(SW * 0.72) + 85, 125); im.alpha_composite(m, (int(SW * 0.72), 40))
        b = emoji("bat", 200); flap = 0.75 + 0.25 * abs(math.sin(tl * 7))
        b = b.resize((200, int(200 * flap)), Image.BICUBIC)
        paste_c(im, b, (tl * 70) % (SW + 300) - 150, SH * 0.55 + 30 * math.sin(tl * 1.4)); return im
    if qi == 14:
        im = Image.new("RGBA", (SW, SH), (8, 7, 6, 255)); rng = random.Random(8)
        for k in range(22):
            n = str(rng.choice([4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 169])); x = (rng.uniform(0, SW) + tl * 15) % SW; y = (rng.uniform(0, SH) - tl * 18) % SH
            paste_c(im, gold_text_cached(n, 44, 0.3), x, y)
        paste_c(im, gold_text_cached("x²", 230, 1.0), SW / 2, SH / 2, scale=1 + 0.04 * math.sin(tl * 3)); return im

@functools.lru_cache(None)
def gold_text_cached(txt, size, alpha):
    g = gold_text(txt, F("anton", size))
    if alpha < 1: g.putalpha(g.getchannel("A").point(lambda v: int(v * alpha)))
    return g
@functools.lru_cache(None)
def periodic(hl, glowq):
    return periodic_scene(SW + 120, SH + 60, highlight=hl, glow=glowq / 10)

def stage_exp(qi, te, sc):
    """te = tempo desde o início da explicação."""
    if qi == 0:
        im = kb(mars_big(), te, 1.0, 1.15, 10, px=0.4, py=0.4)
        if te > 0.6: paste_c(im, pill("IRON OXIDE"), SW / 2, SH - 80, scale=eback((te - 0.6) / 0.4))
        if te > 1.2: paste_c(im, text_img("Fe2O3  =  RUST", F("mont", 40), fill=GOLD_L), SW / 2, 70, alpha=ease((te - 1.2) / 0.4))
        return im
    if qi == 1:
        base, m = world_pacific(); im = kb(base, te, 1.0, 1.06, 12)
        pulse = 0.55 + 0.35 * math.sin(te * 3)
        g = Image.new("RGBA", base.size, (255, 196, 70, 0)); g.putalpha(m.point(lambda v: int(v * pulse * min(1, te / 0.6))))
        im.alpha_composite(kb(g, te, 1.0, 1.06, 12))
        if te > 0.8: paste_c(im, pill("PACIFIC OCEAN"), SW / 2 - 40, SH / 2 + 30, scale=eback((te - 0.8) / 0.4))
        return im
    if qi == 2:
        if te < 3.6:
            ss = 2; im = Image.new("RGBA", (SW * ss, SH * ss), (8, 7, 6, 255)); d = ImageDraw.Draw(im)
            pts = hexagon_pts(SW, SH, 330, 0); d.polygon(pts, fill=(40, 30, 10), outline=(110, 85, 30), width=16)
            for k in range(6):
                p = (te - 0.3 - k * 0.42) / 0.3
                if p > 0:
                    a, b = pts[k], pts[(k + 1) % 6]; pp = min(1, p)
                    d.line([a, (a[0] + (b[0] - a[0]) * pp, a[1] + (b[1] - a[1]) * pp)], fill=GOLD_L, width=26)
                    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; nx, ny = (mx - SW) * 1.22 + SW, (my - SH) * 1.22 + SH
                    if p >= 1: d.text((nx, ny), str(k + 1), font=F("anton", 92), anchor="mm", fill=WHITE)
            im = im.resize((SW, SH), Image.BILINEAR)
            return im
        im = kb(honeycomb(SW + 100, SH + 50, te), te - 3.6, 1.0, 1.1, 8)
        paste_c(im, emoji("honeybee", 150), SW * 0.25 + 60 * math.sin(te), SH * 0.4 + 20 * math.sin(te * 3))
        paste_c(im, pill("6 SIDES  •  6 ANGLES", 44), SW / 2, SH - 70)
        if te < 4.0: im.putalpha(int(255 * ease((te - 3.6) / 0.4)))
        return im
    if qi == 3:
        im = underwater(SW, SH).copy(); d = ImageDraw.Draw(im)
        rows = [("whale", "BLUE WHALE", 30, "30+ m"), ("bus", "BUS", 12, "12 m"), ("elephant", "ELEPHANT", 6, "6 m")]
        for k, (e, nm, L, lab) in enumerate(rows):
            y = 90 + k * 125; p = eout((te - 0.4 - k * 0.5) / 0.9)
            if p <= 0: continue
            x0 = 200; x1 = x0 + 480 * (L / 30) * p
            d.rounded_rectangle((x0, y - 18, x1, y + 18), 18, fill=GOLD if k == 0 else (120, 140, 160))
            paste_c(im, emoji(e, 100), 110, y)
            lt = text_img(f"{nm}  {lab}", F("mont", 30)); paste_c(im, lt, x1 + 20 + lt.width / 2, y - 2, alpha=p)
        if te > 2.5: paste_c(im, pill("100+ TONS", 44), SW - 180, SH - 60, scale=eback((te - 2.5) / 0.4))
        return im
    if qi == 4:
        im = kb(gold_bars(SW + 200, SH + 90, te + 20), te, 1.05, 1.15, 10)
        dim = Image.new("RGBA", im.size, (0, 0, 0, 140)); im.alpha_composite(dim)
        paste_c(im, tile(79, "Au", "Gold", 250), SW / 2 - 200, SH / 2, scale=eback(te / 0.5))
        if te > 1.0: paste_c(im, gold_text_cached("AURUM", 110, 1.0), SW / 2 + 200, SH / 2 - 40, alpha=ease((te - 1.0) / 0.4))
        if te > 1.4: label(im, "LATIN FOR “GOLD”", SW / 2 + 200, SH / 2 + 60, 36, WHITE)
        return im
    if qi == 5:
        base, box = africa(); im = kb(base, te, 1.0, 1.15, 9, px=0.6, py=0.28)
        if te > 0.8:
            a = ease((te - 0.8) / 0.4)
            paste_c(im, pill("EGYPT", 48), SW * 0.72, SH * 0.6, scale=eback((te - 0.8) / 0.4))
            
        return im
    if qi == 6:
        im = Image.new("RGBA", (SW, SH), (8, 7, 6, 255))
        paste_c(im, gold_text_cached("2", 300, 1.0), 220, SH / 2, scale=eback(te / 0.5))
        for k, eq in enumerate(["2 ÷ 1 = 2", "2 ÷ 2 = 1"]):
            if te > 0.8 + k * 0.6: paste_c(im, text_img(eq, F("anton", 84)), 640, 130 + k * 120, alpha=ease((te - 0.8 - k * 0.6) / 0.3))
        if te > 2.2: paste_c(im, pill("ONLY EVEN PRIME", 42), 640, SH - 70, scale=eback((te - 2.2) / 0.4))
        return im
    if qi == 7:
        hw = ease((te - 0.5) / 0.5) * (1 - ease((te - 2.0) / 0.4)); hb = ease((te - 2.2) / 0.5)
        im = piano_scene(SW, SH, te + 30, hi_white=hw, hi_black=hb)
        if te > 0.5: paste_c(im, pill("52 WHITE", 40), SW * 0.25, SH - 60, scale=eback((te - 0.5) / 0.4))
        if te > 2.2: paste_c(im, pill("36 BLACK", 40), SW * 0.75, SH - 60, scale=eback((te - 2.2) / 0.4))
        if te > 3.6: paste_c(im, pill("52 + 36 = 88", 56), SW / 2, SH / 2, scale=eback((te - 3.6) / 0.4))
        return im
    if qi == 8:
        base, box = australia(); im = kb(base, te, 1.0, 1.25, 8, px=0.7, py=0.62)
        # recalcula a posição de Canberra dentro do recorte Ken Burns
        p = ease(te / 8); z = 1 + 0.25 * p; iw, ih = base.size; scale = max(SW / iw, SH / ih); cw, ch = SW / scale / z, SH / scale / z
        x0 = min(max(iw * 0.7 - cw / 2, 0), iw - cw); y0 = min(max(ih * 0.62 - ch / 2, 0), ih - ch)
        d = ImageDraw.Draw(im)
        for nm, lo, la in CITIES:
            x, y = lonlat_px(lo, la, *box, iw, ih); x, y = (x - x0) * SW / cw, (y - y0) * SH / ch
            if nm == "CANBERRA":
                r = 16 + 6 * math.sin(te * 6); d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD_L, outline=(40, 20, 0), width=3)
                if te > 0.6: paste_c(im, pill("CANBERRA", 40), x - 60, y + 70, scale=eback((te - 0.6) / 0.4))
            else:
                label(im, nm, x - 10, y - 30, 24, (190, 190, 190))
        if te > 1.6: paste_c(im, emoji("classical_building", 130), 170, SH - 150, scale=eback((te - 1.6) / 0.4)); label(im, "PARLIAMENT HOUSE", 170, SH - 60, 26) if te > 1.9 else None
        return im
    if qi == 9:
        im = kb(periodic(11, int(min(10, te * 10))), te, 1.0, 1.0, 8)
        if te > 1.0:
            dim = Image.new("RGBA", im.size, (0, 0, 0, int(160 * ease((te - 1.0) / 0.4)))); im.alpha_composite(dim)
            paste_c(im, tile(11, "Na", "Sodium", 250), SW / 2 - 200, SH / 2, scale=eback((te - 1.0) / 0.5))
        if te > 1.6: paste_c(im, gold_text_cached("NATRIUM", 100, 1.0), SW / 2 + 210, SH / 2 - 50, alpha=ease((te - 1.6) / 0.4))
        if te > 2.4: paste_c(im, emoji("salt", 110), SW / 2 + 130, SH / 2 + 80, scale=eback((te - 2.4) / 0.4)); label(im, "TABLE SALT", SW / 2 + 290, SH / 2 + 80, 34) if te > 2.6 else None
        return im
    if qi == 10:
        im = underwater(SW, SH).copy(); bubbles(im, te, 11)
        paste_c(im, emoji("octopus", 260), SW / 2, SH / 2 + 20 + 10 * math.sin(te * 1.3))
        labs = [("GILLS", SW / 2 - 300), ("GILLS", SW / 2 + 300), ("BODY", SW / 2 + 300)]
        for k, (nm, x) in enumerate(labs):
            tk = te - 0.6 - k * 0.6
            if tk > 0:
                y = 110 if k < 2 else 70
                if k == 2: y = 75
                hy = 110 if k < 2 else 300; hx = x if k != 1 else SW / 2 + 300
                if k == 1: hx, hy = SW / 2 + 300, 110
                if k == 2: hx, hy = SW / 2 + 300, 300; hx = SW / 2 + 170 if False else hx
                paste_c(im, emoji("anatomical_heart", 100), hx if k != 2 else SW / 2 - 300, hy, scale=eback(tk / 0.4) * (1 + 0.08 * math.sin(te * 8)))
                label(im, nm, (hx if k != 2 else SW / 2 - 300), hy + 72, 30, GOLD_L)
        return im
    if qi == 11:
        s_ = saturn_big(); im = kb(stars(), te, 1.0, 1.1, 10)
        z = 1 + 0.7 * ease(te / 6); paste_c(im, s_, SW / 2 + 260 * ease(te / 6), SH / 2 - 40 * ease(te / 6), scale=0.42 * z)
        if te > 1.0: paste_c(im, pill("ICE + ROCK", 46), SW / 2, SH - 70, scale=eback((te - 1.0) / 0.4))
        return im
    if qi == 12:
        im = kb(stars(), te, 1.0, 1.05, 10)
        m = moon_big(); paste_c(im, m, SW / 2, SH + 260 - 30 * ease(te / 6))
        paste_c(im, emoji("footprints", 120), SW / 2 + 260, SH - 90, scale=eback((te - 0.8) / 0.4)) if te > 0.8 else None
        if te > 0.3: paste_c(im, pill("JULY 20, 1969", 54), SW / 2, 110, scale=eback((te - 0.3) / 0.4))
        if te > 1.4: label(im, "APOLLO 11  •  NEIL ARMSTRONG", SW / 2, 210, 32, WHITE)
        return im
    if qi == 13:
        im = kb(stars(), te, 1.0, 1.05, 10); d = ImageDraw.Draw(im)
        d.line((SW / 2, 40, SW / 2, SH - 40), fill=(90, 80, 50), width=3)
        paste_c(im, emoji("chipmunk", 150), SW * 0.25, SH * 0.42 + 10 * math.sin(te * 2))
        b = emoji("bat", 170).resize((170, int(170 * (0.75 + 0.25 * abs(math.sin(te * 7))))), Image.BICUBIC)
        paste_c(im, b, SW * 0.75, SH * 0.42 + 20 * math.sin(te * 1.6))
        if te > 0.5: paste_c(im, pill("GLIDING", 40), SW * 0.25, SH - 75, scale=eback((te - 0.5) / 0.4))
        if te > 1.2: paste_c(im, pill("POWERED FLIGHT", 40), SW * 0.75, SH - 75, scale=eback((te - 1.2) / 0.4))
        if te > 0.9: label(im, "FLYING SQUIRREL", SW * 0.25, 60, 28, (200, 200, 200))
        if te > 1.6: label(im, "BAT", SW * 0.75, 60, 30, GOLD_L)
        return im
    if qi == 14:
        im = Image.new("RGBA", (SW, SH), (8, 7, 6, 255))
        rays = Image.new("RGBA", (SW, SH), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
        for k in range(16):
            a = te * 0.3 + k * math.pi / 8; d.polygon([(SW / 2, SH / 2), (SW / 2 + 900 * math.cos(a - 0.08), SH / 2 + 900 * math.sin(a - 0.08)), (SW / 2 + 900 * math.cos(a + 0.08), SH / 2 + 900 * math.sin(a + 0.08))], fill=(255, 200, 80, 26))
        im.alpha_composite(rays)
        paste_c(im, gold_text_cached("12 × 12 = 144", 150, 1.0), SW / 2, SH / 2 - 10, scale=eback(te / 0.6))
        if te > 1.0: paste_c(im, emoji("party_popper", 120), 120, SH - 100, scale=eback((te - 1.0) / 0.4)); paste_c(im, emoji("party_popper", 120).transpose(Image.FLIP_LEFT_RIGHT), SW - 120, SH - 100, scale=eback((te - 1.0) / 0.4))
        return im

@functools.lru_cache(None)
def moon_big(): return sphere("moon.jpg", 900, lon0=10, light=(-0.5, -0.6, 0.6), ambient=0.03)

def compose_stage(img, st, alpha=1.0, scale=1.0, cx=SX + SW / 2, cy=SY + SH / 2):
    st = st.convert("RGBA").copy(); st.putalpha(Image.fromarray(np.minimum(np.asarray(st.getchannel("A")), np.asarray(stage_mask()))))
    fr = stage_frame().copy(); fr.alpha_composite(st, (30, 30))
    paste_c(img, fr, cx, cy, alpha=alpha, scale=scale)

# ------------------------------------------------------------------ render por cena
def render_q(img, sc, tq):
    qi = sc["qi"]; q = QS[qi]; R, CS = sc["R"], sc["CS"]; final = qi == 14
    progress_dots(img, qi, tq)
    paste_c(img, small_logo(), 210, 66)
    paste_c(img, chip(q[0]), W / 2, 66, alpha=ease(tq / 0.4))
    # coluna esquerda
    paste_c(img, text_img("QUESTION" if not final else "FINAL", F("bebas", 44), fill=GOLD, spacing=5), 220, 250)
    paste_c(img, gold_text_cached(f"{qi+1:02d}", 190, 1.0), 220, 380, scale=eback(tq / 0.5) if tq < 0.5 else 1.0)
    paste_c(img, text_img("/ 15", F("bebas", 56), fill=(150, 150, 150)), 220, 500)
    # palco
    EX = R + 1.6
    st = stage_ask(qi, tq) if tq < EX else stage_exp(qi, tq - EX, sc)
    if EX <= tq < EX + 0.35:
        a = stage_ask(qi, tq); b = st; b = b.copy(); b.putalpha(int(255 * ease((tq - EX) / 0.35))); a.alpha_composite(b); st = a
    compose_stage(img, st, alpha=ease(tq / 0.45), scale=0.92 + 0.08 * eout(tq / 0.6))
    # timer
    if tq < CS: frac, num, pulse = 1.0, 7, 0
    elif tq < R:
        e = tq - CS; frac = 1 - e / 7.0; num = 7 - int(e); pulse = max(0, 1 - (e % 1) / 0.25)
    else: frac, num, pulse = 1.0, 0, 0
    tim = timer(frac, num, pulse, done=tq >= R, urgent=(CS + 4 <= tq < R))
    paste_c(img, tim, 1700, 360, alpha=ease(tq / 0.5), scale=1 + (0.12 * max(0, 1 - (tq - R) / 0.4) if tq >= R else 0))
    if tq < R and tq >= CS: paste_c(img, text_img("SECONDS", F("bebas", 36), fill=(170, 170, 170), spacing=4), 1700, 540)
    # pergunta
    qa = ease((tq - 0.5) / 0.4); paste_c(img, question_img(q[1]), W / 2, 664 + 20 * (1 - qa), alpha=qa)
    # alternativas
    for k, opt in enumerate(q[2]):
        t0 = sc["letters"][k] - 0.1 if k < len(sc["letters"]) else 1.5 + k * 0.4
        p = eout((tq - t0) / 0.35)
        if p <= 0: continue
        cx, cy = OPT_POS[k]; L = "ABCD"[k]
        if tq >= R and k == q[3]:
            pp = (tq - R) / 0.45; sc_ = 1 + 0.07 * math.sin(min(pp, 1) * math.pi)
            paste_c(img, option_img(opt, L, "ok"), cx, cy, scale=sc_)
        else:
            a = p if tq < R else p * (1 - 0.68 * ease((tq - R) / 0.3))
            paste_c(img, option_img(opt, L, "n"), cx + 40 * (1 - p) * (-1 if k % 2 == 0 else 1), cy, alpha=a)
    # flash na revelação
    if R <= tq < R + 0.25:
        fl = Image.new("RGBA", (W, H), (255, 220, 140, int(70 * (1 - (tq - R) / 0.25)))); img.alpha_composite(fl)

def render_intro1(img, sc, tl):
    a = 1 - ease((tl - sc["dur"] + 0.4) / 0.4)
    if tl < 0.55:
        r = 4 + 12 * eout(tl / 0.55); d = ImageDraw.Draw(img)
        g = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((100 - r * 2.5, 100 - r * 2.5, 100 + r * 2.5, 100 + r * 2.5), fill=(255, 200, 80, 120))
        paste_c(img, g.filter(ImageFilter.GaussianBlur(12)), W / 2, H / 2)
        d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=GOLD_L)
        return
    p = (tl - 0.55) / 0.6
    particles(img, tl, ease(p) * a)
    q = gold_text_cached("?", 420, 1.0)
    paste_c(img, q, W / 2, H / 2 - 10, scale=(0.1 + 0.9 * eback(p)) * (1 + 0.04 * (tl - 1.1)) if p < 1 else 1 + 0.04 * (tl - 1.1), alpha=a)
    if p < 1: ImageDraw.Draw(img).ellipse((W / 2 - 16, H / 2 + 150 - 16, W / 2 + 16, H / 2 + 150 + 16), fill=GOLD_L + (int(255 * (1 - p)),))

def render_intro2(img, sc, tl):
    particles(img, tl + 10)
    a = ease(tl / 0.3) * (1 - ease((tl - sc["dur"] + 0.3) / 0.3))
    lg = logo(1.0).copy()
    if 0.5 < tl < 1.6:  # brilho passando
        sx = (tl - 0.5) / 1.1 * (lg.width + 300) - 150
        sh = Image.new("RGBA", lg.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(sx, 0), (sx + 70, 0), (sx - 60, lg.height), (sx - 130, lg.height)], fill=(255, 255, 240, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); m = np.minimum(np.asarray(sh.getchannel("A")), np.asarray(lg.getchannel("A")))
        sh.putalpha(Image.fromarray(m)); lg.alpha_composite(sh)
    paste_c(img, halo(lg, 40, (255, 180, 60), 0.35), W / 2, H / 2 - 20, alpha=a)
    paste_c(img, lg, W / 2, H / 2 - 20, scale=(0.82 + 0.18 * eback(tl / 0.7)) * (1 + 0.015 * tl), alpha=a)
    if tl > 1.8: paste_c(img, text_img("THINK FAST  •  KNOW MORE", F("bebas", 48), fill=(200, 200, 200), spacing=6), W / 2, H / 2 + 190, alpha=ease((tl - 1.8) / 0.5) * a)

MONT = [(0, 3), (3, 5), (11, 4), (5, 4), (1, 3), (9, 6), (12, 3), (13, 4)]
def render_intro3(img, sc, tl):
    particles(img, tl + 20)
    k = int(tl / 1.35) % len(MONT); qi, off = MONT[k]; te = tl % 1.35
    st = stage_ask(qi, off + te)
    if qi == 9: st = stage_exp(9, 3 + te, None)
    compose_stage(img, st, alpha=ease(tl / 0.4), scale=1.0 + 0.03 * te, cy=430)
    ws = sc["words"]; v0 = sc["v0"]
    t7 = next(s_ for s_, e_, w in ws if norm(w) == "seven") + v0
    tb = next(s_ for s_, e_, w in ws if norm(w) == "lets") + v0
    if tl < t7 - 0.1: txt, t0 = "15 QUESTIONS", 0.2
    elif tl < tb - 0.1: txt, t0 = "7 SECONDS EACH", t7
    else: txt, t0 = "LET'S PLAY!", tb
    paste_c(img, gold_text_cached(txt, 120, 1.0), W / 2, 820, scale=eback((tl - t0) / 0.35))

def render_score(img, sc, tl):
    particles(img, tl + 30)
    rays = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
    for k in range(18):
        a = tl * 0.25 + k * math.pi / 9; d.polygon([(450, 450), (450 + 600 * math.cos(a - 0.07), 450 + 600 * math.sin(a - 0.07)), (450 + 600 * math.cos(a + 0.07), 450 + 600 * math.sin(a + 0.07))], fill=(255, 200, 80, 22))
    paste_c(img, rays, 520, 520)
    tr = emoji("trophy", 256)
    paste_c(img, glow_of(tr.resize((380, 380)), 40, (255, 190, 60), 0.6), 520, 500 + 10 * math.sin(tl * 2))
    paste_c(img, tr, 520, 500 + 10 * math.sin(tl * 2), scale=(380 / 256) * eback(tl / 0.6))
    paste_c(img, gold_text_cached("YOUR SCORE", 90, 1.0), 520, 160, alpha=ease(tl / 0.4))
    cur = -1
    for k, bt in enumerate(sc["band_t"]):
        if tl >= bt - 0.15: cur = k
    for k, (rg, nm) in enumerate(BANDS):
        bt = sc["band_t"][k] - 0.15
        if tl < bt: continue
        p = eout((tl - bt) / 0.35); y = 230 + k * 140; on = (k == cur)
        box = band_img(rg, nm, on)
        paste_c(img, box, 1360 + 60 * (1 - p), y + 50, alpha=p)

@functools.lru_cache(None)
def band_img(rg, nm, on):
    w_, h_ = 760, 112
    if on:
        g = grad(w_, h_, GOLD_L, GOLD_D).convert("RGBA"); g.putalpha(rrect((w_, h_), 24, (255, 255, 255, 255)).getchannel("A")); im = g
        tc, nc = (24, 14, 2), (24, 14, 2)
    else:
        im = rrect((w_, h_), 24, (22, 20, 24, 240), GOLD + (255,), 2); tc, nc = GOLD_L, WHITE
    d = ImageDraw.Draw(im)
    d.text((40, h_ / 2 + 2), rg, font=F("anton", 62), anchor="lm", fill=tc)
    d.text((250, h_ / 2 + 2), nm, font=F("mont", 40), anchor="lm", fill=nc)
    return im

def render_outro(img, sc, tl):
    particles(img, tl + 40)
    lg = logo(1.0); paste_c(img, halo(lg, 40, (255, 180, 60), 0.3), W / 2, 380)
    paste_c(img, lg, W / 2, 380, scale=0.9 + 0.1 * eback(tl / 0.6))
    if tl > 1.0:
        p = eback((tl - 1.0) / 0.4); pul = 1 + 0.04 * math.sin(tl * 5)
        paste_c(img, sub_btn(), W / 2, 700, scale=p * pul)
    if tl > 2.0: paste_c(img, text_img("COMMENT YOUR SCORE BELOW!", F("bebas", 56), fill=(210, 210, 210), spacing=5), W / 2, 850, alpha=ease((tl - 2.0) / 0.4))
    end = sc["v0"] + sc["vd"] + 0.5
    if tl > end: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ease((tl - end - 1.5) / 0.6)))))

@functools.lru_cache(None)
def sub_btn():
    t_ = text_img("SUBSCRIBE FOR MORE QUIZZES", F("anton", 64), fill=WHITE, shadow=False)
    w_, h_ = t_.width + 200, t_.height + 50
    im = rrect((w_, h_), h_ // 2, (205, 28, 36, 255)); d = ImageDraw.Draw(im)
    cx, cy = 70, h_ / 2; d.polygon([(cx - 18, cy - 24), (cx - 18, cy + 24), (cx + 24, cy)], fill=WHITE)
    im.alpha_composite(t_, (120, (h_ - t_.height) // 2))
    out = Image.new("RGBA", (w_ + 60, h_ + 60), (0, 0, 0, 0)); out.alpha_composite(glow_of(im, 18, (255, 60, 60), 0.6), (30, 30)); out.alpha_composite(im, (30, 30)); return out

# ------------------------------------------------------------------ legenda queimada
@functools.lru_cache(maxsize=256)
def cap_img(k, wi):
    words = [x[2] for x in CHUNKS[k]]; f = F("mont", 38); sp = f.getlength(" ")
    tw = int(f.getlength(" ".join(words))) + 8; asc, desc = f.getmetrics(); th = asc + desc
    im = rrect((tw + 60, th + 26), 18, (0, 0, 0, 150)); d = ImageDraw.Draw(im); x = 30
    for j, w in enumerate(words):
        d.text((x, 13 + asc), w, font=f, anchor="ls", fill=GOLD_L if j == wi else WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
        x += f.getlength(w) + sp
    return im

def draw_caption(img, t):
    for k, (a, b) in enumerate(CH_T):
        if a <= t < b:
            wi = 0
            for j, w in enumerate(CHUNKS[k]):
                if t >= w[0]: wi = j
            paste_c(img, cap_img(k, wi), W / 2, 1030); return

# ------------------------------------------------------------------ frame
def frame(t):
    img = background().copy()
    sc = next((s for s in TL if s["start"] <= t < s["start"] + s["dur"]), TL[-1]); tl = t - sc["start"]
    k = sc["kind"]
    if k == "q": particles(img, t, 0.5); render_q(img, sc, tl)
    elif k == "intro1": img = Image.new("RGBA", (W, H), (0, 0, 0, 255)) if tl < 0.55 else img; render_intro1(img, sc, tl)
    elif k == "intro2": render_intro2(img, sc, tl)
    elif k == "intro3": render_intro3(img, sc, tl)
    elif k == "score": render_score(img, sc, tl)
    elif k == "outro": render_outro(img, sc, tl)
    # transição dourada nas trocas de cena
    for s in TL[1:]:
        dt = t - s["start"]
        if -0.3 <= dt < 0.3:
            p = (dt + 0.3) / 0.6; x = -400 + p * (W + 800)
            band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(band)
            d.polygon([(x - 260, 0), (x + 120, 0), (x - 120, H), (x - 500, H)], fill=(10, 8, 4, 255))
            d.polygon([(x + 120, 0), (x + 170, 0), (x - 70, H), (x - 120, H)], fill=GOLD_L + (255,))
            d.polygon([(x - 300, 0), (x - 260, 0), (x - 500, H), (x - 540, H)], fill=GOLD + (255,))
            img.alpha_composite(band)
    if not (k == "outro" and tl > sc["v0"] + sc["vd"] + 0.6): draw_caption(img, t)
    return img.convert("RGB")

# ------------------------------------------------------------------ áudio
SR = 44100
def load_voice(name):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f"{VOZ}/{name}.wav", "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def env(n, a, d):
    x = np.arange(n) / SR; return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)

def sfx(kind):
    rng = np.random.default_rng(abs(hash(kind)) % 2 ** 32)
    if kind == "tick" or kind == "tick2":
        n = int(0.09 * SR); x = np.arange(n) / SR; f = 1900 if kind == "tick" else 2500
        return (np.sin(2 * np.pi * f * x) * 0.5 + rng.normal(0, 0.25, n)) * env(n, 0.001, 0.012) * 0.55
    if kind == "correct":
        n = int(1.6 * SR); x = np.arange(n) / SR; out = np.zeros(n)
        for k, (f, dt) in enumerate([(1046.5, 0), (1568, 0.09), (2093, 0.18)]):
            i0 = int(dt * SR); xx = x[: n - i0]
            out[i0:] += (np.sin(2 * np.pi * f * xx) + 0.3 * np.sin(2 * np.pi * f * 2.01 * xx)) * np.exp(-xx / 0.45) * 0.28
        return out
    if kind == "victory":
        n = int(2.4 * SR); x = np.arange(n) / SR; out = np.zeros(n)
        for k, f in enumerate([523.25, 659.25, 783.99, 1046.5, 1318.5]):
            i0 = int(k * 0.11 * SR); xx = x[: n - i0]
            out[i0:] += (np.sin(2 * np.pi * f * xx) + 0.4 * np.sin(2 * np.pi * f * 2 * xx)) * np.exp(-xx / 0.7) * 0.22
        return out + sfx("impact")[:n] * 0.5 if len(sfx("impact")) >= n else out
    if kind == "impact":
        n = int(2.6 * SR); x = np.arange(n) / SR
        f = 55 * np.exp(-x * 1.2) + 28; ph = 2 * np.pi * np.cumsum(f) / SR
        boom = np.sin(ph) * np.exp(-x / 0.8) * 0.9
        nz = rng.normal(0, 1, n); nz = np.convolve(nz, np.ones(30) / 30, "same") * np.exp(-x / 0.25) * 0.5
        return boom + nz
    if kind == "whoosh":
        n = int(0.7 * SR); x = np.arange(n) / SR; nz = rng.normal(0, 1, n)
        k = np.clip((x / 0.7), 0, 1); out = np.zeros(n); w_ = 8
        sm = np.convolve(nz, np.ones(w_) / w_, "same")
        out = (nz - sm) * np.sin(np.pi * k) ** 2 * 0.22 + sm * np.sin(np.pi * k) ** 2 * 0.25
        return out
    if kind == "qstart":
        n = int(0.5 * SR); x = np.arange(n) / SR; f = 500 + 700 * x / 0.5
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / 0.5) * 0.12
    if kind == "pluck":
        n = int(1.0 * SR); x = np.arange(n) / SR
        return (np.sin(2 * np.pi * 880 * x) + 0.5 * np.sin(2 * np.pi * 1320 * x)) * np.exp(-x / 0.3) * 0.2
    raise ValueError(kind)

def music(N):
    """Trilha de suspense gerada (loop de 4 compassos, 96 bpm)."""
    beat = 60 / 96; bar = 4 * beat; L = int(4 * bar * SR); x = np.arange(L) / SR
    roots = [55.0, 43.65, 49.0, 41.2]; chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [164.8, 207.7, 246.9]]
    drone = np.zeros(L); pad = np.zeros(L); pulse = np.zeros(L); hats = np.zeros(L); kick = np.zeros(L)
    rng = np.random.default_rng(1)
    for b in range(4):
        i0, i1 = int(b * bar * SR), int((b + 1) * bar * SR); xx = x[i0:i1] - x[i0]; e = np.minimum(1, xx / 0.4) * np.minimum(1, (bar - xx) / 0.3)
        f = roots[b]; drone[i0:i1] = sum(np.sin(2 * np.pi * f * h * xx) / h for h in range(1, 7)) * e * 0.25
        pad[i0:i1] = sum(np.sin(2 * np.pi * c * xx + 0.4 * np.sin(2 * np.pi * 0.3 * xx)) for c in chords[b]) * e * 0.06
        for s8 in range(8):
            j0 = i0 + int(s8 * beat / 2 * SR); n = int(0.3 * SR); xs = np.arange(n) / SR
            pulse[j0:j0 + n] += np.sin(2 * np.pi * f * 2 * xs) * np.exp(-xs / 0.09)[: len(pulse[j0:j0 + n])][:n] * 0.35 if j0 + n <= L else 0
            m = int(0.04 * SR); nz = rng.normal(0, 1, m); nz = nz - np.convolve(nz, np.ones(4) / 4, "same")
            hats[j0:j0 + m] += nz * np.exp(-np.arange(m) / SR / 0.012) * (0.14 if s8 % 2 else 0.07)
        for s4 in (0, 2):
            j0 = i0 + int(s4 * beat * SR); n = int(0.4 * SR); xs = np.arange(n) / SR
            kick[j0:j0 + n] += np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-xs * 30)) / SR) * np.exp(-xs / 0.15) * 0.7
    def tile(a): return np.tile(a, N // L + 1)[:N]
    return tile(drone), tile(pad), tile(pulse), tile(hats), tile(kick)

def smooth(a, sec):
    n = max(1, int(sec * SR)); c = np.cumsum(np.concatenate([np.zeros(n // 2 + 1), a, np.full(n, a[-1])]))
    return ((c[n:n + len(a)] - c[:len(a)]) / n).astype(np.float32)

def build_audio(path):
    N = int((TOTAL + 0.5) * SR)
    voice = np.zeros(N, np.float32)
    for at, name in AUD:
        v = load_voice(name); i = int(at * SR); voice[i:i + len(v)] += v[: N - i]
    voice *= 0.9 / max(1e-6, np.abs(voice).max())
    drone, pad, pulse, hats, kick = music(N)
    tt = np.arange(N) / SR
    g_d = np.ones(N) * 0.8; g_p = np.zeros(N); g_h = np.zeros(N); g_k = np.zeros(N)
    for sc in TL:
        i0, i1 = int(sc["start"] * SR), int((sc["start"] + sc["dur"]) * SR)
        if sc["kind"] in ("q",):
            g_p[i0:i1] = 0.8; g_h[i0:i1] = 0.8; g_k[i0:i1] = 0.35 if sc["qi"] < 14 else 0.9
            c0, c1 = int((sc["start"] + sc["CS"]) * SR), int((sc["start"] + sc["R"]) * SR)
            g_h[c0:c1] = 0.3; g_k[c0:c1] = 0.15
        elif sc["kind"] == "intro3": g_p[i0:i1] = 0.6; g_h[i0:i1] = 0.6
        elif sc["kind"] in ("score",): g_p[i0:i1] = 0.6; g_h[i0:i1] = 0.7; g_k[i0:i1] = 0.3
        elif sc["kind"] == "outro": g_p[i0:i1] = 0.6; g_h[i0:i1] = 0.4
    g_d[: int(1.0 * SR)] = np.linspace(0, 0.8, int(1.0 * SR))
    g = [smooth(a, 0.5) for a in (g_d, g_p, g_h, g_k)]
    mus = drone * g[0] + pad * 3 * g[0] + pulse * g[1] + hats * g[2] + kick * g[3]
    # termina a música no impacto final
    endt = TL[-1]["start"] + TL[-1]["v0"] + TL[-1]["vd"] + 0.5
    mus *= np.clip((endt + 0.05 - tt) / 0.1, 0, 1)
    act = smooth((np.abs(voice) > 0.02).astype(np.float32), 0.35); act = np.clip(act * 3, 0, 1)
    duck = smooth(act, 0.25)
    mus = mus * (0.42 - 0.27 * duck)
    fx = np.zeros(N)
    for at, kind in SFX:
        s_ = sfx(kind); i = int(at * SR); fx[i:i + len(s_)] += s_[: N - i]
    mix = voice + mus * 0.55 + fx * 0.8
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    import soundfile as sf
    sf.write(path, mix.astype(np.float32), SR)

# ------------------------------------------------------------------ main
def render_range(a, b, out):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(a, b): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    if "--info" in sys.argv:
        print("TOTAL", round(TOTAL, 2))
        for s in TL: print(s["kind"], s.get("qi", ""), round(s["start"], 2), round(s["dur"], 2))
        sys.exit()
    if "--qframes" in sys.argv:
        out = []
        for sc in TL:
            if sc["kind"] != "q": continue
            for dt in (5.0, sc["R"] + 1.6 + 1.0, sc["R"] + 1.6 + 4.5):
                x = sc["start"] + dt; frame(x).save(f"{WORK}/q{sc['qi']:02d}_{dt:05.1f}.png"); out.append(x)
        sys.exit()
    if "--frames" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        for x in ts: frame(x).save(f"{WORK}/f_{x:07.2f}.png"); print("ok", x)
        sys.exit()
    if "--part" in sys.argv:
        i, n = int(sys.argv[-2]), int(sys.argv[-1]); NF = int(TOTAL * FPS)
        a, b = NF * i // n, NF * (i + 1) // n; render_range(a, b, f"{WORK}/part{i}.mp4"); sys.exit()
    # completo
    open(f"{WORK}/brainrush01.srt", "w").write(srt())
    build_audio(f"{WORK}/audio.wav")
    n = int(os.environ.get("JOBS", "4"))
    ps = [subprocess.Popen([sys.executable, __file__, "--part", str(i), str(n)]) for i in range(n)]
    for p in ps: p.wait()
    open(f"{WORK}/parts.txt", "w").write("".join(f"file 'part{i}.mp4'\n" for i in range(n)))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{WORK}/parts.txt", "-i", f"{WORK}/audio.wav",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{WORK}/brainrush01.mp4"], check=True)
    print("FIM", TOTAL)
