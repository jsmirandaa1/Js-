"""Bistecone long video v3: only Bistecone footage (Twitch clips + his GTA 6 VOD), his real voice in
'breaks', cinematic synthesized score. Narration = voz2.wav (from build_bis2)."""
import os, sys, json, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music3

D = os.path.dirname(os.path.abspath(__file__)); B2 = f"{D}/../bis"
ANTON = f"{D}/../v/Anton.ttf"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS, SR = 1920, 1080, 30, 44100
YEL = (255, 212, 0)
def run(c): subprocess.run(c, check=True)
for d in ("sh", "ov", "vt"): os.makedirs(f"{D}/{d}", exist_ok=True)

# ---------------- narration time maps (from v2) ----------------
VO, EX = "VO", "EX"
PIECES = [(VO, 0, 136.35), (EX, 0, 40.2), (VO, 136.35, 234.1), (EX, 40.2, 64.0), (VO, 234.1, 258.5), (EX, 64.0, 86.3),
          (VO, 258.5, 270.0), (VO, 276.1, 279.6), (EX, 86.3, 116.6), (VO, 279.6, 302.3), (EX, 116.6, 132.05), (VO, 302.3, 331.81)]
NS = []; t = 0.0
for s, a, b in PIECES: NS.append(t); t += b - a
VDUR = t
def _map(x, which, end):
    for i, (s, a, b) in enumerate(PIECES):
        if s == which and ((a < x <= b) if end else (a <= x < b)): return NS[i] + x - a
    for i, (s, a, b) in enumerate(PIECES):
        if s == which and a <= x <= b: return NS[i] + x - a
def m(x, end=False): return _map(x, VO, end)
def ex(x, end=False): return _map(x, EX, end)

# ---------------- breaks: Bistecone's own voice ----------------
# (V position, clip id, [(in,out),...], bleeps [(t0,t1) clip time])
COLD = [("738217045", [(11.8, 16.3), (23.3, 26.95)], [])]
TITLE = 3.4
BREAKS = [
    (34.45, "1107145058", [(3.9, 7.4)], []),
    (NS[1], "743655411", [(3.0, 9.7)], []),
    (NS[2], "638722551", [(7.3, 10.8)], [(8.84, 9.52)]),
    (219.45, "1717109571", [(22.0, 26.4)], []),
    (NS[4], "2043116765", [(9.2, 11.4), (18.7, 28.3)], []),
    (NS[5], "3151387374", [(21.6, 27.1)], []),
]
def bdur(parts): return sum(b - a for a, b in parts)
COLDD = bdur(COLD[0][1]) + TITLE
def T(v, end=False):
    """V-time (narration) -> final time"""
    o = COLDD
    for p, _, parts, _ in BREAKS:
        if (p < v) if end else (p <= v): o += bdur(parts)
    return v + o
DUR = T(VDUR, True) + 3.5
print("final duration", DUR)

