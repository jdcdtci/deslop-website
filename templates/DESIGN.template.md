---
version: alpha
name: <Brand name>
description: Visual system for <site>. Source of truth: <brand book, version, date>.
colors:
  # Brand masters (cite page). 4-6 named colors with roles. No unsourced values.
  primary: "#______"
  on-primary: "#______"
  accent: "#______"
  background: "#______"     # Justify in prose if it falls in the cream band (OKLCH L .94-.985, H 60-95)
  on-background: "#______"
  muted: "#______"          # must pass 4.5:1 on background for small text
typography:
  display:
    fontFamily: <font>       # justify against the brief (anti-attractor)
    fontWeight: 400
    fontSize: 0px
    lineHeight: 1.1
  body:
    fontFamily: <font>
    fontWeight: 400
    fontSize: 18px           # >= 16px
    lineHeight: 1.55
  # Scale: base __px, ratio __ (list the steps)
spacing:
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  section: 96px
rounded:
  sm: 4px                    # max two radii
  md: 8px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
---

# <Brand>: DESIGN.md

## Overview
Who this is for, the feel in three plain words, and the **signature move**: one distinctive thing tied to the subject.

## Anti-attractor log
| Reflex default | Decision | Reason |
|---|---|---|
| Font | | |
| Palette / background | | |
| Hero layout | | |
| Section order | | |
| Radius / shadow | | |
| Motion | | |

## Color
Roles, proportions, and a contrast pairing table (ratio plus where each pairing is allowed).

## Typography
The pairing, the scale, the limits (max fonts, minimum sizes, case rules).

## Layout and Spacing
Grid, rhythm, breakpoints checked (375 / 768 / 1280 / 1440), page structure.

## Components
Buttons (one primary per section), cards, forms, focus, icons, elevation (one method).

## Imagery
What real photography to use, art direction, consent, specs. No AI images of real people or places.

## Motion
At most one orchestrated moment. Transform and opacity only. `prefers-reduced-motion` honored.

## Voice
Naming rules, banned words, CTA style, proof rules (every number traces to PRODUCT.md).

## Accessibility
WCAG 2.2 AA, target sizes, Core Web Vitals targets.

## Waivers
| Rule | Choice | Reason / source |
|---|---|---|

## Known conflicts and open items

## Change log
- YYYY-MM-DD: v1
