import os, json, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
ANTON = f"{D}/../v/Anton.ttf"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1920, 1080, 30
DUR = 0.0  # set below
YEL = (255, 212, 0)
idx = json.load(open(f"{D}/segs_index.json"))
def run(c): subprocess.run(c, check=True)
os.makedirs(f"{D}/sh", exist_ok=True); os.makedirs(f"{D}/ov", exist_ok=True)
# ---------- voice assembly (original + 5 extras) ----------
VO = f"{D}/voz.mp3"; EX = f"{D}/extra.mp3"
PIECES = [(VO, 0, 136.35), (EX, 0, 40.2), (VO, 136.35, 234.1), (EX, 40.2, 64.0), (VO, 234.1, 258.5), (EX, 64.0, 86.3),
          (VO, 258.5, 270.0), (VO, 276.1, 279.6), (EX, 86.3, 116.6), (VO, 279.6, 302.3), (EX, 116.6, 132.05), (VO, 302.3, 331.81)]
inputs = []; fcv = []
for i, (src, a, b) in enumerate(PIECES):
    inputs += ["-ss", str(a), "-t", f"{b - a:.3f}", "-i", src]; fcv.append(f"[{i}:a]")
run(["ffmpeg", "-loglevel", "error", "-y"] + inputs + ["-filter_complex", "".join(fcv) + f"concat=n={len(PIECES)}:v=0:a=1[a]", "-map", "[a]", "-ar", "44100", f"{D}/voz2.wav"])
NEWSTART = {}; t = 0.0
for i, (src, a, b) in enumerate(PIECES):
    NEWSTART[i] = t; t += b - a
VDUR = t
def _map(x, which, end):
    for i, (src, a, b) in enumerate(PIECES):
        if src != which: continue
        if (a < x <= b) if end else (a <= x < b): return NEWSTART[i] + x - a
    for i, (src, a, b) in enumerate(PIECES):
        if src == which and a <= x <= b: return NEWSTART[i] + x - a
    return None
def m(x, end=False): return _map(x, VO, end)
def ex(x, end=False): return _map(x, EX, end)
MAP = True
DUR = VDUR + 3.2


# ---------- B-roll: (start, end, vod_start) ----------
BR_OLD = [(0, 12, 5050), (12, 30, 3185), (30, 48, 2731),
      (48, 58, 4003), (58, 70.3, 3546),
      (70.3, 102.2, 2161),
      (102.2, 136.35, 1261),
      (136.35, 176.5, 900), (176.5, 210.5, 1471),
      (210.5, 234.1, 1561),
      (234.1, 254.3, 570), (254.3, 258.5, 450), (258.5, 270.0, 454.2),
      (276.1, 279.6, 304.0), (279.6, 283.8, 307.5), (283.8, 302.3, 2281),
      (302.3, 322.5, 3215)]
BR = [(m(x), m(y, True), v) for x, y, v in BR_OLD]
BR += [(ex(0), ex(40.2, True), 1621), (ex(40.2), ex(64.0, True), 2461), (ex(64.0), ex(86.3, True), 1020), (ex(86.3), ex(116.6, True), 1921), (ex(116.6), ex(132.05, True), 3335)]
BR.append((m(322.5), DUR, 2851))
BR.sort()
files = []
for i, (a, b, v) in enumerate(BR):
    d = b - a; out = f"{D}/sh/n{i:02d}.mp4"; files.append(out)
    if os.path.exists(out) and not os.environ.get("REDO"): continue
    ks = [k for k, (t, dd, u) in enumerate(idx) if t + dd > v and t < v + d]
    for k in ks:
        p = f"{D}/ts/{k}.ts"
        if not os.path.exists(p) or os.path.getsize(p) == 0: run(["curl", "-sS", "--max-time", "120", "-o", p, idx[k][2]])
    open(f"{D}/sh/l.txt", "w").write("".join(f"file '{D}/ts/{k}.ts'\n" for k in ks))
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{D}/sh/l.txt", "-c", "copy", f"{D}/sh/cat.ts"])
    t0 = idx[ks[0]][0]
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{v - t0:.3f}", "-i", f"{D}/sh/cat.ts", "-t", f"{d:.3f}", "-an",
         "-vf", f"scale={W}:{H},fps={FPS},eq=contrast=1.04:saturation=1.1,format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
