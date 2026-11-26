"""MICRO TikTok (~10-14s, desafio no 1º frame): RIDDLE (charada com 3 opções) e ODD ONE OUT (ache o diferente).
Uso: python3 build_micro.py [lote]                 -> gera voz + renderiza tudo
     python3 build_micro.py lote --one r2 | o3     -> renderiza um
     python3 build_micro.py lote --frames r0 0,3,7
"""
import os, sys, math, random, subprocess, importlib, functools
os.environ["BR_VID"] = "03"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import build_brainrush01 as B
import build_brainrush01_shorts as S
from brgfx import *

LOTE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "micro01"
MD = importlib.import_module(f"{LOTE}_data")
W, H, FPS, SR = 1080, 1920, 30, B.SR
OUT = f"/tmp/claude-0/{LOTE}"; os.makedirs(OUT, exist_ok=True)
VN = lambda k: f"{LOTE}_{k}"

# ------------------------------------------------------------------ voz (sem legenda, só precisa da duração)
def ensure_voice():
    want = {VN(k): v for k, v in MD.LINES.items()}
    for i, r in enumerate(MD.RIDDLES): want[VN(f"r{i}_q")] = r[1]; want[VN(f"r{i}_a")] = r[4]
    todo = {k: v for k, v in want.items() if k not in B.META or B.META[k]["text"] != v}
    if not todo: return
    import soundfile as sf, json
    from kokoro_onnx import Kokoro
    kk = Kokoro("/tmp/claude-0/kokoro/model.onnx", "/tmp/claude-0/kokoro/voices.npz")
    for name, text in todo.items():
        a, sr = kk.create(text, voice="am_michael", speed=1.12, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(nz[0] - 300, 0): nz[-1] + 1500]
        sf.write(f"{B.VOZ}/{name}.wav", a, sr); B.META[name] = {"dur": len(a) / sr, "text": text, "words": []}
        print("voz", name, round(len(a) / sr, 2), flush=True)
    json.dump(B.META, open(f"{B.VOZ}/meta.json", "w"), indent=1)

def dur(k): return B.META[VN(k)]["dur"]

# ------------------------------------------------------------------ áudio
def mix(total, voices, sfxs, path):
    N = int((total + 0.3) * SR); voice = np.zeros(N, np.float32)
    for at, name in voices:
        v = B.load_voice(VN(name)); i = int(at * SR); voice[i:i + len(v)] += v[: N - i]
    voice *= 0.9 / max(1e-6, np.abs(voice).max())
    drone, pad, pulse, hats, kick = B.music(N)
    mus = drone * 0.8 + pad * 2.4 + pulse * 0.8 + hats * 0.7 + kick * 0.35
    duck = B.smooth(np.clip(B.smooth((np.abs(voice) > 0.02).astype(np.float32), 0.3) * 3, 0, 1), 0.2)
    mus = mus * (0.42 - 0.27 * duck); fade = np.clip(np.arange(N) / SR / 0.05, 0, 1) * np.clip((total - np.arange(N) / SR) / 0.4, 0, 1)
    fx = np.zeros(N)
    for at, kind in sfxs:
        s_ = B.sfx(kind); i = int(at * SR); fx[i:i + len(s_)] += s_[: N - i]
    m = voice + mus * 0.55 * fade + fx * 0.8; m = np.tanh(m * 1.1) / np.tanh(1.1)
    import soundfile as sf; sf.write(path, m.astype(np.float32), SR)

# ------------------------------------------------------------------ RIDDLE
@functools.lru_cache(None)
def q_box(txt):
    f = F("anton", 92); lines = wrap(txt, f, 900)
    if len(lines) > 3: f = F("anton", 76); lines = wrap(txt, f, 920)
    lh = int(f.size * 1.12); h = lh * len(lines) + 70
    im = rrect((980, h), 34, (16, 14, 10, 240), GOLD + (255,), 5); d = ImageDraw.Draw(im); asc, _ = f.getmetrics()
    for k, l in enumerate(lines): d.text((490, 35 + asc + k * lh), l, font=f, anchor="ms", fill=WHITE)
    out = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0)); out.alpha_composite(glow_of(im, 18, (255, 190, 60), 0.5), (30, 30)); out.alpha_composite(im, (30, 30)); return out

