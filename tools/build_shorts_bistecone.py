"""Vertical shorts (1080x1920, >61s) cut from the Bistecone long video. No music (user adds trending sound)."""
import os, sys, io, json, re, subprocess, contextlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
src = open(f"{D}/build_bis3.py").read(); src = src[:src.index('award_bg(f"{D}/ov/award_bg.png")')]
with contextlib.redirect_stdout(io.StringIO()): exec(src)
ANTON = f"{D}/../v/Anton.ttf"; EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H = 1080, 1920; YEL = (255, 212, 0)
LONG = f"{D}/historia_bistecone_v3.mp4"; BASE = f"{D}/base.mp4"; AUD = f"{D}/mix_nomusic.wav"
def run(c): subprocess.run(c, check=True)
os.makedirs(f"{D}/shorts", exist_ok=True)
VW = json.load(open(f"{D}/../bis/voz_words.json"))
def vo_word(word, near):
    c = [q for q in VW if q[2].lower().strip(".,!?") == word.lower() and abs(q[0] - near) < 6]
    return min(c, key=lambda q: abs(q[0] - near))
def Fi(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMO, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)

antes = vo_word("antes", 69.5)[0] - 0.08
pand = vo_word("pandemia", 103.4)[1] + 0.35
onome = vo_word("o", 30.2)[0] - 0.08
sal = vo_word("baixo", 12.5)[1] + 0.3
gta_end = m(vo_word("gta", 265.0)[1] + 0.4, True)
eusou = m(vo_word("eu", 268.0)[0] - 0.08)
B5 = bdur(BREAKS[4][2])
SHORTS = {
    "1_caminhao": dict(r=[(0, T(34.45)), (T(antes), T(pand, True))],
                       t=["ELE DESCARREGAVA", "CAMINHÃO DE MADRUGADA…"], e="🚚"),
    "2_premio": dict(r=[(COLDD, T(sal, True)), (T(onome), T(34.45)), (T(NS[1]), T(NS[2]))],
                     t=["DO CAMINHÃO AO", "PRÊMIO DE REVELAÇÃO"], e="🏆"),
    "3_gta6": dict(r=[(T(NS[4]) - B5, T(gta_end, True))],
                   t=["72 MIL PESSOAS VENDO", "ELE JOGAR GTA 6"], e="🎮"),
    "4_licao": dict(r=[(T(eusou), T(NS[11]))],
                    t=["EU ME VI NA HISTÓRIA", "DO BISTECONE"], e="💛"),
}
END = 3.5
FIX = [(r"(?i)^bistec[oô]n[ia]+([,.!?]?)$", r"Bistecone\1"), (r"(?i)^john([,.!?]?)$", r"Jhon\1"), (r"(?i)^kik([,.!?]?)$", r"Kick\1"),
       (r"(?i)^ami([,.!?]?)$", r"Ammy\1"), (r"(?i)^milvler([,.!?]?)$", r"Miwvlr\1")]

def asr(wav):
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    from faster_whisper import WhisperModel
    mdl = WhisperModel("small", device="cpu", compute_type="int8")
    x = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
    segs, _ = mdl.transcribe(x, language="pt", word_timestamps=True, vad_filter=True,
                             initial_prompt="Bistecone, BisteconeLive, Kick, Twitch, GTA 6, iBest, Jhon, Ammy, Miwvlr, eSports Brasil")
    out = []
    for s in segs:
        for w in s.words:
            t = w.word.strip()
            for a, b in FIX: t = re.sub(a, b, t)
            if t: out.append([w.start, w.end, t])
    return out

EW = json.load(open(f"{D}/../bis/extra_words.json"))
def fixw(t):
    for a, b in FIX: t = re.sub(a, b, t)
    return t
_LIVE = {}
def live_words(cid, a, b):
    k = (cid, a, b)
    if k not in _LIVE:
        p = f"{D}/shorts/lw.wav"
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(a), "-t", f"{b - a:.3f}", "-i", f"{D}/clips/{cid}.mp4", "-ac", "1", "-ar", "16000", p])
        _LIVE[k] = asr(p)
    return _LIVE[k]
