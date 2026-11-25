"""Gera a narração (Kokoro ONNX, voz am_michael) + timestamps por palavra (Whisper)."""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
import importlib
VID = os.environ.get("BR_VID", "01"); D = importlib.import_module(f"brainrush{VID}_data")
INTRO, QS, SCORE, OUTRO = D.INTRO, D.QS, D.SCORE, D.OUTRO
K = "/tmp/claude-0/kokoro/"; OUT = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/claude-0/br{VID}/voz"
os.makedirs(OUT, exist_ok=True)
VOICE, SPEED = "am_michael", 1.08
from kokoro_onnx import Kokoro
k = Kokoro(K + "model.onnx", K + "voices.npz")
segs = [x[:2] for x in INTRO]
for i, q in enumerate(QS, 1):
    if hasattr(D, "PRE"): segs.append((f"q{i:02d}_pre", D.PRE[i - 1]))
    segs += [(f"q{i:02d}_ask", q[4]), (f"q{i:02d}_ans", q[5])]
segs += [x for x in (SCORE, OUTRO) if x]
LETTER_A = getattr(D, "LETTER_A", {"q05_ask", "q05_ans"})  # "A G", "A U", "letters A and U"
from faster_whisper import WhisperModel
wm = WhisperModel("small", compute_type="int8")
meta = json.load(open(f"{OUT}/meta.json")) if os.path.exists(f"{OUT}/meta.json") else {}
for name, text in segs:
    if name in meta and meta[name]["text"] == text: continue
    wav = f"{OUT}/{name}.wav"
    tts = text.replace("BrainRush", "Brain Rush")
    if name in LETTER_A:
        ph = k.tokenizer.phonemize(tts, "en-us")
        ph = re.sub(r"(?<![^\s])ɐ(?=[\s.,!?])", "ˈeɪ", ph)
        a, sr = k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
    else:
        a, sr = k.create(tts, voice=VOICE, speed=SPEED, lang="en-us")
    # corta silêncio das pontas
    nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(nz[0] - 600, 0): nz[-1] + 2400]
    sf.write(wav, a, sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-ar", "16000", "-ac", "1", "/tmp/claude-0/_16k.wav"], check=True)
    a16, _ = sf.read("/tmp/claude-0/_16k.wav", dtype="float32")
    sg, _ = wm.transcribe(a16, language="en", word_timestamps=True, initial_prompt=text)
    words = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for s in sg for w in s.words]
    meta[name] = {"dur": len(a) / sr, "text": text, "words": words}
    json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
    print(name, round(len(a) / sr, 2), " ".join(w[2] for w in words)[:90], flush=True)
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
