"""Confere as transcrições do Whisper de um vídeo e refaz as ruins. Uso: BR_VID=NN python3 fix_transcripts.py"""
import json, re, difflib, subprocess, os, soundfile as sf
from faster_whisper import WhisperModel
V = f"/tmp/claude-0/br{os.environ.get('BR_VID', '01')}/voz"; M = json.load(open(V + "/meta.json"))
n = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
def ratio(m): return difflib.SequenceMatcher(None, [n(x) for x in m["text"].split()], [n(x[2]) for x in m["words"]]).ratio()
wm = None
for k, m in M.items():
    if ratio(m) >= 0.75: continue
    wm = wm or WhisperModel("small", compute_type="int8")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{V}/{k}.wav", "-ar", "16000", "-ac", "1", "/tmp/claude-0/_16k.wav"], check=True)
    a16, _ = sf.read("/tmp/claude-0/_16k.wav", dtype="float32")
    sg, _ = wm.transcribe(a16, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    new = [[w.start, w.end, w.word.strip()] for s in sg for w in s.words]
    old = m["words"]; m["words"] = new
    if ratio(m) < ratio(dict(m, words=old)): m["words"] = old
    print("refeito", k, round(ratio(m), 2))
for k, m in M.items():  # separa "A2," -> "A:" "2,"
    out = []
    for a, b, w in m["words"]:
        mm = re.fullmatch(r"([ABCD])(\d+)([,.]?)", w)
        if mm: mid = (a + b) / 2; out += [[a, mid, mm.group(1) + ":"], [mid, b, mm.group(2) + mm.group(3)]]
        else: out.append([a, b, w])
    m["words"] = out
json.dump(M, open(V + "/meta.json", "w"), indent=1); print("ok")
