"""Build docs/contact-sheet.png, docs/ferrin-wave.gif and docs/previews/<row>.gif from spritesheet.webp."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import ferrin_spec as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DARK, LIGHT = (27, 18, 10, 255), (244, 236, 222, 255)
LABELS = {"idle": "idle: Standing Watch", "running-right": "running-right: Underway", "running-left": "running-left: Underway",
          "waving": "waving: Hail", "jumping": "jumping: Short Burn", "failed": "failed: Casualty Report",
          "waiting": "waiting: Awaiting Orders", "running": "running: Plotting Solution", "review": "review: Debrief",
          "look-a": "look 0-7: Tracking", "look-b": "look 8-15: Tracking"}


def font(size):
    try: return ImageFont.load_default(size=size)
    except TypeError: return ImageFont.load_default()


def checker(w, h, s=12):
    im = Image.new("RGBA", (w, h), (58, 44, 32, 255)); d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2: d.rectangle([x, y, x + s - 1, y + s - 1], fill=(72, 56, 42, 255))
    return im


def frames(atlas, name):
    r = S.ROW_ORDER.index(name)
    return [atlas.crop((i * S.CELL_W, r * S.CELL_H, (i + 1) * S.CELL_W, (r + 1) * S.CELL_H)) for i in range(S.FRAME_COUNTS[name])]


def main():
    atlas = Image.open(os.path.join(ROOT, "spritesheet.webp")).convert("RGBA")
    lw, sc = 230, .75
    cw, ch = int(S.CELL_W * sc), int(S.CELL_H * sc)
    W = lw + cw * S.COLS + 20; H = 70 + ch * S.ROWS + 20 + ch + 30
    sheet = Image.new("RGBA", (W, H), DARK); d = ImageDraw.Draw(sheet)
    d.text((20, 20), "FERRIN sprite atlas: 1536 x 2288, 8 x 11 cells of 192 x 208", fill=(255, 178, 63, 255), font=font(24))
    for r, name in enumerate(S.ROW_ORDER):
        y = 70 + r * ch
        d.text((20, y + ch // 2 - 10), LABELS[name], fill=(255, 243, 214, 255), font=font(17))
        for i, f in enumerate(frames(atlas, name)):
            bg = checker(cw, ch); bg.alpha_composite(f.resize((cw, ch), Image.LANCZOS))
            sheet.paste(bg, (lw + i * cw, y))
    y = 70 + S.ROWS * ch + 20
    d.text((20, y + ch // 2 - 10), "idle[0] still portrait on dark, light, checker", fill=(255, 243, 214, 255), font=font(17))
    still = frames(atlas, "idle")[0].resize((cw, ch), Image.LANCZOS)
    for k, bg in enumerate([Image.new("RGBA", (cw, ch), DARK[:3] + (255,)), Image.new("RGBA", (cw, ch), LIGHT), checker(cw, ch)]):
        bg.alpha_composite(still); sheet.paste(bg, (lw + k * cw, y))
    os.makedirs(os.path.join(DOCS, "previews"), exist_ok=True)
    sheet.convert("RGB").save(os.path.join(DOCS, "contact-sheet.png"), optimize=True)

    def gif(fr, path, ms=125):
        out = []
        for f in fr:
            bg = Image.new("RGBA", f.size, DARK); bg.alpha_composite(f); out.append(bg.convert("P", palette=Image.ADAPTIVE, colors=128))
        out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0, optimize=True, disposal=2)

    for name in S.ROW_ORDER[:9]:
        gif(frames(atlas, name), os.path.join(DOCS, "previews", f"{name}.gif"))
    gif(frames(atlas, "look-a") + frames(atlas, "look-b"), os.path.join(DOCS, "previews", "look.gif"), 110)
    gif(frames(atlas, "waving") * 3 + frames(atlas, "idle"), os.path.join(DOCS, "ferrin-wave.gif"))
    print("wrote docs/contact-sheet.png, docs/ferrin-wave.gif, docs/previews/*.gif")


if __name__ == "__main__":
    main()
