import os, subprocess, wave, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = f"{D}/../fbr"; os.makedirs(f"{O}/shots", exist_ok=True)
TR = f"{D}/rs/tr/GTAVI_Launch_Trailer.mp4"
SHOTS = [l.strip()[2:] for l in open(f"{D}/rs/tr/shots.txt")]
def IMG(i): return f"{D}/rs/tr/shots/{SHOTS[i]}"
ANTON = f"{D}/../v/Anton.ttf"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
DUR = 74.0
def run(c): subprocess.run(c, check=True)

# cards: (start, end, big, lines, color, emoji, stamp)
T0, CD = 4.5, 6.2
BR = [
    ("VICE CITY", "RIO DE JANEIRO", "🏖️"),
    ("JACARÉ NA LOJA DE CONVENIÊNCIA", "CAPIVARA NO SHOPPING", "🛍️"),
    ("LEONIDA KEYS", "ANGRA DOS REIS", "🛥️"),
    ("PÂNTANO DE GRASSRIVERS", "PANTANAL", "🐊"),
    ("PERSEGUIÇÃO POLICIAL", "BLITZ DA LEI SECA", "🚔"),
    ("ASSALTO A BANCO", "PIX À NOITE: LIMITE DE MIL REAIS", "💸"),
    ("COMPRAR UM CARRÃO", "IPVA, SEGURO E 60 PARCELAS", "😭"),
    ("6 ESTRELAS DE PROCURADO", "NOME NO SERASA", "⭐"),
    ("JASON E LÚCIA", "JEFERSON E LUCIANA", "👫"),
    ("ATRAVESSAR O MAPA", "3 HORAS NA MARGINAL", "🚗"),
]
CARDS = [(T0 + i * CD, T0 + (i + 1) * CD) + c for i, c in enumerate(BR)]
END = T0 + len(BR) * CD
SH = [
    (0.0, 1.5, "v", TR, 26.2, ""), (1.5, 3.0, "v", TR, 53.0, ""), (3.0, 4.5, "v", TR, 25.0, ""),
]
srcs = [("i", IMG(125), (0.7, 0.3)), ("i", IMG(96), (0.3, 0.6)), ("i", IMG(91), (0.2, 0.7)), ("i", IMG(86), (0.6, 0.3)),
        ("i", IMG(22), (0.35, 0.6)), ("i", IMG(128), (0.4, 0.6)), ("i", IMG(134), (0.15, 0.45)), ("v", TR, 61.0), ("i", IMG(35), (0.4, 0.6)), ("i", IMG(84), (0.2, 0.7))]
for (a_, b_, *_), sr in zip(CARDS, srcs):
    SH.append((a_, b_, sr[0], sr[1], sr[2], ""))
SH.append((END, DUR, "v", TR, 40.0, ""))
files = []
for i, (a, b, kind, src, st, mode) in enumerate(SH):
    out = f"{O}/shots/s{i:02d}.mp4"; files.append(out); d = b - a
    if os.path.exists(out) and not os.environ.get("REDO"): continue
    g = ",eq=contrast=1.06:saturation=1.15:brightness=-0.05"
    if mode == "gray": g += ",hue=s=0,eq=brightness=-0.04:contrast=1.12,vignette=PI/4"
    if mode == "glitch": g += ",rgbashift=rh=-10:bh=10:gv=4,noise=alls=28:allf=t,eq=saturation=1.4"
    if kind == "v":
        cw = int(2160 * 9 / 16); x = (3840 - cw) // 2
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(st), "-i", src, "-t", f"{d:.3f}",
             "-vf", f"crop={cw}:2160:{x}:0,scale={W}:{H}{g},fps={FPS},format=yuv420p", "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
    else:
        im = Image.open(src).convert("RGB"); sc = H * 1.08 / im.height
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS); tmp = f"{O}/shots/i{i:02d}.png"; im.save(tmp)
        p0, p1 = st; mw = im.width - W; mh = im.height - H
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", tmp, "-t", f"{d:.3f}",
             "-vf", f"crop={W}:{H}:'{mw}*({p0}+({p1}-{p0})*t/{d:.3f})':{mh // 2}{g},format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
open(f"{O}/shots/list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{O}/shots/list.txt", "-c", "copy", f"{O}/base.mp4"])

def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def fit(d, t, s, mw=980):
    while d.textlength(t, font=F(s)) > mw: s -= 4
    return s

# full-frame darkening for readability
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = Image.new("L", (1, H))
for y in range(H): g.putpixel((0, y), int(90 + 60 * abs(y - 900) / 1000))
sh = Image.new("RGBA", (W, H), (0, 0, 0, 255)); sh.putalpha(g.resize((W, H))); sh.save(f"{O}/o_shade.png")

