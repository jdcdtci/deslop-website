# deslop-web Rulebook v1.0.0 (2026-11-13)

127 rules, consolidated from 25+ tools and guides. Built to be used two ways: while **generating** pages and while **auditing** existing ones.

Every rule is here for one of three reasons:
1. At least two independent sources flag it, OR
2. One source flags it and backs it with data or a precise detector, OR
3. It is a quality floor (accessibility, performance, honesty) that no design can skip.

## Keys

**Detection**
- **D**: static, deterministic (regex / CSS / markup)
- **R**: deterministic, but needs a rendered page and computed styles
- **J**: judgment (LLM fresh-eyes reviewer or human)

**Severity**
- **P0**: blocks ship. CI fails.
- **P1**: fix it, or record a waiver with a reason.
- **P2**: counted and reported. Fix when cheap.

**Waves**
- **W1**: 2023–25 defaults (purple, Inter, glass, centered hero)
- **W2**: 2026 tasteful defaults (cream, editorial serif, eyebrows)
- **W3**: emerging late 2026 (teal/sage on cream, status-card hero, stock effects)
- **Q**: quality defect that predates AI

**Waiver:** any rule can be waived only by a line in DESIGN.md → Waivers with the reason and source. Example: "Deep plum #5B2A6E is the official brand color, per the 2026 brand book p.12." Waivers are mirrored into `deslop.config.json` → `waivers`. A waiver with no reason is itself a P1 finding.

---

## 0. Process rules (how the skill works; these beat any single tell)

