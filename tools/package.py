"""Build dist/ferrin.zip (pet), dist/ferrin-skill.zip (skill + prompts) and dist/SHA256SUMS.txt.
Stdlib only. Fixed timestamps make the archives reproducible."""
import hashlib, os, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
STAMP = (2026, 1, 1, 0, 0, 0)


def add(z, path, arc):
    info = zipfile.ZipInfo(arc, STAMP); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o644 << 16
    with open(os.path.join(ROOT, path), "rb") as f: z.writestr(info, f.read())


def tree(rel):
    out = []
    for d, dirs, files in os.walk(os.path.join(ROOT, rel)):
        dirs.sort()
        for f in sorted(files): out.append(os.path.relpath(os.path.join(d, f), ROOT))
    return out


def main():
    os.makedirs(DIST, exist_ok=True)
    with zipfile.ZipFile(os.path.join(DIST, "ferrin.zip"), "w") as z:
        for p in ("pet.json", "spritesheet.webp", "LICENSE"): add(z, p, "ferrin/" + p)
    with zipfile.ZipFile(os.path.join(DIST, "ferrin-skill.zip"), "w") as z:
        for p in tree("skills/ferrin"): add(z, p, p.replace("skills/", "", 1))
        for p in tree("prompts"): add(z, p, "ferrin/" + p)
        add(z, "LICENSE", "ferrin/LICENSE")
    lines = []
    for n in ("ferrin.zip", "ferrin-skill.zip"):
        h = hashlib.sha256(open(os.path.join(DIST, n), "rb").read()).hexdigest(); lines.append(f"{h}  {n}")
    open(os.path.join(DIST, "SHA256SUMS.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
