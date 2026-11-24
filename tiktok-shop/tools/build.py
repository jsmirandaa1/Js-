"""Monta o vídeo de apresentação de um produto (1080x1920, 18s, 30fps).
Uso: python3 build.py <chave>   (chaves em produtos.py)  |  FONTS=<pasta com Anton.ttf, Mont800.ttf, Mont900.ttf>
"""
import os, sys, math, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from produtos import PRODUTOS

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(f"{D}/..")
FONTS = os.environ.get("FONTS", f"{ROOT}/fonts")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS, DUR = 1080, 1920, 30, 18.0
# cenas (inicio, fim)
S = dict(gancho=(0, 3.2), produto=(3.2, 7.4), beneficios=(7.4, 11.8), desejo=(11.8, 14.6), cta=(14.6, DUR))

key = sys.argv[1]; P = PRODUTOS[key]
ACC, ACC2 = P["accent"], P["accent2"]
def F(name, size): return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)

# ---------------- helpers ----------------
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def prep_bg(path, upscale=1.18):
    im = Image.open(path).convert("RGB")
    im = cover(im, round(W * upscale), round(H * upscale))
    im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
    im = ImageOps.autocontrast(im, cutoff=0.5)
    return im

def kenburns(big, p, z0=1.0, z1=1.12, pan=(0.5, 0.5, 0.5, 0.5)):
    z = z0 + (z1 - z0) * p
    bw, bh = big.size
    cw = bw / z; ch = bh / z
    cx = (pan[0] + (pan[2] - pan[0]) * p) * (bw - cw); cy = (pan[1] + (pan[3] - pan[1]) * p) * (bh - ch)
    return big.resize((W, H), Image.BILINEAR, box=(cx, cy, cx + cw, cy + ch))

