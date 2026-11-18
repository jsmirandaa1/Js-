import json, re
def build_ev(path, fixes=(), dur=None):
    w = json.load(open(path))
    toks = [[a, b, t] for a, b, t in w]
    # merge whisper sub-tokens like "-noite"
    m = []
    for a, b, t in toks:
        if t.startswith("-") and m: m[-1][2] += t; m[-1][1] = b
        else: m.append([a, b, t])
    text = " ".join(x[2] for x in m)
    for old, new in fixes:
        # replace word sequences, keep timing of first..last
        ow = old.split(); i = 0
        while i <= len(m) - len(ow):
            if [x[2] for x in m[i:i+len(ow)]] == ow:
                m[i:i+len(ow)] = [[m[i][0], m[i+len(ow)-1][1], new]]
            i += 1
    ev, cur = [], []
    for x in m:
        cur.append(x)
        txt = " ".join(y[2] for y in cur)
        if len(txt) >= 11 or len(cur) >= 3 or re.search(r"[,.?!:…]$", x[2]):
            ev.append([cur[0][0], cur[-1][1], txt]); cur = []
    if cur: ev.append([cur[0][0], cur[-1][1], " ".join(y[2] for y in cur)])
    for j in range(len(ev)):
        nxt = ev[j+1][0] if j + 1 < len(ev) else (dur or ev[j][1] + 0.5)
        ev[j][1] = min(ev[j][1] + 0.35, nxt)
        if nxt - ev[j][1] < 0.3: ev[j][1] = nxt
    return [tuple(e) for e in ev]