@functools.lru_cache(None)
def r_opt(txt, letter, emo, state):
    w_, h_ = 920, 150
    if state == "ok":
        im = grad(w_, h_, GOLD_L, GOLD_D).convert("RGBA"); im.putalpha(rrect((w_, h_), 30, (255, 255, 255, 255)).getchannel("A")); tc = (24, 14, 2)
    else:
        im = rrect((w_, h_), 30, (22, 20, 26, 245), GOLD + (255,), 3); tc = WHITE
    d = ImageDraw.Draw(im); d.ellipse((24, 27, 120, 123), fill=(20, 14, 2) if state == "ok" else GOLD)
    d.text((72, 77), letter, font=F("anton", 62), anchor="mm", fill=GOLD_L if state == "ok" else (16, 12, 4))
    d.text((150, 77), txt, font=F("mont", 62), anchor="lm", fill=tc)
    im.alpha_composite(emoji(emo, 120), (w_ - 145, 15)); return im

def riddle_tl(i):
    T = 6.0; R = 0.3 + max(T, dur(f"r{i}_q") + 3.0); E = R + 0.1 + dur(f"r{i}_a") + 0.25
    return dict(T=R - 0.3, R=R, E=E, total=E + dur("riddle_end") + 0.5)

def riddle_frame(i, t):
    r = MD.RIDDLES[i]; tl = riddle_tl(i); R, E, T = tl["R"], tl["E"], tl["T"]
    img = S.bg_v().copy(); S.particles(img, t, 0.5)
    paste_c(img, B.chip(f"RIDDLE #{i+1}  •  ONLY 10% GET IT"), W / 2, 300)
    qb = q_box(r[0]); paste_c(img, qb, W / 2, 400 + qb.height / 2)
    paste_c(img, emoji("thinking_face", 150), W - 110, 410 + 8 * math.sin(t * 3), scale=0.8)
    y0 = 420 + qb.height + 60
    for k, (txt, emo) in enumerate(r[2]):
        y = y0 + k * 195
        if t >= R and k == r[3]: paste_c(img, r_opt(txt, "ABC"[k], emo, "ok"), W / 2, y, scale=1 + 0.06 * math.sin(min(1, (t - R) / 0.4) * math.pi))
        else: paste_c(img, r_opt(txt, "ABC"[k], emo, "n"), W / 2, y, alpha=1 if t < R else 1 - 0.7 * ease((t - R) / 0.25))
    # barra de tempo
    by = y0 + 3 * 195 - 40; d = ImageDraw.Draw(img); frac = 1 - min(1, max(0, (t - 0.3) / T)) if t < R else 0
    d.rounded_rectangle((80, by - 18, 1000, by + 18), 18, fill=(50, 44, 30))
    if frac > 0: d.rounded_rectangle((80, by - 18, 80 + 920 * frac, by + 18), 18, fill=GOLD if frac > 0.33 else (255, 100, 60))
    if t < R: d.text((1000, by - 50), f"{math.ceil((R - t)):d}s", font=F("anton", 50), anchor="rm", fill=WHITE)
    if R <= t < R + 0.2: img.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 140, int(80 * (1 - (t - R) / 0.2)))))
    if t >= E:
        p = ease((t - E) / 0.25); img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(170 * p))))
        paste_c(img, S.gold_text_cached_v("DID YOU GET IT?", 130), W / 2, 820, scale=eback((t - E) / 0.3))
        if t > E + 0.3: paste_c(img, text_img("COMMENT YOUR ANSWER!", F("anton", 76), fill=WHITE), W / 2, 980, alpha=ease((t - E - 0.3) / 0.25))
    return img.convert("RGB")

def riddle_audio(i, path):
    tl = riddle_tl(i); R, E = tl["R"], tl["E"]
    sf = [(0.0, "impact")] + [(R - k, "tick2" if k <= 2 else "tick") for k in range(1, int(tl["T"]) + 1)] + [(R, "correct")]
    mix(tl["total"], [(0.1, f"r{i}_q"), (R + 0.1, f"r{i}_a"), (E + 0.1, "riddle_end")], sf, path)
    return tl["total"]

# ------------------------------------------------------------------ ODD ONE OUT
GX0, GY0, GW, GH = 60, 470, 960, 940
def odd_pos(i):
    base, odd, rows, cols, T = MD.ODD[i]; rng = random.Random(100 + i)
    return rng.randrange(1, rows - 1), rng.randrange(0, cols)