OV = [("o_shade.png", 0, DUR)]
# intro
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
e = emoji("🇧🇷", 220); im.alpha_composite(e, (540 - e.width // 2, 470))
d.text((540, 820), "SE O GTA 6", font=F(fit(d, "SE O GTA 6", 200)), fill=(255, 255, 255), anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0))
d.text((540, 1020), "FOSSE NO BRASIL", font=F(fit(d, "FOSSE NO BRASIL", 170)), fill=(255, 230, 0), anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0))
im.save(f"{O}/o_intro.png"); OV.append(("o_intro.png", 0, T0))
for k, (a, b, gta, br, em) in enumerate(CARDS):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 170, 990, 186], 8, fill=(255, 255, 255, 70))
    d.rounded_rectangle([90, 170, 90 + int(900 * (k + 1) / len(CARDS)), 186], 8, fill=(255, 230, 0))
    d.text((540, 235), "SE O GTA 6 FOSSE NO BRASIL", font=F(44), fill=(255, 255, 255), anchor="mm")
    d.text((540, 520), "NO GTA 6:", font=F(64), fill=(200, 200, 200), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    d.text((540, 620), gta, font=F(fit(d, gta, 100)), fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
    im.save(f"{O}/o_c{k}a.png")
    im2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(im2)
    e = emoji(em, 190); im2.alpha_composite(e, (540 - e.width // 2, 730))
    d2.text((540, 1010), "NO BRASIL:", font=F(70), fill=(255, 230, 0), anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0))
    words = br.split(); lines = [br] if len(br) <= 18 else [" ".join(words[:len(words) // 2 + 1]), " ".join(words[len(words) // 2 + 1:])]
    yy = 1140
    for ln in lines:
        s_ = fit(d2, ln, 150); d2.text((540, yy), ln, font=F(s_), fill=(255, 230, 0), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0)); yy += int(s_ * 1.1)
    im2.save(f"{O}/o_c{k}b.png")
    OV.append((f"o_c{k}a.png", a, b)); OV.append((f"o_c{k}b.png", a + 1.6, b))
# CTA + follow card
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.text((540, 760), "E AÍ, O QUE MAIS", font=F(fit(d, "E AÍ, O QUE MAIS", 150)), fill=(255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
d.text((540, 920), "SERIA NO BRASIL?", font=F(fit(d, "SERIA NO BRASIL?", 150)), fill=(255, 230, 0), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
d.text((540, 1070), "COMENTA AÍ", font=F(90), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
im.save(f"{O}/o_cta.png"); OV.append(("o_cta.png", END, DUR))
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle([110, 1240, 970, 1640], 40, fill=(0, 0, 0, 215), outline=(255, 230, 0, 255), width=6)
d.text((540, 1320), "ME SEGUE!", font=F(96), fill=(255, 230, 0), anchor="mm")
d.text((540, 1440), "TIKTOK  @jhonexlives", font=F(62), fill=(255, 255, 255), anchor="mm")
d.text((540, 1540), "YOUTUBE / TWITCH  @jhonlivesx", font=F(54), fill=(255, 255, 255), anchor="mm")
im.save(f"{O}/o_follow.png"); OV.append(("o_follow.png", DUR - 4.5, DUR))

# music (same synth as other videos) + sfx
src = open(f"{D}/build7.py").read()
exec(src[src.index("SR = 44100"):src.index("sfx = np.zeros(N)")])
sfx = np.zeros(N)
def whoosh(at_, dur=0.45, amp=0.5):
    n = int(dur * SR); s0 = max(0, int(at_ * SR) - n // 2); noise = np.random.randn(n); k = np.linspace(40, 4, n).astype(int)
    out = np.array([noise[max(0, i - k[i]):i + 1].mean() for i in range(n)]) * np.sin(np.pi * np.arange(n) / n) ** 2
    sfx[s0:s0 + n] += amp * out / (np.abs(out).max() + 1e-9)
def thump(at_, amp=0.8):
    n = int(0.5 * SR); s0 = int(at_ * SR); kt = np.arange(n) / SR
    sfx[s0:s0 + n] += amp * (np.sin(2 * np.pi * (40 + 120 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 6) + np.random.randn(n) * np.exp(-kt * 40) * 0.4)
for c in CARDS: whoosh(c[0]); thump(c[0] + 1.6, 0.5)
whoosh(END)
def wav(fn, x):
    x = np.clip(x, -1, 1); w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wav(f"{O}/music.wav", mus * 0.9); wav(f"{O}/sfx.wav", sfx / (np.abs(sfx).max() + 1e-9) * 0.8)

inp = ["-i", f"{O}/base.mp4"]
for p, *_ in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-i", f"{O}/{p}"]
inp += ["-i", f"{O}/music.wav", "-i", f"{O}/sfx.wav"]
fc = []; prev = "0:v"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i+1}:v]format=rgba,trim=duration={DUR},fade=in:st={a}:d=0.15:alpha=1[o{i}]")
    fc.append(f"[{prev}][o{i}]overlay=0:0:enable='between(t,{a},{b})':shortest=1[v{i}]"); prev = f"v{i}"
flash = "+".join(f"between(t,{c[0]},{c[0]+0.08})" for c in CARDS)
fc.append(f"[{prev}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.8:t=fill:enable='{flash}',format=yuv420p[v]")
nv = len(OV) + 1
fc.append(f"[{nv}:a]volume=0.55,afade=t=out:st={DUR-2}:d=2[m];[{nv+1}:a]volume=0.5[fx];[m][fx]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", str(DUR), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{O}/gta6_no_brasil.mp4"])
print("ok")
