---
name: deslop-web
description: Build or audit web pages so they look authored, not AI-generated. Use when generating, redesigning, reviewing, or de-slopping any website, landing page, HTML artifact, or UI in code, or when asked whether a page looks AI-made, generic, templated, or vibecoded.
---

# deslop-web

Keeps web pages from looking AI-generated, in two modes:
- **Generate:** stop the tells from being written in the first place.
- **Audit:** find, rank and fix the tells in an existing page.

**Core principle:** a tell is an *unchosen default*, not a banned value. A purple you chose and wrote down passes. A purple the model reached for fails. Ban lists alone don't work, because models drift to the next default (purple → cream → teal-on-cream). This skill pairs a written direction step with a deterministic scanner and a fresh-eyes review.

## Files

| File | Use |
|---|---|
| `references/RULES.md` | The full rulebook: 17 process rules plus 110 checks, with detection specs, severities and fixes. **Read it before any audit or full-page build.** |
| `scripts/deslop_scan.py` | Deterministic scanner. Python stdlib for static checks; Playwright + Chrome for rendered checks |
| `templates/DESIGN.template.md` | Google DESIGN.md format: tokens plus rationale, Waivers, change log |
| `templates/PRODUCT.template.md` | Audience, the page's job, voice, proof inventory |
| `templates/deslop.config.json` | Scanner config: waivers, palette, fonts, presets, custom brand patterns |
| `presets/*.json` | Sector word lists (education, saas, nonprofit) |

If any file is missing (e.g. only this SKILL.md is installed), clone the repo: `git clone https://github.com/jdcdtci/deslop-website /tmp/deslop-web`, and use its files. Do not improvise the rules from memory.

## Severity

- **P0:** blocks ship.
- **P1:** fix it, or record a waiver with a reason.
- **P2:** counted and reported.

**Detection types:**
- **D:** static, deterministic.
- **R:** needs a rendered page.
- **J:** judgment, done by a fresh-context reviewer.

## Mode 1: Generate

1. **Brand truth (PR-01).** Find `DESIGN.md` at the project root and follow it as a locked system. If there is none and the page is for a real brand, ask for the brand guide. Never theme a real brand from memory. If the user has no brand, write DESIGN.md from the template first.
2. **Brief (PR-02).** Write or read `PRODUCT.md`: audience, the page's single job, and the proof inventory (every number with source and date). Never invent a fact, name, number, quote, logo or testimonial (PR-11). Use a labelled `[NEEDS: …]` placeholder instead.
3. **Anti-attractor (PR-03).** List your reflex choice for each of: font, palette, background, hero layout, section order, radius, shadow, motion. For each one, reject it or justify it in one line against the brief. Show this list to the user in one compact block.
4. **Token plan (PR-04).** 4–6 colors with roles, a display + body pair, a type scale ratio, a spacing base, at most 2 radii, one shadow approach, and one signature move tied to the subject.
5. **Content-first outline (PR-06).** Every section answers a real audience question. The hero states a thesis or proof, not a welcome.
6. **Hero first (PR-07).** Build the hero, render it, check it, and only then build the rest.
7. **Build the page.** Avoid every P0/P1 tell in RULES.md §1–8 as you write. Meet the §9 quality floor (WCAG 2.2 AA, Core Web Vitals).
8. **Verify (PR-08, PR-09).** Run the scanner with `--render`. Fix every P0. Fix or waive every P1. Then do the J-rule review (below).
9. **Deliver** with the scan summary. Never deliver while the verdict is HOLD unless the user accepts the open items.

**Narrow edit (PR-14):** when asked to change one component, fix only that surface, add no new tells, and do not run a site audit unless asked.

## Mode 2: Audit

1. **Gather.** The URL or files, plus DESIGN.md and PRODUCT.md if they exist. Fail closed (PR-13): if the page can't be rendered, the verdict is HOLD (incomplete).
2. **Scan:**
   ```bash
   python3 scripts/deslop_scan.py <src-dir-or-file> --render <url-or-html> --config deslop.config.json --out .deslop
   ```
   Exit codes: 0 = SHIP-ready; 1 = HOLD on findings; 2 = HOLD because a check could not run. Screenshots land at `.deslop/shot-{1440,1280,768,375}.png`, and full results in `.deslop/scan.json`.