@functools.lru_cache(None)
def odd_grid(i, dim):
    base, odd, rows, cols, T = MD.ODD[i]; orow, ocol = odd_pos(i)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cw, ch = GW / cols, GH / rows
    f = F("mont", int(min(cw * 0.42, ch * 0.62)))
    for r_ in range(rows):
        for c in range(cols):
            x, y = GX0 + c * cw, GY0 + r_ * ch; is_odd = (r_, c) == (orow, ocol)
            d.rounded_rectangle((x + 4, y + 4, x + cw - 4, y + ch - 4), 12, fill=(26, 23, 18, 255))
            col = WHITE if not dim or is_odd else (90, 90, 90)
            d.text((x + cw / 2, y + ch / 2), odd if is_odd else base, font=f, anchor="mm", fill=col)
    return im

def odd_tl(i):
    T = MD.ODD[i][4]; R = 0.3 + T
    return dict(T=T, R=R, total=R + 0.4 + dur("odd_end") + 0.6)

def odd_frame(i, t):
    base, odd, rows, cols, T_ = MD.ODD[i]; tl = odd_tl(i); R, T = tl["R"], tl["T"]
    img = S.bg_v().copy(); S.particles(img, t, 0.4)
    paste_c(img, S.gold_text_cached_v("FIND THE ODD ONE OUT", 96), W / 2, 285)
    if t < R + 0.4: paste_c(img, text_img(f"ONLY 1% FIND IT IN {T} SECONDS", F("bebas", 60), fill=WHITE, spacing=3), W / 2, 385)
    img.alpha_composite(odd_grid(i, t >= R + 0.1))
    if t < R: frac, num, pulse = 1 - max(0, t - 0.3) / T, max(1, min(T, math.ceil(R - t))), 0
    else: frac, num, pulse = 0, 0, 0
    paste_c(img, B.timer(max(frac, 0), num, pulse, done=t >= R, urgent=(R - t) < 3), W / 2, GY0 + GH + 120, scale=0.55)
    if t >= R:
        orow, ocol = odd_pos(i); cw, ch = GW / cols, GH / rows; cx, cy = GX0 + (ocol + 0.5) * cw, GY0 + (orow + 0.5) * ch
        p = eback((t - R) / 0.35); rr = max(cw, ch) * 0.62 * p * (1 + 0.06 * math.sin((t - R) * 8))
        d = ImageDraw.Draw(img); d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=GOLD_L, width=10)
        if R <= t < R + 0.2: img.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 140, int(80 * (1 - (t - R) / 0.2)))))
        if t > R + 0.4: paste_c(img, S.gold_text_cached_v("DID YOU FIND IT?", 110), W / 2, 385 + 0 * t, scale=eback((t - R - 0.4) / 0.3))
    return img.convert("RGB")

def odd_audio(i, path):
    tl = odd_tl(i); R, T = tl["R"], tl["T"]
    sf = [(0.0, "impact")] + [(0.3 + k, "tick2" if k >= T - 3 else "tick") for k in range(T)] + [(R, "correct")]
    mix(tl["total"], [(0.1, "odd_intro"), (R + 0.4, "odd_end")], sf, path)
    return tl["total"]

# ------------------------------------------------------------------ render
def render(key):
    kind, i = key[0], int(key[1:]); wav = f"{OUT}/{key}.wav"
    total = riddle_audio(i, wav) if kind == "r" else odd_audio(i, wav); fr = riddle_frame if kind == "r" else odd_frame
    name = f"{LOTE}_{'riddle' if kind == 'r' else 'oddoneout'}{i+1}.mp4"
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/{name}"], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)): p.stdin.write(fr(i, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print("ok", name, round(total, 1), "s", flush=True)

if __name__ == "__main__":
    if "--frames" in sys.argv:
        key = sys.argv[-2]; fr = riddle_frame if key[0] == "r" else odd_frame
        for x in [float(v) for v in sys.argv[-1].split(",")]: fr(int(key[1:]), x).save(f"{OUT}/f{key}_{x:04.1f}.png")
        sys.exit()
    if "--one" in sys.argv: render(sys.argv[-1]); sys.exit()
    ensure_voice()
    keys = [f"r{i}" for i in range(len(MD.RIDDLES))] + [f"o{i}" for i in range(len(MD.ODD))]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda k: subprocess.run([sys.executable, __file__, LOTE, "--one", k]), keys))
