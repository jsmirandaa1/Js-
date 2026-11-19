"""Build vertical clips from the Twitch VOD. usage: python3 build_clip.py <name>"""
import os, sys, json, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
ANTON = f"{D}/../v/Anton.ttf"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
FC = (1464, 738, 456, 342)          # facecam x,y,w,h in 1920x1080
TOPH = int(W * FC[3] / FC[2])       # 810
GX = 410                            # gameplay crop x
idx = json.load(open(f"{D}/segs_index.json"))
def run(c): subprocess.run(c, check=True)

CLIPS = {
    "mortes": dict(
        parts=[(1950, 2002), (2146, 2156), (2300, 2337)],
        title="EU TENTANDO SER DISCRETO NO GTA 6",
        lines=[(1993, 2002), (2149, 2156)],           # VOD windows with his voice -> captions
        ov=[("TENTATIVA 1", "🤫", 1950, 3.0), ("TENTATIVA 2", "😤", 2300, 3.0), ("2 MORTES. 0 DISCRIÇÃO", "💀", 2331.5, 5.5)],
    ),
    "camaleao": dict(
        parts=[(5722, 5800)],
        title="TEM BICHO EM TODO LUGAR NO GTA 6",
        lines=[(5735, 5745), (5750, 5755), (5760, 5765)],
        ov=[("CAMALEÃO???", "🦎", 5737, 3.5)],
    ),
    "barco": dict(
        parts=[(1318, 1398)],
        title="O GRÁFICO DO GTA 6 É SURREAL",
        lines=[(1325, 1398)],
        ov=[("OLHA ESSA ÁGUA", "🌊", 1322, 3.5), ("ISSO É UM JOGO???", "🤯", 1355, 3.5)],
    ),
    "ponte": dict(
        parts=[(7489.2, 7490.6, 0.5), (7474, 7522, 1.0), (7488.5, 7497.5, 0.5)],
        title="CAIU UM CARRO DA PONTE NO GTA 6",
        lines=[],
        ov=[("ISSO É BUG???", "😳", 0.0, 2.8, "clip"), ("OLHA PRA CIMA", "👆", 7485.5, 3.0), ("REPLAY", "🎬", 50.8, 1.2, "clip")],
    ),
    "basquete": dict(
        parts=[(3540, 3620)],
        title="DÁ PRA JOGAR BASQUETE NO GTA 6?",
        lines=[(3549, 3556)],
        ov=[("SIM, DÁ!", "🏀", 3546, 3.0)],
    ),
}
name = sys.argv[1]; C = CLIPS[name]
O = f"{D}/clips/{name}"; os.makedirs(O, exist_ok=True)

# 1) fetch + cut parts (exact) -> raw 1920x1080 clip
cuts = []
for j, pt in enumerate(C["parts"]):
    a, b = pt[0], pt[1]; sp = pt[2] if len(pt) > 2 else 1.0
    ks = [k for k, (t, d, u) in enumerate(idx) if t + d > a and t < b]
    for k in ks:
        p = f"{D}/ts/{k}.ts"
        if not os.path.exists(p) or os.path.getsize(p) == 0: run(["curl", "-sS", "--max-time", "120", "-o", p, idx[k][2]])
    open(f"{O}/l{j}.txt", "w").write("".join(f"file '{D}/ts/{k}.ts'\n" for k in ks))
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{O}/l{j}.txt", "-c", "copy", f"{O}/cat{j}.ts"])
    t0 = idx[ks[0]][0]
    out = f"{O}/p{j}.mp4"; cuts.append(out)
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a - t0:.3f}", "-i", f"{O}/cat{j}.ts", "-t", f"{(b - a) / sp:.3f}",
         "-vf", f"setpts=PTS/{sp},fps={FPS}", "-af", f"atempo={sp}" if sp >= 0.5 else "atempo=0.5",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "aac", "-ar", "48000", "-ac", "2", out])
open(f"{O}/parts.txt", "w").write("".join(f"file '{c}'\n" for c in cuts))
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{O}/parts.txt", "-c", "copy", f"{O}/raw.mp4"])
DUR = sum((p[1] - p[0]) / (p[2] if len(p) > 2 else 1.0) for p in C["parts"])
def v2c(t):  # VOD time -> clip time
    acc = 0
    for p in C["parts"]:
        a, b = p[0], p[1]; sp = p[2] if len(p) > 2 else 1.0
        if a <= t <= b and sp == 1.0: return acc + t - a
        acc += (b - a) / sp
    return None

