import json, subprocess, numpy as np, sys
from faster_whisper import WhisperModel
a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "audio.mp4", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                 capture_output=True).stdout, np.int16).astype(np.float32) / 32768
# loudness per second
sec = a[: len(a) // 16000 * 16000].reshape(-1, 16000)
rms = 20 * np.log10(np.sqrt((sec ** 2).mean(1)) + 1e-9)
json.dump([round(float(x), 1) for x in rms], open("loud.json", "w"))
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
segs, _ = m.transcribe(a, language="pt", vad_filter=True, beam_size=1, word_timestamps=False, condition_on_previous_text=False)
with open("segs.jsonl", "w") as f:
    for s in segs:
        f.write(json.dumps([round(s.start, 2), round(s.end, 2), s.text.strip()], ensure_ascii=False) + "\n"); f.flush()
print("done")
