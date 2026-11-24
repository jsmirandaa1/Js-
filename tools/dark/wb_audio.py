"""The Wealth Blueprint – áudio da marca (trilha gerada + assinatura sonora). Sem direitos autorais.

make_bed(dur, seed, prog)  -> np.array estéreo 48 kHz (trilha cinematográfica sutil)
signature()               -> np.array estéreo 48 kHz (~3 s: boom grave + sino dourado D5/A5)
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000


def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)


PROGS = {
    'dm': [[38, 50, 53, 57, 62], [34, 46, 50, 53, 58], [41, 48, 53, 57, 60], [36, 48, 52, 55, 60]],   # Dm Bb F C
    'am': [[33, 45, 48, 52, 57], [29, 41, 45, 48, 53], [36, 48, 52, 55, 60], [31, 43, 47, 50, 55]],   # Am F C G
    'fm': [[29, 41, 44, 48, 53], [37, 49, 53, 56, 61], [32, 44, 48, 51, 56], [39, 51, 55, 58, 63]],   # Fm Db Ab Eb
    'up': [[36, 48, 52, 55, 60], [31, 43, 47, 50, 55], [33, 45, 48, 52, 57], [29, 41, 45, 48, 53]],   # C G Am F (inspirador)
}


def reverb(x, seed=11, length=2.8, decay=2.3, mix=0.85):
    r = np.random.default_rng(seed)
    L = int(length * SR); tt = np.arange(L) / SR
    ir = lp(r.standard_normal(L) * np.exp(-tt * decay), 5000) * 0.06
    return x * 0.8 + fftconvolve(x, ir)[:len(x)] * mix


def make_bed(dur, seed=1, prog='dm', bar=4.0, bpm=80, pulse=0.6, piano=1.0, swell_at=None):
    rng = np.random.default_rng(seed)
    N = int(dur * SR); t = np.arange(N) / SR
    CH = PROGS[prog]
    pad = np.zeros(N); bass = np.zeros(N)
    for b in range(int(np.ceil(dur / bar)) + 1):
        ch = CH[b % 4]
        s0 = int((b * bar - 0.8) * SR); L = int((bar + 1.6) * SR); tt = np.arange(L) / SR
        w = np.minimum(1, tt / 1.0) * np.minimum(1, (bar + 1.6 - tt) / 1.0)
        sig = np.zeros(L)
        for m in ch[1:]:
            for det in (-0.1, 0.0, 0.09):
                ff = mtof(m) * 2 ** (det / 12); ph = rng.uniform(0, 6.28)
                for h, a in ((1, 1.0), (2, 0.3), (3, 0.12)):
                    sig += a * np.sin(2 * np.pi * ff * h * tt + ph * h) / 3
        bs = (np.sin(2 * np.pi * mtof(ch[0]) * tt) + 0.3 * np.sin(4 * np.pi * mtof(ch[0]) * tt)) * w
        a_, z = max(0, s0), min(N, s0 + L)
        if z > a_:
            pad[a_:z] += (sig * w)[a_ - s0:z - s0]; bass[a_:z] += bs[a_ - s0:z - s0]
    pad = lp(pad, 1600) * 0.05; bass = lp(bass, 200) * 0.09
    # piano 8th-note arpeggio (sparse)
    pn = np.zeros(N); step = 60 / bpm / 2; k = 0; tc = 0.2
    pat = [0, 2, 1, 3, 2, 4, 3, 1]
    while tc < dur - 0.5:
        ch = CH[int(tc // bar) % 4]; up = [m + 12 for m in ch[1:]]
        if rng.random() < 0.75:
            f = mtof(up[pat[k % 8] % len(up)]); L = int(2.5 * SR); tt = np.arange(L) / SR
            note = sum(a * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (2.2 + h)) for h, a in ((1, 1), (2, 0.35), (3, 0.15)))
            note *= np.minimum(1, tt / 0.005) * rng.uniform(0.5, 1)
            s0 = int(tc * SR); z = min(N, s0 + L); pn[s0:z] += note[:z - s0]
        tc += step; k += 1
    pn = lp(pn, 3500) * 0.05 * piano
    # soft pulse (heartbeat kick) + shaker-ish hats
    pu = np.zeros(N); tb = 60 / bpm * 2
    while tb < dur - 0.3:
        L = int(0.45 * SR); tt = np.arange(L) / SR
        th = np.sin(2 * np.pi * (55 * np.exp(-tt * 9) + 40) * tt) * np.exp(-tt * 10)
        s0 = int(tb * SR); z = min(N, s0 + L); pu[s0:z] += th[:z - s0] * 0.12 * pulse
        L2 = int(0.06 * SR); hat = hp(rng.standard_normal(L2), 7000) * np.exp(-np.arange(L2) / SR * 60) * 0.02 * pulse
        s1 = int((tb + 60 / bpm / 2) * SR); z = min(N, s1 + L2); pu[s1:z] += hat[:z - s1]
        tb += 60 / bpm
    env = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.2)
    if swell_at:
        env *= 0.85 + 0.25 * np.clip((t - swell_at + 4) / 4, 0, 1)
    mono = (pad + bass + pn + pu) * env
    st = np.stack([reverb(mono, 11), reverb(mono, 12)], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.7


def signature():
    """Assinatura sonora: sub-boom + sino D5→A5 com brilho, ~3 s."""
    L = int(3.2 * SR); tt = np.arange(L) / SR
    boom = np.sin(2 * np.pi * (48 * np.exp(-tt * 1.6) + 34) * tt) * np.exp(-tt * 1.8) * 0.5
    def bell(f, t0, amp):
        x = np.zeros(L); s = int(t0 * SR); u = tt[:L - s]
        y = sum(a * np.sin(2 * np.pi * f * r * u) * np.exp(-u * d) for r, a, d in ((1, 1, 2.0), (2.76, 0.35, 3.5), (5.4, 0.18, 6), (8.9, 0.08, 9)))
        x[s:] = y * np.minimum(1, u / 0.003) * amp; return x
    sig = boom + bell(mtof(74), 0.05, 0.22) + bell(mtof(81), 0.42, 0.18)
    sh = hp(np.random.default_rng(4).standard_normal(L), 6000) * np.exp(-tt * 3) * np.minimum(1, tt / 0.3) * 0.02
    sig = sig + sh
    st = np.stack([reverb(sig, 21, 3.0, 1.8, 1.0), reverb(sig, 22, 3.0, 1.8, 1.0)], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.8
