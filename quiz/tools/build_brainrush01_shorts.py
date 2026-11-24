"""Shorts/TikTok verticais (1080x1920) do vídeo 01: 5 cortes de 3 perguntas cada.
Uso: python3 build_brainrush01_shorts.py            (gera voz extra + renderiza os 5)
     python3 build_brainrush01_shorts.py --short i  (renderiza só o short i)
     python3 build_brainrush01_shorts.py --frames i t1,t2
"""
import json, math, os, re, subprocess, sys, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_brainrush01 as B
from brgfx import *
from brainrush01_data import QS

W, H, FPS = 1080, 1920, 30
OUT = "/tmp/claude-0/br01/shorts"; os.makedirs(OUT, exist_ok=True)
SHORTS = [
    dict(qs=[0, 1, 2], hook="ONLY 1% GET 3/3", hook_v="Only one percent of people get all three right. Let's see if you can!"),
    dict(qs=[3, 4, 5], hook="CAN YOU GET 3/3?", hook_v="Three questions. Seven seconds each. Can you get them all?"),
    dict(qs=[6, 7, 8], hook="90% FAIL QUESTION 3", hook_v="Ninety percent of people fail question number three. Are you one of them?"),
    dict(qs=[9, 10, 11], hook="GENIUS TEST: 3/3?", hook_v="Only real geniuses get all three. Let's find out!"),
    dict(qs=[12, 13, 14], hook="FINAL BOSS QUIZ", hook_v="The final three. These are the hardest ones. Ready?"),
]
OUTRO_V = "How many did you get right? Comment your score, and follow for more quizzes!"

# ------------------------------------------------------------------ voz extra (gancho/CTA)
def ensure_voice():
    names = {f"sh{i}_hook": s["hook_v"] for i, s in enumerate(SHORTS)}; names["sh_outro"] = OUTRO_V
    missing = {k: v for k, v in names.items() if k not in B.META}
    if not missing: return
    import soundfile as sf
    from kokoro_onnx import Kokoro
    from faster_whisper import WhisperModel
    k = Kokoro("/tmp/claude-0/kokoro/model.onnx", "/tmp/claude-0/kokoro/voices.npz"); wm = WhisperModel("small", compute_type="int8")
    for name, text in missing.items():
        a, sr = k.create(text, voice="am_michael", speed=1.1, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(nz[0] - 600, 0): nz[-1] + 2400]
        sf.write(f"{B.VOZ}/{name}.wav", a, sr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{B.VOZ}/{name}.wav", "-ar", "16000", "-ac", "1", "/tmp/claude-0/_16k.wav"], check=True)
        a16, _ = sf.read("/tmp/claude-0/_16k.wav", dtype="float32")
        sg, _ = wm.transcribe(a16, language="en", word_timestamps=True, initial_prompt=text)
        B.META[name] = {"dur": len(a) / sr, "text": text, "words": [[w.start, w.end, w.word.strip()] for s in sg for w in s.words]}
        print("voz", name, round(len(a) / sr, 2))
    json.dump(B.META, open(f"{B.VOZ}/meta.json", "w"), indent=1)

# ------------------------------------------------------------------ linha do tempo de um short
def setup(si):
    S = SHORTS[si]; TL, AUD, SFX, CW = [], [], [], []; t = 0.0
    def voice(name, at):
        AUD.append((at, name)); CW.extend((at + a, at + b, w) for a, b, w in B.align(name))
    hk = f"sh{si}_hook"; d = B.META[hk]["dur"]
    TL.append(dict(kind="intro3", start=0.0, dur=0.3 + d + 0.5, hook=S["hook"])); voice(hk, 0.3); SFX.append((0.0, "impact")); t = TL[-1]["dur"]
    for n, qi in enumerate(S["qs"]):
        src = next(s for s in B.TL if s["kind"] == "q" and s["qi"] == qi)
        ans = f"q{qi+1:02d}_ans"; dur = src["AN"] + B.META[ans]["dur"] + 0.9
        sc = dict(src, start=t, dur=dur, n=n); TL.append(sc)
        voice(f"q{qi+1:02d}_ask", t + src["A0"]); voice(ans, t + src["AN"])
        SFX += [(t, "whoosh"), (t + 0.55, "qstart")] + [(t + src["CS"] + k, "tick" if k < 4 else "tick2") for k in range(7)]
        SFX.append((t + src["R"], "victory" if n == 2 else "correct")); t += dur
    d = B.META["sh_outro"]["dur"]
    TL.append(dict(kind="outro", start=t, dur=0.4 + d + 1.6, v0=0.4, vd=d)); voice("sh_outro", t + 0.4); SFX.append((t, "whoosh")); t += TL[-1]["dur"]
    # aplica no módulo base (áudio e legenda usam esses globais)
    B.TL, B.AUD, B.SFX, B.CAP_WORDS, B.TOTAL = TL, AUD, SFX, CW, t
    B.CHUNKS = B.build_chunks(); B.CH_T = [(c[0][0], c[-1][1] + 0.25) for c in B.CHUNKS]
    for k in range(len(B.CH_T) - 1): B.CH_T[k] = (B.CH_T[k][0], min(B.CH_T[k][1], B.CHUNKS[k + 1][0][0]))
    B.cap_img.cache_clear()
    return TL, t

# ------------------------------------------------------------------ elementos verticais
@functools.lru_cache(None)
def bg_v():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.4) / H) ** 2)
    g = np.clip(1 - r * 1.5, 0, 1) ** 2
    img = np.array(BG, np.float32) + g[..., None] * np.array([36, 26, 6], np.float32)
    im = Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rr = 46
    for j in range(-1, int(H / (rr * 1.5)) + 2):
        for i in range(-1, int(W / (rr * 1.732)) + 2):
            cx = i * rr * 1.732 + (j % 2) * rr * 0.866; cy = j * rr * 1.5
            d.polygon(hexagon_pts(cx, cy, rr - 2, math.pi / 6), outline=(212, 170, 60, 10))
    im.alpha_composite(ov); return im