# ---------------- B-roll plan (V-time) ----------------
segs = json.load(open(f"{D}/vod/segs.json"))
P = [
    (0, 6.5, "v", 5482, "sad"), (6.5, 13.3, "v", 9942, "sad"),
    (13.3, 19.1, "c", "2043116765", 3.0, ""), (19.1, 25.2, "v", 42, ""), (25.2, 30.9, "c", "3151387374", 30, ""),
    (30.9, 34.45, "c", "2602527287", 30.5, ""),
    (34.45, 40.6, "c", "3699536874", 20, ""), (40.6, 46.0, "c", "409600665", 0.5, ""),
    (46.0, 50.0, "c", "1107145058", 10, ""), (50.0, 53.0, "c", "3381447727", 0.5, ""), (53.0, 56.5, "c", "2632735977", 0.5, ""),
    (56.5, 60.5, "c", "2500696696", 3, ""), (60.5, 64.5, "c", "2337022284", 5, ""), (64.5, 68.8, "c", "667153230", 10, ""),
    (68.8, 80.3, "v", 5492, "sad"), (80.3, 92.5, "v", 9962, "sad"), (92.5, 102.2, "c", "2955771663", 5, "sad"),
    (102.2, 109.3, "c", "2614753413", 0.5, ""), (109.3, 114.2, "c", "2632735977", 5, ""), (114.2, 119.7, "c", "2043116765", 12, ""),
    (119.7, 124.6, "c", "1107145058", 14, ""), (124.6, 129.7, "c", "3381447727", 5, ""), (129.7, NS[1], "c", "2602527287", 36, ""),
    (NS[1], ex(23.8), "award", None, None, ""),
    (ex(23.8), ex(31.0), "c", "2602527287", 45, ""), (ex(31.0), NS[2], "c", "738217045", 40, ""),
    (NS[2], m(142.9), "v", 2583, ""), (m(142.9), m(148.8), "c", "3699536874", 0.5, ""), (m(148.8), m(155.4), "c", "3837563374", 0.5, ""),
    (m(155.4), m(160.8), "c", "2312876563", 0.5, ""), (m(160.8), m(166.9), "v", 3323, ""),
    (m(166.9), m(172.9), "c", "1107145058", 0.3, ""), (m(172.9), 219.45, "c", "738217045", 12, ""),
    (219.45, m(185.4), "c", "3783329525", 0.5, ""), (m(185.4), m(190.9), "c", "2500696696", 8, ""),
    (m(190.9), m(196.7), "v", 4803, ""), (m(196.7), m(209.8), "v", 7021, ""),
    (m(209.8), m(220.0), "c", "2908932040", 5, ""), (m(220.0), m(227.2), "c", "3736571791", 3, ""), (m(227.2), NS[3], "c", "517996475", 5, ""),
    (NS[3], ex(47.0), "c", "2337022284", 12, ""), (ex(47.0), ex(51.0), "c", "1717109571", 0.5, ""),
    (ex(51.0), ex(56.0), "c", "4025044787", 5, ""), (ex(56.0), NS[4], "c", "2312876563", 8, ""),
    (NS[4], m(239.3), "v", 42, ""), (m(239.3), m(246.0), "v", 12198, ""), (m(246.0), m(254.3), "c", "2923406987", 10, ""),
    (m(254.3), NS[5], "c", "414403545", 20, ""),
    (NS[5], ex(71.5), "v", 9988, ""), (ex(71.5), ex(80.3), "v", 14424, ""), (ex(80.3), NS[6], "c", "3699536874", 35, ""),
    (NS[6], NS[6] + 7.0, "v", 10728, ""), (NS[6] + 7.0, NS[8], "v", 15167, ""),
    (NS[8], ex(98.7), "v", 11468, "sad"), (ex(98.7), ex(109.4), "v", 13678, "sad"),
    (ex(109.4), NS[9], "c", "2043116765", 20, ""),
    (NS[9], m(287.4), "c", "667153230", 0.5, ""), (m(287.4), m(292.1), "c", "3837563374", 10, ""),
    (m(292.1), m(295.9), "c", "2500696696", 12, ""), (m(295.9), NS[10], "c", "2955771663", 30, ""),
    (NS[10], NS[11], "c", "1940353369", 18.5, "slow"),
    (NS[11], m(308.2), "c", "738217045", 23, ""),
    (m(308.2), VDUR + 3.5, "v", 16662, ""),
]

def vod_cut(vt, d, out, sad=False):
    ks = [k for k, (t0, dd, u) in enumerate(segs) if t0 + dd > vt and t0 < vt + d]
    for k in ks:
        p = f"{D}/vt/{k}.ts"
        if not os.path.exists(p) or os.path.getsize(p) == 0: run(["curl", "-sS", "--max-time", "120", "-o", p, segs[k][2]])
    open(f"{D}/sh/l.txt", "w").write("".join(f"file '{D}/vt/{k}.ts'\n" for k in ks))
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{D}/sh/l.txt", "-c", "copy", f"{D}/sh/cat.ts"])
    g = grade(sad)
    # enlarge his facecam (988,128 292x192 in 720p) as a PiP with yellow frame
    fc = (f"[0:v]fps={FPS},split[a][b];[a]scale={W}:{H},{g}[bg];"
          f"[b]crop=292:192:988:128,scale=630:414,{g},pad=642:426:6:6:color=0xFFD400[cam];"
          f"[bg][cam]overlay={W - 642 - 50}:{H - 426 - 60},format=yuv420p[v]")
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{vt - segs[ks[0]][0]:.3f}", "-i", f"{D}/sh/cat.ts", "-t", f"{d:.3f}", "-an",
         "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", out])

