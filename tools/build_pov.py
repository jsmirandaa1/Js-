"""POV: faltam 5 minutos pro GTA 6. Usage: python3 build_pov.py  (expects ../fpov/voz.mp3 + voz_words.json)"""
import os, sys, json, re, subprocess, wave, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from capw import build_ev
O = f"{D}/../fpov"; os.makedirs(f"{O}/shots", exist_ok=True)
TR = f"{D}/rs/tr/GTAVI_Launch_Trailer.mp4"; PL = f"{D}/rs/tr/GTAVI_Pre-Load_Now.mp4"
SHOTS = [l.strip()[2:] for l in open(f"{D}/rs/tr/shots.txt")]
def IMG(i): return f"{D}/rs/tr/shots/{SHOTS[i]}"
ANTON = f"{D}/../v/Anton.ttf"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
def run(c): subprocess.run(c, check=True)
def norm(s): return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode().strip(".,!?:;…\"'")

VDUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{O}/voz.mp3"],
                            capture_output=True, text=True).stdout)
words = json.load(open(f"{O}/voz_words.json"))
toks = []
for a, b, t in words:
    if t.startswith("-") and toks: toks[-1][2] += t; toks[-1][1] = b
    else: toks.append([a, b, t])
N_ = [norm(t[2]) for t in toks]

def find(seq, after=0.0):
    seq = [norm(x) for x in seq.split()]
    for i in range(len(N_) - len(seq) + 1):
        if toks[i][0] >= after and N_[i:i + len(seq)] == seq: return toks[i][0]
    return None
def anchor(options, after, default):
    for o in options:
        t = find(o, after)
        if t is not None: return t
    return default

# anchors (fall back to proportional guesses if whisper wrote numbers differently)
T = {}
T["55"] = anchor(["cinquenta e cinco", "23 55", "23:55", "55"], 0.5, VDUR * 0.07)
T["56"] = anchor(["cinquenta e seis", "23:56", "56"], T["55"] + 1, VDUR * 0.25)
T["57"] = anchor(["cinquenta e sete", "23:57", "57"], T["56"] + 1, VDUR * 0.36)
T["58"] = anchor(["cinquenta e oito", "23:58", "58"], T["57"] + 1, VDUR * 0.52)
T["59"] = anchor(["cinquenta e nove", "23:59", "59"], T["58"] + 1, VDUR * 0.62)
for k in ["55", "56", "57", "58", "59"]:
    i = min(range(len(toks)), key=lambda j: abs(toks[j][0] - T[k]))
    if i > 0 and N_[i - 1] == "23": T[k] = toks[i - 1][0]
    t = find("vinte e tres", T[k] - 2.5)
    if t is not None and t < T[k]: T[k] = t
T["00"] = anchor(["meia-noite", "meia noite"], T["59"] + 1, VDUR * 0.78)
T["upd"] = anchor(["instalando"], T["00"], T["00"] + 1.5)
T["esp"] = anchor(["e voce esperou", "voce esperou", "esperou treze", "esperou 13"], T["upd"], T["upd"] + 3)
T["cta"] = anchor(["comenta"], T["esp"], VDUR - 4)
print({k: round(v, 2) for k, v in T.items()}, "VDUR", round(VDUR, 2))

DUR = max(VDUR + 2.5, 61.6)   # >= 1:01 for TikTok monetization
S0 = T["00"]
SH = [  # (start, end, kind, src, t/pan, mode)
    (0.0, T["55"], "v", TR, 17.9, ""),
    (T["55"], T["55"] + (T["56"] - T["55"]) / 2, "v", TR, 59.0, ""),
    (T["55"] + (T["56"] - T["55"]) / 2, T["56"], "v", PL, 15.0, ""),
    (T["56"], T["57"], "v", TR, 36.4, ""),
    (T["57"], T["57"] + (T["58"] - T["57"]) / 2, "v", TR, 45.0, ""),
    (T["57"] + (T["58"] - T["57"]) / 2, T["58"], "v", PL, 3.0, ""),
    (T["58"], T["59"], "v", TR, 35.0, ""),
    (T["59"], S0, "v", TR, 63.0, "slow"),
    (S0, T["upd"], "v", TR, 23.2, ""),
    (T["upd"], T["cta"], "black", None, 0, ""),
    (T["cta"], DUR, "v", TR, 40.0, ""),
]
files = []
for i, (a, b, kind, src, st, mode) in enumerate(SH):
    out = f"{O}/shots/s{i:02d}.mp4"; files.append(out); d = b - a
    if d <= 0.05: files.pop(); continue
    if kind == "black":
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=0x07070c:s={W}x{H}:r={FPS}:d={d:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]); continue
    g = ",eq=contrast=1.06:saturation=1.15"
    pre = ""
    if mode == "slow": pre = "setpts=2.5*PTS,"; g += ",vignette=PI/4"
    cw = int(2160 * 9 / 16); x = (3840 - cw) // 2
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(st), "-i", src, "-t", f"{d:.3f}",
         "-vf", f"{pre}crop={cw}:2160:{x}:0,scale={W}:{H}{g},fps={FPS},format=yuv420p", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