| ID | Rule | Mode | Origin |
|---|---|---|---|
| PR-01 | **Brand truth first.** Never theme a real brand from memory. Read DESIGN.md. Missing tokens are marked TBC, and you ask for them instead of inventing them. | G/A | Hallmark brand-truth.md |
| PR-02 | **Brief before pixels.** State the subject, the audience, the page's single job, and the proof inventory (real stats with source and date) before writing code. Store it in PRODUCT.md. | G | Anthropic frontend-design, Impeccable |
| PR-03 | **Anti-attractor step.** List your reflex default for each of font, palette, background, hero layout, section order, radius, shadow and motion. Reject each one, or justify keeping it in writing against the brief. | G | Impeccable 2.0, Uncodixfy, samber |
| PR-04 | **Token plan before code.** 4–6 named colors with roles. A display + body pair. A type scale with a stated ratio. A spacing base unit. At most 2 radii. One shadow approach. One signature move tied to the subject. | G | Anthropic, samber |
| PR-05 | **Justify, don't ban.** A tell value that was chosen and written down passes. An unchosen default fails. Review the justification, not just the value. | G/A | unslop-ui, Anthropic 2026 rewrite |
| PR-06 | **Content-first structure.** Derive the outline from the content. Every section must answer a real audience question. The hero states a thesis or proof. | G | Anthropic 2026 |
| PR-07 | **Hero first.** Build and review the hero alone before building the rest of the page. | G | Hallmark |
| PR-08 | **Render and look.** Screenshot at 375, 768, 1280 and 1440 px minimum. Never judge from source alone. About 20% of rules only fire after a render. | G/A | Hallmark, Impeccable test |
| PR-09 | **Three-layer check.** (1) Deterministic scan of the rendered page. (2) Quality floor. (3) A fresh-context reviewer for the J rules. None of the three is skipped. | G/A | consolidated |
| PR-10 | **Preserve on redesign.** Every link, form field, handler and heading that existed before must exist after, or be listed as intentionally removed. | A | Hallmark --kept |
| PR-11 | **Never invent facts.** Do not add any name, number, date, quote, testimonial, logo or citation that is not in the source or supplied by the user. Use labelled placeholders instead. | G/A | miqdadbadjuber R-17/36/38 |
| PR-12 | **Approval gate in audits.** Write numbered findings to `deslop/audit-NNN-YYYY-MM-DD.md`. Fix only the IDs the user approves. Auto-fix only mechanical Q items (focus ring, body below 16px, missing lang, alt prompts). | A | miqdadbadjuber, gstack |
| PR-13 | **Fail closed.** If any check could not run (no render, no DESIGN.md, a page that won't load), the verdict is HOLD, not SHIP. | G/A | tastecheck |
| PR-14 | **Narrow stays narrow.** A request to edit one component does not turn into a site audit. Fix that surface and add no new tells. | G | MengTo no-ai-design-slop |
| PR-15 | **Template defaults, not an AI verdict.** Report tells by category with counts. Never claim a page was made by AI. | A | Krebs, HN critique, Wikipedia |
| PR-16 | **Fix the cause, not the symptom.** Swapping a flagged word or hex value without fixing the empty idea behind it is not a fix. A reviewer rejects cosmetic swaps. | G/A | Wikipedia Signs of AI writing |
| PR-17 | **Keep the chosen direction.** When the art direction is deliberate and recorded, de-slopping must not flatten it into neutral corporate. | A | MengTo |

---

## 1. Color (14)

| ID | Tell | Wave | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|---|
| C-01 | Vibe purple/indigo accent on CTAs and links | W1 | D/R | Primary button background, link color or h1–h3 color with OKLCH H 250–320 and C > 0.10. Tailwind `indigo/violet/purple-*` on primary. Hex list: #6366f1 #4f46e5 #8b5cf6 #7c3aed #a855f7 #667eea #764ba2 #6d28d9 #818cf8 | P0 | Derive the accent from the subject or brand |
| C-02 | AI gradient on hero or section backgrounds | W1 | D | `linear/radial/conic-gradient` with ≥2 stops, one stop in the purple band and one in the blue (H 200–264), cyan or pink band. Tailwind `from-(purple\|violet\|indigo)-* to-(blue\|cyan\|pink\|fuchsia\|indigo)-*` | P0 | Flat surface, or a real photograph |
| C-03 | Gradient text | W1 | D | `background-clip:text` together with a gradient. Tailwind `bg-clip-text` + `bg-gradient-to-*` | P0 | Solid ink; emphasis through size or weight |
| C-04 | Colored glow | W1 | R | box-shadow or text-shadow with blur ≥ 15px and shadow color C > 0.10 | P1 | Neutral elevation, or none |
| C-05 | Cream "tasteful default" background | W2 | R | Page background in OKLCH L 0.94–0.985, C 0.008–0.045, H 60–95. Hex list: #f4f1ea #f5f1ea #f7f5f1 #fbf8f1 #efeae0 #ece6db #faf7f1 #e8dfcb #faf8f5, plus Tailwind `stone-50`, `amber-50` | P1 | Background from the brand. Justify cream in Waivers |
| C-06 | Terracotta, clay, brass or oxblood accent on cream | W2 | R | C-05 fires, and the accent has H 25–60 and C > 0.08 | P1 | Same as C-05 |
| C-07 | Near-black page with one acid accent | W2 | R | Background L < 0.15, and exactly one accent with C > 0.20 at H 125–150 (acid green) or H 25–40 (vermilion) | P1 | Multi-role palette from the subject |
| C-08 | Teal or sage on cream | W3 | R | C-05 fires, and the accent has H 150–200 | P1 | Same as C-05 |
| C-09 | Framework defaults shipped untouched | W1 | D | shadcn zinc/slate `:root` tokens, `--radius: 0.625rem`, `--font-sans: var(--font-geist-sans)`, Tailwind `blue-600` as primary, `emerald-500` / #10B981 as the only accent or success color | P1 | Custom tokens |
| C-10 | Gray text on a colored background | Q | R | Text with C < 0.02 over a background with C > 0.05 | P1 | Darker shade of the background's hue |
| C-11 | Untinted extremes | Q | D | Pure #000 text on pure #fff background on the same element; all neutrals with C = 0 | P2 | Tint neutrals toward the brand hue (C 0.005–0.02) |
| C-12 | Accent overuse | Q | R | The accent fills more than 3 distinct element roles in one viewport (for example button, heading, icon tile and badge) | P2 | Accent on the primary CTA and key marks only |
| C-13 | Decorative grid or stripe backgrounds | W2/W3 | D | Background-image grid made with `repeating-linear-gradient`, an SVG grid pattern or dot-grid | P2 | Remove, or make it encode something real |
| C-14 | Unchosen dark theme, or dark mode by inversion | W1 | J | Dark theme on a non-tool, non-media site with no reason in the brief; dark tokens that are simple inversions of light ones | P1 | Choose the theme on purpose. Design dark mode separately, with elevation shown by lightness |

## 2. Typography (13)

| ID | Tell | Wave | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|---|
| T-01 | Default face as the whole identity | W1 | R | Computed h1 **and** body both in {Inter, Roboto, Arial, Helvetica, Open Sans, Lato, Montserrat, system-ui stack, Segoe UI} | P0 | A deliberate display + body pair |
| T-02 | Templated display face | W2/W3 | R | h1 family in {Fraunces, Instrument Serif, Space Grotesk, Geist, Syne, Recoleta, Newsreader, Plus Jakarta Sans, Mona Sans, Satoshi, Outfit, Cabinet Grotesk, Inter} | P1 | Choose from the subject's own vernacular. A waiver needs a stated source |
| T-03 | One hero word set apart | W2 | R | A span inside h1 with a different family, font-style or color from the rest of the h1 | P1 | One voice per headline |
| T-04 | Tracked all-caps eyebrows | W2 | R | ≥3 elements directly before headings with `text-transform:uppercase` and letter-spacing ≥ 0.05em | P1 | Only where the label carries real information |
| T-05 | Template chrome | W2 | D | Monospace font on non-code labels; regex `\w+ · \w+ · \w+` meta strings; version or format footers | P2 | Remove |
| T-06 | Default size ladder | W1 | R | Every computed font size falls in {12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72} with no consistent ratio between them | P2 | A modular scale (1.2, 1.25 or 1.333) from a stated base |
| T-07 | Flat hierarchy | Q | R | Fewer than 3 distinct sizes, or a single weight across the whole page | P2 | Separate the size and weight steps |
| T-08 | Extreme display | W2 | R | h1 > 8vw at 1440px, or letter-spacing < −0.04em | P2 | Scale the headline to its content |
| T-09 | Font declared but never loaded | Q | D | A font-family with no matching @font-face or font link | P1 | Load it, or remove it |
| T-10 | Unreadable body text | Q | R | Body < 16px; line-height < 1.3; measure > 75ch; `text-align: justify`; uppercase body text; UI text < 12px | P1 | 16px or more, line-height 1.4–1.6, measure 45–75ch |
| T-11 | Over-wide hero copy | W1 | R | Hero headline or subhead measure > 45ch at desktop width | P2 | 30–45ch |
| T-12 | Inflated body weight | W1 | R | Body text weight ≥ 600 | P2 | 400 for body; keep 600+ for emphasis |
| T-13 | Wide tracking on text | Q | R | letter-spacing ≥ 0.06em on non-label text | P2 | Remove |

## 3. Layout and structure (12)

| ID | Tell | Wave | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|---|
| L-01 | Centered hero with a pill badge | W1 | R | Small rounded (pill) element directly before a centered h1 | P0 | Open with the most characteristic real thing in the subject's world |
| L-02 | Template page order | W1 | J+R | 5 or more of these, in this order: hero → logo strip → 3 features → testimonials → stats or pricing → FAQ → CTA band → 4-column footer | P0 | Content-first outline (PR-06) |
| L-03 | Three equal icon cards | W1 | R | 3 equal-width siblings, each holding an icon tile + title + blurb (also flags any repeated grid of 3–12 such tiles) | P1 | Give the main point more space; use real imagery; vary the composition |
| L-04 | Stat banner | W1 | R+D | A row of big numerals with small labels, matching `\d+[kKmM]?\+`, `\d+(\.\d)?%`, `★` or `x` | P1 | Real, sourced numbers placed in context (X-02) |
| L-05 | Decorative numbering | W2 | D/J | 3 or more standalone 01/02/03 or 1·2·3 markers where the content is not a real sequence | P1 | Number only real sequences |
| L-06 | Everything centered | W1 | R | More than 70% of text elements over 20 characters are centered (at least 5 such elements) | P1 | Left-aligned reading; deliberate asymmetry |
| L-07 | Monotonous spacing | W1 | R | Spacing values in 4px buckets: one bucket holds over 60% of values with 3 or fewer distinct non-zero buckets; or every section has the same padding and heading size | P2 | A rhythm scale with real jumps between groups and sections |
| L-08 | Text left, status card right | W3 | J | Hero split with copy on the left and a floating card or widget mockup on the right, standing in for real content | P1 | Same as L-01 |
| L-09 | Cardocalypse | W1 | R | Over 70% of content blocks wrapped in cards, or any card nested inside a card | P1 | Group with spacing and dividers; flatten nesting |
| L-10 | Filler FAQ | W1 | J | An FAQ accordion whose questions are not ones real users actually ask | P2 | Answer real questions, or remove it |
| L-11 | Broadsheet cosplay | W2 | J | Hairline rules, zero radius and dense newspaper columns on content that is not editorial | P2 | Use only for editorial content |
| L-12 | Broken mobile | Q | R | A desktop layout shrunk down (text < 14px or horizontal scroll at 375px), or critical features hidden on mobile | P1 | Recompose for small screens |

## 4. Components (13)

| ID | Tell | Wave | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|---|
| K-01 | Side-tab accent card | W1 | D/R | Colored `border-left/right/top` ≥ 3px on a rounded element (≥ 1px when Tailwind `rounded` is on the same element); skip blockquote, nav, pre, code, input | P0 | Drop the stripe or the radius |
| K-02 | One radius and one shadow everywhere | W1/W3 | R | The same radius on over 80% of surfaces, or ≥ 16px radius on every container, or more than 2 radius values in use | P1 | Assign radius by element role; at most 2 values |
| K-03 | Stacked elevation | W2 | R | Border ≤ 1px plus shadow blur ≥ 24px on one element; or shadow, border and tinted background all on the same card | P1 | One elevation method |
| K-04 | Every button primary | Q | R | More than 1 primary-styled button per viewport section | P1 | One primary per section; the rest secondary or tertiary |
| K-05 | Arrow welded to every CTA | W2/W3 | D | → or an ArrowRight icon in over 50% of buttons | P2 | Use arrows only for real navigation |
| K-06 | Stock effect components | W3 | D | Aceternity or Magic UI names and classes: spotlight, beams, meteors, shimmer-button, border-beam, marquee, aurora, sparkles | P1 | Custom motion with a purpose, or none |
| K-07 | Gradient borders | W1 | D | `border-image` gradient, or a gradient wrapper used as a 1px border | P2 | Remove |
| K-08 | Pill overload | W1 | R | More than 6 decorative pill badges or chips on one page, outside filters and tags | P2 | Plain labels |
| K-09 | Fake window chrome | W2 | D | Three colored traffic-light dots on a mockup | P2 | Real screenshots |
| K-10 | Decorative data | W1 | J | Sparklines, charts or progress rings with no real data behind them | P1 | Real data, or remove |
| K-11 | Uniform hover, or hover-only actions | W1 | D/R | The same `hover:opacity-80` / `scale-105` on over 70% of interactive elements; actions visible only on hover | P2 | Hover states by role; keep actions visible |
| K-12 | Glassmorphism by reflex | W1 | D | `backdrop-filter: blur` on translucent panels on more than 1 component type | P2 | Solid surfaces. (Downgraded from P0: complaint data shows people do not mind it) |
| K-13 | Modal by default | Q | J | A modal used where an inline, drawer or in-place flow would work | P2 | Use the in-place pattern |

## 5. Imagery and iconography (7)

| ID | Tell | Wave | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|---|
| I-01 | AI-generated people or places for a real organization | W2 | J | Synthetic photos of students, staff, campus, customers; AI artifacts (garbled text, hands, impossible architecture) | P0 | Real, consented photography |
| I-02 | Emoji as design | W1 | D | 40% or more of nav links emoji-prefixed; emoji in headings, feature bullets or button labels; ✅ checklists used as design | P1 | Words, or a restrained icon set |
| I-03 | Default icon tics | W1 | D | Lucide or Heroicons Sparkles, Zap, Rocket or Wand used decoratively; an icon above every heading | P1 | Fewer icons, with meaning; a custom or restrained set |
| I-04 | Placeholder and generated avatars | W1 | D | Domains dicebear, ui-avatars, pravatar, picsum, placehold.co, source.unsplash random; gradient initial circles | P1 | Real people with consent, or no avatar |
| I-05 | Generic stock energy | W1 | J | Handshakes, a diverse smiling group looking at a laptop, a lightbulb brain | P1 | The actual subject, art-directed |
| I-06 | Blob and shape illustrations | W1/W2 | D/J | 3D blobs, shape-assembled SVG people, abstract mesh blobs used as the hero image | P2 | Commissioned illustration or real photography |
| I-07 | Grain overlay by default | W2 | D | SVG `feTurbulence` or noise PNG overlay on the whole page | P2 | Only if the art direction calls for it |

## 6. Motion (7)

| ID | Tell | Wave | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|---|
| M-01 | Content hidden at rest | Q | R | Text with opacity 0 or off-screen until JavaScript or scroll runs; content missing with JavaScript disabled | P0 | Visible by default; animation is an enhancement |
| M-02 | No reduced-motion support | Q | D | Any animation without a `prefers-reduced-motion` rule | P0 | Add the media query |
| M-03 | Bounce or elastic easing | W1 | D | `animate-bounce`; cubic-bezier with y outside −0.1 to 1.1; animation names containing bounce, elastic, wobble, jiggle or spring | P1 | ease-out quart, quint or expo |
| M-04 | Animating layout properties | Q | D | Transitions on width, height, padding, margin, top or left | P1 | Transform and opacity only |
| M-05 | Same entrance animation everywhere | W1 | D | Identical fade-up keyframes on 6 or more sections or elements | P2 | One orchestrated moment |
| M-06 | Perpetual decoration | W1 | D | Marquees, pulsing status dots, blinking cursors, floating blobs, count-up numbers | P2 | Motion only when it signals a state change |
| M-07 | `transition: all` | Q | D | `transition: all` or Tailwind `transition-all` | P2 | List the specific properties |

## 7. Copy and microcopy (14)

Copy is scored with a weighted model (§11). The rules below define what gets counted.

| ID | Tell | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|
| W-01 | Chat residue | D | "As an AI", "Certainly! Here is", "I hope this helps", "here is your page", "Feel free to" | P0 | Delete |
| W-02 | Buzzwords | D | Blocklist (general): elevate, seamless, unlock, empower, leverage, robust, cutting-edge, world-class, best-in-class, next-generation, revolutionize, supercharge, streamline, transform, delve, game-changer, journey, tapestry, synergy. Sector lists load from `presets/*.json` (e.g. education). Flag at ≥ 1 per 150 visible words | P1 | Concrete nouns and verbs from the subject |
| W-03 | Inflated significance | D | stands as a testament, plays a vital/pivotal role, underscores the importance, rich tapestry, a beacon of, at the heart of, more than just | P1 | State the specific fact |
| W-04 | Negative parallelism | D | Regex for "not just X(,\| —) (it's\|but) Y" and "It's not X. It's Y."; flag at 2 or more per page | P1 | A plain statement |
| W-05 | Filler openers and closers | D | In today's fast-paced world; Whether you're X or Y; In conclusion; Ultimately; At the end of the day | P1 | Cut |
| W-06 | Vague attribution | D | studies show, experts agree, research suggests, many believe, with no source | P1 | Cite the source, or cut |
| W-07 | Generic CTAs and link text | D | Get Started, Learn More, Submit, Sign Up, Click Here, Read More as a primary label | P1 | Verb + object ("Book a campus tour", "Request tuition info") |
| W-08 | Rule-of-three reflex | J | 3 or more triads ("X, Y, and Z") in one section | P2 | Use the real number of items |
| W-09 | Em-dash density | D | More than 2 em dashes per 200 visible words | P2 | Commas, periods, parentheses |
| W-10 | Redundant intro | J | The paragraph under a heading restates the heading | P2 | Cut, or add new information |
| W-11 | Title Case Everywhere | D | Over 80% of headings in Title Case on a site whose style is not Title Case | P2 | Pick one case and record it in DESIGN.md |
| W-12 | Bad state copy | J | "Something went wrong", "Invalid input", blame phrasing; no empty, loading or error states | P1 | Name the problem, its cause and the fix; design all states |
| W-13 | Duplicate copy across pages | D | Word-shingle (5-gram) Jaccard ≥ 0.8 between paragraphs on different pages | P1 | Write it for each page, or reuse a component on purpose |
| W-14 | Emoji headings and checkmark feature lists | D | An emoji at the start of headings, or ✅ / ✔ list bullets | P2 | Plain text |

## 8. Content integrity (5)

| ID | Tell | Det | Detection spec | Sev | Fix |
|---|---|---|---|---|---|
| X-01 | Invented social proof | D+J | "Trusted by N+", "10,000+", "99.9%", "4.9★"; testimonials without a real name and role; logo walls with no permission record | P0 | Real, attributable proof from PRODUCT.md, or a labelled placeholder |
| X-02 | Unsourced numbers | J | Any statistic that is not in the PRODUCT.md proof inventory with a source and date | P1 | Source it, or remove it |
| X-03 | Placeholders | D | lorem ipsum, [Your Company], example.com, api.yourdomain.com, 555-numbers, `href="#"`, John Doe, Jane Smith, Sarah Johnson, Acme, Globex, Initech, "Feature one" | P0 | Real content |
| X-04 | Leaked build strings | D | Footer or meta lines like "v2.1 · dark mode · single-file", template names, prompt text | P1 | Remove |
| X-05 | Broken or invented links | R | 4xx/5xx links, `#` anchors with no target, links to pages that don't exist | P1 | Fix or remove |

## 9. Quality floor (14) — WCAG 2.2 AA + Core Web Vitals

| ID | Check | Det | Threshold | Sev |
|---|---|---|---|---|
| Q-01 | Text contrast | R | 4.5:1 for body text; 3:1 for large text and UI components | P0 |
| Q-02 | Focus visible | D/R | `outline:none` without a `:focus-visible` replacement; aim for a 2px outline with offset | P0 |
| Q-03 | Alt text | D | Missing alt = P0; generic alt ("image", "photo", the file name) = P1; decorative images use `alt=""` | P0/P1 |
| Q-04 | Target size | R | At least 24×24 CSS px; aim for 44×44 on touch | P1 |
| Q-05 | Heading structure | D | Exactly one h1; no skipped levels | P1 |
| Q-06 | Color-only meaning | J | Errors, status or chart series shown by color alone | P1 |
| Q-07 | Zoom and inputs | D | `user-scalable=no` or `maximum-scale=1`; input font < 16px on mobile; paste blocked | P1 |
| Q-08 | Language | D | `<html lang>` missing | P1 |
| Q-09 | Forms | D/R | Every input has a visible label; errors are tied to fields with `aria-describedby` | P1 |
| Q-10 | Layout shift | D | Images without width/height or aspect-ratio; LCP image lazy-loaded | P1 |
| Q-11 | Core Web Vitals | R | LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 (lab run if no field data) | P1 |
| Q-12 | Runtime health | R | Console errors, broken images, failed requests | P1 |
| Q-13 | Skip link and landmarks | D | No skip link; no main, nav or footer landmarks | P2 |
| Q-14 | Images | D | No modern format (AVIF/WebP); images over 2× their display size | P2 |

## 10. Consistency (3) and institutional/admissions module (5, optional)

| ID | Rule | Det | Spec | Sev |
|---|---|---|---|---|
| S-01 | Values outside the tokens | D | Any hex, font, radius or shadow not defined in DESIGN.md | P1 |
| S-02 | Cross-page drift | R | Nav, fonts, radius or button styles differ between pages | P1 |
| S-03 | Waiver hygiene | D | A waiver with no reason or source; a waiver that is in the config but not in DESIGN.md (or the reverse) | P1 |
| E-01 | Proof-led hero | J | The hero leads with a verifiable claim or the real place and people, not "Welcome to [Organization]" | P1 |
| E-02 | Primary path everywhere | R | The primary action (e.g. Inquire, Book a visit, Apply, Donate) is visible on every page and reachable in 1 click | P1 |
| E-03 | Top audience questions in 2 clicks | J | The top 5 audience questions (e.g. price, programs, visits, schedule, contact) reachable within 2 clicks of home | P1 |
| E-04 | Real testimonials | J | Named and consented voices of real customers, members or families; outcomes over facility claims | P1 |
| E-05 | Consent and safety | J | Photos of minors have consent on file; no full names alongside the faces of minors unless policy allows it | P0 |

---

## 11. Scoring and verdict

**Visual tell score.** Count the distinct C, T, L, K, I and M rules that fire at P0 or P1, excluding waived ones. The thresholds come from Krebs' Show HN scoring of 1,590 sites:
- 0–1: Low
- 2–3: Medium
- 4 or more: High

**Corroboration.** If 3 or more tells fire in one category, mark that category a cluster and escalate its P1s to P0. This is the aislopfixer principle: stacked tells mean more than any single one. It is also how waves get caught. Cream (C-05) + Fraunces (T-02) + an italic hero word (T-03) together equal the second-wave look.

**Copy score.** Weighted sum per 1,000 visible words, using halans' weights:

| Weight | Rules |
|---|---|
| 15 | W-01 |
| 8 | W-02, W-03, W-06 |
| 4 | W-04, W-05, W-07, W-12 |
| 2 | W-08, W-09, W-11, W-14 |
| 1 | W-10 |

The score is capped at 100. 0–34 means clean, 35–64 means review, 65 or more means rewrite. Recalibrate against 10 real pages before trusting these cutoffs.

**Noise control.** If the user dismisses a rule as "not slop" 3 times in a project, halve its confidence for that project and log it for the monthly review.

**Verdict.**
- **SHIP:** 0 P0; every P1 fixed or waived; visual score Low; copy score below 35; Q-01 to Q-12 all pass; fresh-eyes review done.
- **HOLD:** anything else, including any check that could not run (PR-13).

**Report format.** Group findings by category: rule ID, severity, file:line or selector, screenshot crop, fix. Show the totals first. Never write an "AI-generated" verdict.

---

## 12. Watch list (tracked, not enforced)

- **Bento grids, mesh and aurora backgrounds:** complaint data (unslop-ui, 3,033 comments) shows people do not mind them. Flag only when they are content-free (L-09 or I-06 cover that).
- **Wave-3 tells (C-08, L-08, K-06):** based on a handful of late-2026 tests. Promote or demote at the monthly review.
- **Fonts on the T-02 list that other skills still recommend** (Geist, Satoshi, Outfit): this is attractor migration happening in real time. Keep watching.

## 13. Cut, and why

| Cut | Reason |
|---|---|
| Absolute bans (no radius over 12px, no pills at all, no serifs ever, max 1 accent) | Context-blind. They flatten real brands and conflict with PR-05 and PR-17 |
| Uncodixfy and no-slop-ui dashboard specifics (sidebar width, KPI grids) | Dashboard-only. Keep as an optional module if internal tools are ever built |
| Code-quality lint (KarpeSlop, dmmulroy anti-slop, Evil Martians TS rules, aislopfixer security checks) | Not a design concern. Use a code linter |
| Prescriptive aesthetics (taste-skill dials at their 8/6/4 defaults, MengTo's "use Geist/Satoshi") | Prescribing a look creates the next wave. Dials are fine as brief vocabulary, but their defaults are too loud for institutional sites |
| Single-source unverified rules (claude-deslop DS010–013, unslop scanner internals) | Already covered by better-specified rules (C-01, L-06, I-02, K-01) |
| "Missing tight tracking on big headlines" (ux-skill) | Contradicts T-08 and is a matter of taste, not a tell |
| Brand color on more than 3 surfaces as P1 | Kept only as P2 (C-12). Many brands legitimately use their primary color heavily |
| Raw rule counts as a score | Stripe scores 87 findings on Impeccable. Raw counts without categories mean nothing |

## 14. Sources

Impeccable (pbakaus) · Hallmark (Nutlope) · Anthropic frontend-design (2026 rewrite and Sep 3 update) · design-slop-cop + "Scoring Show HN submissions" (Krebs) · avoid-ai-design (funboy322) · Gesso anti-slop · taste-skill (Leonxlnx) · Vercel web-interface-guidelines · samber frontend-design-deslop · slop-detect (ravidsrk) · aiseo design_slop.rs · ux-skill (Laith0003) · aislopfixer (mertsoylu) · anti-slop (miqdadbadjuber) · ai-pattern-detection (halans) · Wikipedia: Signs of AI writing · unslop-ui / vibecoded-design-tells · wystack agent-kit · Uncodixfy / no-slop-ui · tastecheck · gstack · MengTo no-ai-design-slop · Google DESIGN.md spec · WCAG 2.2 · web.dev Core Web Vitals