PUSH = [0]
def push(d):
    PUSH[0] += 1
    z0, z1 = (1.0, 1.07) if PUSH[0] % 2 else (1.07, 1.0)
    return (f"scale=w='trunc({int(W*1.1)}*({z0}+({z1 - z0:.3f})*t/{d:.3f})/2)*2':h=-2:eval=frame,crop={W}:{H}")

def grade(sad):
    return ("eq=saturation=0.25:contrast=1.08:brightness=-0.04,colorbalance=bs=0.12:bm=0.05" if sad
            else "eq=contrast=1.05:saturation=1.15")

CAM = {"738217045": (718, 404, 1202, 165), "2043116765": (718, 404, 1202, 165), "1940353369": (510, 287, 1410, 165)}
def clip_cut(cid, cin, d, out, mode=""):
    src = f"{D}/clips/{cid}.mp4"
    L = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    sp = 1.0
    if mode == "slow": sp = 1.6
    need = d / sp
    if cin + need > L - 0.2:
        if need <= L - 0.4: cin = max(0, L - 0.3 - need)
        else: cin = 0; sp = max(sp, d / (L - 0.4))
    cam = (f"crop={CAM[cid][0]}:{CAM[cid][1]}:{CAM[cid][2]}:{CAM[cid][3]},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.8," if cid in CAM else "")
    vf = (f"setpts={sp:.4f}*PTS,fps={FPS},{cam}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{push(d)},"
          f"{grade(mode == 'sad')},format=yuv420p")
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{cin:.3f}", "-i", src, "-t", f"{need + 0.1:.3f}", "-an", "-vf", vf,
         "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", out])

# ---------------- graphics helpers ----------------
def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def blank(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def fit(d, t, s, mw):
    while d.textlength(t, font=F(s)) > mw: s -= 3
    return s

# award background (still image -> video)
def award_bg(path):
    im = Image.new("RGB", (W, H), (8, 6, 2)); d = ImageDraw.Draw(im)
    cx, cy = 1290, 400
    rays = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(rays)
    for k in range(18):
        a = np.deg2rad(k * 20 + 5)
        pts = [(cx, cy), (cx + 2600 * np.cos(a - 0.06), cy + 2600 * np.sin(a - 0.06)), (cx + 2600 * np.cos(a + 0.06), cy + 2600 * np.sin(a + 0.06))]
        dr.polygon(pts, fill=60)
    rays = rays.filter(ImageFilter.GaussianBlur(10))
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse([cx - 520, cy - 520, cx + 520, cy + 520], fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    gold = Image.new("RGB", (W, H), (255, 190, 40))
    im = Image.composite(gold, im, Image.eval(rays, lambda v: v)); im = Image.composite(gold, im, Image.eval(glow, lambda v: int(v * 0.55)))
    tro = emoji("🏆", 430); im.paste(tro, (cx - tro.width // 2, cy - tro.height // 2 - 20), tro)
    d = ImageDraw.Draw(im)
    d.text((cx, 800), "PRÊMIO ESPORTS BRASIL 2025", font=F(80), fill=YEL, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    d.text((cx, 905), "STREAMER REVELAÇÃO", font=F(60), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
    rr = np.random.default_rng(3)
    for _ in range(160):  # confetti
        x, y = rr.integers(0, W), rr.integers(0, H); c = [YEL, (255, 255, 255), (255, 140, 0)][rr.integers(0, 3)]
        d.rectangle([x, y, x + rr.integers(4, 12), y + rr.integers(8, 20)], fill=c)
    im.save(path)

def still_cut(img, d, out):
    run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img, "-t", f"{d:.3f}",
         "-vf", f"scale=2400:-1,zoompan=z='min(1+0.0004*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", out])

# ---------------- build video segments in FINAL time ----------------
pieces = []  # (final_start, final_end, maker)
# cold open + title
t = 0.0
for i, (a, b) in enumerate(COLD[0][1]):
    pieces.append((t, t + b - a, ("clip", COLD[0][0], a, "")))
    t += b - a
pieces.append((t, t + TITLE, ("title",)))
# narration b-roll
for row in P:
    a, b, kind = row[0], row[1], row[2]
    fa, fb = T(a), T(b, True)
    pieces.append((fa, fb, (kind,) + tuple(row[3:])))
for p, cid, parts, _ in BREAKS:
    t = T(p) - bdur(parts)
    for a, b in parts:
        pieces.append((t, t + b - a, ("clip", cid, a, "")))
        t += b - a
pieces.sort()
# sanity: contiguous
for (a1, b1, _), (a2, b2, _) in zip(pieces, pieces[1:]):
    if abs(b1 - a2) > 0.02: print("GAP/OVERLAP", round(b1, 2), round(a2, 2))
award_bg(f"{D}/ov/award_bg.png")
files = []
for i, (a, b, mk) in enumerate(pieces):
    d = round(b - a, 3); out = f"{D}/sh/p{i:03d}.mp4"; files.append(out)
    if os.path.exists(out) and not os.environ.get("REDO"): continue
    k = mk[0]
    if k == "clip": clip_cut(mk[1], mk[2], d, out)
    elif k == "c": clip_cut(mk[1], mk[2], d, out, mk[3])
    elif k == "v": vod_cut(mk[1], d, out, mk[2] == "sad")
    elif k == "award": still_cut(f"{D}/ov/award_bg.png", d, out)
    elif k == "title":
        src = f"{D}/clips/2043116765.mp4"
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "12", "-i", src, "-t", f"{d / 1.5 + 0.1:.3f}", "-an", "-vf",
             f"setpts=1.5*PTS,fps={FPS},scale={W}:{H},eq=brightness=-0.18:saturation=0.6,gblur=sigma=6,format=yuv420p",
             "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", out])
open(f"{D}/sh/list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{D}/sh/list.txt", "-c", "copy", f"{D}/base.mp4"])

# ---------------- overlays ----------------
OV = []
def addF(img, fa, fb, name):
    p = f"ov/{name}.png"; img.save(f"{D}/{p}"); OV.append((p, fa, fb))
MAP = True
def add(img, a, b, name):
    if MAP: a, b = m(a), m(b, True)
    addF(img, T(a), T(b, True), name)

g = Image.new("L", (1, H))
for y in range(H): g.putpixel((0, y), int(130 * max(0, (y - 700) / 380) ** 1.4))
im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); im.putalpha(g.resize((W, H)))
ImageDraw.Draw(im).text((60, 60), "@jhonlivesx", font=F(36), fill=(255, 255, 255, 200), anchor="lm")
addF(im, 0, DUR, "base")