def grad_overlay(top=0.45, bottom=0.88, color=(0, 0, 0)):
    a = np.zeros((H, 1), np.float32)
    y = np.arange(H) / H
    a[:, 0] = np.maximum(top * np.clip(1 - y / 0.38, 0, 1) ** 1.6, bottom * np.clip((y - 0.38) / 0.5, 0, 1) ** 1.2)
    arr = np.zeros((H, W, 4), np.uint8); arr[..., :3] = color; arr[..., 3] = (np.repeat(a, W, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")
GRAD = grad_overlay()

def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(im).text((4, 4), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox()); return im.resize((size, round(im.height * size / im.width)), Image.LANCZOS)

def text_layer(text, font, fill=(255, 255, 255), stroke=0, stroke_fill=(0, 0, 0), shadow=True, pad=30):
    bb = font.getbbox(text, stroke_width=stroke)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - bb[0] + 6, pad - bb[1] + 10), text, font=font, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(9)))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def pill(text, font, bg, fg=(255, 255, 255), padx=34, pady=18, r=None, icon=None):
    bb = font.getbbox(text); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    iw = icon.width + 18 if icon else 0
    w, h = tw + padx * 2 + iw, th + pady * 2; r = h // 2 if r is None else r
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 28, 20 + w, 28 + h), r, fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), r, fill=bg)
    if icon: im.alpha_composite(icon, (20 + padx, 20 + (h - icon.height) // 2))
    d.text((20 + padx + iw - bb[0], 20 + pady - bb[1]), text, font=font, fill=fg)
    return im

def check_icon(size, color):
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=color)
    s = size * 4; d.line([(s * .27, s * .52), (s * .44, s * .68), (s * .74, s * .34)], fill=(255, 255, 255), width=int(s * .11), joint="curve")
    return im.resize((size, size), Image.LANCZOS)

def place(frame, layer, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if alpha <= 0.01 or scale <= 0.01: return
    l = layer
    if rot: l = l.rotate(rot, Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.005: l = l.resize((max(1, round(l.width * scale)), max(1, round(l.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        a = l.getchannel("A").point(lambda v: int(v * alpha)); l = l.copy(); l.putalpha(a)
    frame.alpha_composite(l, (round(cx - l.width / 2), round(cy - l.height / 2)))

def pop(t, t0, d=0.35):  # (scale, alpha)
    if t < t0: return 0, 0
    x = (t - t0) / d; return (0.55 + 0.45 * ease_back(x)), min(1, x * 2.5)

# ---------------- assets ----------------
prod = Image.open(f"{ROOT}/assets/prod/{P['prod']}.jpg").convert("RGB")
ia = [prep_bg(f"{ROOT}/assets/ia/{n}.png") for n in P["ia"]]

def product_card(size, radius=46):
    card = Image.new("RGBA", (size + 80, size + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((40, 56, 40 + size, 56 + size), radius, fill=(0, 0, 0, 150))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(22)))
    p = cover(prod, size, size)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), radius, fill=255)
    card.paste(p, (40, 40), m)
    ImageDraw.Draw(card).rounded_rectangle((40, 40, 40 + size, 40 + size), radius, outline=(255, 255, 255), width=6)
    return card
CARD = product_card(860); CARD_S = product_card(700)

def prod_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    top = np.array(ACC, np.float32) * 0.62; bot = np.array([12, 10, 14], np.float32)
    k = (yy / H)[..., None] ** 0.9
    arr = top * (1 - k) + bot * k
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
    glow = (np.clip(1 - r * 2.4, 0, 1) ** 2)[..., None]
    arr = arr + (np.array(ACC, np.float32) * 0.9 + 60) * glow * 0.55
    vig = (1 - np.clip(r - 0.25, 0, 1) * 0.9)[..., None]
    arr = np.clip(arr * vig, 0, 255).astype(np.uint8)
    a = np.full((H, W, 1), 255, np.uint8)
    return Image.fromarray(np.concatenate([arr, a], 2), "RGBA")
PBG = prod_bg()

# sparkles (partículas) para cena de produto
rng = np.random.default_rng(3)
SPK = [(rng.uniform(80, W - 80), rng.uniform(200, H - 300), rng.uniform(0, 6.28), rng.uniform(6, 16)) for _ in range(26)]
def sparkles(frame, t):
    d = ImageDraw.Draw(frame)
    for x, y, ph, s in SPK:
        a = (math.sin(t * 3 + ph) + 1) / 2
        if a < 0.3: continue
        y2 = y - (t * 40 + ph * 30) % 160; s2 = s * a
        col = (255, 255, 255, int(220 * a))
        d.polygon([(x, y2 - s2 * 2), (x + s2 * .45, y2), (x, y2 + s2 * 2), (x - s2 * .45, y2)], fill=col)
        d.polygon([(x - s2 * 2, y2), (x, y2 + s2 * .45), (x + s2 * 2, y2), (x, y2 - s2 * .45)], fill=col)

# ---------------- textos pré-renderizados ----------------
T_TAG = pill(P["tag"], F("Mont900", 40), ACC + (255,), fg=(20, 20, 20), icon=emoji("🔥", 44))
T_G = [text_layer(P["gancho"][0], F("Anton", 150), stroke=6), text_layer(P["gancho"][1], F("Anton", 150), fill=ACC2, stroke=6)]
T_TIT = [text_layer(P["titulo"][0], F("Anton", 92), stroke=4), text_layer(P["titulo"][1], F("Mont900", 50), fill=ACC2, stroke=3)]
def badge(txt, r=125):
    im = Image.new("RGBA", (r * 2 + 40, r * 2 + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for i in range(48):
        a = i / 48 * 2 * math.pi; rr = r if i % 2 == 0 else r * 0.9
        pts.append((r + 20 + rr * math.cos(a), r + 20 + rr * math.sin(a)))
    d.polygon(pts, fill=(235, 28, 36)); d.ellipse((20 + r * .16, 20 + r * .16, 20 + r * 1.84, 20 + r * 1.84), outline=(255, 255, 255), width=5)
    f = F("Anton", int(r * (0.78 if len(txt) <= 3 else 0.6))); bb = f.getbbox(txt)
    d.text((r + 20 - (bb[0] + bb[2]) / 2, r + 20 - r * .16 - (bb[1] + bb[3]) / 2), txt, font=f, fill=(255, 255, 255))
    f2 = F("Mont900", int(r * .26)); bb = f2.getbbox("OFF")
    d.text((r + 20 - (bb[0] + bb[2]) / 2, r + 20 + r * .42 - (bb[1] + bb[3]) / 2), "OFF", font=f2, fill=(255, 255, 255))
    return im
T_BADGE = badge(P["desconto"])
CHK = check_icon(64, ACC + (255,))
T_BEN = [pill(b, F("Mont800", 46), (255, 255, 255, 240), fg=(25, 25, 25), padx=30, pady=26, r=28, icon=CHK) for b in P["beneficios"]]
T_BEN_H = text_layer("POR QUE TODO MUNDO QUER:", F("Mont900", 50), stroke=3)
T_D = [text_layer(P["desejo"][0], F("Anton", 128), stroke=6), text_layer(P["desejo"][1], F("Anton", 128), fill=ACC2, stroke=6)]
T_DSUB = pill(P["desejo_sub"], F("Mont800", 40), (0, 0, 0, 170), padx=32, pady=20)
T_PRE = text_layer(P["preco_pre"], F("Mont900", 58), stroke=3)
T_PRECO = text_layer(P["preco"], F("Anton", 210), fill=ACC2, stroke=8)
T_CTA = pill("TOCA NO CARRINHO", F("Mont900", 58), (235, 28, 36, 255), padx=46, pady=34, icon=emoji("🛒", 70))
T_URG = text_layer("Promoção por tempo limitado", F("Mont800", 40), stroke=2)
T_SETA = emoji("👇", 110)

# ---------------- render por quadro ----------------
def frame_at(t):
    sc = next(k for k, (a, b) in S.items() if a <= t < b) if t < DUR else "cta"
    a, b = S[sc]; lt = t - a; p = lt / (b - a)
    punch = 1 + 0.07 * (1 - ease_out(lt / 0.35))  # zoom de impacto no corte
    if sc == "gancho":
        f = kenburns(ia[0], p, 1.0 * punch, 1.10, (0.5, 0.35, 0.5, 0.55)).convert("RGBA"); f.alpha_composite(GRAD)
        s, al = (1, 1) if lt < 0.001 else pop(lt, 0.0); place(f, T_TAG, W / 2, 1010, s, al)
        for i, L in enumerate(T_G):
            s, al = (1, 1) if lt < 0.001 and i == 0 else pop(lt, i * 0.2, 0.35); place(f, L, W / 2, 1170 + i * 170, s, al, rot=(-2 if i else 0))
    elif sc == "produto":
        f = PBG.copy(); sparkles(f, t)
        e = ease_back(lt / 0.55); z = 0.6 + 0.4 * e + 0.04 * p
        place(f, CARD, W / 2, 1010 + (1 - ease_out(lt / 0.5)) * 500, z, min(1, lt * 3))
        for i, L in enumerate(T_TIT):
            s, al = pop(lt, 0.35 + i * 0.18); place(f, L, W / 2, 300 + i * 105, s, al)
        s, al = pop(lt, 0.9, 0.4); place(f, T_BADGE, W / 2 + 330, 640, s, al, rot=math.sin(t * 2.4) * 8 + 10)
    elif sc == "beneficios":
        f = kenburns(ia[1], p, 1.04 * punch, 1.13, (0.5, 0.3, 0.5, 0.5)).convert("RGBA"); f.alpha_composite(GRAD); f.alpha_composite(GRAD)
        s, al = pop(lt, 0.1); place(f, T_BEN_H, W / 2, 300, s, al)
        for i, L in enumerate(T_BEN):
            t0 = 0.45 + i * 0.7
            if lt < t0: continue
            x = ease_out((lt - t0) / 0.4); place(f, L, W / 2 - (1 - x) * 900, 820 + i * 165, 1, min(1, x * 1.5))
    elif sc == "desejo":
        f = kenburns(ia[2], p, 1.0 * punch, 1.12, (0.4, 0.4, 0.6, 0.4)).convert("RGBA"); f.alpha_composite(GRAD)
        for i, L in enumerate(T_D):
            s, al = pop(lt, 0.1 + i * 0.22, 0.4); place(f, L, W / 2, 1120 + i * 150, s, al)
        s, al = pop(lt, 0.8); place(f, T_DSUB, W / 2, 1450, s, al)
    else:
        f = PBG.copy(); sparkles(f, t)
        e = ease_back(lt / 0.5); place(f, CARD_S, W / 2, 560, (0.7 + 0.3 * e) * (1 + 0.015 * math.sin(t * 4)), min(1, lt * 3))
        s, al = pop(lt, 0.2); place(f, T_BADGE, W / 2 + 290, 280, s * 0.85, al, rot=math.sin(t * 2.4) * 8 + 10)
        s, al = pop(lt, 0.45); place(f, T_PRE, W / 2, 1000, s, al)
        s, al = pop(lt, 0.65, 0.45); place(f, T_PRECO, W / 2, 1150, s, al)
        if lt > 1.1:
            puls = 1 + 0.05 * math.sin((lt - 1.1) * 7)
            s, al = pop(lt, 1.1); place(f, T_CTA, W / 2, 1365, s * puls, al)
            place(f, T_SETA, 170, 1520 + 22 * math.sin(lt * 8), 1, min(1, (lt - 1.1) * 3), rot=0)
        s, al = pop(lt, 1.5); place(f, T_URG, W / 2 + 40, 1500, s, al * 0.95)
    # flash branco curto nos cortes
    for a2, _ in S.values():
        if a2 > 0 and 0 <= t - a2 < 0.12:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - (t - a2) / 0.12)))); f.alpha_composite(fl)
    return f.convert("RGB")

# ---------------- trilha (gerada, sem direitos autorais) ----------------
SR = 44100
def music():
    N = int(SR * (DUR + 0.5)); mus = np.zeros(N); bpm = 124; beat = 60 / bpm; bar = 4 * beat
    rk = P["key"]; prog = [(48, [60, 64, 67]), (55, [59, 62, 67]), (57, [60, 64, 69]), (53, [57, 60, 65])]
    hz = lambda m: 440 * 2 ** ((m + rk - 69) / 12)
    rng = np.random.default_rng(7)
    for i in range(int(DUR / bar) + 1):
        root, ch = prog[i % 4]; s0 = int(i * bar * SR); n = min(int(bar * SR), N - s0)
        if n <= 0: break
        tt = np.arange(n) / SR
        pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.5 * np.sin(2 * np.pi * hz(m) * 2.005 * tt) for m in ch) * 0.035
        mus[s0:s0 + n] += pad * np.minimum(1, tt / 0.2) * np.minimum(1, (bar - tt) / 0.2)
        for s16 in range(16):  # pluck arpejo
            p0 = s0 + int(s16 * beat / 4 * SR); pn = int(0.22 * SR)
            if p0 + pn > N: break
            m = ch[[0, 1, 2, 1][s16 % 4]] + (12 if s16 % 8 >= 4 else 0); pt = np.arange(pn) / SR
            mus[p0:p0 + pn] += 0.07 * (np.sign(np.sin(2 * np.pi * hz(m) * pt)) * 0.3 + np.sin(2 * np.pi * hz(m) * pt)) * np.exp(-pt * 16)
        for e8 in range(8):  # baixo offbeat
            b0 = s0 + int((e8 * beat / 2 + beat / 4) * SR); bn = int(beat / 4 * SR)
            if b0 + bn > N: break
            bt = np.arange(bn) / SR; mus[b0:b0 + bn] += 0.22 * np.sin(2 * np.pi * hz(root - 12) * bt) * np.exp(-bt * 6)
        for q in range(4):
            k0 = s0 + int(q * beat * SR); kn = int(0.3 * SR)
            if k0 + kn > N: break
            kt = np.arange(kn) / SR
            mus[k0:k0 + kn] += 0.55 * np.sin(2 * np.pi * (48 + 110 * np.exp(-kt * 35)) * kt) * np.exp(-kt * 10)
            if q % 2 == 1:
                cn = int(0.18 * SR); mus[k0:k0 + cn] += rng.standard_normal(cn) * np.exp(-np.arange(cn) / SR * 22) * 0.16
            h0 = k0 + int(beat / 2 * SR); hn = int(0.06 * SR)
            if h0 + hn < N: mus[h0:h0 + hn] += np.diff(rng.standard_normal(hn + 1)) * np.exp(-np.arange(hn) / SR * 60) * 0.07
    # intro abafada no 1o segundo (riser)
    mus /= np.abs(mus).max() + 1e-9
    return mus
def sfx():
    N = int(SR * (DUR + 0.5)); x = np.zeros(N); rng = np.random.default_rng(1)
    def whoosh(at, dur=0.4, amp=0.45):
        n = int(dur * SR); s0 = max(0, int(at * SR) - n // 2); nz = rng.standard_normal(n)
        nz = np.convolve(nz, np.ones(18) / 18, "same") * np.sin(np.pi * np.arange(n) / n) ** 2
        x[s0:s0 + n] += amp * nz / (np.abs(nz).max() + 1e-9)
    def blip(at, f=880, amp=0.25):
        n = int(0.12 * SR); s0 = int(at * SR); tt = np.arange(n) / SR
        x[s0:s0 + n] += amp * np.sin(2 * np.pi * f * (1 + 0.6 * tt / 0.12) * tt) * np.exp(-tt * 30)
    def ding(at):
        n = int(1.0 * SR); s0 = int(at * SR); tt = np.arange(n) / SR
        y = sum(np.sin(2 * np.pi * fr * tt) * np.exp(-tt * dk) for fr, dk in [(1318.5, 4), (1760, 5), (2637, 7)]) * 0.3
        x[s0:s0 + n] += y[:N - s0]
    for a, _ in S.values():
        if a > 0: whoosh(a)
    for i in range(2): blip(0.02 + i * 0.2, 700 + i * 200)
    for i in range(4): blip(S["beneficios"][0] + 0.45 + i * 0.7, 900 + i * 80, 0.18)
    ding(S["cta"][0] + 0.65)
    return x
def wav(fn, x):
    x = np.clip(x, -1, 1); w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

if __name__ == "__main__":
    out_dir = f"{ROOT}/videos"; os.makedirs(out_dir, exist_ok=True); tmp = f"/tmp/tts_{key}"; os.makedirs(tmp, exist_ok=True)
    mix = music() * 0.55 + sfx() * 0.6; mix /= max(1, np.abs(mix).max() / 0.95)
    fi = np.minimum(1, np.arange(len(mix)) / (0.05 * SR)); fo = np.clip((DUR - np.arange(len(mix)) / SR) / 0.6, 0, 1)
    wav(f"{tmp}/a.wav", mix * fi * fo)
    if len(sys.argv) > 2:  # preview: salva alguns quadros
        for tt in map(float, sys.argv[2].split(",")): frame_at(tt).save(f"{tmp}/f_{tt:05.2f}.jpg", quality=88)
        sys.exit()
    out = f"{out_dir}/{P['arquivo']}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", f"{tmp}/a.wav", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(frame_at(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print("ok", out)
