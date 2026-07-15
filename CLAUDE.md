# ai4saferroads-ph

Open speed-safety map. Flags every drivable street where the posted or design speed is higher than a survivable speed given how the road is used (a Safe System screening), across 50 Philippine cities and Metro Manila. Built from OpenStreetMap speed limits, a safe-speed model, satellite imagery, and crash validation. Answers "will a lower speed limit actually make us safer?" No login, open data.

Single-file MapLibre + PMTiles map at `build/web/index.html` (~1600 lines, EN/FIL i18n toggle). Secondary pages: `sim.html` (60 vs 30 stopping-distance), `methodology.html`. Hero GIF `docs/demo.gif`, share card `build/web/og-card.png`.

## Deploy and verify

- Deploy: `vercel --prod --cwd build/web --yes` on the PERSONAL `xmpuspus` Vercel account (never a work account). `build/web` is the deploy root, so `index.html` serves at `/`. `sim.html` and `methodology.html` 308-redirect to `/sim` and `/methodology` (fingerprint prod with `curl -L`).
- Claims oracle, must pass before shipping any number change: `python3 tests/verify_claims.py` (99/99). It recomputes every headline figure from committed artifacts and fails on drift.
- Local server for QA and renders (Range-capable, PMTiles needs 206 responses): from `build/`, `python3 web/serve.py 8799`. The screenshot harness `build/ux_audit_shots.mjs` and the OG/GIF scripts default to `localhost:8799`, NOT prod, so they see local edits.
- Visual QA gate: screenshot both viewports (1920x1080 desktop, 390x844 mobile), EN and FIL, and Read every shot back. After a deploy, fingerprint the live surface (grep the HTML for a marker, screenshot the live page).
- After deploy, leave `main == origin/main`.

## Colour palette (scarlet danger, no coral or amber)

Xavier rejected the old coral accent (#E0574A) as reading like Anthropic house colour. Current palette, do NOT reintroduce coral or orange:

- `--accent` scarlet `#EE3B3B`, `--safe` teal `#54A89B`, `--focus` blue `#5B8DB8`, accent tint `rgba(238,59,59,*)`.
- Danger road ramp (SSS_COLOR, `.ramp`, `.tk-ramp.score`, `col()`, hexbin): violet `#3B0F70` to `#7E1E82` to `#B71E68` to `#DE2A4E` to red `#FF3A46`.
- Speed ramp (Now/Safe view): teal to cool neutrals (`#7C9D9E`, `#B07487`) to red. Never gold-into-red, that blends to orange at 60 km/h.

## A colour or copy sweep must cover every surface

Not just `index.html`. Also `sim.html`, `methodology.html`, the `rgba()` forms of a token (not only `#hex`), the OG card (`build/og_stat_shot.mjs`, re-render), the hero GIF (re-record, it captures the live map), and committed screenshots the README embeds (`screenshots/sim_v2.png`, regenerate by screenshotting `sim.html#shot`). grep the repo to zero before declaring done.

## Regenerating artifacts

- Hero GIF: `REC_URL=http://localhost:8799/web/index.html node build/record_demo_15s.mjs`, then `DESIGNED=16.9 bash build/encode_demo.sh <webm> <TRIM_S> <MARK_FLIP> <MARK_END>` (the recorder prints those three marks). `docs/demo.mp4` is the video (gitignored, upload this to LinkedIn); `docs/demo.gif` is committed.
- OG card: `OG_DSR=1 OG_OUT=web/og-card.png node build/og_stat_shot.mjs` from `build/` (1200x630). On a real swap, cache-bust the `og:image` URL with `?v=<date>` (LinkedIn caches OG images hard).
- Frame-extract and Read GIF beats before shipping; the OG card and GIF must match the live map colours.

## LinkedIn posts

Xavier's voice is casual first-person, not a polished essay ("too clean" is a rejection). Use "basically", "I mean", "turns out", "so yeah", short fragments, honest about limits, a reflective PH close. Put links in the FIRST comment, not the body (LinkedIn throttles body links). Comments cap at 1,250 characters, split into numbered comments if longer. Draft lives in `docs/linkedin-post-adb.md`, ready-to-paste comments in `docs/linkedin-comment-*.txt`. Deslop bar: no em-dash, no colon-in-prose, no "also", no "corridor" or "binds".

## Git

Commit-message lines must NOT start with a dash. The git-safety hook reads a leading `-` as a force flag and blocks the whole command. Stage explicit paths, never `git add -A`.
