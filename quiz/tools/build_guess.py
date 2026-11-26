"""GUESS THE ANIMAL BY ITS SHADOW — vídeo longo 16:9 (100 animais, 4 níveis) + shorts verticais (10 animais cada).
Uso: python3 build_guess.py [lote]                  -> voz + longo + shorts + srt
     python3 build_guess.py lote --part i n         -> (interno) renderiza parte do longo
     python3 build_guess.py lote --short k          -> (interno) renderiza short k
     python3 build_guess.py lote --frames L|S t1,t2 [k]
"""
import os, sys, math, json, random, subprocess, importlib, functools
os.environ["BR_VID"] = "03"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import build_brainrush01 as B
import build_brainrush01_shorts as S
from brgfx import *

LOTE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "guess01"
GD = importlib.import_module(f"{LOTE}_data")
FPS, SR = 30, B.SR
OUT = f"/tmp/claude-0/{LOTE}"; os.makedirs(OUT, exist_ok=True)
VN = lambda k: f"{LOTE}_{k}"
ITEMS = []   # (nível, índice global, arquivo, nome, falado)
for li, (lname, col, arr) in enumerate(GD.LEVELS):
    for f, show, say in arr: ITEMS.append((li, len(ITEMS), f, show, say))
N = len(ITEMS)
efile = lambda f: f.lower().replace(" ", "_")

# ------------------------------------------------------------------ voz
def ensure_voice():
    want = {VN("intro"): GD.INTRO_V, VN("outro"): GD.OUTRO_V, VN("send"): GD.SHORT_END_V}
    for i, v in enumerate(GD.LEVEL_V): want[VN(f"lv{i}")] = v
    for li, gi, f, show, say in ITEMS: want[VN(f"a{gi}")] = say + "!"
    todo = {k: v for k, v in want.items() if k not in B.META or B.META[k]["text"] != v}
    if not todo: return
    import soundfile as sf
    from kokoro_onnx import Kokoro
    kk = Kokoro("/tmp/claude-0/kokoro/model.onnx", "/tmp/claude-0/kokoro/voices.npz")
    for name, text in todo.items():
        a, sr = kk.create(text, voice="am_michael", speed=1.1, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(nz[0] - 300, 0): nz[-1] + 1500]
        sf.write(f"{B.VOZ}/{name}.wav", a, sr); B.META[name] = {"dur": len(a) / sr, "text": text, "words": []}
    json.dump(B.META, open(f"{B.VOZ}/meta.json", "w"), indent=1); print("voz ok", len(todo), flush=True)
dur = lambda k: B.META[VN(k)]["dur"]

# ------------------------------------------------------------------ linha do tempo
def timeline_long():
    TL = []; t = 0.0
    d = dur("intro"); TL.append(dict(kind="intro", start=t, dur=0.4 + d + 0.8)); t += TL[-1]["dur"]
    for li in range(len(GD.LEVELS)):
        d = dur(f"lv{li}"); TL.append(dict(kind="level", li=li, start=t, dur=0.3 + d + 1.2)); t += TL[-1]["dur"]
        for it in [x for x in ITEMS if x[0] == li]:
            TL.append(dict(kind="item", it=it, start=t, dur=GD.GUESS_T + GD.REVEAL_T)); t += GD.GUESS_T + GD.REVEAL_T
    d = dur("outro"); TL.append(dict(kind="outro", start=t, dur=0.4 + d + 2.5, vd=d)); t += TL[-1]["dur"]
    return TL, t

