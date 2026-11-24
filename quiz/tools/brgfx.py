"""Helpers gráficos do BrainRush Quiz (fontes, texto dourado, mapas, cenas)."""
import json, math, functools, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from planets import sphere, saturn

A = "/tmp/claude-0/quiz_assets/"
GOLD = (222, 180, 70); GOLD_L = (255, 226, 140); GOLD_D = (168, 120, 30)
WHITE = (245, 245, 245); BG = (6, 6, 8)

@functools.lru_cache(None)
def F(name, size):
    p = {"anton": "Anton.ttf", "bebas": "BebasNeue.ttf", "mont": "Montserrat-ExtraBold.ttf"}[name]
    return ImageFont.truetype("/root/.fonts/" + p, size)

def ease(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def eout(x):
    x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3
def eback(x):
    x = min(max(x, 0.0), 1.0); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def grad(w, h, top, bot):
    t = np.linspace(0, 1, h)[:, None, None]
    g = np.array(top, float) * (1 - t) + np.array(bot, float) * t
    return Image.fromarray(np.broadcast_to(g, (h, w, 3)).astype(np.uint8), "RGB")

def text_img(txt, font, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), spacing=0, shadow=True):
    """RGBA com o texto (opcionalmente com letter-spacing e sombra)."""
    if spacing:
        ws = [font.getbbox(c)[2] - font.getbbox(c)[0] if c != " " else font.size * 0.3 for c in txt]
        tw = int(sum(ws) + spacing * (len(txt) - 1))
    else:
        b = font.getbbox(txt, stroke_width=stroke); tw = b[2]
    asc, desc = font.getmetrics(); th = asc + desc + 2 * stroke
    pad = 24
    im = Image.new("RGBA", (tw + 2 * pad + 2 * stroke, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def put(dd, col, sw=stroke, off=(0, 0)):
        if spacing:
            x = pad + stroke
            for c, w in zip(txt, ws):
                dd.text((x + off[0], pad + off[1]), c, font=font, fill=col, stroke_width=sw, stroke_fill=stroke_fill if col != (0, 0, 0, 160) else col)
                x += w + spacing
        else:
            dd.text((pad + stroke + off[0], pad + off[1]), txt, font=font, fill=col, stroke_width=sw, stroke_fill=stroke_fill if col != (0, 0, 0, 160) else col)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); put(ImageDraw.Draw(sh), (0, 0, 0, 160), off=(0, max(2, font.size // 18)))
        sh = sh.filter(ImageFilter.GaussianBlur(max(2, font.size // 14)))
        im.alpha_composite(sh)
    put(d, fill)
    return im.crop(im.getbbox()) if im.getbbox() else im

def gold_text(txt, font, spacing=0, glow=True, top=GOLD_L, bot=GOLD_D, stroke=0):
    m = text_img(txt, font, fill=(255, 255, 255), spacing=spacing, shadow=False, stroke=stroke, stroke_fill=(255, 255, 255))
    a = m.getchannel("A")
    g = grad(m.width, m.height, top, bot).convert("RGBA"); g.putalpha(a)
    pad = 30
    out = Image.new("RGBA", (m.width + 2 * pad, m.height + 2 * pad), (0, 0, 0, 0))
    if glow:
        gl = Image.new("RGBA", out.size, (0, 0, 0, 0)); gl.paste((255, 190, 60, 0), (0, 0) + out.size)
        ga = Image.new("L", out.size, 0); ga.paste(a, (pad, pad)); ga = ga.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55))
        gl.putalpha(ga); out.alpha_composite(gl)
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); sa = Image.new("L", out.size, 0); sa.paste(a, (pad, pad + max(2, font.size // 20)))
    sh.putalpha(sa.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.7))); out.alpha_composite(sh)
    out.alpha_composite(g, (pad, pad))
    return out

def wrap(txt, font, maxw):
    words = txt.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def rrect(size, r, fill, outline=None, width=0):
    im = Image.new("RGBA", (size[0] * 2, size[1] * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] * 2 - 1, size[1] * 2 - 1), r * 2, fill=fill, outline=outline, width=width * 2)
    return im.resize(size, Image.LANCZOS)

def paste_c(dst, src, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        src = src.resize((max(1, int(src.width * scale)), max(1, int(src.height * scale))), Image.BICUBIC)
    if alpha < 1.0:
        if alpha <= 0: return
        src = src.copy(); src.putalpha(src.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - src.width / 2), int(cy - src.height / 2)
    if x >= dst.width or y >= dst.height or x + src.width <= 0 or y + src.height <= 0: return
    dst.alpha_composite(src, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))

@functools.lru_cache(None)
def emoji(name, size):
    im = Image.open(A + f"e_{name}_3d.png").convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)

def glow_of(im, radius=18, color=(255, 200, 80), strength=0.8):
    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(min(255, v * strength)))
    g = Image.new("RGBA", im.size, color + (0,)); g.putalpha(a); return g

# ---------- estrelas / fundos ----------
@functools.lru_cache(None)
def starfield(w, h, seed=1, n=500):
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (3, 3, 6, 255)); d = ImageDraw.Draw(im)
    neb = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dn = ImageDraw.Draw(neb)
    for _ in range(6):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(80, 260)
        c = [(40, 30, 70), (60, 40, 20), (20, 30, 60)][rng.integers(3)]
        dn.ellipse((x - r, y - r, x + r, y + r), fill=c + (70,))
    im.alpha_composite(neb.filter(ImageFilter.GaussianBlur(90)))
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h); b = int(rng.uniform(80, 255)); s = rng.choice([0.6, 0.8, 1.2, 1.8], p=[.5, .3, .15, .05])
        d.ellipse((x - s, y - s, x + s, y + s), fill=(b, b, min(255, b + 20), 255))
    return im

