import sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    a = np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i",f,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout, np.int16).astype(np.float32)/32768
    segs, _ = m.transcribe(a, language="pt", word_timestamps=True, vad_filter=False, beam_size=5)
    out = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for s in segs for w in s.words]
    json.dump(out, open(f.replace(".mp3", "_words.json"), "w"), ensure_ascii=False, indent=0)
    print(f, len(out)); print(" ".join(f"{w[2]}@{w[0]:.2f}" for w in out[:40]))