open(f"{O}/shots/list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{O}/shots/list.txt", "-c", "copy", f"{O}/base.mp4"])

# captions
ev = build_ev(f"{O}/voz_words.json", [("23 ,55.", "23:55."), ("23 ,56.", "23:56."), ("23 ,57.", "23:57."), ("23 ,58.", "23:58."), ("23 ,59.", "23:59."), ("soar", "suar"), ("Meia noite.", "Meia-noite."), ("100 %", "100%")], VDUR)
ev = [e for e in ev if not (T["upd"] - 0.05 <= e[0] < T["esp"])]  # update gag is shown as on-screen text
HL = {"GTA", "6", "MEIA-NOITE", "TREZE", "13", "ADIAMENTOS", "VAZAMENTO", "MÃE", "SUAR", "FRIO", "NADA", "ATUALIZAÇÃO", "POV", "POV:",
      "HISTÓRICO", "CEM", "100", "TREZENTAS", "300", "SILÊNCIO", "COMENTA", "SEGUE", "GAMEPLAY"}
def at(t): return f"0:{int(t//60):02d}:{t%60:05.2f}"
def fmt(x):
    o = []
    for w in x.upper().split():
        c = re.sub(r"[,.?!:…\"]", "", w)
        o.append("{\\c&H00E6FF&}" + w + "{\\c&HFFFFFF&}" if c in HL or w in HL else w)
    return " ".join(o)
lines = [f"Dialogue: 0,{at(a)},{at(b)},Cap,,0,0,0,,{{\\pos(540,1400)\\fscx70\\fscy70\\t(0,80,\\fscx104\\fscy104)\\t(80,140,\\fscx100\\fscy100)}}{fmt(x)}"
         for a, b, x in ev]
open(f"{O}/caps.ass", "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,108,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,1,0,1,10,6,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n")

def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def fit(d, t, s, mw=980):
    while d.textlength(t, font=F(s)) > mw: s -= 4
    return s