@functools.lru_cache(None)
def underwater(w, h):
    im = grad(w, h, (12, 70, 110), (2, 10, 25)).convert("RGBA")
    rays = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
    rng = random.Random(4)
    for i in range(9):
        x = rng.uniform(-100, w); ww = rng.uniform(30, 90)
        d.polygon([(x, 0), (x + ww, 0), (x + ww * 3 + 200, h), (x + 200, h)], fill=(180, 230, 255, 26))
    im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(18)))
    return im

def bubbles(img, t, seed=3, n=40):
    d = ImageDraw.Draw(img); rng = random.Random(seed); w, h = img.size
    for i in range(n):
        x = rng.uniform(0, w) + 10 * math.sin(t * 1.5 + i); sp = rng.uniform(25, 70)
        y = (rng.uniform(0, h) - t * sp) % h; r = rng.uniform(1.5, 5)
        d.ellipse((x - r, y - r, x + r, y + r), outline=(200, 240, 255, 120), width=1)

# ---------- mapas (world-atlas 50m) ----------
@functools.lru_cache(None)
def _topo():
    tj = json.load(open(A + "package/countries-50m.json"))
    sc, tr = tj["transform"]["scale"], tj["transform"]["translate"]
    arcs = []
    for arc in tj["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)
    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    countries = []
    for g in tj["objects"]["countries"]["geometries"]:
        polys = []
        if g["type"] == "Polygon": polys = [g["arcs"]]
        elif g["type"] == "MultiPolygon": polys = g["arcs"]
        for p in polys:
            countries.append((g.get("id"), g["properties"].get("name"), [ring(r) for r in p]))
    return countries

def map_img(lon0, lon1, lat0, lat1, W, H, land=(38, 38, 44), edge=(110, 90, 50), sea=(8, 14, 26), hi=None, hi_fill=GOLD, wrap360=False):
    """Mapa equiretangular vetorial. hi = conjunto de ids de países em destaque."""
    ss = 2; im = Image.new("RGBA", (W * ss, H * ss), sea + (255,)); d = ImageDraw.Draw(im)
    def proj(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * W * ss, (lat1 - lat) / (lat1 - lat0) * H * ss)
    for cid, name, rings in _topo():
        for ri, r in enumerate(rings):
            if ri > 0: continue
            pts = []; prev = None
            for lon, lat in r:
                if wrap360 and lon < 0: lon += 360
                if prev is not None:
                    while lon - prev > 180: lon -= 360
                    while lon - prev < -180: lon += 360
                pts.append((lon, lat)); prev = lon
            for off in (-360, 0, 360):
                pp = [proj(lo + off, la) for lo, la in pts]
                xs = [p[0] for p in pp]
                if max(xs) < 0 or min(xs) > W * ss or len(pp) < 3: continue
                f = hi_fill if hi and cid in hi else land
                d.polygon(pp, fill=f + (255,), outline=edge + (255,), width=ss)
    return im.resize((W, H), Image.LANCZOS)

def lonlat_px(lon, lat, lon0, lon1, lat0, lat1, W, H):
    return ((lon - lon0) / (lon1 - lon0) * W, (lat1 - lat) / (lat1 - lat0) * H)

# ---------- desenhos procedurais ----------
def hexagon_pts(cx, cy, r, rot=0.0):
    return [(cx + r * math.cos(rot + k * math.pi / 3), cy + r * math.sin(rot + k * math.pi / 3)) for k in range(6)]

def pyramids_scene(w, h, t):
    im = grad(w, h, (40, 22, 40), (230, 130, 60)).convert("RGBA")
    d = ImageDraw.Draw(im)
    sx, sy = w * 0.72, h * 0.52 - t * 3
    for r, a in [(140, 30), (90, 60), (55, 255)]:
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 210, 120, a))
    im = im.filter(ImageFilter.GaussianBlur(1)); d = ImageDraw.Draw(im)
    base = h * 0.78
    for (cx, hw, hh) in [(w * 0.30, 250, 260), (w * 0.56, 190, 200), (w * 0.76, 110, 120)]:
        apex = (cx, base - hh)
        d.polygon([apex, (cx - hw, base), (cx + hw * 0.15, base)], fill=(205, 140, 70, 255))
        d.polygon([apex, (cx + hw * 0.15, base), (cx + hw, base)], fill=(120, 70, 40, 255))
    d.rectangle((0, base, w, h), fill=(190, 125, 65, 255))
    for i in range(6):
        y = base + 12 + i * 14
        d.line((0, y, w, y + 6), fill=(170, 110, 55, 255), width=3)
    return im

