import os, subprocess, wave, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = f"{D}/../ftl"; os.makedirs(f"{O}/shots", exist_ok=True)
TR = f"{D}/rs/tr/GTAVI_Launch_Trailer.mp4"
SHOTS = [l.strip()[2:] for l in open(f"{D}/rs/tr/shots.txt")]
def IMG(i): return f"{D}/rs/tr/shots/{SHOTS[i]}"
ANTON = f"{D}/../v/Anton.ttf"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
DUR = 66.0
def run(c): subprocess.run(c, check=True)

# cards: (start, end, big, lines, color, emoji, stamp)
CARDS = [
    (0.0, 4.5, "13 ANOS", ["A HISTÓRIA DO GTA 6", "EM 1 MINUTO"], (255, 230, 0), "⏳", None),
    (4.5, 11.0, "2013", ["O GTA 5 É LANÇADO", "NINGUÉM IMAGINAVA QUE O", "PRÓXIMO IA DEMORAR TANTO"], (255, 255, 255), "🎮", None),
    (11.0, 17.0, "2014–2021", ["8 ANOS DE SILÊNCIO", "SÓ RUMOR, TEORIA E MEME"], (170, 170, 170), "🤡", None),
    (17.0, 23.0, "FEV 2022", ["A ROCKSTAR CONFIRMA:", "O GTA 6 EXISTE"], (80, 220, 120), "✅", None),
    (23.0, 30.0, "SET 2022", ["O MAIOR VAZAMENTO", "DA HISTÓRIA DOS GAMES:", "90 VÍDEOS DO JOGO VAZAM"], (255, 70, 70), "😱", None),
    (30.0, 37.0, "DEZ 2023", ["SAI O TRAILER 1", "90 MILHÕES DE VIEWS", "EM 24 HORAS"], (255, 120, 200), "🔥", None),
    (37.0, 43.5, "MAIO 2025", ["PRA MAIO DE 2026"], (255, 255, 255), "💀", ("ADIADO", -10)),
    (43.5, 50.0, "NOV 2025", ["PRA 19 DE NOVEMBRO"], (255, 255, 255), "😭", ("ADIADO DE NOVO", 8)),
    (50.0, 58.0, "HOJE", ["19 DE NOVEMBRO, 00:00", "A ESPERA ACABOU"], (120, 200, 255), "🎮", None),
    (58.0, DUR, "E VOCÊ?", ["ESPEROU DESDE QUANDO?", "COMENTA O ANO"], (255, 230, 0), "👇", None),
]
# shots: (start, end, kind, src, t/pan, mode)
SH = [
    (0.0, 1.5, "v", TR, 61.0, ""), (1.5, 3.0, "v", TR, 53.0, ""), (3.0, 4.5, "v", TR, 49.4, ""),
    (4.5, 11.0, "i", IMG(137), (0.2, 0.7), "gray"),
    (11.0, 14.0, "v", TR, 28.0, "gray"), (14.0, 17.0, "i", IMG(86), (0.6, 0.3), "gray"),
    (17.0, 20.0, "v", TR, 18.2, ""), (20.0, 23.0, "i", IMG(120), (0.6, 0.3), ""),
    (23.0, 26.5, "v", TR, 65.5, "glitch"), (26.5, 30.0, "v", TR, 42.0, "glitch"),
    (30.0, 33.5, "v", TR, 26.2, ""), (33.5, 37.0, "v", TR, 40.0, ""),
    (37.0, 40.0, "v", TR, 8.0, ""), (40.0, 43.5, "v", TR, 47.0, ""),
    (43.5, 47.0, "v", TR, 59.0, "gray"), (47.0, 50.0, "v", TR, 33.0, "gray"),
    (50.0, 53.0, "v", TR, 77.6, ""), (53.0, 58.0, "i", IMG(125), (0.7, 0.3), ""),
    (58.0, 62.0, "i", IMG(44), (0.3, 0.6), ""), (62.0, DUR, "v", TR, 67.5, ""),
]
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
for k, (a, b, big, lines, col, em, stamp) in enumerate(CARDS):
    # progress bar (timeline) at top
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 170, 990, 186], 8, fill=(255, 255, 255, 70))
    d.rounded_rectangle([90, 170, 90 + int(900 * (k + 1) / len(CARDS)), 186], 8, fill=(255, 230, 0))
    d.text((540, 235), "LINHA DO TEMPO DO GTA 6", font=F(44), fill=(255, 255, 255), anchor="mm")
    y = 700
    if em: e = emoji(em, 170); im.alpha_composite(e, (540 - e.width // 2, 470))
    s = fit(d, big, 260); d.text((540, y), big, font=F(s), fill=col, anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0))
    im.save(f"{O}/o_c{k}a.png")
    # lines appear slightly later
    im2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(im2); yy = 900
    if stamp:
        txt, rot = stamp
        st = Image.new("RGBA", (1000, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); red = (230, 20, 30, 255)
        sd.rounded_rectangle([20, 20, 980, 280], 26, outline=red, width=20)
        ss = fit(sd, txt, 190, 880); sd.text((500, 150), txt, font=F(ss), fill=red, anchor="mm")
        st = st.rotate(rot, expand=True, resample=Image.BICUBIC)
        im2.alpha_composite(st, (540 - st.width // 2, 1000 - st.height // 2)); yy = 1220
    for j, ln in enumerate(lines):
        s = fit(d2, ln, 92 if j == 0 else 78)
        d2.text((540, yy), ln, font=F(s), fill=(255, 255, 255) if j == 0 else (255, 230, 0), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
        yy += int(s * 1.25)
    im2.save(f"{O}/o_c{k}b.png")
    OV.append((f"o_c{k}a.png", a, b)); OV.append((f"o_c{k}b.png", min(a + 0.7, b), b))

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
for c in CARDS[1:]: whoosh(c[0])
thump(37.7); thump(44.2)
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
flash = "+".join(f"between(t,{c[0]},{c[0]+0.08})" for c in CARDS[1:])
fc.append(f"[{prev}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.8:t=fill:enable='{flash}',format=yuv420p[v]")
nv = len(OV) + 1
fc.append(f"[{nv}:a]volume=0.55,afade=t=out:st={DUR-2}:d=2[m];[{nv+1}:a]volume=0.5[fx];[m][fx]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", str(DUR), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{O}/linha_do_tempo_gta6.mp4"])
print("ok")
