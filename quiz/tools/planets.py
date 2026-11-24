"""Renderiza planetas realistas (esfera com textura + iluminação) com numpy."""
import numpy as np
from PIL import Image
A = "/tmp/claude-0/quiz_assets/"
_tex = {}
def tex(name):
    if name not in _tex:
        _tex[name] = np.asarray(Image.open(A + name).convert("RGB")).astype(np.float32) / 255
    return _tex[name]

def sphere(texname, size, lon0=0.0, tilt=0.0, light=(-0.6, -0.35, 0.75), ambient=0.06, atmo=None, spec=None):
    """Retorna RGBA (size x size). lon0 em graus = longitude no centro."""
    T = tex(texname); H, W, _ = T.shape
    r = np.linspace(-1, 1, size, dtype=np.float32)
    x, y = np.meshgrid(r, r)
    d2 = x * x + y * y; m = d2 <= 1
    z = np.sqrt(np.clip(1 - d2, 0, 1))
    ct, st = np.cos(np.radians(tilt)), np.sin(np.radians(tilt))
    yy = y * ct - z * st; zz = y * st + z * ct
    lat = np.arcsin(np.clip(-yy, -1, 1))
    lon = np.arctan2(x, zz) + np.radians(lon0)
    u = ((lon / (2 * np.pi) + 0.5) % 1) * (W - 1)
    v = (0.5 - lat / np.pi) * (H - 1)
    col = T[v.astype(int), u.astype(int)]
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    nd = np.clip(x * L[0] + y * L[1] + z * L[2], 0, 1)
    shade = ambient + (1 - ambient) * nd ** 0.9
    out = col * shade[..., None]
    if spec is not None:
        S = tex(spec)[v.astype(int), u.astype(int), 0]
        h = np.clip(2 * nd * z - L[2], 0, 1)
        out += (S * h ** 30 * 0.5)[..., None]
    if atmo is not None:
        rim = (1 - z) ** 3 * (0.3 + 0.7 * nd)
        out = out + rim[..., None] * np.array(atmo, np.float32)
    a = np.clip((1 - np.sqrt(d2)) * size / 2, 0, 1) * m
    rgba = np.dstack([np.clip(out, 0, 1), a])
    return Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")

def saturn(size, lon0=0.0):
    """Saturno com anéis inclinados. Retorna RGBA (2.4*size x 1.3*size)."""
    W, H = int(size * 2.4), int(size * 1.3)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ring_c = tex("saturnring.jpg")[32]
    ring_a = np.asarray(Image.open(A + "saturnringpat.gif").convert("L")).astype(np.float32)[32] / 255
    xs = (np.arange(W) - W / 2) / (size / 2); ys = (np.arange(H) - H / 2) / (size / 2)
    X, Y = np.meshgrid(xs, ys)
    inc = 0.32; rot = np.radians(-12)
    Xr = X * np.cos(rot) - Y * np.sin(rot); Yr = X * np.sin(rot) + Y * np.cos(rot)
    R = np.sqrt(Xr ** 2 + (Yr / inc) ** 2)
    r0, r1 = 1.24, 2.27
    t = (R - r0) / (r1 - r0); inring = (t >= 0) & (t < 1)
    idx = np.clip(t * (len(ring_c) - 1), 0, len(ring_c) - 1).astype(int)
    rc = ring_c[idx] * 1.1; ra = ring_a[idx] * inring
    # sombra do planeta sobre o anel (lado de trás-direita)
    shadow = (Yr < 0) & (np.abs(Xr) < 1.0) & (Xr > -0.2)
    rc = rc * np.where(shadow, 0.25, 1.0)[..., None]
    ring = np.dstack([np.clip(rc, 0, 1), ra * 0.95])
    ring_img = Image.fromarray((ring * 255).astype(np.uint8), "RGBA")
    back = ring_img.copy(); front = ring_img.copy()
    bmask = Image.fromarray(((Yr < 0) * 255).astype(np.uint8)); fmask = Image.fromarray(((Yr >= 0) * 255).astype(np.uint8))
    back.putalpha(Image.fromarray(np.minimum(np.asarray(back.getchannel("A")), np.asarray(bmask))))
    front.putalpha(Image.fromarray(np.minimum(np.asarray(front.getchannel("A")), np.asarray(fmask))))
    img.alpha_composite(back)
    p = sphere("saturn.jpg", size, lon0=lon0, tilt=-18, light=(-0.7, -0.3, 0.65), ambient=0.04)
    p = p.rotate(12, resample=Image.BICUBIC)
    img.alpha_composite(p, ((W - size) // 2, (H - size) // 2))
    img.alpha_composite(front)
    return img
