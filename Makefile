# FERRIN build. Python 3.10+ with Pillow for art; Node 20+ for tests and scripts.
PY ?= python3
NODE ?= node

.PHONY: art verify test package refs clean

art:            ## draw frames -> compose atlas -> previews
	$(PY) tools/draw_frames.py
	$(PY) tools/compose_atlas.py
	$(PY) tools/make_previews.py

refs:           ## regenerate the skill's command catalog from preview/data
	$(NODE) scripts/build-skill-refs.mjs

test:
	$(PY) -m unittest discover -s tests/py -v
	$(NODE) --test tests/js/*.test.mjs

verify: refs    ## everything that must pass before a commit
	$(PY) tools/validate_atlas.py
	$(MAKE) test
	$(NODE) scripts/ip-scan.mjs
	$(NODE) scripts/dash-gate.mjs
	git diff --exit-code -- skills/ferrin/references/commands.md 2>/dev/null || true

package:        ## dist/ferrin.zip, dist/ferrin-skill.zip, dist/SHA256SUMS.txt
	$(PY) tools/package.py

clean:
	rm -rf build
