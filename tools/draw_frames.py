"""Render every FERRIN frame from tools/ferrin_spec.py to build/frames/<row>/<nn>.png.

Drawing is parametric: each frame is a pose, each part a polygon in body space. Parts are
transformed (squash, lean, bob), drawn at SS x resolution with Pillow, then downsampled.
Requires Pillow (the only third-party dependency in the art pipeline).
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageOps
sys.path.insert(0, os.path.dirname(__file__))
import ferrin_spec as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "frames")


def rgb(name, a=255):
    h = S.PALETTE[name].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# ---------------------------------------------------------------- geometry helpers
def rot(pts, deg, cx=0.0, cy=0.0):
    t = math.radians(deg); c, s = math.cos(t), math.sin(t)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def shift(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def rrect(cx, cy, w, h, r, n=6):
    r = min(r, w / 2, h / 2); pts = []
    for (ox, oy, a0) in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts


def ellipse(cx, cy, w, h, n=48):
    return [(cx + w / 2 * math.cos(2 * math.pi * k / n), cy + h / 2 * math.sin(2 * math.pi * k / n)) for k in range(n)]


def arc(cx, cy, w, bulge, n=16):
    """polyline arc across width w; bulge < 0 arches upward"""
    return [(cx - w / 2 + w * k / n, cy + bulge * math.sin(math.pi * k / n)) for k in range(n + 1)]


class Frame:
    def __init__(self, p):
        self.p = p
        self.img = Image.new("RGBA", (S.CELL_W * S.SS, S.CELL_H * S.SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    # body-space point -> cell space
    def T(self, pts):
        p = self.p; out = []
        piv = (0.0, S.BODY_H)
        for x, y in pts:
            y = piv[1] + (y - piv[1]) * p["squash"]
            x, y = rot([(x, y)], p["lean"], *piv)[0]
            out.append((S.CX + x, S.BODY_TOP + p["bob"] + y))
        return out

    def S(self, pts):
        return [(x * S.SS, y * S.SS) for x, y in pts]

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon(self.S(pts), fill=fill, outline=outline, width=int(width * S.SS) if outline else 0)

    def line(self, pts, fill, width):
        self.d.line(self.S(pts), fill=fill, width=int(width * S.SS), joint="curve")

    # ------------------------------------------------------------ parts
    def puck(self):
        c = S.PUCK; t = self.p["puck_tilt"]
        body = rot(ellipse(S.CX, c["cy"], c["w"], c["h"]), t, S.CX, c["cy"])
        self.poly(body, rgb("gunmetal"))
        top = rot(ellipse(S.CX, c["cy"] - 2, c["w"] - 6, c["h"] - 6), t, S.CX, c["cy"])
        self.poly(top, rgb("rim"))
        inner = rot(ellipse(S.CX, c["cy"] - 2, c["w"] - 10, c["h"] - 9), t, S.CX, c["cy"])
        self.poly(inner, rgb("gunmetal"))
        for k in (-1, 0, 1):
            pip = rot(ellipse(S.CX + 9 * k, c["cy"] + 3.2, 3.2, 2.4, 12), t, S.CX, c["cy"])
            self.poly(pip, rgb("mint"))

    def beam(self):
        c = S.PUCK
        top_l, top_r = self.T([(-22, S.BODY_H - 2), (22, S.BODY_H - 2)])
        bot_y = c["cy"] - c["h"] / 2 + 1
        bot_l, bot_r = (S.CX - S.BEAM["bottom_w"] / 2, bot_y), (S.CX + S.BEAM["bottom_w"] / 2, bot_y)
        lerp = lambda a, b, t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        cols = ["beam_low", "beam_mid", "beam_high"]
        for i in range(3):
            t0, t1 = i / 3, (i + 1) / 3
            q = [lerp(bot_l, top_l, t0), lerp(bot_r, top_r, t0), lerp(bot_r, top_r, t1), lerp(bot_l, top_l, t1)]
            self.poly(q, rgb(cols[i]))

    def fin(self, side, ang):
        pts = rot(S.FIN_POLY, -ang)
        mark = rot(S.FIN_MARK, -ang)
        hx, hy = S.FIN_HINGE
        pts = [(side * (x + hx), y + hy) for x, y in pts]
        mark = [(side * (x + hx), y + hy) for x, y in mark]
        self.poly(self.T(pts), rgb("body"), rgb("outline"), 2)
        self.poly(self.T(mark), rgb("olive"))
        nub = ellipse(side * (hx - 1), hy, 7, 7, 16)
        self.poly(self.T(nub), rgb("outline"))

    def mast(self):
        m = S.MAST; tipc = self.p["tip"]
        stem = [(-m["w"] / 2, 1), (m["w"] / 2, 1), (m["w"] / 2, -m["h"]), (-m["w"] / 2, -m["h"])]
        self.poly(self.T(stem), rgb("rim"), rgb("outline"), 1)
        tip = rrect(0, -m["h"] - m["tip"] / 2 + 1, m["w"] + 3, m["tip"], 2.5)
        self.poly(self.T(tip), rgb(tipc), rgb("outline"), 1)

    def body(self):
        fill = rgb(self.p["fill"])
        self.poly(self.T(S.BODY_POLY), fill)
        # scanlines, clipped to the body silhouette
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        sc = S.SCAN; period = sc["gap"] * sc["count"]
        for k in range(-1, sc["count"] + 1):
            y = sc["y0"] + ((k * sc["gap"] + self.p["scan"]) % period)
            band = [(-60, y), (60, y), (60, y + sc["thick"]), (-60, y + sc["thick"])]
            ld.polygon(self.S(self.T(band)), fill=rgb("scan"))
        mask = Image.new("L", self.img.size, 0)
        ImageDraw.Draw(mask).polygon(self.S(self.T(S.BODY_POLY)), fill=255)
        band_region = Image.new("L", self.img.size, 0)   # keep bands between visor and insignia
        ImageDraw.Draw(band_region).polygon(self.S(self.T([(-60, sc["y0"] - 1), (60, sc["y0"] - 1), (60, sc["y0"] + period - 3), (-60, sc["y0"] + period - 3)])), fill=255)
        from PIL import ImageChops
        m = ImageChops.multiply(mask, band_region)
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), m))
        self.img.alpha_composite(layer)
        # outline on top of the bands
        self.d.polygon(self.S(self.T(S.BODY_POLY)), outline=rgb("outline"), width=S.OUTLINE_W * S.SS)
        # insignia: chevron over bar, symmetric
        iy, iw = S.INSIGNIA["y"], S.INSIGNIA["w"]
        ih = S.INSIGNIA["h"]
        chev = [(-iw / 2, iy), (-iw / 2 + 3.5, iy), (0, iy + 3.5), (iw / 2 - 3.5, iy), (iw / 2, iy), (0, iy + 6)]
        bar = [(-iw / 2 + 1, iy + ih - 2), (iw / 2 - 1, iy + ih - 2), (iw / 2 - 1, iy + ih), (-iw / 2 + 1, iy + ih)]
        self.poly(self.T(chev), rgb("olive")); self.poly(self.T(bar), rgb("olive"))

    def visor_and_eye(self):
        v, e, p = S.VISOR, S.EYE, self.p
        self.poly(self.T(rrect(0, v["y"] + v["h"] / 2, v["w"], v["h"], v["r"])), rgb("outline"))
        max_dx = (v["w"] - e["w"]) / 2 - 2; max_dy = (v["h"] - e["h"]) / 2
        ex = max(-max_dx, min(max_dx, p["eye_dx"])); ey = max(-max_dy, min(max_dy, p["eye_dy"]))
        cx, cy = ex, v["y"] + v["h"] / 2 + ey
        kind = p["eye"]
        if kind == "arc_up":
            self.line(self.T(arc(cx, cy + 2, e["w"] - 2, -5)), rgb("mint"), 3)
        elif kind == "arc_down":
            self.line(self.T(arc(cx, cy - 2, e["w"] - 2, 5)), rgb("mint"), 3)
        else:
            h = {"pill": e["h"], "blink": 2, "narrow": 4}[kind] if p["eye_h"] is None else p["eye_h"]
            self.poly(self.T(rrect(cx, cy, e["w"], h, h / 2)), rgb("mint"))
            if h >= 6:
                self.poly(self.T(rrect(cx + 1, cy + h / 2 - 1.2, e["w"] - 6, 2, 1)), rgb("mint_shadow"))
                self.poly(self.T(rrect(cx + 5, cy - .5, e["core"], e["core"], 1.2)), rgb("core"))

    def render(self):
        self.beam(); self.puck()
        self.fin(-1, self.p["fin_l"]); self.fin(1, self.p["fin_r"])
        self.mast(); self.body(); self.visor_and_eye()
        img = self.img.convert("RGBa").reduce(S.SS).convert("RGBA")   # premultiplied box filter: clean edges, no ringing
        # zero RGB under alpha 0 (host rule: no hidden residue)
        px = img.load()
        for y in range(S.CELL_H):
            for x in range(S.CELL_W):
                if px[x, y][3] == 0: px[x, y] = (0, 0, 0, 0)
        return img


def main():
    R = S.rows()
    frames = {}
    for name in S.ROW_ORDER:
        spec = R[name]
        if isinstance(spec, str) and spec.startswith("mirror:"):
            frames[name] = [ImageOps.mirror(f) for f in frames[spec.split(":")[1]]]
        else:
            frames[name] = [Frame(p).render() for p in spec]
        assert len(frames[name]) == S.FRAME_COUNTS[name], name
        d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
        for i, f in enumerate(frames[name]):
            f.save(os.path.join(d, f"{i:02d}.png"))
    print(f"rendered {sum(len(v) for v in frames.values())} frames to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
