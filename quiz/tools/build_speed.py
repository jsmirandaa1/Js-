"""SPEED QUIZ vertical (TikTok): 8 perguntas, timer curto, HARD no meio, FINAL BOSS no fim, sem tela de intro longa.
Uso: python3 build_speed.py [lote]           -> gera voz + renderiza todos os speed quizzes do lote (padrão speed01)
     python3 build_speed.py lote --one i      -> renderiza só o i
     python3 build_speed.py lote --frames i t1,t2
"""
import os, sys, json, re, math, subprocess, importlib, functools
os.environ["BR_VID"] = "03"          # motor com as cenas dos vídeos 01, 02 e 03 carregadas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import build_brainrush01 as B
import build_brainrush01_shorts as S
from brgfx import *

LOTE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "speed01"
SD = importlib.import_module(f"{LOTE}_data")
QSRC = {v: importlib.import_module(f"brainrush0{v}_data").QS for v in (1, 2, 3)}
ASK = {1: B.V1_ASK, 2: B.V2_ASK, 3: B.stage_ask}
EXP = {1: B.V1_EXP, 2: B.V2_EXP, 3: B.stage_exp}
W, H, FPS = 1080, 1920, 30
OUT = f"/tmp/claude-0/{LOTE}"; os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ voz
def lines():
    L = {}
    for si, s in enumerate(SD.SPEED):
        L[f"sp{si}_h"] = s["hook_v"]
        for k, (v, qi, lv, q, a) in enumerate(s["qs"]):
            L[f"sp{si}_q{k}"] = q; L[f"sp{si}_a{k}"] = a
    L["sp_outro"] = SD.OUTRO_V
    return {f"{LOTE}_{k}": v for k, v in L.items()}

