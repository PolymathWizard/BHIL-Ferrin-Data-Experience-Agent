"""FERRIN sprite specification: the single source of truth for palette, geometry and poses.

Edit art here, never by hand-editing PNGs. Every other tool reads this module.
Coordinates are in cell pixels (192 x 208). The drawing tool renders at SS x supersampling.
"""

# ---------------------------------------------------------------- host contract (fixed)
CELL_W, CELL_H = 192, 208
COLS, ROWS = 8, 11
ATLAS_W, ATLAS_H = CELL_W * COLS, CELL_H * ROWS   # 1536 x 2288
SPRITE_VERSION = 2

ROW_ORDER = ["idle", "running-right", "running-left", "waving", "jumping",
             "failed", "waiting", "running", "review", "look-a", "look-b"]
FRAME_COUNTS = {"idle": 6, "running-right": 8, "running-left": 8, "waving": 4, "jumping": 5,
                "failed": 8, "waiting": 6, "running": 6, "review": 6, "look-a": 8, "look-b": 8}

# ---------------------------------------------------------------- palette
PALETTE = {
    "body": "#FFB23F",        # Holo Amber
    "scan": "#C7771E",        # Deep Amber
    "core": "#FFF3D6",        # Warm Core White
    "mint": "#34F5B4",        # Signal Mint
    "mint_shadow": "#1FA57A", # Mint Shadow
    "outline": "#3A2410",     # Outline Umber
    "gunmetal": "#2A3036",    # Emitter Gunmetal
    "rim": "#4A545E",         # Emitter Rim
    "olive": "#5B6B3A",       # Olive Drab
    "coral": "#FF5A4E",       # Alert Coral (failed only)
    "dimmed": "#B98A45",      # Dimmed Amber (failed flicker)
    "beam_low": "#FFE2B0",
    "beam_mid": "#F7B35C",
    "beam_high": "#E8962E",
}

# ---------------------------------------------------------------- geometry
SS = 4                      # supersampling factor
CX = 96                     # horizontal center
PAD = 21                    # 10% of 208, rounded up: keep every opaque pixel inside
PUCK = {"cy": 179, "w": 62, "h": 13, "rim": 2}
BODY_TOP = 62               # body top at rest
BODY_H = 90
# faceted lantern outline, relative to (CX, BODY_TOP): widest at mid-height, tapering both ways
BODY_POLY = [(-27, 0), (27, 0), (40, 17), (43, 47), (34, 76), (24, 90),
             (-24, 90), (-34, 76), (-43, 47), (-40, 17)]
OUTLINE_W = 3
SCAN = {"thick": 3, "gap": 12, "y0": 40, "count": 3}   # bands live between visor and insignia, wrap every 36 px
VISOR = {"y": 21, "w": 56, "h": 16, "r": 8}
EYE = {"w": 20, "h": 9, "core": 4}
MAST = {"w": 5, "h": 11, "tip": 7}
FIN_HINGE = (43, 47)        # relative to body origin (right side); left is mirrored
FIN_POLY = [(0, -11), (19, -18), (26, -9), (26, 9), (19, 18), (0, 11)]   # chevron plate 26 x 36, hinge at (0,0)
FIN_MARK = [(7, -7), (11, -7), (17, 0), (11, 7), (7, 7), (12, 0)]        # olive chevron on the plate
INSIGNIA = {"y": 76, "w": 14, "h": 9}
BEAM = {"bottom_w": 34, "top_w": 56}


def pose(**kw):
    """A frame pose. Defaults describe FERRIN at rest."""
    p = dict(bob=0, lean=0.0, squash=1.0, fin_l=0.0, fin_r=0.0, eye="pill", eye_dx=0.0, eye_dy=0.0,
             eye_h=None, tip="mint", fill="body", scan=0, puck_tilt=0.0)
    p.update(kw)
    return p


def rows():
    """Per-row list of poses, in host order."""
    R = {}
    R["idle"] = [pose(bob=b, scan=2 * i, fin_l=[0, 1, 2, 2, 1, 0][i], fin_r=[0, 1, 2, 2, 1, 0][i],
                      eye="blink" if i == 4 else "pill")
                 for i, b in enumerate([0, -1, -2, -2, -1, 0])]
    R["running-right"] = [pose(bob=[0, -2][i % 2], lean=8, puck_tilt=3, eye_dx=11,
                               fin_l=-22 + (6 if i % 2 else -6), fin_r=-12 + (-6 if i % 2 else 6), scan=2 * i)
                          for i in range(8)]
    R["running-left"] = "mirror:running-right"
    R["waving"] = [pose(fin_r=a, eye="arc_up", fin_l=l, bob=b) for a, l, b in ((15, 0, 0), (45, 2, -1), (70, 3, -1), (45, 2, 0))]
    R["jumping"] = [pose(bob=b, squash=s) for b, s in ((0, .9), (-12, 1.0), (-20, 1.02), (-9, 1.0), (0, .96))]
    R["failed"] = [pose(fill="body" if i % 2 == 0 else "dimmed", fin_l=-25, fin_r=-25, eye="arc_down", tip="coral",
                        bob=3 if i >= 6 else 0, squash=.95 if i >= 6 else 1.0, lean=-3 if i >= 6 else 0)
                   for i in range(8)]
    R["waiting"] = [pose(lean=-6, fin_l=30, eye="pill", eye_h=[9, 9, 9, 5, 2, 9][i], bob=[0, -1, -1, 0, 0, 0][i])
                    for i in range(6)]
    R["running"] = [pose(eye_dx=dx, tip="mint" if i % 2 == 0 else "mint_shadow",
                         fin_l=8 if i % 2 == 0 else 0, fin_r=0 if i % 2 == 0 else 8)
                    for i, dx in enumerate([-14, -7, 0, 7, 14, 7])]
    R["review"] = [pose(bob=1, lean=-4, eye="narrow", fin_r=78 + [0, 2, 4, 4, 2, 0][i], eye_dx=4)
                   for i in range(6)]
    looks = []
    import math
    for i in range(16):
        a = math.radians(i * 22.5)            # clockwise from straight up
        dx, dy = math.sin(a), -math.cos(a)
        looks.append(pose(eye_dx=18 * dx, eye_dy=3 * dy, lean=6 * dx, bob=round(-2 * max(0, -dy))))
    R["look-a"], R["look-b"] = looks[:8], looks[8:]
    return R