PART = [(np.random.default_rng(k).uniform(0, W), np.random.default_rng(k + 50).uniform(0, H), np.random.default_rng(k + 9).uniform(8, 30), np.random.default_rng(k + 3).uniform(0.8, 2.6)) for k in range(60)]
def particles(img, t, alpha=1.0):
    d = ImageDraw.Draw(img)
    for x, y, sp, r in PART:
        yy = (y - t * sp) % H; xx = x + 12 * math.sin(t * 0.4 + y); a = int((90 + 80 * math.sin(t * 1.3 + x)) * alpha)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(230, 190, 90, max(0, a)))

@functools.lru_cache(None)
def q_img(txt):
    f = F("mont", 56); lines = wrap(txt, f, 960)
    if len(lines) > 2: f = F("mont", 48); lines = wrap(txt, f, 980)
    lh = int(f.size * 1.18); asc, desc = f.getmetrics()
    out = Image.new("RGBA", (1060, lh * len(lines) + desc + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for k, l in enumerate(lines):
        ds.text((530, 10 + asc + k * lh + 3), l, font=f, anchor="ms", fill=(0, 0, 0, 170)); d.text((530, 10 + asc + k * lh), l, font=f, anchor="ms", fill=WHITE)
    sh = sh.filter(ImageFilter.GaussianBlur(4)); sh.alpha_composite(out); return sh

STG = 0.98                       # escala do palco (1040x440 -> ~1019x431)
ST_CY = 540
OPT_X = 500; OPT_Y = [1215, 1330, 1445, 1560]   # alternativas empilhadas (longe dos botões do TikTok)

def render_qv(img, sc, tq):
    qi = sc["qi"]; q = QS[qi]; R, CS = sc["R"], sc["CS"]; n = sc["n"]
    paste_c(img, B.small_logo(), W / 2, 180)
    paste_c(img, B.chip(f"QUESTION {n+1} OF 3  •  {q[0]}"), W / 2, 255, alpha=ease(tq / 0.4))
    EX = R + 1.6
    st = B.stage_ask(qi, tq) if tq < EX else B.stage_exp(qi, tq - EX, sc)
    if EX <= tq < EX + 0.35:
        a = B.stage_ask(qi, tq); b = st.copy(); b.putalpha(int(255 * ease((tq - EX) / 0.35))); a.alpha_composite(b); st = a
    B.compose_stage(img, st, alpha=ease(tq / 0.45), scale=STG * (0.92 + 0.08 * eout(tq / 0.6)), cx=W / 2, cy=ST_CY)
    if tq < CS: frac, num, pulse = 1.0, 7, 0
    elif tq < R: e = tq - CS; frac = 1 - e / 7.0; num = 7 - int(e); pulse = max(0, 1 - (e % 1) / 0.25)
    else: frac, num, pulse = 1.0, 0, 0
    tim = B.timer(frac, num, pulse, done=tq >= R, urgent=(CS + 4 <= tq < R))
    paste_c(img, tim, W / 2, 900, alpha=ease(tq / 0.5), scale=0.72 * (1 + (0.12 * max(0, 1 - (tq - R) / 0.4) if tq >= R else 0)))
    qa = ease((tq - 0.5) / 0.4); paste_c(img, q_img(q[1]), W / 2, 1088 + 20 * (1 - qa), alpha=qa)
    for k, opt in enumerate(q[2]):
        t0 = sc["letters"][k] - 0.1 if k < len(sc["letters"]) else 1.5 + k * 0.4
        p = eout((tq - t0) / 0.35)
        if p <= 0: continue
        L = "ABCD"[k]; cx, cy = OPT_X, OPT_Y[k]
        if tq >= R and k == q[3]:
            pp = (tq - R) / 0.45; paste_c(img, B.option_img(opt, L, "ok"), cx, cy, scale=1.04 * (1 + 0.07 * math.sin(min(pp, 1) * math.pi)))
        else:
            a = p if tq < R else p * (1 - 0.68 * ease((tq - R) / 0.3))
            paste_c(img, B.option_img(opt, L, "n"), cx - 40 * (1 - p), cy, alpha=a, scale=1.04)
    if R <= tq < R + 0.25: img.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 140, int(70 * (1 - (tq - R) / 0.25)))))