def ensure_voice():
    todo = {k: v for k, v in lines().items() if k not in B.META or B.META[k]["text"] != v}
    if not todo: return
    import soundfile as sf
    from kokoro_onnx import Kokoro
    from faster_whisper import WhisperModel
    kk = Kokoro("/tmp/claude-0/kokoro/model.onnx", "/tmp/claude-0/kokoro/voices.npz"); wm = WhisperModel("small", compute_type="int8")
    for name, text in todo.items():
        if name.replace(f"{LOTE}_", "") in SD.PHONEME_A:
            ph = re.sub(r"(?<![^\s])ɐ(?=[\s.,!?])", "ˈeɪ", kk.tokenizer.phonemize(text, "en-us"))
            a, sr = kk.create(ph, voice="am_michael", speed=1.15, is_phonemes=True)
        else:
            a, sr = kk.create(text, voice="am_michael", speed=1.15, lang="en-us")
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(nz[0] - 400, 0): nz[-1] + 1800]
        sf.write(f"{B.VOZ}/{name}.wav", a, sr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{B.VOZ}/{name}.wav", "-ar", "16000", "-ac", "1", "/tmp/claude-0/_16k.wav"], check=True)
        a16, _ = sf.read("/tmp/claude-0/_16k.wav", dtype="float32")
        sg, _ = wm.transcribe(a16, language="en", word_timestamps=True, initial_prompt=text)
        B.META[name] = {"dur": len(a) / sr, "text": text, "words": [[w.start, w.end, w.word.strip()] for s_ in sg for w in s_.words]}
        print("voz", name, round(len(a) / sr, 2), flush=True)
    json.dump(B.META, open(f"{B.VOZ}/meta.json", "w"), indent=1)

# ------------------------------------------------------------------ linha do tempo
def setup(si):
    S_ = SD.SPEED[si]; P = f"{LOTE}_sp{si}"; TL, AUD, SFX = [], [], []; t = 0.0
    d = B.META[f"{P}_h"]["dur"]
    TL.append(dict(kind="intro3", start=0, dur=0.15 + d + 0.25)); AUD.append((0.15, f"{P}_h")); SFX.append((0.0, "impact")); t = TL[-1]["dur"]
    n = len(S_["qs"])
    for k, (v, qi, lv, qtxt, atxt) in enumerate(S_["qs"]):
        qd = B.META[f"{P}_q{k}"]["dur"]; ad = B.META[f"{P}_a{k}"]["dur"]; T = SD.TIMER[lv]
        A0 = 0.2; CS = A0 + qd + 0.1; R = CS + T; AN = R + 0.12
        dur = R + max(2.0, 0.12 + ad + 1.1)
        TL.append(dict(kind="q", start=t, dur=dur, v=v, sq=qi, lv=lv, k=k, n=n, A0=A0, CS=CS, R=R, AN=AN, T=T, qi=29 if lv == "B" else 0))
        AUD += [(t + A0, f"{P}_q{k}"), (t + AN, f"{P}_a{k}")]
        SFX.append((t, "impact" if lv in "HB" else "whoosh"))
        SFX += [(t + CS + j, "tick2" if j >= T - 2 else "tick") for j in range(T)]
        SFX.append((t + R, "victory" if lv == "B" else "correct")); t += dur
    d = B.META[f"{LOTE}_sp_outro"]["dur"]
    TL.append(dict(kind="outro", start=t, dur=0.2 + d + 1.2, v0=0.2, vd=d)); AUD.append((t + 0.2, f"{LOTE}_sp_outro")); SFX.append((t, "whoosh")); t += TL[-1]["dur"]
    B.TL, B.AUD, B.SFX, B.TOTAL = TL, AUD, SFX, t
    return TL, t

# ------------------------------------------------------------------ desenho
@functools.lru_cache(None)
def tag(txt):
    t_ = text_img(txt, F("anton", 54), fill=WHITE, shadow=False)
    im = rrect((t_.width + 70, t_.height + 28), (t_.height + 28) // 2, (200, 30, 40, 255), (255, 210, 120, 255), 3)
    im.alpha_composite(t_, (35, 14)); out = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    out.alpha_composite(glow_of(im, 16, (255, 60, 60), 0.8), (30, 30)); out.alpha_composite(im, (30, 30)); return out

@functools.lru_cache(None)
def banner(txt): return S.gold_text_cached_v(txt, 104)

ST_CY, TM_Y, Q_Y, OPT_Y = 600, 940, 1085, [1205, 1315, 1425, 1535]

def render_q(img, sc, tq, hook):
    v, qi, lv = sc["v"], sc["sq"], sc["lv"]; q = QSRC[v][qi]; R, CS, T = sc["R"], sc["CS"], sc["T"]
    paste_c(img, banner(hook), W / 2, 215)
    if lv not in "HB": paste_c(img, B.chip(f"QUESTION {sc['k']+1} / {sc['n']}"), W / 2, 320)
    shake = 10 * math.sin(tq * 60) * max(0, 1 - tq / 0.35) if lv in "HB" else 0
    EX = R + 0.15
    st = ASK[v](qi, tq) if tq < EX else EXP[v](qi, tq - EX + 0.5, None)
    if EX <= tq < EX + 0.2:
        a = ASK[v](qi, tq); b = st.copy(); b.putalpha(int(255 * (tq - EX) / 0.2)); a.alpha_composite(b); st = a
    B.compose_stage(img, st, alpha=ease(tq / 0.2), scale=0.98 * (0.94 + 0.06 * eout(tq / 0.3)), cx=W / 2 + shake, cy=ST_CY)
    if lv in "HB": paste_c(img, tag("⚡ HARD QUESTION".replace("⚡ ", "") if lv == "H" else "FINAL BOSS"), W / 2, 320, scale=eback(tq / 0.3) * (1 + 0.05 * math.sin(tq * 8)))
    if tq < CS: frac, num, pulse = 1.0, T, 0
    elif tq < R: e = tq - CS; frac = 1 - e / T; num = T - int(e); pulse = max(0, 1 - (e % 1) / 0.25)
    else: frac, num, pulse = 1.0, 0, 0
    paste_c(img, B.timer(frac, num, pulse, done=tq >= R, urgent=(R - 2 <= tq < R)), W / 2, TM_Y, scale=0.62 * (1 + (0.15 * max(0, 1 - (tq - R) / 0.3) if tq >= R else 0)))
    qa = ease(tq / 0.25); qim = S.q_img(q[1]); paste_c(img, qim, W / 2, Q_Y - max(0, qim.height - 150) / 2, alpha=qa)
    for k, opt in enumerate(q[2]):
        p = eout((tq - 0.15 - k * 0.1) / 0.25)
        if p <= 0: continue
        L = "ABCD"[k]
        if tq >= R and k == q[3]:
            pp = (tq - R) / 0.4; paste_c(img, B.option_img(opt, L, "ok"), 500, OPT_Y[k], scale=1.04 * (1 + 0.08 * math.sin(min(pp, 1) * math.pi)))
        else:
            a = p if tq < R else p * (1 - 0.7 * ease((tq - R) / 0.25))
            paste_c(img, B.option_img(opt, L, "n"), 500 - 50 * (1 - p), OPT_Y[k], alpha=a, scale=1.04)
    if R <= tq < R + 0.2: img.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 140, int(80 * (1 - (tq - R) / 0.2)))))
    if tq < 0.12: img.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 200, int(120 * (1 - tq / 0.12)))))

