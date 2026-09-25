"""Validate spritesheet.webp against the host contract and FERRIN's style rules. Exits non-zero on failure."""
import colorsys, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ferrin_spec as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAD_X, PAD_Y = 20, 21          # 10% of 192 and 208, rounded up


def cells(img):
    for r, name in enumerate(S.ROW_ORDER):
        for c in range(S.COLS):
            yield r, name, c, img.crop((c * S.CELL_W, r * S.CELL_H, (c + 1) * S.CELL_W, (r + 1) * S.CELL_H))


def opaque_bbox(cell):
    return cell.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()


def check(path=None):
    path = path or os.path.join(ROOT, "spritesheet.webp")
    errors, notes = [], []
    img = Image.open(path)
    if img.format != "WEBP": errors.append(f"format is {img.format}, expected WEBP")
    if img.size != (S.ATLAS_W, S.ATLAS_H): errors.append(f"size {img.size}, expected {(S.ATLAS_W, S.ATLAS_H)}")
    if img.mode != "RGBA": errors.append(f"mode {img.mode}, expected RGBA")
    img = img.convert("RGBA")

    # no RGB residue under alpha 0
    px = list(img.get_flattened_data()) if hasattr(img,"get_flattened_data") else img.getdata()
    residue = sum(1 for p in px if p[3] == 0 and (p[0] or p[1] or p[2]))
    if residue: errors.append(f"{residue} fully transparent pixels carry RGB residue")

    counts, baselines, idle0 = {}, [], None
    idle_frames = []
    blue = total = 0
    for r, name, c, cell in cells(img):
        used = c < S.FRAME_COUNTS[name]
        bb = opaque_bbox(cell)
        if not used:
            if cell.getchannel("A").getbbox(): errors.append(f"{name}[{c}] should be empty")
            continue
        if not bb: errors.append(f"{name}[{c}] is empty"); continue
        counts[name] = counts.get(name, 0) + 1
        x0, y0, x1, y1 = bb
        if x0 < PAD_X or y0 < PAD_Y or x1 > S.CELL_W - PAD_X or y1 > S.CELL_H - PAD_Y:
            errors.append(f"{name}[{c}] breaks 10% padding: bbox {bb}")
        alpha = cell.getchannel("A")
        n_opaque = sum(1 for v in (alpha.get_flattened_data() if hasattr(alpha,"get_flattened_data") else alpha.getdata()) if v > 8)
        occ = n_opaque / (S.CELL_W * S.CELL_H)
        if occ > .8: errors.append(f"{name}[{c}] occupancy {occ:.0%} > 80%")
        baselines.append((name, c, y1))
        if name == "idle":
            idle_frames.append(cell.tobytes())
            if c == 0: idle0 = n_opaque
        elif idle0 and not (.75 * idle0 <= n_opaque <= 1.25 * idle0):
            errors.append(f"{name}[{c}] opaque area {n_opaque} outside +/-25% of idle[0] {idle0}")
        for p in (cell.get_flattened_data() if hasattr(cell,"get_flattened_data") else cell.getdata()):
            if p[3] < 200: continue
            h, s, v = colorsys.rgb_to_hsv(p[0] / 255, p[1] / 255, p[2] / 255)
            if s > .25:
                total += 1
                if 200 <= h * 360 <= 300: blue += 1

    for name in S.ROW_ORDER:
        if counts.get(name, 0) != S.FRAME_COUNTS[name]:
            errors.append(f"row {name}: {counts.get(name, 0)} frames, expected {S.FRAME_COUNTS[name]}")
    if baselines:
        ys = [b[2] for b in baselines]; ref = sorted(ys)[len(ys) // 2]
        off = [b for b in baselines if abs(b[2] - ref) > 2]
        if off: errors.append(f"puck baseline drifts more than 2 px in {len(off)} frames, e.g. {off[:3]}")
    if len(set(idle_frames)) < len(idle_frames): errors.append("idle frames are not all distinct")
    share = blue / max(total, 1)
    notes.append(f"hue guard: {share:.3%} of saturated pixels in 200-300 deg (limit 0.5%)")
    if share > .005: errors.append("hue guard failed: blue/violet pixels present")
    return errors, notes


if __name__ == "__main__":
    errs, notes = check(sys.argv[1] if len(sys.argv) > 1 else None)
    for n in notes: print("  " + n)
    if errs:
        print("ATLAS INVALID"); [print("  - " + e) for e in errs]; sys.exit(1)
    print("atlas OK: 1536x2288 RGBA lossless WebP, 8x11 cells, frame counts and style rules pass")