LFIX = {"louca?": "louco, cara?", "merda": "mano!", "acredito": "não acredito,", "que": ""}
BFIX = {"Sais": "Sai", "quadro,": "quarto,", "tigão,": "Tigrão!", "tigão": "Tigrão!", "Jô,": "Joe", "Jô": "Joe", "Brasil,": "brasileiro!",
        "Portuguesa": "português!", "Minutos,": "14 minutos,"}
def timeline_words():
    out = []
    for i, (src_, a, b) in enumerate(PIECES):
        for q in (VW if src_ == VO else EW):
            if a <= q[0] < b:
                v = NS[i] + q[0] - a; ve = NS[i] + min(q[1], b) - a
                out.append([T(v), T(ve, True), fixw(q[2])])
    t = 0.0
    for a, b in COLD[0][1]:
        out += [[t + w0, t + w1, LFIX.get(w, w)] for w0, w1, w in live_words(COLD[0][0], a, b)]; t += b - a
    for p, cid, parts, bl in BREAKS:
        t = T(p) - bdur(parts)
        for a, b in parts:
            ws = live_words(cid, a, b)
            for w0, w1, w in ws:
                if any(min(a + w1, b1) - max(a + w0, b0) > 0.5 * (w1 - w0) for b0, b1 in bl): w = "***"
                out.append([t + w0, t + w1, BFIX.get(w, w)])
            t += b - a
    out = sorted(out); res = []
    for w in out:
        lw = res[-1][2].lower() if res else ""
        t = w[2]
        if t.lower().startswith("best") and lw == "e": res[-1] = [res[-1][0], w[1], "iBest" + t[4:]]; continue
        if t.lower().startswith("sports") and lw == "e": res[-1] = [res[-1][0], w[1], "eSports" + t[6:]]; continue
        if t.lower().startswith("zocca") and lw == "alan": res[-1] = [res[-1][0], w[1], "Alanzoka" + t[5:]]; continue
        if t.startswith("Kick") and lw == "eventos": t = "geek" + t[4:]
        t = re.sub(r"(?i)^kazimiro", "Casimiro", t); t = re.sub(r"(?i)^selbit", "Cellbit", t)
        if t: res.append([w[0], w[1], t])
    return res
ALLW = None