open(f"{D}/sh/list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{D}/sh/list.txt", "-c", "copy", f"{D}/base.mp4"])

# ---------- graphics ----------
def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
def blank(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def fit(d, t, s, mw):
    while d.textlength(t, font=F(s)) > mw: s -= 3
    return s
OV = []
def add(img, a, b, name):
    p = f"ov/{name}.png"; img.save(f"{D}/{p}")
    if MAP and not name.startswith("base"): a, b = m(a), m(b, True)
    OV.append((p, a, b))

# permanent bottom gradient + small brand tag
g = Image.new("L", (1, H))
for y in range(H): g.putpixel((0, y), int(150 * max(0, (y - 650) / 430) ** 1.4))
im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); im.putalpha(g.resize((W, H)))
d = ImageDraw.Draw(im); d.text((60, 60), "@jhonlivesx", font=F(36), fill=(255, 255, 255, 200), anchor="lm")
add(im, 0, DUR, "base")

def dim(a, b, name, alpha=120):
    add(Image.new("RGBA", (W, H), (0, 0, 0, alpha)), a, b, name)

def chapter(n, title, a, dur=4.0):
    im = blank(); d = ImageDraw.Draw(im)
    tw = d.textlength(title, font=F(64))
    d.rectangle([60, 860, 60 + tw + 220, 990], fill=(0, 0, 0, 200))
    d.rectangle([60, 860, 76, 990], fill=YEL)
    d.text((110, 892), f"CAPÍTULO {n}", font=F(34), fill=YEL, anchor="lm")
    d.text((110, 945), title, font=F(64), fill=(255, 255, 255), anchor="lm")
    add(im, a, a + dur, f"ch{n}")