def card(fn, big=None, bigcol=(255, 255, 255), sub=None, subcol=(255, 230, 0), em=None, y=640, bigsize=330):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if em: e = emoji(em, 150); im.alpha_composite(e, (540 - e.width // 2, y - 330))
    if big: d.text((540, y), big, font=F(fit(d, big, bigsize)), fill=bigcol, anchor="mm", stroke_width=16, stroke_fill=(0, 0, 0))
    if sub:
        yy = y + 230
        for j, ln in enumerate(sub if isinstance(sub, list) else [sub]):
            s = fit(d, ln, 96); d.text((540, yy), ln, font=F(s), fill=subcol if j == 0 else (255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0)); yy += int(s * 1.2)
    im.save(f"{O}/{fn}")

g = Image.new("L", (1, H))
for y in range(H): g.putpixel((0, y), int(70 + 90 * abs(y - 800) / 1100))
sh = Image.new("RGBA", (W, H), (0, 0, 0, 255)); sh.putalpha(g.resize((W, H))); sh.save(f"{O}/o_shade.png")
card("o_title.png", "POV:", (255, 230, 0), ["FALTAM 5 MINUTOS", "PRO GTA 6"], (255, 255, 255), "⏰", 700, 300)
card("o_55.png", "23:55", (255, 255, 255), "🎮 100% BAIXADO".replace("🎮 ", ""), em="🎮")
card("o_56.png", "23:56", (255, 255, 255), "\"AGORA NÃO, MÃE\"", em="🍽️")
card("o_57.png", "23:57", (255, 200, 60), "300 MENSAGENS NO ZAP", em="💬")
card("o_58.png", "23:58", (255, 120, 60), "ATUALIZA… NADA", em="🔄")
card("o_59.png", "23:59", (255, 50, 50), ["13 ANOS", "2 ADIAMENTOS"], em="😰")
card("o_00.png", "00:00", (90, 255, 140), None, y=330, bigsize=230)
card("o_esp.png", None, sub=["13 ANOS…", "ESPERA MAIS UM POUQUINHO"], y=880)
card("o_cta.png", "VOCÊ TÁ", (255, 230, 0), ["NESSE POV AGORA?", "COMENTA 👇".replace(" 👇", "")], (255, 255, 255), "👇", 700, 240)
# update screen
c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
d.text((540, 640), "INSTALANDO ATUALIZAÇÃO", font=F(fit(d, "INSTALANDO ATUALIZAÇÃO", 90)), fill=(255, 255, 255), anchor="mm")
d.rounded_rectangle([140, 720, 940, 770], 25, fill=(50, 50, 60)); d.rounded_rectangle([140, 720, 156, 770], 25, fill=(40, 220, 100))
d.text((540, 830), "2%", font=F(110), fill=(40, 220, 100), anchor="mm")
c.save(f"{O}/o_upd.png")

M = lambda a, b: (a + b) / 2
OV = [("o_shade.png", 0, DUR), ("o_title.png", 0, T["55"] - 0.05),
      ("o_55.png", T["55"], T["56"]), ("o_56.png", T["56"], T["57"]), ("o_57.png", T["57"], T["58"]),
      ("o_58.png", T["58"], T["59"]), ("o_59.png", T["59"], S0), ("o_00.png", S0, T["upd"]),
      ("o_upd.png", T["upd"], T["cta"]), ("o_esp.png", T["esp"], T["cta"]), ("o_cta.png", T["cta"], DUR)]

# music: same synth, cut to silence at 23:59, back after update gag
src = open(f"{D}/build7.py").read()
DUR_ = DUR; exec(src[src.index("SR = 44100"):src.index("sfx = np.zeros(N)")].replace("DUR", "DUR_"))
a59, a00, aup, acta = (int(x * SR) for x in (T["59"], S0, T["upd"], T["cta"]))
fade = np.ones(N); fade[a59:a00] = np.linspace(1, 0.0, a00 - a59); fade[a00:aup] = 1.0; fade[aup:acta] = 0.0
fade[acta:] = np.minimum(1, np.arange(N - acta) / (0.8 * SR))
mus = mus * fade
sfx = np.zeros(N)
def tick(at_, amp=0.35):
    n = int(0.05 * SR); s0 = int(at_ * SR); kt = np.arange(n) / SR
    if s0 + n < N: sfx[s0:s0 + n] += amp * np.sin(2 * np.pi * 1800 * kt) * np.exp(-kt * 120)
def thump(at_, amp=0.9):
    n = int(0.6 * SR); s0 = int(at_ * SR); kt = np.arange(n) / SR
    sfx[s0:s0 + n] += amp * (np.sin(2 * np.pi * (40 + 120 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 5) + np.random.randn(n) * np.exp(-kt * 40) * 0.4)
t = T["55"]
while t < S0: tick(t, 0.25 if t < T["59"] else 0.45); t += 1.0 if t < T["58"] else 0.5
thump(S0); thump(T["upd"], 0.6)
def wav(fn, x):
    x = np.clip(x, -1, 1); w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wav(f"{O}/music.wav", mus * 0.9); wav(f"{O}/sfx.wav", sfx / (np.abs(sfx).max() + 1e-9) * 0.8)

inp = ["-i", f"{O}/base.mp4"]
for p, *_ in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-i", f"{O}/{p}"]
inp += ["-i", f"{O}/voz.mp3", "-i", f"{O}/music.wav", "-i", f"{O}/sfx.wav"]
fc = []; prev = "0:v"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i+1}:v]format=rgba,trim=duration={DUR},fade=in:st={a}:d=0.12:alpha=1[o{i}]")
    fc.append(f"[{prev}][o{i}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})':shortest=1[v{i}]"); prev = f"v{i}"
fc.append(f"[{prev}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.9:t=fill:enable='between(t,{S0:.3f},{S0+0.15:.3f})',"
          f"ass={O}/caps.ass:fontsdir={os.path.dirname(ANTON)},format=yuv420p[v]")
nv = len(OV) + 1
fc.append(f"[{nv}:a]apad,volume=1.15[vv];[{nv+1}:a]volume=0.18[m];[{nv+2}:a]volume=0.6[fx];"
          f"[vv][m][fx]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", f"{DUR:.2f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{O}/pov_5min_gta6.mp4"])
print("ok", round(DUR, 2))