def ass_time(t): h = int(t // 3600); mi = int(t % 3600 // 60); s = t % 60; return f"{h}:{mi:02d}:{s:05.2f}"
def make_ass(words, path, dur):
    ev, cur = [], []
    for w in words:
        cur.append(w); txt = " ".join(y[2] for y in cur)
        if len(txt) >= 12 or len(cur) >= 3 or re.search(r"[,.?!…]$", w[2]): ev.append(cur); cur = []
    if cur: ev.append(cur)
    L = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: C,Anton,112,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,7,4,5,60,60,0,1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for j, g in enumerate(ev):
        a = g[0][0]; nxt = ev[j + 1][0][0] if j + 1 < len(ev) else min(dur, g[-1][1] + 0.6)
        for k, w in enumerate(g):  # highlight active word in yellow
            s0 = w[0] if k else a; s1 = g[k + 1][0] if k + 1 < len(g) else nxt
            if s1 - s0 < 0.02: continue
            parts = [("{\\c&H00D4FF&}" + y[2].upper() + "{\\c&HFFFFFF&}") if i == k else y[2].upper() for i, y in enumerate(g)]
            L.append(f"Dialogue: 0,{ass_time(s0)},{ass_time(s1)},C,,0,0,0,,{{\\pos(540,1460)\\fad(40,0)}}" + " ".join(parts))
    open(path, "w").write("\n".join(L) + "\n")

def title_png(lines, e, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 250
    for j, ln in enumerate(lines):
        s = 118
        while d.textlength(ln, font=Fi(s)) > 980: s -= 4
        d.text((W // 2 + 6, y + 8), ln, font=Fi(s), fill=(0, 0, 0, 180), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, 180))
        d.text((W // 2, y), ln, font=Fi(s), fill=(255, 255, 255) if j == 0 else YEL, anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
        y += int(s * 1.18)
    em = emoji(e, 120); im.alpha_composite(em, (W // 2 - em.width // 2, 70))
    # frame around the video panel
    d.rectangle([0, 653, W, 659], fill=YEL); d.rectangle([0, 1267, W, 1273], fill=YEL)
    im.save(path)

def end_png(path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 170)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 640, 990, 1280], 40, fill=(0, 0, 0, 230), outline=YEL, width=8)
    d.text((W // 2, 760), "ME SEGUE!", font=Fi(130), fill=YEL, anchor="mm")
    d.text((W // 2, 900), "PRA MAIS HISTÓRIAS E GTA 6", font=Fi(58), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 1040), "TIKTOK  @jhonexlives", font=Fi(70), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 1150), "YOUTUBE / TWITCH  @jhonlivesx", font=Fi(62), fill=(255, 255, 255), anchor="mm")
    im.save(path)
end_png(f"{D}/shorts/end.png")

only = sys.argv[1:]
for name, cfg in SHORTS.items():
    global_dummy = None
    if only and name not in only: continue
    o = f"{D}/shorts/{name}"
    # cut pieces (video panel from LONG, bg from BASE, audio from no-music mix)
    vl, bl, al = [], [], []
    for i, (a, b) in enumerate(cfg["r"]):
        d = b - a
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-i", LONG, "-t", f"{d:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", f"{o}_v{i}.mp4"])
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-i", BASE, "-t", f"{d:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", f"{o}_b{i}.mp4"])
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-i", AUD, "-t", f"{d:.3f}", "-af", f"afade=t=in:d=0.03,afade=t=out:st={d - 0.05:.3f}:d=0.05", f"{o}_a{i}.wav"])
        vl.append(f"{o}_v{i}.mp4"); bl.append(f"{o}_b{i}.mp4"); al.append(f"{o}_a{i}.wav")
    for lst, out in ((vl, f"{o}_V.mp4"), (bl, f"{o}_B.mp4")):
        open(f"{o}_l.txt", "w").write("".join(f"file '{x}'\n" for x in lst))
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{o}_l.txt", "-c", "copy", out])
    run(["ffmpeg", "-loglevel", "error", "-y"] + sum([["-i", x] for x in al], []) + ["-filter_complex", "".join(f"[{i}:a]" for i in range(len(al))) + f"concat=n={len(al)}:v=0:a=1[a]", "-map", "[a]", f"{o}_A.wav"])
    CD = sum(b - a for a, b in cfg["r"]); TD = CD + END
    if ALLW is None: ALLW = timeline_words()
    words = []; off = 0.0
    for a, b in cfg["r"]:
        words += [[w0 - a + off, min(w1, b) - a + off, w] for w0, w1, w in ALLW if a <= w0 < b - 0.05]
        off += b - a
    json.dump(words, open(f"{o}_words.json", "w"), ensure_ascii=False)
    make_ass(words, f"{o}.ass", CD)
    title_png(cfg["t"], cfg["e"], f"{o}_title.png")
    fc = (f"[1:v]tpad=stop_mode=clone:stop_duration={END},scale=-2:{H},crop={W}:{H},gblur=sigma=28,eq=brightness=-0.22:saturation=1.2[bg];"
          f"[0:v]tpad=stop_mode=clone:stop_duration={END},scale={W}:608,setsar=1[fg];"
          f"[bg][fg]overlay=0:660[c];[c][2:v]overlay=0:0[t];"
          f"[t]ass={o}.ass:fontsdir={D}/../v[s];"
          f"[3:v]format=rgba,fade=in:st=0:d=0.3:alpha=1,setpts=PTS+{CD:.3f}/TB[e];[s][e]overlay=0:0:eof_action=pass,format=yuv420p[v];"
          f"[4:a]apad=pad_dur={END},loudnorm=I=-14:TP=-1.5[a]")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{o}_V.mp4", "-i", f"{o}_B.mp4", "-loop", "1", "-i", f"{o}_title.png",
         "-loop", "1", "-t", f"{END}", "-i", f"{D}/shorts/end.png", "-i", f"{o}_A.wav", "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-t", f"{TD:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{D}/shorts/short_{name}.mp4"])
    print(name, round(TD, 1), flush=True)