def dim(a, b, name, alpha=120): add(Image.new("RGBA", (W, H), (0, 0, 0, alpha)), a, b, name)
def chapter(n, title, a, dur=4.0):
    im = blank(); d = ImageDraw.Draw(im); tw = d.textlength(title, font=F(64))
    d.rectangle([60, 860, 60 + tw + 220, 990], fill=(0, 0, 0, 200)); d.rectangle([60, 860, 76, 990], fill=YEL)
    d.text((110, 892), f"CAPÍTULO {n}", font=F(34), fill=YEL, anchor="lm"); d.text((110, 945), title, font=F(64), fill=(255, 255, 255), anchor="lm")
    if MAP: aa = m(a)
    else: aa = a
    addF(im, T(aa), T(aa) + dur, f"ch{n}")
def big(lines, a, b, name, em=None, y=540, sizes=(150, 80), cols=(YEL, (255, 255, 255)), dimit=True):
    if dimit: dim(a, b, name + "_dim", 110)
    im = blank(); d = ImageDraw.Draw(im); yy = y - (len(lines) - 1) * 60
    if em: e = emoji(em, 150); im.alpha_composite(e, (W // 2 - e.width // 2, yy - 260))
    for j, ln in enumerate(lines):
        s = fit(d, ln, sizes[min(j, 1)], 1700)
        d.text((W // 2, yy), ln, font=F(s), fill=cols[min(j, 1)], anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0)); yy += int(s * 1.15)
    add(im, a, b, name)
SLIDE = set()
def side(lines, a, b, name, em=None):
    SLIDE.add(f"ov/{name}.png")
    im = blank(); d = ImageDraw.Draw(im); h = 120 + 95 * len(lines)
    d.rounded_rectangle([60, 300, 900, 300 + h], 28, fill=(0, 0, 0, 200), outline=YEL, width=5); yy = 370
    if em: e = emoji(em, 80); im.alpha_composite(e, (90, 330))
    for j, ln in enumerate(lines):
        s = fit(d, ln, 76 if j == 0 else 56, 720)
        d.text((200 if (em and j == 0) else 100, yy), ln, font=F(s), fill=YEL if j == 0 else (255, 255, 255), anchor="lm"); yy += 95
    add(im, a, b, name)
def lst(items, upto, a, b, name, title):
    dim(a, b, name + "_dim", 120); im = blank(); d = ImageDraw.Draw(im)
    d.text((W // 2, 170), title, font=F(70), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0)); yy = 330
    for j, it in enumerate(items[:upto]):
        d.text((300, yy), it, font=F(fit(d, it, 84, 1350)), fill=YEL if j == upto - 1 else (200, 200, 200), anchor="lm", stroke_width=6, stroke_fill=(0, 0, 0)); yy += 130
    add(im, a, b, name)
def screens(a, b, name):
    paths = ["/root/.claude/uploads/762ec768-073a-5bf9-9078-d9e72100cb94/216975da-image.png",
             "/root/.claude/uploads/762ec768-073a-5bf9-9078-d9e72100cb94/26564ac4-image.png"]
    im = blank()
    for x, pth in zip([1180, 1540], paths):
        s = Image.open(pth).convert("RGB").crop((0, 200, 921, 1000)); s = s.resize((340, int(340 * s.height / s.width)), Image.LANCZOS)
        card = Image.new("RGBA", (s.width + 16, s.height + 16), YEL + (255,)); card.paste(s, (8, 8))
        im.alpha_composite(card, (x, 200))
    add(im, a, b, name)

# title card + "AO VIVO" badges on breaks
im = blank(); d = ImageDraw.Draw(im)
d.text((W // 2, 430), "DO CAMINHÃO AO TOPO", font=F(150), fill=YEL, anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
d.text((W // 2, 600), "A HISTÓRIA DO BISTECONE", font=F(96), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
tA = bdur(COLD[0][1]); addF(im, tA, tA + TITLE, "title")
def badge():
    im = blank(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1430, 40, 1870, 120], 18, fill=(220, 20, 40, 235))
    d.ellipse([1455, 64, 1487, 96], fill=(255, 255, 255)); d.text((1505, 80), "BISTECONE AO VIVO", font=F(46), fill=(255, 255, 255), anchor="lm")
    return im
bim = badge()
addF(bim, 0, tA, "bdg_cold")
for i, (p, cid, parts, _) in enumerate(BREAKS):
    addF(bim, T(p) - bdur(parts), T(p), f"bdg{i}")
im = blank(); ImageDraw.Draw(im).text((W // 2, 900), "EU SOU O VENCEDOR!", font=F(110), fill=YEL, anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
addF(im, T(NS[2]) - 2.0, T(NS[2]), "venc_sub")
im = blank(); ImageDraw.Draw(im).text((W // 2, 900), "\"TUDO VAI MUDAR!\"", font=F(110), fill=YEL, anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
addF(im, T(NS[4]) - 3.0, T(NS[4]), "tudo_sub")

# --- original overlays (VO times) ---
side(["+5 MILHÕES", "de inscritos (2 canais)"], 18.1, 22.3, "s5mi", "📈")
side(["PRÊMIO iBEST", "Streamer Influenciador"], 22.4, 23.7, "sibest", "🏆")
side(["GTA 6", "dezenas de milhares ao vivo"], 23.8, 29.5, "sgta", "🎮")
big(["DAVID"], 30.0, 33.2, "david", sizes=(220, 80), cols=((255, 255, 255), (255, 255, 255)))
big(["BISTECONE"], 33.2, 34.4, "bist", sizes=(260, 80))
chapter(1, "QUEM É O BISTECONE", 48.0)
side(["+15 HORAS", "de live sem parar"], 52.7, 56.5, "s15h", "⏱️")
chapter(2, "O DESCARREGADOR DE CAMINHÃO", 70.3)
side(["MADRUGADA", "descarregando caminhão"], 76.3, 82.5, "smad", "🚚")
side(["MOTOBOY", "mais liberdade, longe do sonho"], 94.7, 101.4, "smoto", "🏍️")
chapter(3, "A VIRADA", 102.2)
big(["“VÍDEOS DE", "QUALIDADE DUVIDOSA”"], 131.4, 136.3, "quote", sizes=(130, 130), cols=(YEL, YEL))
chapter(4, "A FÓRMULA DO BISTECONE", 136.5)
F5 = ["1. FREQUÊNCIA", "2. DOIS CANAIS", "3. A REAÇÃO VALE MAIS", "4. PROXIMIDADE", "5. CORAGEM PRA MUDAR"]
lst(F5, 1, 141.1, 146.4, "f1", "A FÓRMULA")
side(["700+ e 900+", "vídeos publicados"], 146.5, 151.9, "svid", "🎬")
lst(F5, 2, 152.0, 155.4, "f2", "A FÓRMULA")
screens(155.5, 168.9, "scr1"); side(["CANAL ALEATÓRIO", "+ LIVES SEM CORTES"], 155.5, 168.9, "s2can")
lst(F5, 3, 169.0, 179.2, "f3", "A FÓRMULA")
lst(F5, 4, 179.8, 187.5, "f4", "A FÓRMULA")
lst(F5, 5, 187.6, 194.6, "f5", "A FÓRMULA")
big(["“3 DIAS NA KICK RENDERAM", "UM MÊS DE TWITCH”"], 194.7, 198.2, "kick", sizes=(110, 110), cols=(YEL, YEL))
dim(198.3, 209.8, "cta_dim", 150)
im = blank(); d = ImageDraw.Draw(im)
d.rounded_rectangle([360, 250, 1560, 830], 40, fill=(0, 0, 0, 220), outline=YEL, width=8)
d.text((W // 2, 350), "CURTE O BISTECONE?", font=F(90), fill=YEL, anchor="mm")
d.text((W // 2, 480), "LIVE DE GTA 6 TODA NOITE", font=F(78), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 620), "TWITCH / YOUTUBE  @jhonlivesx", font=F(64), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 720), "TIKTOK  @jhonexlives", font=F(64), fill=(255, 255, 255), anchor="mm")
add(im, 198.3, 209.8, "cta")
chapter(5, "OS NÚMEROS", 210.5)
side(["2,2 MILHÕES", "canal Bistecone"], 211.1, 215.3, "n1", "📺")
side(["3,4 MILHÕES", "canal BisteconeLive"], 215.4, 218.7, "n2", "🔴")
screens(211.1, 218.7, "scr2")
side(["PRÊMIO iBEST", "Streamer Influenciador"], 218.8, 228.8, "n3", "🏆")
side(["SANA", "Fortaleza"], 228.9, 234.0, "n4", "🎤")
chapter(6, "GTA 6: A PROVA DE FOGO", 234.3)
big(["15h43min", "DE LIVE NA KICK"], 240.8, 246.3, "n15", sizes=(200, 80))
big(["~72 MIL", "AO VIVO AO MESMO TEMPO"], 249.1, 253.6, "n72", sizes=(220, 80))
chapter(7, "O QUE EU APRENDI COM ELE", 265.8)
L4 = ["1. NÃO ESPERA FICAR PERFEITO", "2. CONSTÂNCIA VENCE TALENTO", "3. SEJA VOCÊ", "4. COMEÇA COM O QUE TEM"]
for j, (a, b) in enumerate([(281.4, 287.3), (287.4, 292.0), (292.1, 295.8), (295.9, 302.3)]):
    lst(L4, j + 1, a, b, f"l{j}", "O QUE EU APRENDI")
big(["OBRIGADO, BISTECONE"], 302.5, 309.0, "obg", em="💛", sizes=(150, 80))
dim(309.1, 331.8, "end_dim", 150)
im = blank(); d = ImageDraw.Draw(im)
d.rounded_rectangle([360, 230, 1560, 850], 40, fill=(0, 0, 0, 220), outline=YEL, width=8)
d.text((W // 2, 340), "ME SEGUE!", font=F(120), fill=YEL, anchor="mm")
d.text((W // 2, 490), "SE INSCREVE + ATIVA O SININHO", font=F(70), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 640), "TWITCH / YOUTUBE  @jhonlivesx", font=F(68), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 750), "TIKTOK  @jhonexlives", font=F(68), fill=(255, 255, 255), anchor="mm")
add(im, 309.1, 331.8, "end"); OV[-1] = (OV[-1][0], OV[-1][1], DUR); OV[-2] = (OV[-2][0], OV[-2][1], DUR)

MAP = False
E = ex
chapter("3.5", "O PRIMEIRO GRANDE PRÊMIO", E(0.0))
side(["STREAMER REVELAÇÃO", "Prêmio eSports Brasil 2025"], E(14.0), E(19.0), "e1a", "🏆")
side(["FINALISTAS", "Ammy • Miwvlr • Bistecone"], E(19.1), E(23.7), "e1b", "🎖️")
big(["VENCEU!"], E(23.8), E(30.9), "e1c", em="🏆", sizes=(240, 80))
side(["240+ MILHÕES", "de views no canal principal"], E(41.3), E(46.9), "e2a", "👀")
im = blank(); s_ = Image.open("/root/.claude/uploads/762ec768-073a-5bf9-9078-d9e72100cb94/216975da-image.png").convert("RGB").crop((0, 1220, 921, 1830))
s_ = s_.resize((760, int(760 * s_.height / s_.width)), Image.LANCZOS)
card = Image.new("RGBA", (s_.width + 16, s_.height + 16), YEL + (255,)); card.paste(s_, (8, 8)); im.alpha_composite(card, (1080, 260))
add(im, E(47.0), E(53.7), "e2scr")
side(["BASTIDORES", "série exclusiva pra membros"], E(47.0), E(53.7), "e2b", "🎬")
side(["\"ZERANDO O GTA 6 HOJE\"", "a live do dia seguinte"], E(66.0), E(73.7), "e3a", "🎮")
big(["~60 MIL", "NO COMEÇO DA TARDE"], E(73.8), E(78.8), "e3b", sizes=(220, 80))
big(["É COMUNIDADE."], E(80.3), E(86.0), "e3c", sizes=(170, 80))
side(["@jhonlivesx", "live de GTA 6 toda noite"], E(99.7), E(105.9), "e4a", "🎮")
big(["\"NÃO IMPORTA DE ONDE", "VOCÊ COMEÇOU\""], E(120.6), E(123.2), "e5a", sizes=(120, 120), cols=(YEL, YEL))
big(["CORAGEM DE COMEÇAR.", "CONTINUAR QUANDO NINGUÉM TÁ OLHANDO."], E(123.3), E(128.7), "e5b", sizes=(110, 70))
big(["NÃO DESISTIR SÓ PORQUE", "AINDA NÃO CHEGOU A SUA VEZ."], E(128.8), E(132.0), "e5c", sizes=(100, 100), cols=(YEL, YEL))

# white flashes at chapter starts and break starts
fl = Image.new("RGBA", (W, H), (255, 255, 255, 170)); fl.save(f"{D}/ov/flash.png")
FLASH = [p0 for (p0, a0, b0) in OV if "/ch" in p0] + [p0 for (p0, a0, b0) in OV if "/bdg" in p0]
FT = sorted(set([a0 for (p0, a0, b0) in OV if p0 in FLASH]))
for k, ft in enumerate(FT): OV.append(("ov/flash.png", ft, ft + 0.18))
WH = sorted(set([a0 for (p0, a0, b0) in OV if p0 in SLIDE or ("_dim" not in p0 and ("/f" in p0 or "/l" in p0 or "/n" in p0 or "/e" in p0))]))
CHT = sorted(set([a0 for (p0, a0, b0) in OV if "/ch" in p0]))

# ---------------- audio ----------------
def dec(path, ss=None, tt=None):
    c = ["ffmpeg", "-loglevel", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-t", str(tt)] if tt is not None else []) + \
        ["-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, np.int16).astype(np.float32) / 32768
N = int(DUR * SR) + SR
voice = np.zeros(N, np.float32); live = np.zeros(N, np.float32)
vz = dec(f"{B2}/voz2.wav")
cuts = sorted([0.0] + [p for p, *_ in BREAKS] + [VDUR])
for a, b in zip(cuts, cuts[1:]):
    x = vz[int(a * SR):int(b * SR)]; i = int(T(a) * SR); voice[i:i + len(x)] += x[:N - i]
def put_live(cid, parts, bleeps, t0):
    t = t0
    for a, b in parts:
        x = dec(f"{D}/clips/{cid}.mp4", a, b - a).copy()
        for b0, b1 in bleeps:
            if a <= b0 < b:
                i0, i1 = int((b0 - a) * SR), int((b1 - a) * SR); n = i1 - i0
                x[i0:i1] = 0.25 * np.sin(2 * np.pi * 1000 * np.arange(n) / SR)
        f = int(0.04 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        rms = np.sqrt(np.mean(x ** 2)) + 1e-6; x *= min(4.0, 0.12 / rms)
        i = int(t * SR); live[i:i + len(x)] += x[:N - i]; t += b - a
put_live(COLD[0][0], COLD[0][1], COLD[0][2], 0.0)
for p, cid, parts, bl in BREAKS: put_live(cid, parts, bl, T(p) - bdur(parts))

# music sections (final time)
S = [(0, tA, 0.0), (tA, T(m(68.8)), 0.35), (T(m(68.8)), T(m(102.2)), 0.2), (T(m(102.2)), T(NS[1]), (0.4, 0.66)),
     (T(NS[1]), T(NS[2], True), 0.9), (T(NS[2]), T(NS[4], True), 0.6), (T(NS[4]) - bdur(BREAKS[4][2]), T(NS[6]), 1.0),
     (T(NS[6]), T(NS[8] + 28.0), 0.25), (T(NS[8] + 28.0), T(NS[10]), 0.6), (T(NS[10]), T(NS[11]), 0.95), (T(NS[11]), DUR, 0.5)]
HITS = [tA, T(ex(23.8)), T(NS[2]) - bdur(BREAKS[2][2]), T(NS[4]) - bdur(BREAKS[4][2]), T(NS[10])]
mus = music3.make(DUR, S, HITS)[:N]
sfx = np.zeros(N, np.float32)
rg = np.random.default_rng(11)
def whoosh(d=0.55):
    n = int(d * SR); tt = np.arange(n) / SR; x = rg.standard_normal(n); y = np.zeros(n); st = 0.0
    for i in range(0, n, 512):
        fc_ = 400 + 5000 * np.sin(np.pi * i / n); a_ = np.exp(-2 * np.pi * fc_ / SR)
        from scipy.signal import lfilter
        y[i:i + 512] = lfilter([1 - a_], [1, -a_], x[i:i + 512])
    return y * np.sin(np.pi * tt / d) ** 2
def sub(d=1.6):
    n = int(d * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-tt * 9)) / SR) * np.exp(-tt * 2.5)
def sput(x, t0, g):
    i = int(t0 * SR)
    if 0 <= i < N: j = min(N, i + len(x)); sfx[i:j] += g * x[:j - i]
for t0 in WH: sput(whoosh(), t0 - 0.15, 0.10)
for t0 in CHT: sput(sub(), t0, 0.35); sput(whoosh(0.8), t0 - 0.4, 0.12)
mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
# ducking envelope
act = np.abs(voice) + np.abs(live)
k = int(0.05 * SR); env = np.convolve(act, np.ones(k) / k, "same")
env = np.convolve((env > 0.01).astype(np.float32), np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
livemask = np.convolve((np.abs(live) > 0.005).astype(np.float32), np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
gain = 0.42 - 0.24 * np.clip(env, 0, 1) - 0.1 * np.clip(livemask, 0, 1)
fo = int(3 * SR); gain[-fo:] *= np.linspace(1, 0, fo)
mix = mus * gain[:, None] + (1.0 * voice + 1.0 * live + sfx)[:, None]
mix = np.clip(mix, -1, 1)
w = wave.open(f"{D}/mix.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()

# ---------------- compose ----------------
inp = ["-i", f"{D}/base.mp4"]
for p, a, b in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b - a:.2f}", "-i", f"{D}/{p}"]
inp += ["-i", f"{D}/mix.wav"]
fc = ["[0:v]vignette=angle=PI/4.5,eq=contrast=1.03[base0]"]; prev = "base0"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i + 1}:v]format=rgba,fade=in:st=0:d=0.25:alpha=1,setpts=PTS+{a:.3f}/TB[o{i}]")
    xx = f"'if(lt(t-{a:.3f},0.45),-900+900*sin(PI/2*(t-{a:.3f})/0.45),0)'" if p in SLIDE else "0"
    fc.append(f"[{prev}][o{i}]overlay=x={xx}:y=0:eof_action=pass:repeatlast=0[v{i}]"); prev = f"v{i}"
fc.append(f"[{prev}]format=yuv420p[v]")
na = len(OV) + 1
fc.append(f"[{na}:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", f"{DUR}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{D}/historia_bistecone_v3.mp4"])
print("ok", DUR)