def piano_scene(w, h, t, hi_white=None, hi_black=None, show_counts=0.0):
    im = Image.new("RGBA", (w, h), (10, 10, 12, 255)); d = ImageDraw.Draw(im)
    kw = 34; n = 52; total = kw * n; x0 = (w - total) / 2 - 40 * math.sin(t * 0.3)
    top, bot = h * 0.18, h * 0.92
    press = int((t * 6) % 60) - 4
    for i in range(n):
        x = x0 + i * kw
        c = (250, 248, 240) if i != press else (255, 214, 110)
        if hi_white is not None and hi_white > 0: c = tuple(int(c[j] * (1 - hi_white) + GOLD_L[j] * hi_white) for j in range(3))
        d.rounded_rectangle((x + 1, top, x + kw - 1, bot), 4, fill=c)
    pat = [1, 1, 0, 1, 1, 1, 0]  # A0 começa: A# entre A-B
    for i in range(n - 1):
        if pat[(i) % 7]:
            x = x0 + (i + 1) * kw - kw * 0.32
            c = (16, 16, 18) if hi_black is None or hi_black <= 0 else tuple(int(16 * (1 - hi_black) + v * hi_black) for v in GOLD_D)
            d.rounded_rectangle((x, top, x + kw * 0.64, top + (bot - top) * 0.62), 3, fill=c)
    d.rectangle((0, 0, w, top), fill=(20, 12, 8, 255))
    d.rectangle((0, top - 6, w, top), fill=(150, 30, 30, 255))
    return im

