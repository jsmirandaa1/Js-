"""Gera a narração (Kokoro ONNX, voz am_michael) + timestamps por palavra (Whisper)."""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from brainrush01_data import INTRO, QS, SCORE, OUTRO
K = "/tmp/claude-0/kokoro/"; OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/br01/voz"
os.makedirs(OUT, exist_ok=True)
VOICE, SPEED = "am_michael", 1.08
from kokoro_onnx import Kokoro
k = Kokoro(K + "model.onnx", K + "voices.npz")
segs = list(INTRO)
for i, q in enumerate(QS, 1):
    segs += [(f"q{i:02d}_ask", q[4]), (f"q{i:02d}_ans", q[5])]
segs += [SCORE, OUTRO]
LETTER_A = {"q05_ask", "q05_ans"}  # "A G", "A U", "letters A and U"
from faster_whisper import WhisperModel
wm = WhisperModel("small", compute_type="int8")
meta = {}
for name, text in segs:
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
    print(name, round(len(a) / sr, 2), " ".join(w[2] for w in words)[:90], flush=True)
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