def big(lines, a, b, name, em=None, y=540, sizes=(150, 80), cols=(YEL, (255, 255, 255)), dimit=True):
    if dimit: dim(a, b, name + "_dim", 110)
    im = blank(); d = ImageDraw.Draw(im)
    yy = y - (len(lines) - 1) * 60
    if em: e = emoji(em, 150); im.alpha_composite(e, (W // 2 - e.width // 2, yy - 260))
    for j, ln in enumerate(lines):
        s = fit(d, ln, sizes[min(j, 1)], 1700)
        d.text((W // 2, yy), ln, font=F(s), fill=cols[min(j, 1)], anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
        yy += int(s * 1.15)
    add(im, a, b, name)

def side(lines, a, b, name, em=None):
    """card on the left third"""
    im = blank(); d = ImageDraw.Draw(im)
    h = 120 + 95 * len(lines)
    d.rounded_rectangle([60, 300, 900, 300 + h], 28, fill=(0, 0, 0, 200), outline=YEL, width=5)
    yy = 370
    if em: e = emoji(em, 80); im.alpha_composite(e, (90, 330)); yy = 370
    for j, ln in enumerate(lines):
        s = fit(d, ln, 76 if j == 0 else 56, 720)
        d.text((200 if (em and j == 0) else 100, yy), ln, font=F(s), fill=YEL if j == 0 else (255, 255, 255), anchor="lm"); yy += 95
    add(im, a, b, name)

def lst(items, upto, a, b, name, title):
    dim(a, b, name + "_dim", 120)
    im = blank(); d = ImageDraw.Draw(im)
    d.text((W // 2, 170), title, font=F(70), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    yy = 330
    for j, it in enumerate(items[:upto]):
        on = j == upto - 1
        d.text((300, yy), it, font=F(fit(d, it, 84, 1350)), fill=YEL if on else (200, 200, 200), anchor="lm", stroke_width=6, stroke_fill=(0, 0, 0))
        yy += 130
    add(im, a, b, name)

def screens(a, b, name, which=(0, 1)):
    paths = ["/root/.claude/uploads/762ec768-073a-5bf9-9078-d9e72100cb94/216975da-image.png",
             "/root/.claude/uploads/762ec768-073a-5bf9-9078-d9e72100cb94/26564ac4-image.png"]
    im = blank()
    xs = [1180, 1540] if len(which) == 2 else [1360]
    for x, k in zip(xs, which):
        s = Image.open(paths[k]).convert("RGB").crop((0, 200, 921, 1000))
        s = s.resize((340, int(340 * s.height / s.width)), Image.LANCZOS)
        card = Image.new("RGBA", (s.width + 16, s.height + 16), YEL + (255,)); card.paste(s, (8, 8))
        m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width, card.height], 24, fill=255)
        card.putalpha(m)
        sh = Image.new("RGBA", (card.width + 60, card.height + 60), (0, 0, 0, 0)); sh.paste((0, 0, 0, 160), (30, 30, 30 + card.width, 30 + card.height))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (x - 30, 180)); im.alpha_composite(card, (x, 200))
    add(im, a, b, name)

# --- cap0
side(["+5 MILHÕES", "de inscritos (2 canais)"], 18.1, 22.3, "s5mi", "📈")
side(["PRÊMIO iBEST", "Streamer Influenciador"], 22.4, 23.7, "sibest", "🏆")
side(["GTA 6", "dezenas de milhares ao vivo"], 23.8, 29.5, "sgta", "🎮")
big(["DAVID"], 30.0, 33.2, "david", sizes=(220, 80), cols=((255, 255, 255), (255, 255, 255)))
big(["BISTECONE"], 33.2, 36.5, "bist", sizes=(260, 80))
# --- cap1
chapter(1, "QUEM É O BISTECONE", 48.0)
side(["+15 HORAS", "de live sem parar"], 52.7, 56.5, "s15h", "⏱️")
# --- cap2
chapter(2, "O DESCARREGADOR DE CAMINHÃO", 70.3)
side(["MADRUGADA", "descarregando caminhão"], 76.3, 82.5, "smad", "🚚")
side(["MOTOBOY", "mais liberdade, longe do sonho"], 94.7, 101.4, "smoto", "🏍️")
# --- cap3
chapter(3, "A VIRADA", 102.2)
big(["“VÍDEOS DE", "QUALIDADE DUVIDOSA”"], 131.4, 136.3, "quote", sizes=(130, 130), cols=(YEL, YEL))
# --- cap4
chapter(4, "A FÓRMULA DO BISTECONE", 136.5)
F5 = ["1. FREQUÊNCIA", "2. DOIS CANAIS", "3. A REAÇÃO VALE MAIS", "4. PROXIMIDADE", "5. CORAGEM PRA MUDAR"]
lst(F5, 1, 141.1, 146.4, "f1", "A FÓRMULA")
side(["700+ e 900+", "vídeos publicados"], 146.5, 151.9, "svid", "🎬")
lst(F5, 2, 152.0, 155.4, "f2", "A FÓRMULA")
screens(155.5, 168.9, "scr1")
side(["CANAL ALEATÓRIO", "+ LIVES SEM CORTES"], 155.5, 168.9, "s2can")
lst(F5, 3, 169.0, 179.7, "f3", "A FÓRMULA")
lst(F5, 4, 179.8, 187.5, "f4", "A FÓRMULA")
lst(F5, 5, 187.6, 194.6, "f5", "A FÓRMULA")
big(["“3 DIAS NA KICK RENDERAM", "UM MÊS DE TWITCH”"], 194.7, 198.2, "kick", sizes=(110, 110), cols=(YEL, YEL))
# CTA
dim(198.3, 209.8, "cta_dim", 150)
im = blank(); d = ImageDraw.Draw(im)
d.rounded_rectangle([360, 250, 1560, 830], 40, fill=(0, 0, 0, 220), outline=YEL, width=8)
d.text((W // 2, 350), "CURTE O BISTECONE?", font=F(90), fill=YEL, anchor="mm")
d.text((W // 2, 480), "LIVE DE GTA 6 TODA NOITE", font=F(78), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 620), "TWITCH / YOUTUBE  @jhonlivesx", font=F(64), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 720), "TIKTOK  @jhonexlives", font=F(64), fill=(255, 255, 255), anchor="mm")
add(im, 198.3, 209.8, "cta")
# --- cap5
chapter(5, "OS NÚMEROS", 210.5)
side(["2,2 MILHÕES", "canal Bistecone"], 211.1, 215.3, "n1", "📺")
side(["3,4 MILHÕES", "canal BisteconeLive"], 215.4, 218.7, "n2", "🔴")
screens(211.1, 218.7, "scr2")
side(["PRÊMIO iBEST", "Streamer Influenciador"], 218.8, 228.8, "n3", "🏆")
side(["SANA", "Fortaleza"], 228.9, 234.0, "n4", "🎤")
# --- cap6
chapter(6, "GTA 6: A PROVA DE FOGO", 234.3)
big(["15h43min", "DE LIVE NA KICK"], 240.8, 246.3, "n15", sizes=(200, 80))
big(["~72 MIL", "AO VIVO AO MESMO TEMPO"], 249.1, 253.6, "n72", sizes=(220, 80))
# --- cap7
chapter(7, "O QUE EU APRENDI COM ELE", 265.8)
L4 = ["1. NÃO ESPERA FICAR PERFEITO", "2. CONSTÂNCIA VENCE TALENTO", "3. SEJA VOCÊ", "4. COMEÇA COM O QUE TEM"]
for j, (a, b) in enumerate([(281.4, 287.3), (287.4, 292.0), (292.1, 295.8), (295.9, 302.3)]):
    lst(L4, j + 1, a, b, f"l{j}", "O QUE EU APRENDI")
# --- cap8
big(["OBRIGADO, BISTECONE"], 302.5, 309.0, "obg", em="💛", sizes=(150, 80))
dim(309.1, 331.8, "end_dim", 150)
im = blank(); d = ImageDraw.Draw(im)
d.rounded_rectangle([360, 230, 1560, 850], 40, fill=(0, 0, 0, 220), outline=YEL, width=8)
d.text((W // 2, 340), "ME SEGUE!", font=F(120), fill=YEL, anchor="mm")
d.text((W // 2, 490), "SE INSCREVE + ATIVA O SININHO", font=F(70), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 640), "TWITCH / YOUTUBE  @jhonlivesx", font=F(68), fill=(255, 255, 255), anchor="mm")
d.text((W // 2, 750), "TIKTOK  @jhonexlives", font=F(68), fill=(255, 255, 255), anchor="mm")
add(im, 309.1, 331.8, "end"); OV[-1] = (OV[-1][0], OV[-1][1], DUR); OV[-2] = (OV[-2][0], OV[-2][1], DUR)


# ---------- overlays for the 5 extra narration pieces ----------
MAP = False
def E(x): return ex(x)
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

# ---------- music ----------
src = open(f"{D}/../f5/build7.py").read()
DUR_ = DUR; exec(src[src.index("SR = 44100"):src.index("sfx = np.zeros(N)")].replace("DUR", "DUR_"))
def wav(fn, x):
    x = np.clip(x, -1, 1); w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wav(f"{D}/music.wav", mus * 0.9)

# ---------- compose ----------
inp = ["-i", f"{D}/base.mp4"]
for p, a, b in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b-a:.2f}", "-i", f"{D}/{p}"]
inp += ["-i", f"{D}/voz2.wav", "-i", f"{D}/music.wav"]
fc = []; prev = "0:v"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i+1}:v]format=rgba,fade=in:st=0:d=0.25:alpha=1,setpts=PTS+{a:.3f}/TB[o{i}]")
    fc.append(f"[{prev}][o{i}]overlay=0:0:eof_action=pass:repeatlast=0[v{i}]"); prev = f"v{i}"
fc.append(f"[{prev}]format=yuv420p[v]")
nv = len(OV) + 1
fc.append(f"[{nv+1}:a]volume=0.10,afade=t=out:st={DUR-3}:d=3[m];[{nv}:a]apad,asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400[md];"
          f"[vo]volume=1.1[vv];[vv][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", f"{DUR}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{D}/historia_bistecone_v2.mp4"])
print("ok")