def periodic_scene(w, h, highlight=None, glow=0.0, focus=None):
    """Tabela periódica estilizada (18 colunas)."""
    layout = {1: (1, 1), 2: (1, 18)}
    rows = [(3, 2, [1, 2] + list(range(13, 19))), (11, 3, [1, 2] + list(range(13, 19))), (19, 4, range(1, 19)), (37, 5, range(1, 19)), (55, 6, [1, 2, 3] + list(range(4, 19))), (87, 7, [1, 2, 3] + list(range(4, 19)))]
    for z0, r, cols in rows:
        z = z0
        for c in cols:
            layout[z] = (r, c); z += 1
            if r == 6 and c == 3: z = 72
            if r == 7 and c == 3: z = 104
    sym = {1: "H", 2: "He", 3: "Li", 4: "Be", 5: "B", 6: "C", 7: "N", 8: "O", 9: "F", 10: "Ne", 11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar", 19: "K", 20: "Ca", 26: "Fe", 29: "Cu", 30: "Zn", 47: "Ag", 64: "Gd", 79: "Au", 78: "Pt", 80: "Hg", 82: "Pb", 92: "U", 53: "I", 50: "Sn", 55: "Cs", 56: "Ba"}
    im = Image.new("RGBA", (w, h), (8, 8, 12, 255)); d = ImageDraw.Draw(im)
    cw = (w - 80) / 18; ch = min((h - 60) / 7, cw * 1.05)
    ox, oy = 40, (h - ch * 7) / 2
    for z, (r, c) in layout.items():
        x, y = ox + (c - 1) * cw, oy + (r - 1) * ch
        hl = (z == highlight)
        fill = (32, 30, 36) if not hl else tuple(int(32 + (v - 32) * glow) for v in GOLD)
        d.rounded_rectangle((x + 2, y + 2, x + cw - 2, y + ch - 2), 5, fill=fill, outline=(90, 75, 45) if not hl else GOLD_L, width=1 if not hl else 2)
        s = sym.get(z)
        if s:
            f = F("mont", int(ch * 0.36))
            d.text((x + cw / 2, y + ch / 2 + 2), s, font=f, anchor="mm", fill=(200, 200, 205) if not hl else (20, 14, 4))
    return im

def tile(z, s, name, size=300, mass=""):
    im = Image.new("RGBA", (size, int(size * 1.12)), (0, 0, 0, 0))
    g = grad(size, int(size * 1.12), (255, 225, 140), (176, 124, 34)).convert("RGBA")
    m = rrect((size, int(size * 1.12)), 26, (255, 255, 255, 255)).getchannel("A"); g.putalpha(m)
    im.alpha_composite(g); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, size - 9, int(size * 1.12) - 9), 20, outline=(90, 60, 10), width=3)
    d.text((24, 18), str(z), font=F("mont", size // 8), fill=(40, 26, 4))
    d.text((size / 2, size * 0.52), s, font=F("anton", int(size * 0.42)), anchor="mm", fill=(30, 20, 2))
    d.text((size / 2, size * 0.90), name.upper(), font=F("mont", size // 10), anchor="mm", fill=(40, 26, 4))
    return im

def gold_bars(w, h, t):
    im = Image.new("RGBA", (w, h), (6, 6, 8, 255))
    gl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((w * 0.2, h * 0.2, w * 0.8, h * 1.1), fill=(255, 190, 60, 60))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    d = ImageDraw.Draw(im)
    bw, bh, tw = 230, 70, 170
    def bar(cx, by):
        top = [(cx - tw / 2, by - bh), (cx + tw / 2, by - bh), (cx + bw / 2, by), (cx - bw / 2, by)]
        d.polygon(top, fill=(214, 160, 50))
        d.polygon([(cx - tw / 2, by - bh), (cx + tw / 2, by - bh), (cx + tw / 2 - 12, by - bh - 22), (cx - tw / 2 + 12, by - bh - 22)], fill=(255, 226, 140))
        d.line((cx - tw / 2 + 20, by - bh + 14, cx + tw / 2 - 20, by - bh + 14), fill=(255, 236, 170), width=3)
    base = h * 0.86; cx = w / 2
    for i in range(4): bar(cx - 360 + i * 240, base)
    for i in range(3): bar(cx - 240 + i * 240, base - 82)
    for i in range(2): bar(cx - 120 + i * 240, base - 164)
    # brilho que passa
    sx = (t * 0.35 % 1.6 - 0.3) * w
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(sx, 0), (sx + 60, 0), (sx - 140, h), (sx - 200, h)], fill=(255, 255, 230, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    return im

def honeycomb(w, h, t, r=58):
    im = Image.new("RGBA", (w, h), (24, 16, 4, 255)); d = ImageDraw.Draw(im)
    dx, dy = r * math.sqrt(3), r * 1.5
    for j in range(-1, int(h / dy) + 2):
        for i in range(-1, int(w / dx) + 2):
            cx = i * dx + (j % 2) * dx / 2 - t * 8; cy = j * dy
            ph = 0.5 + 0.5 * math.sin(i * 0.7 + j * 1.3 + t)
            fill = (int(180 + 60 * ph), int(120 + 50 * ph), 20)
            d.polygon(hexagon_pts(cx, cy, r - 5, math.pi / 6), fill=fill, outline=(90, 55, 5), width=4)
    return im

def halo(im, radius=30, color=(255, 200, 80), strength=0.4):
    p = radius * 3; big = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); big.alpha_composite(im, (p, p))
    return glow_of(big, radius, color, strength)
