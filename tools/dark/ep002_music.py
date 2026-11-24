"""Trilha cinematográfica gerada (sem direitos autorais) para o Ep. 002 (mesma estrutura do Ep. 001 + assinatura sonora no fim).
Ambient em Ré menor: pad + graves + piano esparso + risers/booms nas trocas de capítulo.
Uso: WORK=/root/work/ep1 python3 ep001_music.py  -> WORK/music.wav (48 kHz estéreo)
"""
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

WORK = os.environ.get('WORK', '/root/work/ep2')
SR = 48000
TL = json.load(open(f'{WORK}/tl3.json'))
DUR = sf.info(f'{WORK}/voice3.wav').duration
N = int(DUR * SR)
rng = np.random.default_rng(8)
t_all = np.arange(N) / SR


def T(i): return TL[i]['start']
def E(i): return TL[i]['end']


def mtof(m): return 440 * 2 ** ((m - 69) / 12)


# chapter boundaries (same as the renderer)
TITLE = E(9) + 0.5
CARDS = [E(26) + 0.5, E(46) + 0.5, E(65) + 0.5, E(81) + 0.5, E(97) + 0.5]
END = T(109) - 0.4

# progression: Dm  Bb  F  C   (each chord 8 s)
CHORDS = [[38, 50, 53, 57, 62], [34, 46, 50, 53, 58], [41, 48, 53, 57, 60], [36, 48, 52, 55, 60]]
BAR = 8.0


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


# intensity envelope over the episode (0..1)
def intensity(t):
    pts = [(0, 0.35), (TITLE - 2, 0.55), (TITLE + 1, 0.8), (TITLE + 6, 0.5), (CARDS[0], 0.6), (CARDS[1], 0.65),
           (CARDS[1] + 40, 0.75), (CARDS[2], 0.6), (CARDS[3], 0.55), (CARDS[3] + 40, 0.75), (CARDS[4], 0.7),
           (END - 6, 0.8), (END + 2, 1.0), (DUR - 4, 0.9), (DUR, 0.0)]
    xs, ys = zip(*pts)
    return np.interp(t, xs, ys)


env = intensity(t_all)
pad = np.zeros(N)
bass = np.zeros(N)
nb = int(np.ceil(DUR / BAR)) + 1
for b in range(nb):
    ch = CHORDS[b % 4]
    s0 = int((b * BAR - 1.5) * SR)
    L = int((BAR + 3.0) * SR)
    tt = np.arange(L) / SR
    w = np.minimum(1, tt / 2.2) * np.minimum(1, (BAR + 3.0 - tt) / 2.2)
    sig = np.zeros(L)
    for m in ch[1:]:
        f = mtof(m)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            # soft saw-ish: few harmonics
            for h, amp in ((1, 1.0), (2, 0.32), (3, 0.14), (4, 0.06)):
                sig += amp * np.sin(2 * np.pi * ff * h * tt + ph * h) / 3
    sig *= w
    bs = np.sin(2 * np.pi * mtof(ch[0]) * tt) + 0.3 * np.sin(2 * np.pi * mtof(ch[0]) * 2 * tt)
    bs *= w
    a, z = max(0, s0), min(N, s0 + L)
    if z > a:
        pad[a:z] += sig[a - s0:z - s0]
        bass[a:z] += bs[a - s0:z - s0]

pad = lp(pad, 1400) * 0.05
pad *= (1 + 0.15 * np.sin(2 * np.pi * t_all / 13))
bass = lp(bass, 220) * 0.10

# piano: sparse arpeggio notes
piano = np.zeros(N)
pat = [0, 2, 1, 3, 2, 4, 3, 1]
step = BAR / 8
k = 0
tcur = 4.0
while tcur < DUR - 3:
    b = int(tcur // BAR)
    ch = CHORDS[b % 4]
    upper = [m + 12 for m in ch[1:]]
    m = upper[pat[k % 8] % len(upper)]
    if rng.random() < 0.82:
        f = mtof(m)
        L = int(3.5 * SR)
        tt = np.arange(L) / SR
        note = sum(a * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (1.6 + h * 0.9)) for h, a in ((1, 1), (2, 0.4), (3, 0.18), (4, 0.08)))
        note *= np.minimum(1, tt / 0.006)
        vel = rng.uniform(0.55, 1.0)
        s0 = int(tcur * SR)
        z = min(N, s0 + L)
        piano[s0:z] += note[:z - s0] * vel
    tcur += step
    k += 1
piano = lp(piano, 3200) * 0.045
pian_env = intensity(t_all) ** 1.5

# soft pulse in "momentum" sections (chapters 3 and 4)
pulse = np.zeros(N)
bpm = 64
for s_, e_ in ((CARDS[1] + 3, CARDS[3] - 1),):
    tb = s_
    while tb < e_:
        L = int(0.5 * SR); tt = np.arange(L) / SR
        thump = np.sin(2 * np.pi * (52 * np.exp(-tt * 8) + 38) * tt) * np.exp(-tt * 9)
        s0 = int(tb * SR); z = min(N, s0 + L)
        fade = min(1, (tb - s_) / 8, (e_ - tb) / 6)
        pulse[s0:z] += thump[:z - s0] * 0.10 * fade
        tb += 60 / bpm

# risers + booms at transitions
fx = np.zeros(N)
for tc in [TITLE] + CARDS + [END]:
    L = int(2.2 * SR); tt = np.arange(L) / SR
    nz = rng.standard_normal(L)
    rise = hp(lp(nz, 2500), 300) * (tt / 2.2) ** 2.5 * 0.05
    s0 = int((tc - 2.2) * SR)
    if s0 > 0:
        fx[s0:s0 + L] += rise
    L2 = int(4.0 * SR); tt = np.arange(L2) / SR
    boom = np.sin(2 * np.pi * (45 * np.exp(-tt * 1.2) + 30) * tt) * np.exp(-tt * 1.3) * 0.22
    boom += lp(rng.standard_normal(L2), 400) * np.exp(-tt * 3) * 0.05
    s1 = int(tc * SR)
    z = min(N, s1 + L2)
    fx[s1:z] += boom[:z - s1]

dry = (pad + bass) * env + piano * pian_env + pulse + fx

# reverb (synthetic IR), stereo by decorrelated IRs
def ir(seed):
    r = np.random.default_rng(seed)
    L = int(3.2 * SR); tt = np.arange(L) / SR
    x = r.standard_normal(L) * np.exp(-tt * 2.1)
    return lp(x, 5000) * 0.06

out = []
for sd in (11, 12):
    wet = fftconvolve(dry, ir(sd))[:N]
    out.append(dry * 0.75 + wet * 0.9)
st = np.stack(out, 1)
# fade in/out
fade = np.minimum(1, t_all / 2.0) * np.minimum(1, (DUR - t_all) / 3.5)
st *= fade[:, None]
st /= np.max(np.abs(st)) + 1e-9
st *= 0.7
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wb_audio
sig = wb_audio.signature()
s0 = int((E(110) + 0.8) * SR)
z = min(N, s0 + len(sig))
st[s0:z] += sig[:z - s0] * 0.9
st /= np.max(np.abs(st)) + 1e-9
st *= 0.7
sf.write(f'{WORK}/music.wav', st.astype(np.float32), SR)
print('music ok', DUR)
