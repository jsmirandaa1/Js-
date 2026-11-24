"""Narração de episódio longo a partir do roteiro .md (cenas '## SCENE', linhas de fala; ignora **VISUAL**).
Uso: python3 ep_tts.py roteiro.md OUTDIR   -> OUTDIR/voice3.wav, tl3.json (mesmo formato do Ep. 001)
Pausas: 0,85s (frase curta) / 0,65s, 4s entre cenas, +4s depois do gancho (título), +9s no fim (tela final).
"""
import json, re, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
md, out = sys.argv[1], sys.argv[2]
TTS_FIX = {}   # display -> tts (ex.: valores com $ por extenso)
S = []; scene = 0
for ln in open(md):
    ln = ln.strip()
    if ln.startswith('## SCENE'):
        scene += 1; continue
    if not scene or not ln or ln.startswith('**') or ln.startswith('*END') or ln.startswith('#') or ln.startswith('-'):
        continue
    S.append((scene, ln))
k = Kokoro('/root/work/kok/kokoro-v1.0.onnx', '/root/work/kok/voices-v1.0.bin')
st = k.get_voice_style('am_michael') * 0.6 + k.get_voice_style('am_onyx') * 0.4
sr = 24000; parts = [np.zeros(int(sr * 1.2), np.float32)]; t = 1.2; meta = []; prev = None
for i, (scn, disp) in enumerate(S):
    if prev is not None:
        gap = (2.8 + 4.0 if prev == 1 else 4.0) if scn != prev else (0.85 if len(disp) < 40 else 0.65)
        parts.append(np.zeros(int(sr * gap), np.float32)); t += gap
    a, _ = k.create(TTS_FIX.get(disp, disp), voice=st, speed=0.88, lang='en-us'); a = a.astype(np.float32)
    idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 240):idx[-1] + 600]
    d = len(a) / sr; meta.append(dict(i=i, scene=scn, text=disp, start=round(t, 3), end=round(t + d, 3)))
    parts.append(a); t += d; prev = scn
parts.append(np.zeros(int(sr * 12.0), np.float32))
y = np.concatenate(parts); sf.write(f'{out}/voice3.wav', y, sr); json.dump(meta, open(f'{out}/tl3.json', 'w'), indent=0)
print('sentences', len(S), 'total', round(len(y) / sr, 1))
