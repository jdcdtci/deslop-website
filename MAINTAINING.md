# Maintaining deslop-web

The rulebook goes stale on its own. Every published ban list pushes models toward the next default. This file is the monthly update procedure.

## Sources to check

| Source | Feed | What to look for |
|---|---|---|
| Anthropic frontend-design | https://github.com/anthropics/skills/commits/main/skills/frontend-design/SKILL.md.atom | Named clusters, process changes |
| Impeccable | https://github.com/pbakaus/impeccable/releases.atom | New detector rule IDs |
| Hallmark | https://github.com/Nutlope/hallmark/releases.atom | sloplint tells, gates |
| avoid-ai-design | https://github.com/funboy322/avoid-ai-design/releases.atom | SD-series tells |
| Gesso anti-slop | https://github.com/Gesso-Build/skills/releases.atom | New guards and thresholds |
| taste-skill | https://github.com/Leonxlnx/taste-skill (CHANGELOG.md) | Font and hex ban lists |
| design-slop-cop | https://github.com/AdrianKrebs/design-slop-cop/commits/main.atom | Pattern list, Show HN stats |
| slop-detect | https://github.com/ravidsrk/slop-detect/releases.atom | Calibration, copy axis |
| anti-slop | https://github.com/miqdadbadjuber/anti-slop | R-series rules |
| aislopfixer | https://www.npmjs.com/package/@mertsoylu/aislopfixer | Copy and placeholder detectors |
| MengTo no-ai-design-slop | https://github.com/MengTo/Skills | Catalog changes |
| Vercel web-interface-guidelines | https://github.com/vercel-labs/web-interface-guidelines/commits/main.atom | Quality floor |
| Google DESIGN.md | https://github.com/google-labs-code/design.md/releases.atom | Spec changes (still alpha) |
| WCAG / web.dev | https://www.w3.org/WAI/standards-guidelines/wcag/ , https://web.dev/articles/vitals | Threshold changes |
| Discovery | https://github.com/topics/ai-slop , https://github.com/topics/frontend-design , hn.algolia.com searches for "AI slop design" and "vibe coded" | New tools and new tells |

## Monthly procedure

1. **Diff the sources** against the dates in the CHANGELOG. List every new tell, threshold change or rule retirement.
2. **Apply the evidence bar:**
   - **Add** a tell only if 2+ independent sources name it, or 1 source names it with data or a precise detector.
   - **New tells start on the watch list** (RULES.md §12). Promote a tell to P1 once 2+ sources cite it within 60 days. Promote to P0 only with data or broad consensus.
   - **Demote or retire** a tell when complaint data shows people don't mind it, or when it produces false positives on the clean fixture.
3. **Edit** `references/RULES.md`, the rule index in `SKILL.md`, and the detector in `scripts/deslop_scan.py` together. A rule without a detection spec is not done.
4. **Regression test:**
   ```bash
   python3 scripts/deslop_scan.py fixtures/slop.html --render fixtures/slop.html   # must exit 1 with 10+ visual tells
   python3 scripts/deslop_scan.py fixtures/clean.html --render fixtures/clean.html # must exit 0
   python3 scripts/deslop_scan.py fixtures/after.html --render fixtures/after.html # must exit 0
   ```
   If a new rule fires on clean.html, fix the rule, not the fixture. Add each new tell to slop.html.
5. **Version and log:** bump the version in RULES.md (patch = thresholds, minor = rules added or removed, major = process change) and add a CHANGELOG entry citing sources.
6. **Rule count discipline:** keep the P0 list short (under 30). Prefer clustering and better specs over more rules.
