"""Repository checks (stdlib unittest; the atlas test also needs Pillow)."""
import json, os, re, subprocess, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))


class Manifest(unittest.TestCase):
    def test_pet_json(self):
        p = json.load(open(os.path.join(ROOT, "pet.json")))
        self.assertEqual(p["id"], "ferrin"); self.assertEqual(p["displayName"], "Ferrin")
        self.assertEqual(p["spriteVersionNumber"], 2); self.assertEqual(p["spritesheetPath"], "spritesheet.webp")
        self.assertTrue(os.path.exists(os.path.join(ROOT, p["spritesheetPath"])))


class Atlas(unittest.TestCase):
    def test_contract_and_style(self):
        try: import validate_atlas
        except ImportError as e: self.skipTest(f"Pillow not installed: {e}")
        errors, _ = validate_atlas.check()
        self.assertEqual(errors, [])


class Branding(unittest.TestCase):
    ALLOWED = {"LICENSE", "ATTRIBUTION.md", "README.md", "CHANGELOG.md", "CLAUDE.md"}

    def files(self):
        try:
            out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
            if out: return out
        except Exception: pass
        res = []
        for d, dirs, fs in os.walk(ROOT):
            dirs[:] = [x for x in dirs if x not in (".git", "build", "node_modules", "__pycache__")]
            res += [os.path.relpath(os.path.join(d, f), ROOT) for f in fs]
        return res

    def test_no_upstream_branding_outside_credits(self):
        text = re.compile(r"\.(md|json|js|mjs|py|html|yml)$")
        for f in self.files():
            if f in self.ALLOWED or not text.search(f) or f.startswith("tests/"): continue
            with open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore") as fh: t = fh.read()
            self.assertNotRegex(t, re.compile(r"\brupet\b", re.I), f)

    def test_pet_package_has_no_upstream_id(self):
        self.assertNotIn("rupet", open(os.path.join(ROOT, "pet.json")).read().lower())


if __name__ == "__main__":
    unittest.main()