3. **Look.** Open the 1440 and 375 screenshots, every time.
4. **J-rule review.** Use a fresh-context subagent if one is available. Otherwise, re-read the screenshots cold, as if you had never seen the page. Check: L-02 template page order, L-08, L-09, L-10, L-11, K-10, K-13, I-01, I-05, C-14, W-08, W-10, W-12, X-02, the E-rules (if the institutional module is on), and PR-16 (cosmetic swaps that don't fix the underlying idea).
5. **Report** to `.deslop/audit-NNN-YYYY-MM-DD.md` (NNN increments). Lead with the verdict and scores, then findings grouped by category, each with: number, rule ID, severity, location, screenshot crop or selector, and fix. Describe tells as template defaults. **Never say the page was made by AI** (PR-15).
6. **Approval gate (PR-12).** Ask which finding numbers to fix. Auto-fix only mechanical quality items: focus ring, missing `lang`, body text under 16px, image dimensions, alt prompts. Everything else waits for approval.
7. **Fix and re-scan.** On redesigns, every link, form field, handler and heading must survive (PR-10). Keep the chosen art direction (PR-17). Swapping a word or hex value without fixing the idea behind it is not a fix (PR-16).

## Scoring (RULES.md §11)

- **Visual tells:** distinct P0/P1 visual rules fired. 0–1 Low, 2–3 Medium, 4+ High.
- **Clusters:** 3 or more tells in one category escalate that category's P1s to P0.
- **Copy score:** weighted per 1,000 words. Under 35 is clean, 35–64 needs review, 65+ needs a rewrite.
- **SHIP** requires all of: 0 P0, all P1s handled, visual Low, copy under 35, quality floor passing, render complete, and the J review done.

## Waivers

A deliberate choice that matches a tell is recorded twice:
1. In `DESIGN.md` → Waivers, with the rule ID, the choice and the reason or source.
2. In `deslop.config.json` → `waivers`.

The scanner flags a waiver with no reason as S-03.

## Rule index (full specs in references/RULES.md)

- **Process:** PR-01 brand truth · PR-02 brief · PR-03 anti-attractor · PR-04 token plan · PR-05 justify, don't ban · PR-06 content-first · PR-07 hero first · PR-08 render at 4 widths · PR-09 three-layer check · PR-10 preserve on redesign · PR-11 never invent facts · PR-12 approval gate · PR-13 fail closed · PR-14 narrow stays narrow · PR-15 no AI verdicts · PR-16 fix causes · PR-17 keep the chosen direction
- **Color:** C-01 purple accent P0 · C-02 AI gradient P0 · C-03 gradient text P0 · C-04 glow P1 · C-05 cream bg P1 · C-06 terracotta on cream P1 · C-07 black + acid accent P1 · C-08 teal/sage on cream P1 · C-09 framework defaults P1 · C-10 gray on color P1 · C-11 untinted extremes P2 · C-12 accent overuse P2 · C-13 grid/stripe bg P2 · C-14 unchosen dark P1
- **Type:** T-01 default faces only P0 · T-02 templated display P1 · T-03 hero word set apart P1 · T-04 eyebrows P1 · T-05 template chrome P2 · T-06 default size ladder P2 · T-07 flat hierarchy P2 · T-08 extreme display P2 · T-09 font not loaded P1 · T-10 unreadable body P1 · T-11 wide hero copy P2 · T-12 heavy body P2 · T-13 wide tracking P2
- **Layout:** L-01 centered hero + pill P0 · L-02 template page order P0 · L-03 three icon cards P1 · L-04 stat banner P1 · L-05 decorative 01/02/03 P1 · L-06 everything centered P1 · L-07 monotonous spacing P2 · L-08 status-card hero P1 · L-09 cardocalypse P1 · L-10 filler FAQ P2 · L-11 broadsheet cosplay P2 · L-12 broken mobile P1
- **Components:** K-01 side-tab border P0 · K-02 one radius everywhere P1 · K-03 stacked elevation P1 · K-04 every button primary P1 · K-05 arrow on every CTA P2 · K-06 stock effects P1 · K-07 gradient borders P2 · K-08 pill overload P2 · K-09 fake window dots P2 · K-10 decorative data P1 · K-11 uniform hover P2 · K-12 glass P2 · K-13 modal default P2
- **Imagery:** I-01 AI people/places for a real org P0 · I-02 emoji as design P1 · I-03 icon tics P1 · I-04 placeholder avatars P1 · I-05 stock energy P1 · I-06 blobs P2 · I-07 grain P2
- **Motion:** M-01 hidden at rest P0 · M-02 no reduced-motion P0 · M-03 bounce P1 · M-04 layout animation P1 · M-05 same entrance everywhere P2 · M-06 perpetual decoration P2 · M-07 transition all P2
- **Copy:** W-01 chat residue P0 · W-02 buzzwords P1 · W-03 inflated significance P1 · W-04 negative parallelism P1 · W-05 filler P1 · W-06 vague attribution P1 · W-07 generic CTA P1 · W-08 rule of three P2 · W-09 em dashes P2 · W-10 redundant intro P2 · W-11 Title Case P2 · W-12 bad state copy P1 · W-13 duplicate copy P1 · W-14 emoji headings P2
- **Content:** X-01 invented social proof P0 · X-02 unsourced numbers P1 · X-03 placeholders P0 · X-04 leaked build strings P1 · X-05 broken links P1
- **Quality:** Q-01 contrast P0 · Q-02 focus P0 · Q-03 alt P0/P1 · Q-04 targets P1 · Q-05 headings P1 · Q-06 color-only P1 · Q-07 zoom P1 · Q-08 lang P1 · Q-09 forms P1 · Q-10 CLS P1 · Q-11 CWV P1 · Q-12 runtime P1 · Q-13 landmarks P2 · Q-14 image formats P2
- **Consistency:** S-01 off-token values P1 · S-02 cross-page drift P1 · S-03 waiver hygiene P1
- **Institutional (optional):** E-01 proof-led hero · E-02 primary path everywhere · E-03 top questions in 2 clicks · E-04 real testimonials · E-05 consent for minors P0