# 2) word-level captions for his lines
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{O}/raw.mp4", "-ac", "1", "-ar", "16000", f"{O}/a.wav"], check=True)
from faster_whisper import WhisperModel
import wave
wv = wave.open(f"{O}/a.wav"); aud = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(aud, language="pt", word_timestamps=True, beam_size=5, vad_filter=True)
words = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]
wins = [(v2c(a) - 2.5, v2c(b) + 2.0) for a, b in C["lines"] if v2c(a) is not None]
keep = [w for w in words if any(x <= w[0] <= y for x, y in wins)]
json.dump(words, open(f"{O}/words_all.json", "w"), ensure_ascii=False)
ev, cur = [], []
for w in keep:
    if cur and w[0] - cur[-1][1] > 0.8: ev.append(cur); cur = []
    cur.append(w)
    if len(" ".join(x[2] for x in cur)) >= 12 or len(cur) >= 3 or re.search(r"[,.?!]$", w[2]): ev.append(cur); cur = []
if cur: ev.append(cur)
def at(t): return f"0:{int(t//60):02d}:{t%60:05.2f}"
L = []
for e in ev:
    txt = " ".join(x[2] for x in e).upper()
    L.append(f"Dialogue: 0,{at(e[0][0])},{at(e[-1][1] + 0.3)},Cap,,0,0,0,,{{\\pos(540,1010)\\fscx70\\fscy70\\t(0,80,\\fscx104\\fscy104)\\t(80,140,\\fscx100\\fscy100)}}{txt}")
print("captions:", [" ".join(x[2] for x in e) for e in ev])
open(f"{O}/caps.ass", "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,1,0,1,10,6,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(L) + "\n")

# 3) overlays
def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def fit(d, t, s, mw=1000):
    while d.textlength(t, font=F(s)) > mw: s -= 3
    return s
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
s = fit(d, C["title"], 64, 960); tw = d.textlength(C["title"], font=F(s))
d.rounded_rectangle([540 - tw / 2 - 30, 40, 540 + tw / 2 + 30, 40 + s * 1.5], 22, fill=(0, 0, 0, 200))
d.text((540, 40 + s * 0.75), C["title"], font=F(s), fill=(255, 230, 0), anchor="mm")
d.rectangle([0, TOPH - 4, W, TOPH + 4], fill=(255, 230, 0, 255))
im.save(f"{O}/o_title.png")
OV = [("o_title.png", 0, DUR)]
for i, o in enumerate(C["ov"]):
    txt, em, vt, dur = o[:4]; t = vt if len(o) > 4 else v2c(vt)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    e = emoji(em, 150); im.alpha_composite(e, (540 - e.width // 2, 1180))
    s = fit(d, txt, 130, 980)
    d.text((540, 1430), txt, font=F(s), fill=(255, 230, 0), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0))
    im.save(f"{O}/o{i}.png"); OV.append((f"o{i}.png", t, min(DUR, t + dur)))
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle([190, 1700, 890, 1800], 50, fill=(255, 40, 80, 230))
d.text((540, 1750), "SEGUE PRA MAIS 🎮".replace(" 🎮", ""), font=F(60), fill=(255, 255, 255), anchor="mm")
im.save(f"{O}/o_follow.png"); OV.append(("o_follow.png", max(0, DUR - 4), DUR))

# 4) compose
fx, fy, fw, fh = FC
gw = int(1080 * W / (H - TOPH))
inp = ["-i", f"{O}/raw.mp4"]
for p, *_ in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-i", f"{O}/{p}"]
fc = [f"[0:v]split=2[a][b]",
      f"[a]crop={fw}:{fh}:{fx}:{fy},scale={W}:{TOPH},eq=contrast=1.05:saturation=1.1[top]",
      f"[b]crop={gw}:1080:{GX}:0,scale={W}:{H - TOPH},eq=contrast=1.05:saturation=1.15[bot]",
      f"[top][bot]vstack=2[st]"]
prev = "st"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i+1}:v]format=rgba,trim=duration={DUR},fade=in:st={a:.2f}:d=0.15:alpha=1[o{i}]")
    fc.append(f"[{prev}][o{i}]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})':shortest=1[v{i}]"); prev = f"v{i}"
fc.append(f"[{prev}]ass={O}/caps.ass:fontsdir={os.path.dirname(ANTON)},format=yuv420p[v]")
fc.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", f"{DUR:.2f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{O}/corte_{name}.mp4"])
print("ok", name, DUR)
