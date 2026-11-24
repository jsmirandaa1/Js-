"""Cinematic emotional score synthesized with numpy (no copyright).
make(dur, sections, hits) -> stereo float array (N,2) at SR.
sections: list of (t0, t1, intensity 0..1)  ; hits: list of times for impacts (with riser before)."""
import numpy as np
from scipy.signal import lfilter, fftconvolve

SR = 44100
BPM = 80.0
BEAT = 60 / BPM          # 0.75s
BAR = 4 * BEAT           # 3s
# A minor: Am - F - C - G   (epic: Am F C G / F G Am Am)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G (root octave 3/4)
BASS = [45, 41, 36, 43]

rng = np.random.default_rng(7)

def env_at(sections, t):
    out = np.zeros_like(t)
    for a, b, i in sections:
        m = (t >= a) & (t < b)
        out[m] = i
    # smooth 1.5s
    k = int(1.5 * 100)
    return out

def intensity_curve(sections, n, rate=100):
    t = np.arange(n) / rate
    e = np.zeros(n)
    for a, b, i in sections:
        if isinstance(i, tuple):
            m = (t >= a) & (t < b); e[m] = i[0] + (i[1] - i[0]) * (t[m] - a) / max(b - a, 1e-3)
        else:
            e[(t >= a) & (t < b)] = i
    k = np.ones(rate) / rate
    return np.convolve(e, k, mode="same")

def piano_note(f, dur, vel):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for h, a in enumerate([1, .55, .3, .18, .1, .06], 1):
        fh = f * h * (1 + 0.0004 * h * h)
        x += a * np.sin(2 * np.pi * fh * t) * np.exp(-t * (1.2 + 0.9 * h))
    att = np.minimum(1, t / 0.004)
    return vel * x * att

def pad_note(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for det in (-0.12, -0.04, 0.05, 0.13):
        ff = f * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * np.pi)
        for h in range(1, 9):
            x += (1 / h) * np.sin(2 * np.pi * ff * h * t + ph * h) * (0.9 ** h)
    x /= 8
    a = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9).clip(0, 1)
    return x * a

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)

def kick(n=int(0.5 * SR)):
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)

def snare(n=int(0.45 * SR)):
    t = np.arange(n) / SR
    no = lowpass(rng.standard_normal(n), 6000) * np.exp(-t * 11)
    return 0.7 * no + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 18)

def tom(f, n=int(0.6 * SR)):
    t = np.arange(n) / SR
    ff = f * (1 + 0.5 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 6)

def boom(n=int(3.0 * SR)):
    t = np.arange(n) / SR
    f = 30 + 60 * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    x += 0.35 * lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 4)
    return x

def riser(d=2.0):
    n = int(d * SR); t = np.arange(n) / SR
    no = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep via blockwise lowpass
    blk = 2048
    for i in range(0, n, blk):
        fc = 300 + 7000 * (i / n) ** 2
        out[i:i + blk] = lowpass(no[i:i + blk], fc)
    return out * (t / d) ** 2

def place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    j = min(len(buf), i + len(x))
    buf[max(i, 0):j] += g * x[max(0, -i):j - i]

def make(dur, sections, hits, start=0.0):
    N = int(dur * SR)
    piano = np.zeros(N); pad = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N); fx = np.zeros(N)
    I = intensity_curve(sections, int(dur * 100) + 10)
    def Ia(t): return I[min(int(t * 100), len(I) - 1)]
    nb = int((dur - start) / BAR) + 2
    K, S = kick(), snare()
    for b in range(nb):
        t0 = start + b * BAR
        if t0 >= dur: break
        ci = b % 4
        ch = CHORDS[ci]
        it = Ia(t0 + 0.1)
        if it <= 0.01: continue
        # pad
        for nn in ch: place(pad, pad_note(midi(nn), BAR + 0.6), t0 - 0.2, 0.22)
        if it > 0.55:
            for nn in ch: place(pad, pad_note(midi(nn + 12), BAR + 0.6), t0 - 0.2, 0.12 * it)
        # piano arpeggio (8ths) - pattern root,5th,octave,3rd up
        arp = [ch[0] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 24, ch[2] + 12]
        for k, nn in enumerate(arp):
            tt = t0 + k * BEAT / 2
            v = 0.32 * (1.0 if k % 2 == 0 else 0.75)
            place(piano, piano_note(midi(nn), 2.2, v), tt)
        place(piano, piano_note(midi(ch[0]), 3.5, 0.35), t0)
        # bass pulse
        if it > 0.45:
            for k in range(8):
                tt = t0 + k * BEAT / 2
                place(bass, pad_note(midi(BASS[ci]), BEAT / 2 + 0.05) * 1.0, tt, 0.5 * min(1, (it - 0.4) * 2))
        elif it > 0.15:
            place(bass, pad_note(midi(BASS[ci]), BAR), t0, 0.35)
        # drums
        if it > 0.68:
            place(drums, K, t0, 1.0); place(drums, S, t0 + 2 * BEAT, 0.8)
            place(drums, K, t0 + 1.5 * BEAT, 0.6)
            if it > 0.85:
                place(drums, K, t0 + 3 * BEAT, 0.7); place(drums, S, t0 + 3.5 * BEAT, 0.35)
                for k in range(8): place(drums, lowpass(rng.standard_normal(int(0.05 * SR)), 9000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 60), t0 + k * BEAT / 2, 0.07)
            if b % 4 == 3:
                for k, f in enumerate([180, 150, 120, 95]): place(drums, tom(f), t0 + 3 * BEAT + k * BEAT / 4, 0.7)
    for h in hits:
        place(fx, riser(2.0), h - 2.0, 0.35); place(fx, boom(), h, 1.0)
    pad = lowpass(pad, 2500); bass = lowpass(bass, 400)
    dry = 0.9 * piano + 0.8 * pad + 0.9 * bass + 0.75 * drums + 0.55 * fx
    # reverb
    ir_n = int(2.8 * SR); tt = np.arange(ir_n) / SR
    out = []
    for s in (1, 2):
        ir = rng.standard_normal(ir_n) * np.exp(-tt * 2.4); ir[:int(0.01 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum())
        wet = fftconvolve(0.7 * piano + 0.9 * pad + 0.4 * drums + 0.4 * fx, ir)[:N]
        out.append(dry + 0.35 * wet)
    x = np.stack(out, 1)
    x /= np.abs(x).max() + 1e-9
    return x * 0.9