def render_hook(img, sc, tl):
    particles(img, tl)
    lg = B.logo(1.0); paste_c(img, lg, W / 2, 330, scale=0.62 * (0.85 + 0.15 * eback(tl / 0.5)))
    words = sc["hook"].split(); f = 150 if len(sc["hook"]) <= 16 else 128
    lines = [" ".join(words[:2]), " ".join(words[2:])] if len(words) > 2 else [sc["hook"]]
    for k, l in enumerate(lines):
        p = eback((tl - 0.15 - k * 0.25) / 0.4)
        if p > 0: paste_c(img, gold_text_cached_v(l, f), W / 2, 760 + k * 190, scale=p)
    if tl > 0.9: paste_c(img, text_img("3 QUESTIONS  •  7 SECONDS EACH", F("bebas", 60), fill=(215, 215, 215), spacing=4), W / 2, 1180, alpha=ease((tl - 0.9) / 0.4))
    paste_c(img, B.emoji("brain", 200), W / 2, 1420 + 15 * math.sin(tl * 3), scale=eback((tl - 0.3) / 0.5) if tl > 0.3 else 0.01)

@functools.lru_cache(None)
def gold_text_cached_v(txt, size): return gold_text(txt, F("anton", size))

def render_end(img, sc, tl):
    particles(img, tl + 5)
    paste_c(img, B.emoji("trophy", 256), W / 2, 470 + 10 * math.sin(tl * 2), scale=1.1 * eback(tl / 0.5))
    paste_c(img, gold_text_cached_v("HOW MANY", 140), W / 2, 820, scale=eback((tl - 0.1) / 0.4))
    paste_c(img, gold_text_cached_v("DID YOU GET?", 140), W / 2, 980, scale=eback((tl - 0.3) / 0.4))
    if tl > 0.8: paste_c(img, text_img("COMMENT  0 / 1 / 2 / 3  👇".replace("👇", ""), F("anton", 76), fill=WHITE), W / 2, 1170, alpha=ease((tl - 0.8) / 0.4))
    if tl > 1.4: paste_c(img, follow_btn(), W / 2, 1360, scale=eback((tl - 1.4) / 0.4) * (1 + 0.04 * math.sin(tl * 5)))

