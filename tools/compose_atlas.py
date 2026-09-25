"""Compose build/frames into spritesheet.webp (lossless, RGBA, 1536 x 2288) and build/spritesheet.png."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ferrin_spec as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    atlas = Image.new("RGBA", (S.ATLAS_W, S.ATLAS_H), (0, 0, 0, 0))
    for r, name in enumerate(S.ROW_ORDER):
        for i in range(S.FRAME_COUNTS[name]):
            f = Image.open(os.path.join(ROOT, "build", "frames", name, f"{i:02d}.png")).convert("RGBA")
            atlas.paste(f, (i * S.CELL_W, r * S.CELL_H))
    # zero RGB wherever alpha is 0 (no hidden residue)
    a = atlas.getchannel("A"); black = Image.new("RGBA", atlas.size, (0, 0, 0, 0))
    atlas = Image.composite(atlas, black, a.point(lambda v: 255 if v else 0))
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    atlas.save(os.path.join(ROOT, "build", "spritesheet.png"))
    atlas.save(os.path.join(ROOT, "spritesheet.webp"), "WEBP", lossless=True, quality=100, method=6, exact=True)
    print("wrote spritesheet.webp", atlas.size)


if __name__ == "__main__":
    main()