def short_items(k):
    out = []
    for li in range(len(GD.LEVELS)):
        arr = [x for x in ITEMS if x[0] == li]; n = len(arr); per = [n // 10 + (1 if j < n % 10 else 0) for j in range(10)]
        a = sum(per[:k]); out += arr[a:a + per[k]]
    return out

def timeline_short(k):
    TL = []; t = 0.0
    for it in short_items(k):
        TL.append(dict(kind="item", it=it, start=t, dur=GD.GUESS_T + GD.REVEAL_T)); t += GD.GUESS_T + GD.REVEAL_T
    d = dur("send"); TL.append(dict(kind="outro", start=t, dur=0.2 + d + 1.2, vd=d)); t += TL[-1]["dur"]
    return TL, t

def audio(TL, total, path):
    Nn = int((total + 0.3) * SR); voice = np.zeros(Nn, np.float32)
    def put(at, name):
        v = B.load_voice(VN(name)); i = int(at * SR); voice[i:i + len(v)] += v[: Nn - i]
    fx = np.zeros(Nn)
    def sfx(at, kind):
        s_ = B.sfx(kind); i = int(at * SR); fx[i:i + len(s_)] += s_[: Nn - i]
    for sc in TL:
        s0 = sc["start"]
        if sc["kind"] == "intro": put(s0 + 0.4, "intro"); sfx(s0, "impact")
        elif sc["kind"] == "level": put(s0 + 0.3, f"lv{sc['li']}"); sfx(s0, "impact" if sc["li"] == 3 else "whoosh")
        elif sc["kind"] == "item":
            sfx(s0, "qstart")
            for j in range(3): sfx(s0 + j, "tick" if j < 2 else "tick2")
            sfx(s0 + GD.GUESS_T, "correct"); put(s0 + GD.GUESS_T + 0.15, f"a{sc['it'][1]}")
        else: put(s0 + 0.3, "outro" if total > 120 else "send"); sfx(s0, "whoosh")
    voice *= 0.9 / max(1e-6, np.abs(voice).max())
    drone, pad, pulse, hats, kick = B.music(Nn)
    mus = drone * 0.8 + pad * 2.4 + pulse * 0.8 + hats * 0.7 + kick * 0.35
    duck = B.smooth(np.clip(B.smooth((np.abs(voice) > 0.02).astype(np.float32), 0.3) * 3, 0, 1), 0.2)
    tt = np.arange(Nn) / SR; fade = np.clip(tt / 0.3, 0, 1) * np.clip((total - tt) / 1.0, 0, 1)
    m = voice + mus * (0.42 - 0.27 * duck) * 0.55 * fade + fx * 0.8; m = np.tanh(m * 1.1) / np.tanh(1.1)
    import soundfile as sf; sf.write(path, m.astype(np.float32), SR)

# ------------------------------------------------------------------ peças visuais
@functools.lru_cache(maxsize=256)
def animal(f, size, sil):
    e = Image.open(A + f"e_{efile(f)}_3d.png").convert("RGBA").resize((size, size), Image.LANCZOS)
    if not sil: return e
    s = Image.new("RGBA", e.size, (8, 8, 10, 255)); s.putalpha(e.getchannel("A")); return s

@functools.lru_cache(maxsize=16)
def spotlight(w, h, col):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = (np.clip(1 - r, 0, 1) ** 1.6 * 255).astype(np.uint8)
    im = Image.new("RGBA", (w, h), (min(255, col[0] // 2 + 120), min(255, col[1] // 2 + 120), min(255, col[2] // 2 + 120), 0)); im.putalpha(Image.fromarray(a)); return im

@functools.lru_cache(maxsize=8)
def lvl_chip(li):
    name, col, _ = GD.LEVELS[li]; t_ = text_img(f"LEVEL {li+1}  •  {name}", F("anton", 46), fill=(14, 10, 4), shadow=False)
    im = rrect((t_.width + 70, t_.height + 26), (t_.height + 26) // 2, col + (255,)); im.alpha_composite(t_, (35, 13)); return im

@functools.lru_cache(maxsize=256)
def name_img(txt, size): return gold_text(txt.upper(), F("anton", size))

def progress(img, gi, x0, x1, y, h=14):
    d = ImageDraw.Draw(img); seg = (x1 - x0) / N
    for j in range(N):
        col = GD.LEVELS[ITEMS[j][0]][1]; c = col if j < gi else (tuple(int(v * 0.25) for v in col) if j > gi else GOLD_L)
        d.rectangle((x0 + j * seg + 1, y, x0 + (j + 1) * seg - 1, y + h), fill=c)

def item_draw(img, sc, tl, cx, cy, size, name_y, name_size, timer_xy, timer_scale):
    li, gi, f, show, say = sc["it"]; col = GD.LEVELS[li][1]; G = GD.GUESS_T
    sp = spotlight(int(size * 2.2), int(size * 2.2), col); paste_c(img, sp, cx, cy, alpha=0.55 + 0.1 * math.sin(tl * 3))
    if tl < G:
        sc_ = 0.85 + 0.15 * eback(tl / 0.3); paste_c(img, animal(f, size, True), cx, cy + 6 * math.sin(tl * 2.5), scale=sc_)
        paste_c(img, gold_text_cached_q(), cx + size * 0.42, cy - size * 0.42, scale=0.9 + 0.08 * math.sin(tl * 6))
    else:
        r = tl - G; p = min(1, r / 0.25); pop = 1 + 0.12 * math.sin(min(1, r / 0.35) * math.pi)
        paste_c(img, animal(f, size, True), cx, cy, alpha=1 - p, scale=pop)
        paste_c(img, halo(animal(f, size, False), 30, (255, 210, 120), 0.5), cx, cy, alpha=p * 0.9, scale=pop)
        paste_c(img, animal(f, size, False), cx, cy, alpha=p, scale=pop)
        paste_c(img, name_img(show, name_size), cx, name_y, scale=eback(r / 0.3))
        if r < 0.2: img.alpha_composite(Image.new("RGBA", img.size, (255, 230, 160, int(70 * (1 - r / 0.2)))))
    if tl < G: e = tl; frac = 1 - e / G; num = 3 - int(e); pulse = max(0, 1 - (e % 1) / 0.25)
    else: frac, num, pulse = 1, 0, 0
    paste_c(img, B.timer(frac, num, pulse, done=tl >= G, urgent=(tl > G - 1)), *timer_xy, scale=timer_scale)

@functools.lru_cache(None)
def gold_text_cached_q(): return gold_text("?", F("anton", 160))

# ------------------------------------------------------------------ longo 16:9
W, H = 1920, 1080
TLL = None
def frame_long(t):
    global TLL
    if TLL is None: TLL = timeline_long()[0]
    img = B.background().copy(); B.particles(img, t, 0.5)
    sc = next((s for s in TLL if s["start"] <= t < s["start"] + s["dur"]), TLL[-1]); tl = t - sc["start"]
    if sc["kind"] == "intro":
        paste_c(img, intro_grid(), W / 2, H / 2, alpha=0.22)
        paste_c(img, gold_text_cached2("GUESS 100 ANIMALS", 150), W / 2, 420, scale=eback(tl / 0.5))
        paste_c(img, gold_text_cached2("BY THEIR SHADOW", 100, white=True), W / 2, 570, scale=eback((tl - 0.3) / 0.5))
        if tl > 1.2: paste_c(img, text_img("EASY  •  MEDIUM  •  HARD  •  IMPOSSIBLE", F("bebas", 60), fill=(220, 220, 220), spacing=4), W / 2, 700, alpha=ease((tl - 1.2) / 0.4))
        if tl > 2.0: paste_c(img, text_img("3 SECONDS EACH", F("bebas", 60), fill=GOLD_L, spacing=4), W / 2, 780, alpha=ease((tl - 2.0) / 0.4))
    elif sc["kind"] == "level":
        li = sc["li"]; name, col, _ = GD.LEVELS[li]
        paste_c(img, spotlight(1200, 900, col), W / 2, H / 2, alpha=0.6)
        paste_c(img, gold_text_cached2(f"LEVEL {li+1}", 170), W / 2, 400, scale=eback(tl / 0.4))
        paste_c(img, level_word(li), W / 2, 590, scale=eback((tl - 0.25) / 0.4))
        if tl > 0.8: paste_c(img, text_img(f"{len(GD.LEVELS[li][2])} ANIMALS", F("bebas", 64), fill=WHITE, spacing=5), W / 2, 740, alpha=ease((tl - 0.8) / 0.4))
        progress(img, sum(len(GD.LEVELS[j][2]) for j in range(li)), 260, 1660, 1010)
    elif sc["kind"] == "item":
        li, gi = sc["it"][0], sc["it"][1]
        paste_c(img, B.small_logo(), 210, 66); paste_c(img, lvl_chip(li), W / 2, 70)
        paste_c(img, gold_text_cached2(f"{gi+1}/{N}", 72), W - 170, 70)
        item_draw(img, sc, tl, W / 2, 520, 470, 880, 110, (1640, 500), 0.85)
        paste_c(img, text_img("GUESS THE ANIMAL", F("bebas", 58), fill=(200, 200, 200), spacing=5), 280, 500)
        progress(img, gi, 260, 1660, 1010)
    else:
        lg = B.logo(1.0); paste_c(img, lg, W / 2, 230, scale=0.8)
        for k, (rg, nm) in enumerate(GD.BANDS):
            if tl > 0.4 + k * 0.35: paste_c(img, B.band_img(rg, nm, k == len(GD.BANDS) - 1), W / 2, 420 + k * 120, scale=eout((tl - 0.4 - k * 0.35) / 0.3))
        if tl > 2.5: paste_c(img, B.sub_btn(), W / 2, 1010, scale=eback((tl - 2.5) / 0.4))
    return img.convert("RGB")

@functools.lru_cache(None)
def gold_text_cached2(txt, size, white=False):
    return gold_text(txt, F("anton", size), top=(255, 255, 255) if white else GOLD_L, bot=(205, 205, 210) if white else GOLD_D)
@functools.lru_cache(None)
def level_word(li):
    name, col, _ = GD.LEVELS[li]; return gold_text(name, F("anton", 150), top=tuple(min(255, c + 60) for c in col), bot=col)
@functools.lru_cache(None)
def intro_grid():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rng = random.Random(3); pick = rng.sample(ITEMS, 24)
    for k, it in enumerate(pick): paste_c(im, animal(it[2], 170, False), 160 + (k % 8) * 230, 170 + (k // 8) * 370 + (k % 2) * 60)
    return im

# ------------------------------------------------------------------ shorts 9:16
WS, HS = 1080, 1920
def frame_short(k, t, TL):
    img = S.bg_v().copy(); S.particles(img, t, 0.5)
    sc = next((s for s in TL if s["start"] <= t < s["start"] + s["dur"]), TL[-1]); tl = t - sc["start"]
    hook = GD.SHORT_HOOKS[k % len(GD.SHORT_HOOKS)]
    hi = hook_img(hook); paste_c(img, hi, WS / 2, 300 - hi.height / 2 + 40)
    if sc["kind"] == "item":
        n = [s for s in TL if s["kind"] == "item"].index(sc)
        paste_c(img, lvl_chip(sc["it"][0]), WS / 2, 410)
        paste_c(img, text_img(f"{n+1} / {len(TL)-1}", F("anton", 60), fill=WHITE), WS / 2, 495)
        item_draw(img, sc, tl, WS / 2, 890, 560, 1280, 120, (WS / 2, 1450), 0.7)
    else:
        paste_c(img, S.gold_text_cached_v("HOW MANY", 150), WS / 2, 720, scale=eback(tl / 0.3))
        paste_c(img, S.gold_text_cached_v("DID YOU GET?", 150), WS / 2, 900, scale=eback((tl - 0.15) / 0.3))
        if tl > 0.5: paste_c(img, text_img(f"COMMENT YOUR SCORE /{len(TL)-1}", F("anton", 80), fill=WHITE), WS / 2, 1100, alpha=ease((tl - 0.5) / 0.3))
        if tl > 0.9: paste_c(img, S.follow_btn(), WS / 2, 1300, scale=eback((tl - 0.9) / 0.3))
    return img.convert("RGB")

@functools.lru_cache(None)
def hook_img(txt):
    f = F("anton", 104); lines = wrap(txt, f, 980)
    if len(lines) > 1: f = F("anton", 92); lines = wrap(txt, f, 1000)
    ims = [gold_text(l, f) for l in lines]; h = sum(i.height for i in ims) - 40 * (len(ims) - 1)
    out = Image.new("RGBA", (max(i.width for i in ims), h), (0, 0, 0, 0)); y = 0
    for i in ims: out.alpha_composite(i, ((out.width - i.width) // 2, y)); y += i.height - 40
    return out

# ------------------------------------------------------------------ render
def ff(path, w, h, wav):
    return subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-"] +
                            (["-i", wav] if wav else []) + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p"] +
                            (["-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest"] if wav else []) +
                            ["-movflags", "+faststart", path], stdin=subprocess.PIPE)

def srt_long():
    TL, total = timeline_long(); out = []; k = 1
    def fmt(x):
        ms = int(round(x * 1000)); h_, ms = divmod(ms, 3600000); m_, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000); return f"{h_:02d}:{m_:02d}:{s_:02d},{ms:03d}"
    for sc in TL:
        if sc["kind"] == "intro": txt, a, b = GD.INTRO_V, sc["start"] + 0.4, sc["start"] + sc["dur"]
        elif sc["kind"] == "level": txt, a, b = GD.LEVEL_V[sc["li"]], sc["start"] + 0.3, sc["start"] + sc["dur"]
        elif sc["kind"] == "item": txt, a, b = sc["it"][4] + "!", sc["start"] + GD.GUESS_T + 0.15, sc["start"] + sc["dur"]
        else: txt, a, b = GD.OUTRO_V, sc["start"] + 0.4, sc["start"] + sc["dur"]
        out.append(f"{k}\n{fmt(a)} --> {fmt(b)}\n{txt}\n"); k += 1
    return "\n".join(out)

if __name__ == "__main__":
    if "--frames" in sys.argv:
        i = sys.argv.index("--frames"); mode = sys.argv[i + 1]; ts = [float(x) for x in sys.argv[i + 2].split(",")]
        for x in ts:
            if mode == "L": frame_long(x).save(f"{OUT}/L_{x:06.1f}.png")
            else: k = int(sys.argv[i + 3]); TL, _ = timeline_short(k); frame_short(k, x, TL).save(f"{OUT}/S{k}_{x:05.1f}.png")
        sys.exit()
    if "--part" in sys.argv:
        i, n = int(sys.argv[-2]), int(sys.argv[-1]); TL, total = timeline_long(); NF = int(total * FPS)
        a, b = NF * i // n, NF * (i + 1) // n; p = ff(f"{OUT}/part{i}.mp4", W, H, None)
        for f in range(a, b): p.stdin.write(frame_long(f / FPS).tobytes())
        p.stdin.close(); p.wait(); sys.exit()
    if "--short" in sys.argv:
        k = int(sys.argv[-1]); TL, total = timeline_short(k); audio(TL, total, f"{OUT}/s{k}.wav")
        p = ff(f"{OUT}/{LOTE}_short{k+1}.mp4", WS, HS, f"{OUT}/s{k}.wav")
        for f in range(int(total * FPS)): p.stdin.write(frame_short(k, f / FPS, TL).tobytes())
        p.stdin.close(); p.wait(); print("short", k + 1, round(total, 1), flush=True); sys.exit()
    ensure_voice()
    TL, total = timeline_long(); print("longo", round(total, 1), "s", flush=True)
    open(f"{OUT}/{LOTE}.srt", "w").write(srt_long()); audio(TL, total, f"{OUT}/long.wav")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex: list(ex.map(lambda i: subprocess.run([sys.executable, __file__, LOTE, "--part", str(i), "4"]), range(4)))
    open(f"{OUT}/parts.txt", "w").write("".join(f"file 'part{i}.mp4'\n" for i in range(4)))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/parts.txt", "-i", f"{OUT}/long.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "22",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/{LOTE}.mp4"], check=True)
    print("LONGO OK", flush=True)
    with ThreadPoolExecutor(4) as ex: list(ex.map(lambda k: subprocess.run([sys.executable, __file__, LOTE, "--short", str(k)]), range(10)))
    print("TUDO OK", flush=True)