@functools.lru_cache(None)
def follow_btn():
    t_ = text_img("FOLLOW FOR MORE QUIZZES", F("anton", 60), fill=(24, 14, 2), shadow=False)
    w_, h_ = t_.width + 90, t_.height + 50
    g = grad(w_, h_, GOLD_L, GOLD_D).convert("RGBA"); g.putalpha(rrect((w_, h_), h_ // 2, (255, 255, 255, 255)).getchannel("A"))
    g.alpha_composite(t_, (45, (h_ - t_.height) // 2)); out = Image.new("RGBA", (w_ + 60, h_ + 60), (0, 0, 0, 0))
    out.alpha_composite(glow_of(g, 16, (255, 190, 60), 0.8), (30, 30)); out.alpha_composite(g, (30, 30)); return out

@functools.lru_cache(maxsize=256)
def cap_v(k, wi):
    words = [x[2] for x in B.CHUNKS[k]]; f = F("mont", 44); sp = f.getlength(" ")
    lines = wrap(" ".join(words), f, 940); asc, desc = f.getmetrics(); lh = asc + desc + 6
    tw = int(max(f.getlength(l) for l in lines)) + 8
    im = rrect((tw + 60, lh * len(lines) + 24), 20, (0, 0, 0, 160)); d = ImageDraw.Draw(im); j = 0
    for li, l in enumerate(lines):
        x = 30 + (tw - f.getlength(l)) / 2
        for w in l.split():
            d.text((x, 12 + asc + li * lh), w, font=f, anchor="ls", fill=GOLD_L if j == wi else WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
            x += f.getlength(w) + sp; j += 1
    return im

def frame(t, TL):
    img = bg_v().copy()
    sc = next((s for s in TL if s["start"] <= t < s["start"] + s["dur"]), TL[-1]); tl = t - sc["start"]
    if sc["kind"] == "q": particles(img, t, 0.5); render_qv(img, sc, tl)
    elif sc["kind"] == "intro3": render_hook(img, sc, tl)
    else: render_end(img, sc, tl)
    for s in TL[1:]:
        dt = t - s["start"]
        if -0.3 <= dt < 0.3:
            p = (dt + 0.3) / 0.6; y = -500 + p * (H + 1000)
            band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(band)
            d.polygon([(0, y - 300), (W, y - 500), (W, y + 100), (0, y + 300)], fill=(10, 8, 4, 255))
            d.polygon([(0, y + 300), (W, y + 100), (W, y + 150), (0, y + 350)], fill=GOLD_L + (255,))
            d.polygon([(0, y - 350), (W, y - 550), (W, y - 500), (0, y - 300)], fill=GOLD + (255,))
            img.alpha_composite(band)
    for k, (a, b) in enumerate(B.CH_T):
        if a <= t < b:
            wi = max([j for j, w in enumerate(B.CHUNKS[k]) if t >= w[0]], default=0)
            paste_c(img, cap_v(k, wi), W / 2, 1710 if sc["kind"] == "q" else 1640); break
    return img.convert("RGB")

def render_short(si):
    TL, total = setup(si); cap_v.cache_clear()
    B.build_audio(f"{OUT}/s{si}.wav")
    path = f"{OUT}/brainrush01_short{si+1}.mp4"
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{OUT}/s{si}.wav",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)): p.stdin.write(frame(f / FPS, TL).tobytes())
    p.stdin.close(); p.wait(); print("short", si + 1, round(total, 1), "s")

if __name__ == "__main__":
    if "--frames" in sys.argv:
        i = int(sys.argv[-2]); TL, total = setup(i); print("dur", round(total, 1))
        for x in [float(v) for v in sys.argv[-1].split(",")]: frame(x, TL).save(f"{OUT}/v{i}_{x:05.1f}.png")
        sys.exit()
    if "--short" in sys.argv: render_short(int(sys.argv[-1])); sys.exit()
    ensure_voice()
    ps = [subprocess.Popen([sys.executable, __file__, "--short", str(i)]) for i in range(len(SHORTS))]
    for p in ps: p.wait()