def render_hook(img, sc, tl, hook):
    S.particles(img, tl)
    words = hook.split(); lines_ = [" ".join(words[:2]), " ".join(words[2:])] if len(words) > 2 else [hook]
    for k, l in enumerate(lines_):
        p = eback((tl - k * 0.15) / 0.3)
        if p > 0: paste_c(img, S.gold_text_cached_v(l, 160), W / 2, 700 + k * 200, scale=p)
    if tl > 0.4: paste_c(img, text_img("8 QUESTIONS  •  3 SECONDS", F("bebas", 70), fill=WHITE, spacing=4), W / 2, 1150, alpha=ease((tl - 0.4) / 0.3))
    paste_c(img, B.emoji("brain", 220), W / 2, 380 + 12 * math.sin(tl * 4), scale=eback(tl / 0.4))

def render_end(img, sc, tl):
    S.particles(img, tl + 3)
    paste_c(img, S.gold_text_cached_v("HOW MANY", 150), W / 2, 640, scale=eback(tl / 0.3))
    paste_c(img, S.gold_text_cached_v("DID YOU GET?", 150), W / 2, 820, scale=eback((tl - 0.15) / 0.3))
    if tl > 0.5: paste_c(img, text_img("COMMENT YOUR SCORE /8", F("anton", 84), fill=WHITE), W / 2, 1020, alpha=ease((tl - 0.5) / 0.3))
    if tl > 0.9: paste_c(img, S.follow_btn(), W / 2, 1220, scale=eback((tl - 0.9) / 0.3))

def frame(t, TL, hook):
    img = S.bg_v().copy()
    sc = next((s for s in TL if s["start"] <= t < s["start"] + s["dur"]), TL[-1]); tl = t - sc["start"]
    if sc["kind"] == "q": S.particles(img, t, 0.4); render_q(img, sc, tl, hook)
    elif sc["kind"] == "intro3": render_hook(img, sc, tl, hook)
    else: render_end(img, sc, tl)
    return img.convert("RGB")

def render_one(si):
    TL, total = setup(si); hook = SD.SPEED[si]["hook"]
    B.build_audio(f"{OUT}/s{si}.wav")
    path = f"{OUT}/{LOTE}_tiktok{si+1}.mp4"
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{OUT}/s{si}.wav",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)): p.stdin.write(frame(f / FPS, TL, hook).tobytes())
    p.stdin.close(); p.wait(); print("speed", si + 1, round(total, 1), "s", flush=True)

if __name__ == "__main__":
    if "--frames" in sys.argv:
        i = int(sys.argv[-2]); TL, total = setup(i); print("dur", round(total, 1))
        for x in [float(v) for v in sys.argv[-1].split(",")]: frame(x, TL, SD.SPEED[i]["hook"]).save(f"{OUT}/f{i}_{x:05.1f}.png")
        sys.exit()
    if "--one" in sys.argv: render_one(int(sys.argv[-1])); sys.exit()
    ensure_voice()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda i: subprocess.run([sys.executable, __file__, LOTE, "--one", str(i)]), range(len(SD.SPEED))))
