#!/usr/bin/env python3
"""deslop_scan.py - deterministic scanner for the deslop-web rulebook.

Static mode (stdlib only): scans .html .htm .css .jsx .tsx .js .ts .vue .svelte .astro .md .mdx
Render mode (--render): needs `pip install playwright` + a Chromium/Chrome. Adds the R rules
(computed fonts, colors, contrast, centering, radii, shadows, hidden content, mobile overflow)
and saves screenshots at 375/768/1280/1440.

Usage:
  python3 deslop_scan.py PATH [PATH...] [--config deslop.config.json] [--json] [--render URL_OR_HTML]
Exit codes: 0 = SHIP-ready, 1 = HOLD (findings), 2 = HOLD (a required check could not run)
"""
import argparse, json, math, os, re, sys
from collections import Counter, defaultdict

EXTS = {".html", ".htm", ".css", ".scss", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro", ".md", ".mdx"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "coverage", "vendor", ".deslop"}

# ---------------------------------------------------------------- rule metadata
RULES = {
 # id: (severity, category, title)
 "C-01": ("P0","color","Vibe purple/indigo accent"),
 "C-02": ("P0","color","Purple-blue/pink AI gradient"),
 "C-03": ("P0","color","Gradient text"),
 "C-04": ("P1","color","Colored glow shadow"),
 "C-05": ("P1","color","Cream 'tasteful default' background"),
 "C-06": ("P1","color","Terracotta/clay/brass accent on cream"),
 "C-07": ("P1","color","Near-black + single acid accent"),
 "C-08": ("P1","color","Teal/sage on cream"),
 "C-09": ("P1","color","Framework default tokens shipped"),
 "C-13": ("P2","color","Decorative grid/stripe background"),
 "T-01": ("P0","type","Default face as the whole identity"),
 "T-02": ("P1","type","Templated display face"),
 "T-03": ("P1","type","Hero word set apart (font/style/color)"),
 "T-04": ("P1","type","Tracked all-caps eyebrows"),
 "T-05": ("P2","type","Template chrome / A · B · C meta strings"),
 "T-06": ("P2","type","Default Tailwind size ladder"),
 "T-07": ("P2","type","Flat hierarchy"),
 "T-08": ("P2","type","Extreme display size/tracking"),
 "T-09": ("P1","type","Font declared but not loaded"),
 "T-10": ("P1","type","Unreadable body text"),
 "T-12": ("P2","type","Inflated body weight"),
 "T-13": ("P2","type","Wide tracking on text"),
 "L-01": ("P0","layout","Centered hero + pill badge"),
 "L-04": ("P1","layout","Stat banner"),
 "L-05": ("P1","layout","Decorative 01/02/03 numbering"),
 "L-06": ("P1","layout","Everything centered"),
 "L-07": ("P2","layout","Monotonous spacing"),
 "L-12": ("P1","layout","Broken mobile (horizontal overflow)"),
 "K-01": ("P0","component","Side-tab accent border on rounded card"),
 "K-02": ("P1","component","One radius everywhere / >2 radii"),
 "K-03": ("P1","component","Hairline border + wide shadow"),
 "K-05": ("P2","component","Arrow welded to every CTA"),
 "K-06": ("P1","component","Stock effect components"),
 "K-07": ("P2","component","Gradient borders"),
 "K-09": ("P2","component","Fake window chrome dots"),
 "K-11": ("P2","component","Uniform hover everywhere"),
 "K-12": ("P2","component","Glassmorphism by reflex"),
 "I-02": ("P1","imagery","Emoji as design"),
 "I-03": ("P1","imagery","Default icon tics"),
 "I-04": ("P1","imagery","Placeholder/generated avatars & images"),
 "I-07": ("P2","imagery","Grain overlay by default"),
 "M-01": ("P0","motion","Content hidden at rest"),
 "M-02": ("P0","motion","No prefers-reduced-motion"),
 "M-03": ("P1","motion","Bounce/elastic easing"),
 "M-04": ("P1","motion","Animating layout properties"),
 "M-05": ("P2","motion","Same entrance animation everywhere"),
 "M-06": ("P2","motion","Perpetual decorative motion"),
 "M-07": ("P2","motion","transition: all"),
 "W-01": ("P0","copy","Chat residue"),
 "W-02": ("P1","copy","Buzzwords"),
 "W-03": ("P1","copy","Inflated significance"),
 "W-04": ("P1","copy","Negative parallelism"),
 "W-05": ("P1","copy","Filler openers/closers"),
 "W-06": ("P1","copy","Vague attribution"),
 "W-07": ("P1","copy","Generic CTA / link text"),
 "W-09": ("P2","copy","Em-dash density"),
 "W-11": ("P2","copy","Title Case everywhere"),
 "W-13": ("P1","copy","Duplicate copy across pages"),
 "W-14": ("P2","copy","Emoji headings / checkmark lists"),
 "X-01": ("P0","content","Invented social proof"),
 "X-03": ("P0","content","Placeholders"),
 "X-04": ("P1","content","Leaked build strings"),
 "Q-01": ("P0","quality","Text contrast below WCAG AA"),
 "Q-02": ("P0","quality","Focus outline removed"),
 "Q-03": ("P0","quality","Missing/generic alt text"),
 "Q-04": ("P1","quality","Target size < 24px"),
 "Q-05": ("P1","quality","Heading structure"),
 "Q-07": ("P1","quality","Zoom disabled"),
 "Q-08": ("P1","quality","Missing lang"),
 "Q-10": ("P1","quality","Layout shift risk (unsized/lazy LCP images)"),
 "Q-12": ("P1","quality","Runtime errors / broken images"),
 "S-01": ("P1","consistency","Value outside design tokens"),
 "S-03": ("P1","consistency","Waiver without reason"),
}
VISUAL_CATS = {"color","type","layout","component","imagery","motion"}
COPY_WEIGHTS = {"W-01":15,"W-02":8,"W-03":8,"W-06":8,"W-04":4,"W-05":4,"W-07":4,"W-12":4,
                "W-08":2,"W-09":2,"W-11":2,"W-14":2,"W-10":1}

# ---------------------------------------------------------------- color math
def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) in (3,4): h = "".join(c*2 for c in h[:3])
    h = h[:6]
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def _lin(c):
    c /= 255
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def oklch(rgb):
    r,g,b = (_lin(x) for x in rgb)
    l = (0.4122214708*r+0.5363325363*g+0.0514459929*b)**(1/3)
    m = (0.2119034982*r+0.6806995451*g+0.1073969566*b)**(1/3)
    s = (0.0883024619*r+0.2817188376*g+0.6299787005*b)**(1/3)
    L = 0.2104542553*l+0.7936177850*m-0.0040720468*s
    a = 1.9779984951*l-2.4285922050*m+0.4505937099*s
    bb= 0.0259040371*l+0.7827717662*m-0.8086757660*s
    return L, math.hypot(a,bb), math.degrees(math.atan2(bb,a)) % 360

def lum(rgb):
    r,g,b = (_lin(x) for x in rgb)
    return 0.2126*r+0.7152*g+0.0722*b

def contrast(a,b):
    la, lb = sorted([lum(a),lum(b)], reverse=True)
    return (la+0.05)/(lb+0.05)

def is_purple(rgb):
    L,C,H = oklch(rgb); return C > 0.10 and 250 <= H <= 320
def is_cream(rgb):
    L,C,H = oklch(rgb); return 0.94 <= L <= 0.985 and 0.008 <= C <= 0.045 and 60 <= H <= 95
def band(rgb):
    L,C,H = oklch(rgb)
    if C < 0.06: return "neutral"
    if 250 <= H <= 320: return "purple"
    if 200 <= H < 250: return "blue"
    if 150 <= H < 200: return "teal"
    if 125 <= H < 150: return "green"
    if 320 < H or H < 25: return "pink" if H > 330 or H < 10 else "red"
    if 25 <= H < 60: return "terracotta"
    return "yellow"

PURPLE_HEX = {"6366f1","4f46e5","8b5cf6","7c3aed","a855f7","667eea","764ba2","6d28d9","818cf8","9333ea","c084fc","a78bfa"}
CREAM_HEX = {"f4f1ea","f5f1ea","f7f5f1","fbf8f1","efeae0","ece6db","faf7f1","e8dfcb","faf8f5","fafaf9","fffbeb"}

# ---------------------------------------------------------------- word lists
BUZZ = ["elevate","seamless","seamlessly","unlock","unleash","empower","leverage","robust","cutting-edge","world-class",
        "best-in-class","next-generation","next-gen","revolutionize","revolutionary","supercharge","streamline",
        "transformative","delve","game-changer","game-changing","synergy","tapestry","state-of-the-art",
        "effortless","effortlessly","reimagine","reimagined","unlock your potential"]
# Sector word lists live in presets/*.json ("extra_buzzwords") so the core stays neutral.
INFLATED = [r"stands? as a testament", r"plays? an? (vital|pivotal|crucial|key) role", r"underscores? the importance",
            r"rich tapestry", r"a beacon of", r"at the heart of", r"more than just", r"is a testament to"]
FILLER = [r"in today'?s (fast-paced|digital|ever-changing|modern) (world|landscape|age)", r"whether you'?re an? .{1,40}? or ",
          r"\bin conclusion\b", r"at the end of the day", r"look no further", r"in the ever-evolving"]
VAGUE = [r"studies (show|suggest)", r"experts (agree|say)", r"research (shows|suggests)", r"many believe", r"it is widely (known|believed)"]
NEGPAR = [r"\bnot just (an? )?\w+[^.]{0,40}?(,|—|–|;)\s*(it'?s|but|they)\b", r"\bit'?s not (just )?(an? )?\w+\. it'?s\b",
          r"\bdon'?t just \w+[^.]{0,40}?;\s*they\b", r"\bnot only\b[^.]{0,60}?\bbut\b"]
RESIDUE = [r"as an ai\b", r"certainly! here", r"i hope this helps", r"here is your (page|website|landing page)", r"feel free to (reach|let)",
           r"as of my (last|knowledge)", r"\bi'?m (an ai|a language model)"]
GENERIC_CTA = {"get started","learn more","submit","sign up","click here","read more","start now","try it free","find out more"}
PLACEHOLDER = [r"lorem ipsum", r"\[your [a-z ]+\]", r"\bexample\.com\b", r"yourdomain\.com", r"\b555-\d{4}\b", r"\(555\)",
               r"\bjohn doe\b", r"\bjane (doe|smith)\b", r"\bsarah johnson\b", r"\bacme( corp| inc)?\b", r"\bglobex\b", r"\binitech\b",
               r"\bfeature (one|two|three)\b", r"\bplaceholder text\b"]
SOCIAL = [r"trusted by (over )?[\d,.]+[km]?\+", r"\b[\d,]{2,}\+ (happy |satisfied )?(customers|users|developers|teams|companies|students|families)",
          r"\b99\.9+%", r"\b4\.\d ?★", r"★★★★★"]
LEAK = [r"single-file html", r"\bv\d+\.\d+ · ", r"generated (by|with) (ai|claude|chatgpt|gpt)", r"\bdark mode · "]
STOCK_FX = ["spotlight","border-beam","borderbeam","meteors","shimmer-button","shimmerbutton","aurora-background","sparkles-core",
            "background-beams","animated-beam","magic-card","text-generate-effect","lamp-container","wavy-background"]
DEFAULT_FONTS = {"inter","roboto","arial","helvetica","open sans","lato","montserrat","system-ui","segoe ui","-apple-system","blinkmacsystemfont","helvetica neue"}
TEMPLATED_DISPLAY = {"fraunces","instrument serif","space grotesk","geist","syne","recoleta","newsreader","plus jakarta sans",
                     "mona sans","satoshi","outfit","cabinet grotesk","inter","general sans","clash display"}
GENERIC_FAMILIES = {"serif","sans-serif","monospace","cursive","fantasy","system-ui","ui-sans-serif","ui-serif","ui-monospace",
                    "inherit","initial","-apple-system","blinkmacsystemfont","segoe ui","helvetica neue","arial","helvetica",
                    "apple color emoji","segoe ui emoji","segoe ui symbol","noto color emoji","var","sans","unset"}
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅]")

# ---------------------------------------------------------------- helpers
class Report:
    def __init__(self, cfg):
        self.cfg = cfg; self.findings = []; self.incomplete = []; self.words = 0
        self.waivers = {k.upper(): v for k, v in (cfg.get("waivers") or {}).items()}
    def add(self, rid, where, detail, sev=None, title=None):
        if rid not in RULES and not sev: return
        s, cat, t0 = RULES.get(rid, (sev, "brand", title or detail))
        title = title or t0
        if sev: s = sev
        s = (self.cfg.get("severity_overrides") or {}).get(rid, s)
        self.findings.append({"rule": rid, "severity": s, "category": cat, "title": title,
                              "where": where, "detail": detail[:220], "waived": rid in self.waivers})

def strip_code(text):
    t = re.sub(r"<script\b.*?</script>", " ", text, flags=re.S|re.I)
    t = re.sub(r"<style\b.*?</style>", " ", t, flags=re.S|re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"\{[^{}]*\}", " ", t)          # JSX expressions
    t = re.sub(r"<[^>]+>", "\n", t)
    t = re.sub(r"&nbsp;", " ", t); t = re.sub(r"&amp;", "&", t); t = re.sub(r"&mdash;", "—", t)
    return t

def visible_text(path, raw):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".css", ".scss"): return ""
    if ext in (".md", ".mdx"): return re.sub(r"```.*?```", " ", raw, flags=re.S)
    if ext in (".js", ".ts"): return ""
    return strip_code(raw)

def lineno(raw, idx): return raw.count("\n", 0, idx) + 1

def iter_files(paths, ignore):
    for p in paths:
        if os.path.isfile(p):
            yield p; continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for f in files:
                fp = os.path.join(root, f)
                if os.path.splitext(f)[1].lower() in EXTS and not any(re.search(g, fp) for g in ignore):
                    yield fp

def shingles(text, n=5):
    w = re.findall(r"[a-z']+", text.lower())
    return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}

# ---------------------------------------------------------------- static rules
def scan_static(path, raw, rep, cfg, para_bank):
    low = raw.lower(); rel = os.path.relpath(path)
    def hit(rid, m, detail=None):
        rep.add(rid, f"{rel}:{lineno(raw, m.start())}", detail or m.group(0).strip())

    # --- color
    for m in re.finditer(r"\b(bg|text|from|via|to|border|ring|fill)-(indigo|violet|purple)-(\d{2,3})\b", raw):
        if m.group(1) in ("bg","text","from","via","to"): hit("C-01", m)
    for m in re.finditer(r"#([0-9a-fA-F]{6})\b", raw):
        if m.group(1).lower() in PURPLE_HEX: hit("C-01", m)
    for m in re.finditer(r"\bfrom-(purple|violet|indigo|fuchsia|pink)-\d+[^\"'`]{0,80}?\bto-(blue|cyan|pink|fuchsia|indigo|purple|violet|sky)-\d+", raw):
        hit("C-02", m)
    for m in re.finditer(r"(linear|radial|conic)-gradient\(([^;{}]{0,300})\)", raw, flags=re.I):
        cols = [hex_to_rgb(h) for h in re.findall(r"#([0-9a-fA-F]{3,8})\b", m.group(2))]
        bands = {band(c) for c in cols}
        hues = [oklch(c)[2] for c in cols if oklch(c)[1] > 0.06]
        purpleish = any(250 <= h <= 320 for h in hues)
        spread = (max(hues) - min(hues)) if len(hues) >= 2 else 0
        if purpleish and (bands & {"blue","pink","teal"} or spread >= 20): hit("C-02", m, "gradient " + m.group(0)[:90])
        if re.search(r"repeating-linear-gradient", raw[max(0,m.start()-12):m.start()+10], re.I): hit("C-13", m)
    for m in re.finditer(r"(-webkit-)?background-clip\s*:\s*text", raw, flags=re.I):
        ctx = raw[max(0, m.start()-400): m.end()+400]
        if "gradient" in ctx.lower(): hit("C-03", m)
    for m in re.finditer(r"\bbg-clip-text\b", raw):
        ctx = raw[max(0, m.start()-200): m.end()+200]
        if "gradient" in ctx: hit("C-03", m)
    for m in re.finditer(r"(?:box|text)-shadow\s*:[^;]*?(\d+)px[^;]*?(#[0-9a-fA-F]{6}|rgba?\([^)]*\))", raw, flags=re.I):
        col = m.group(2)
        rgb = hex_to_rgb(col) if col.startswith("#") else tuple(int(float(x)) for x in re.findall(r"[\d.]+", col)[:3])
        blurs = [int(x) for x in re.findall(r"(\d+)px", m.group(0))]
        if len(rgb)==3 and max(blurs or [0]) >= 15 and oklch(rgb)[1] > 0.10: hit("C-04", m, m.group(0)[:100])
    for m in re.finditer(r"background(?:-color)?\s*:\s*#([0-9a-fA-F]{6})", raw, flags=re.I):
        if m.group(1).lower() in CREAM_HEX or is_cream(hex_to_rgb(m.group(1))): hit("C-05", m)
    for m in re.finditer(r"\bbg-(stone-50|amber-50|\[#(?:" + "|".join(CREAM_HEX) + r")\])", raw, flags=re.I):
        hit("C-05", m)
    for pat in [r"--radius\s*:\s*0\.625rem", r"--font-sans\s*:\s*var\(--font-geist-sans\)", r"\bbg-blue-600\b", r"#10b981\b", r"\bemerald-500\b"]:
        for m in re.finditer(pat, raw, flags=re.I): hit("C-09", m)
    for m in re.finditer(r"repeating-linear-gradient|bg-grid|dot-pattern|grid-pattern", raw, flags=re.I):
        hit("C-13", m)

    # --- typography
    for m in re.finditer(r"text-transform\s*:\s*uppercase[^}]{0,120}letter-spacing\s*:\s*0?\.(\d+)em|letter-spacing\s*:\s*0?\.(\d+)em[^}]{0,120}text-transform\s*:\s*uppercase", raw, flags=re.I):
        pass  # rendered rule T-04 is authoritative; static only counts Tailwind eyebrows below
    eyebrows = re.findall(r"uppercase[^\"'`]{0,60}tracking-(?:wide|wider|widest|\[0\.\d+em\])|tracking-(?:wide|wider|widest)[^\"'`]{0,60}uppercase", raw)
    if len(eyebrows) >= 3:
        rep.add("T-04", rel, f"{len(eyebrows)} uppercase+tracked labels")
    for m in re.finditer(r"\w+ · \w+ · \w+", strip_code(raw) if path.endswith(("html","htm","jsx","tsx","vue","svelte","astro")) else ""):
        rep.add("T-05", rel, m.group(0))
    for m in re.finditer(r"text-align\s*:\s*justify|\btext-justify\b", raw, flags=re.I): hit("T-10", m, "justified text")
    for m in re.finditer(r"line-height\s*:\s*(1(?:\.[0-2]\d*)?|0?\.\d+)\s*[;}]", raw, flags=re.I):
        try:
            if float(m.group(1)) < 1.3 and not re.search(r"h[1-6]|display|title|heading|hero", raw[max(0,m.start()-200):m.start()], re.I):
                hit("T-10", m, "tight line-height " + m.group(1))
        except ValueError: pass
    for m in re.finditer(r"letter-spacing\s*:\s*0?\.(0[6-9]|[1-9]\d?)\d*(em|rem)", raw, flags=re.I):
        ctx = raw[max(0,m.start()-200): m.start()].lower()
        if "uppercase" not in ctx and "label" not in ctx and "eyebrow" not in ctx: hit("T-13", m)
    # fonts declared vs loaded
    fams = set()
    for m in re.finditer(r"font-family\s*:\s*([^;}\n]+)", raw, flags=re.I):
        for f in m.group(1).split(","):
            f = f.strip().strip("'\"").lower()
            if f and f not in GENERIC_FAMILIES and not f.startswith("var("): fams.add(f)
    loaded = set(x.lower() for x in re.findall(r"@font-face\s*{[^}]*?font-family\s*:\s*['\"]?([^;'\"]+)", raw, flags=re.I))
    for g in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"'\s>]+)", raw):
        for fam in re.findall(r"family=([^&:]+)", g): loaded.add(fam.replace("+"," ").lower())
    rep._fams = getattr(rep, "_fams", set()) | fams
    mf = cfg.get("max_font_families")
    if mf and len(fams) > mf: rep.add("S-01", rel, f"{len(fams)} font families ({', '.join(sorted(fams))}); max {mf}")
    rep._loaded = getattr(rep, "_loaded", set()) | loaded

    # --- layout
    text = visible_text(path, raw)
    for m in re.finditer(r"(?<![\w.])(0[1-9])\s*(?:[/.·—-]|\n)", text):
        pass
    nums = re.findall(r"(?m)^\s*0[1-9]\s*$", text)
    if len(nums) >= 3: rep.add("L-05", rel, f"{len(nums)} standalone 01/02/03 markers")
    stats = re.findall(r"(?m)^\s*(\d[\d,.]*\s*[kKmM]?\+|\d+(?:\.\d)?%|\d(?:\.\d)?\s*★|\d+x)\s*$", text)
    if len(stats) >= 3: rep.add("L-04", rel, "stat banner: " + ", ".join(stats[:5]))

    # --- components
    for m in re.finditer(r"\bborder-([lrse])-(\d+)\b", raw):
        ctx = raw[max(0,m.start()-150): m.end()+150]
        w = int(m.group(2)); rounded = re.search(r"\brounded", ctx)
        if (rounded and w >= 1) or w >= 4:
            if not re.search(r"blockquote|<nav|<pre|<code|<input", ctx): hit("K-01", m, m.group(0) + (" + rounded" if rounded else ""))
    for m in re.finditer(r"border-(left|right)\s*:\s*(\d+)px\s+solid|border-(left|right)-width\s*:\s*(\d+)px", raw, flags=re.I):
        w = int(m.group(2) or m.group(4))
        block = raw[raw.rfind("{",0,m.start())-80 if raw.rfind("{",0,m.start())>80 else 0 : raw.find("}", m.end())+1]
        if w >= 3 and "border-radius" in block and not re.search(r"blockquote|nav|pre|code|input", block[:80], re.I):
            hit("K-01", m)
    buttons = re.findall(r"<(button|a)\b[^>]*?(?:class(?:Name)?=[\"'][^\"']*(?:btn|button|cta)[^\"']*[\"'])?[^>]*>(.*?)</\1>", raw, flags=re.S|re.I)
    btn_text = [re.sub(r"<[^>]+>", " ", b[1]) for b in buttons if b[0].lower()=="button" or re.search(r"btn|button|cta", b[1] + "", re.I) or True]
    btn_only = [re.sub(r"<[^>]+>", " ", t) for tag, t in re.findall(r"<(button)\b[^>]*>(.*?)</button>", raw, flags=re.S|re.I)]
    arrows = [t for t in btn_only if "→" in t or "arrowright" in t.lower() or "&rarr;" in t]
    if len(btn_only) >= 3 and len(arrows)/len(btn_only) > 0.5: rep.add("K-05", rel, f"{len(arrows)}/{len(btn_only)} buttons with arrows")
    for fx in STOCK_FX:
        for m in re.finditer(r"\b" + re.escape(fx) + r"\b", low): hit("K-06", m)
    for m in re.finditer(r"border-image\s*:[^;]*gradient", raw, flags=re.I): hit("K-07", m)
    if all(c in low for c in ("#ff5f57","#febc2e","#28c840")) or all(c in low for c in ("#ff5f56","#ffbd2e","#27c93f")):
        rep.add("K-09", rel, "macOS traffic-light dots")
    hov = re.findall(r"hover:(opacity-\d+|scale-\d+|-translate-y-\d+)", raw)
    if len(hov) >= 6 and Counter(hov).most_common(1)[0][1] / len(hov) > 0.7:
        rep.add("K-11", rel, f"{Counter(hov).most_common(1)[0][0]} on {len(hov)} elements")
    glass = len(re.findall(r"backdrop-filter\s*:\s*blur|\bbackdrop-blur(-\w+)?\b", raw, flags=re.I))
    if glass >= 2: rep.add("K-12", rel, f"{glass} backdrop blur uses")

    # --- imagery
    for m in re.finditer(r"<(h[1-6]|button|nav|li)\b[^>]*>([^<]{0,80})", raw, flags=re.I):
        if EMOJI_RE.search(m.group(2)): hit("I-02", m, f"emoji in <{m.group(1)}>: {m.group(2).strip()[:40]}")
    for m in re.finditer(r"\b(Sparkles|Zap|Rocket|Wand2?|WandSparkles)\b", raw):
        if re.search(r"lucide|heroicons|<" + m.group(1), raw): hit("I-03", m)
    for m in re.finditer(r"(dicebear\.com|ui-avatars\.com|pravatar\.cc|picsum\.photos|placehold\.co|placeholder\.com|via\.placeholder|source\.unsplash\.com|randomuser\.me)", low):
        hit("I-04", m)
    for m in re.finditer(r"feturbulence|noise\.(png|svg|webp)|grain\.(png|svg|webp)", low): hit("I-07", m)

    # --- motion
    animates = re.search(r"@keyframes|animation\s*:|\banimate-|transition\s*:|\btransition\b|framer-motion|motion\.", raw)
    if animates and "prefers-reduced-motion" not in low and "motion-reduce" not in low and "usereducedmotion" not in low:
        rep._anim_files = getattr(rep, "_anim_files", []) + [rel]
    if "prefers-reduced-motion" in low or "motion-reduce" in low or "usereducedmotion" in low:
        rep._rm = True
    for m in re.finditer(r"\banimate-bounce\b|animation(-name)?\s*:[^;]*\b(bounce|elastic|wobble|jiggle|spring)", raw, flags=re.I): hit("M-03", m)
    for m in re.finditer(r"cubic-bezier\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)", raw):
        y1, y2 = float(m.group(2)), float(m.group(4))
        if not (-0.1 <= y1 <= 1.1 and -0.1 <= y2 <= 1.1): hit("M-03", m)
    for m in re.finditer(r"transition(?:-property)?\s*:\s*([^;}]+)", raw, flags=re.I):
        v = m.group(1).lower()
        if re.search(r"\ball\b", v): hit("M-07", m)
        elif re.search(r"\b(width|height|padding|margin|top|left|right|bottom|max-height|min-height)\b", v): hit("M-04", m)
    for m in re.finditer(r"\btransition-all\b", raw): hit("M-07", m)
    fade = re.findall(r"(fade-?in-?up|fadeInUp|animate-fade-up|data-aos=\"fade-up\"|whileInView)", raw)
    if len(fade) >= 6: rep.add("M-05", rel, f"{len(fade)} identical entrance animations")
    for m in re.finditer(r"<marquee|\bmarquee\b|animate-pulse|blink-caret|countup|count-up|animate-ping", low): hit("M-06", m)

    # --- quality (static)
    if path.endswith((".html", ".htm")):
        if re.search(r"<html\b", raw, re.I) and not re.search(r"<html\b[^>]*\blang=", raw, re.I): rep.add("Q-08", rel, "<html> has no lang")
        h1 = len(re.findall(r"<h1\b", raw, re.I))
        if h1 != 1 and re.search(r"<body", raw, re.I): rep.add("Q-05", rel, f"{h1} <h1> elements")
        levels = [int(x) for x in re.findall(r"<h([1-6])\b", raw, re.I)]
        for a, b in zip(levels, levels[1:]):
            if b > a + 1: rep.add("Q-05", rel, f"heading skips h{a}→h{b}"); break
        if re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1(\.0)?\b", raw, re.I): rep.add("Q-07", rel, "zoom disabled in viewport meta")
    for m in re.finditer(r"<img\b[^>]*>", raw, flags=re.I):
        tag = m.group(0)
        if not re.search(r"\balt\s*=", tag): hit("Q-03", m, "img without alt")
        elif re.search(r"\balt\s*=\s*[\"'](image|photo|picture|img|graphic|banner|[\w-]+\.(jpe?g|png|webp|gif))[\"']", tag, re.I):
            rep.add("Q-03", f"{rel}:{lineno(raw,m.start())}", "generic alt: " + tag[:80], sev="P1")
        if not (re.search(r"\bwidth\s*=", tag) and re.search(r"\bheight\s*=", tag)) and "aspect-" not in tag and "fill" not in tag:
            hit("Q-10", m, "img without width/height")
    first_img = re.search(r"<img\b[^>]*>", raw, flags=re.I)
    if first_img and re.search(r"loading\s*=\s*[\"']lazy", first_img.group(0)): hit("Q-10", first_img, "first (likely LCP) image is lazy-loaded")
    for m in re.finditer(r"outline\s*:\s*(none|0)\b|\boutline-none\b", raw, flags=re.I):
        if not re.search(r"focus-visible", raw, re.I): hit("Q-02", m, "outline removed, no :focus-visible replacement in file")

    # --- copy (visible text only)
    if text.strip():
        tl = text.lower(); words = len(re.findall(r"[A-Za-z']+", text)); rep.words += words
        def thit(rid, pat, flags=re.I, label=None):
            for m in re.finditer(pat, text, flags):
                rep.add(rid, f"{rel}", (label or "") + m.group(0).strip()[:90])
        for p in RESIDUE: thit("W-01", p)
        bl = BUZZ + [w.lower() for w in cfg.get("extra_buzzwords", [])]
        allow = {w.lower() for w in cfg.get("allow_words", [])}
        for w in bl:
            if w in allow: continue
            for m in re.finditer(r"\b" + re.escape(w) + r"\b", tl): rep.add("W-02", rel, w)
        for p in INFLATED: thit("W-03", p)
        for p in NEGPAR: thit("W-04", p)
        for p in FILLER: thit("W-05", p)
        for p in VAGUE: thit("W-06", p)
        for t in btn_only + re.findall(r"<a\b[^>]*>([^<]{1,40})</a>", raw, flags=re.I):
            if re.sub(r"[^a-z ]", "", t.lower()).strip() in GENERIC_CTA: rep.add("W-07", rel, t.strip())
        em = text.count("—") + text.count("&mdash;")
        lim = cfg.get("max_emdash_per_200_words", 2)
        if words and em / max(words, 1) * 200 > lim: rep.add("W-09", rel, f"{em} em dashes in {words} words", sev=cfg.get("emdash_severity"))
        heads = [h.strip() for h in re.findall(r"<h[1-3]\b[^>]*>([^<]{6,120})</h[1-3]>", raw, re.I)]
        tc = [h for h in heads if len(h.split()) >= 3 and all(w[0].isupper() for w in h.split() if len(w) > 3)]
        if len(heads) >= 4 and len(tc) / len(heads) > 0.8: rep.add("W-11", rel, f"{len(tc)}/{len(heads)} headings in Title Case")
        for m in re.finditer(r"(?m)^\s*(✅|✔️?|☑️?)", text): rep.add("W-14", rel, "checkmark bullet")
        for p in PLACEHOLDER: thit("X-03", p)
        for p in SOCIAL: thit("X-01", p)
        for p in LEAK: thit("X-04", p)
        mx = cfg.get("max_exclamations_per_page")
        if mx is not None:
            n = len(re.findall(r"!(?!\[)", text))
            if n > mx: rep.add("BRAND-EXCL", rel, f"{n} exclamation points", sev="P1", title=f"More than {mx} exclamation point(s) per page")
        for p in re.split(r"\n\s*\n", text):
            if len(p.split()) >= 25: para_bank.append((rel, p.strip()))
    for m in re.finditer(r"href\s*=\s*[\"']#[\"']", raw): hit("X-03", m, 'href="#"')

    # --- brand config: custom patterns, palette, fonts
    for cp in cfg.get("custom_patterns", []):
        src = text if cp.get("scope", "text") == "text" else raw
        for m in re.finditer(cp["regex"], src, re.I if cp.get("ignore_case", True) else 0):
            pos = raw.find(m.group(0)); ln = lineno(raw, pos) if pos >= 0 else "?"
            rep.add(cp["id"], f"{rel}:{ln}", m.group(0)[:80], sev=cp.get("severity", "P1"), title=cp["message"])
    pal = {c.lower().lstrip("#") for c in cfg.get("allowed_colors", [])}
    if pal:
        for m in re.finditer(r"#([0-9a-fA-F]{6})\b", raw):
            if m.group(1).lower() not in pal: hit("S-01", m, f"#{m.group(1)} not in DESIGN.md palette")

def finish_static(rep, cfg, para_bank):
    fams, loaded = getattr(rep, "_fams", set()), getattr(rep, "_loaded", set())
    for f in sorted(fams):
        if f not in loaded and f not in GENERIC_FAMILIES and loaded:
            rep.add("T-09", "fonts", f"'{f}' declared but no @font-face/link found")
    allowed = {f.lower() for f in cfg.get("allowed_fonts", [])}
    if allowed:
        for f in sorted(fams - allowed - GENERIC_FAMILIES): rep.add("S-01", "fonts", f"font '{f}' not in DESIGN.md")
    if getattr(rep, "_anim_files", None) and not getattr(rep, "_rm", False):
        rep.add("M-02", ", ".join(rep._anim_files[:4]), "animation/transition with no prefers-reduced-motion anywhere in project")
    # W-13 duplicates across files
    seen = []
    for rel, p in para_bank:
        sh = shingles(p)
        for rel2, p2, sh2 in seen:
            if rel2 != rel and sh and sh2:
                j = len(sh & sh2) / len(sh | sh2)
                if j >= 0.8: rep.add("W-13", f"{rel} ~ {rel2}", f"Jaccard {j:.2f}: {p[:70]}…"); break
        seen.append((rel, p, sh))
    for k, v in rep.waivers.items():
        if not str(v).strip() or len(str(v).strip()) < 12: rep.add("S-03", "config", f"waiver {k} has no real reason")

# ---------------------------------------------------------------- render rules
RENDER_JS = r"""
() => {
 const out = {};
 const rgb = s => { const m = (s||'').match(/[\d.]+/g); return m ? m.slice(0,4).map(Number) : null; };
 const vis = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
   return r.width>0 && r.height>0 && cs.visibility!=='hidden' && cs.display!=='none'; };
 const bgOf = el => { while (el) { const c = rgb(getComputedStyle(el).backgroundColor);
   if (c && (c.length<4 || c[3]>0.9)) return c.slice(0,3); el = el.parentElement; } return [255,255,255]; };
 const fam = el => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g,'').trim().toLowerCase();
 const h1 = document.querySelector('h1');
 out.h1Font = h1 ? fam(h1) : null; out.bodyFont = fam(document.body);
 out.h1Px = h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0;
 out.h1Track = h1 ? getComputedStyle(h1).letterSpacing : 'normal';
 out.h1Align = h1 ? getComputedStyle(h1).textAlign : null;
 out.vw = innerWidth;
 out.h1Spans = [];
 if (h1) { const base = getComputedStyle(h1);
   h1.querySelectorAll('span,em,i,strong').forEach(s => { const c = getComputedStyle(s);
     if (fam(s)!==fam(h1) || c.fontStyle!==base.fontStyle || c.color!==base.color) out.h1Spans.push(s.textContent.trim().slice(0,40)); }); }
 // pill before h1
 out.pillBeforeH1 = false;
 if (h1) { let p = h1.previousElementSibling || (h1.parentElement && h1.parentElement.previousElementSibling);
   if (p && vis(p)) { const r = p.getBoundingClientRect(); const br = parseFloat(getComputedStyle(p).borderTopLeftRadius);
     if (r.height < 48 && br >= r.height/2 - 1 && p.textContent.trim().length < 60) out.pillBeforeH1 = p.textContent.trim(); } }
 const bodyBg = bgOf(document.body); out.bodyBg = bodyBg;
 // primary accent: first visible button/cta background with chroma
 const btns = [...document.querySelectorAll('button, a[class*="btn"], a[class*="button"], [role=button], input[type=submit]')].filter(vis);
 out.buttonBgs = btns.slice(0,12).map(b => rgb(getComputedStyle(b).backgroundColor)).filter(c => c && (c.length<4||c[3]>0.5)).map(c=>c.slice(0,3));
 out.links = [...document.querySelectorAll('a')].filter(vis).slice(0,30).map(a => rgb(getComputedStyle(a).color).slice(0,3));
 // text elements
 const texts = [...document.querySelectorAll('p,li,h1,h2,h3,h4,h5,h6,a,button,span,label,td,blockquote,figcaption')].filter(el => vis(el) && el.childElementCount===0 && el.textContent.trim().length>1);
 out.contrast = []; let centered=0, eligible=0; const sizes = new Set(); const weights = new Set();
 texts.slice(0,600).forEach(el => { const cs = getComputedStyle(el); const fg = rgb(cs.color); const bg = bgOf(el);
   const px = parseFloat(cs.fontSize); const bold = parseInt(cs.fontWeight)>=700; sizes.add(Math.round(px)); weights.add(cs.fontWeight);
   out.contrast.push({t: el.textContent.trim().slice(0,40), fg: fg.slice(0,3), a: fg[3]===undefined?1:fg[3], bg, px, bold, tag: el.tagName});
   if (el.textContent.trim().length > 20) { eligible++; if (cs.textAlign==='center') centered++; } });
 out.centered = [centered, eligible]; out.sizes=[...sizes]; out.weights=[...weights];
 const p = document.querySelector('main p, article p, p');
 if (p) { const cs = getComputedStyle(p); out.body = {px: parseFloat(cs.fontSize), lh: (isNaN(parseFloat(cs.lineHeight)) ? 1.2 : parseFloat(cs.lineHeight)/parseFloat(cs.fontSize)), w: parseInt(cs.fontWeight), ch: p.getBoundingClientRect().width / (parseFloat(cs.fontSize)*0.5)}; }
 // eyebrows
 out.eyebrows = [...document.querySelectorAll('h1,h2,h3')].map(h => h.previousElementSibling).filter(e => e && vis(e)).filter(e => { const c = getComputedStyle(e);
   return c.textTransform==='uppercase' && parseFloat(c.letterSpacing)/parseFloat(c.fontSize) >= 0.05 && e.textContent.trim().length < 40; }).length;
 // radii, shadows
 const boxes = [...document.querySelectorAll('div,section,article,aside,a,button,img,li')].filter(e => { const r = e.getBoundingClientRect(); return vis(e) && r.width>60 && r.height>40; }).slice(0,800);
 const radii = []; out.glow = []; out.stacked = 0;
 boxes.forEach(b => { const c = getComputedStyle(b); const r = parseFloat(c.borderTopLeftRadius);
   const hasSurface = c.backgroundColor!=='rgba(0, 0, 0, 0)' || c.boxShadow!=='none' || parseFloat(c.borderTopWidth)>0;
   if (hasSurface && r>0) radii.push(Math.round(r));
   if (c.boxShadow!=='none') { const parts = c.boxShadow.split(/,(?![^(]*\))/);
     parts.forEach(s => { const col = rgb(s); const nums = s.replace(/rgba?\([^)]*\)/,'').match(/-?[\d.]+px/g)||[]; const blur = nums[2]?parseFloat(nums[2]):0;
       if (col && blur>=15) out.glow.push({col: col.slice(0,3), blur});
       if (blur>=24 && parseFloat(c.borderTopWidth)>0 && parseFloat(c.borderTopWidth)<=1) out.stacked++; }); } });
 out.radii = radii;
 // hidden at rest
 out.hidden = [...document.querySelectorAll('h1,h2,h3,p,li')].filter(e => { const c = getComputedStyle(e); return e.textContent.trim().length>10 && (parseFloat(c.opacity)<0.05) && e.getBoundingClientRect().height>0; }).length;
 // targets
 out.smallTargets = [...document.querySelectorAll('a,button,input,select,[role=button]')].filter(vis).filter(e => { const r = e.getBoundingClientRect();
   const inline = getComputedStyle(e).display==='inline' && e.closest('p,li'); return !inline && (r.width<24 || r.height<24); }).length;
 out.overflow = document.documentElement.scrollWidth > innerWidth + 2;
 out.brokenImgs = [...document.images].filter(i => i.complete && i.naturalWidth===0).length;
 return out;
}
"""

def scan_render(target, rep, cfg, outdir):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        rep.incomplete.append("render: playwright not installed (pip install playwright)"); return
    url = target if re.match(r"^https?://|^file://", target) else "file://" + os.path.abspath(target)
    os.makedirs(outdir, exist_ok=True)
    errors = []
    try:
        with sync_playwright() as p:
            exe = cfg.get("chrome_path") or next((c for c in ["/usr/bin/google-chrome","/usr/bin/chromium","/usr/bin/chromium-browser",
                   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] if os.path.exists(c)), None)
            br = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
            data = {}
            for w in (1440, 1280, 768, 375):
                pg = br.new_page(viewport={"width": w, "height": 900})
                pg.on("pageerror", lambda e: errors.append(str(e)[:120]))
                pg.goto(url, wait_until="networkidle", timeout=45000)
                pg.wait_for_timeout(400)
                pg.screenshot(path=os.path.join(outdir, f"shot-{w}.png"), full_page=True)
                d = pg.evaluate(RENDER_JS); data[w] = d; pg.close()
            br.close()
    except Exception as e:
        rep.incomplete.append(f"render failed: {e}"[:200]); return
    D = data[1440]; where = f"render:{target}"
    # typography
    if D["h1Font"] and D["h1Font"] in DEFAULT_FONTS and D["bodyFont"] in DEFAULT_FONTS:
        rep.add("T-01", where, f"h1 '{D['h1Font']}' + body '{D['bodyFont']}'")
    if D["h1Font"] in TEMPLATED_DISPLAY: rep.add("T-02", where, f"h1 font '{D['h1Font']}'")
    if D["h1Spans"]: rep.add("T-03", where, f"h1 span set apart: {D['h1Spans'][:2]}")
    if D["eyebrows"] >= 3: rep.add("T-04", where, f"{D['eyebrows']} uppercase tracked labels above headings")
    if D["h1Px"] > 0.08 * D["vw"]: rep.add("T-08", where, f"h1 {D['h1Px']:.0f}px at {D['vw']}px wide")
    ladder = {12,14,16,18,20,24,30,36,48,60,72}
    if len(D["sizes"]) >= 4 and set(D["sizes"]) <= ladder: rep.add("T-06", where, f"sizes {sorted(D['sizes'])}")
    if len(D["sizes"]) < 3 or len(D["weights"]) < 2: rep.add("T-07", where, f"{len(D['sizes'])} sizes, {len(D['weights'])} weights")
    b = D.get("body")
    if b:
        if b["px"] < 16 or b["lh"] < 1.3 or b["ch"] > 85: rep.add("T-10", where, f"body {b['px']:.0f}px, line-height {b['lh']:.2f}, ~{b['ch']:.0f}ch")
        if b["w"] >= 600: rep.add("T-12", where, f"body weight {b['w']}")
    # layout
    if D["pillBeforeH1"] and D["h1Align"] == "center": rep.add("L-01", where, f"pill '{D['pillBeforeH1']}' above centered h1")
    c, e = D["centered"]
    if e >= 5 and c / e > 0.7: rep.add("L-06", where, f"{c}/{e} text blocks centered")
    if data[375]["overflow"]: rep.add("L-12", where, "horizontal overflow at 375px")
    # color
    accents = [x for x in D["buttonBgs"] if oklch(tuple(x))[1] > 0.06] or [x for x in D["links"] if oklch(tuple(x))[1] > 0.06]
    if any(is_purple(tuple(a)) for a in accents): rep.add("C-01", where, f"accent {accents[0]} in purple band")
    bg = tuple(D["bodyBg"])
    if is_cream(bg):
        rep.add("C-05", where, f"page background rgb{bg} in cream band")
        if any(band(tuple(a)) in ("terracotta", "red", "yellow") for a in accents): rep.add("C-06", where, "warm clay/brass accent on cream")
        if any(band(tuple(a)) == "teal" or band(tuple(a)) == "green" for a in accents): rep.add("C-08", where, "teal/sage accent on cream")
    if oklch(bg)[0] < 0.15 and len({band(tuple(a)) for a in accents}) == 1 and accents and oklch(tuple(accents[0]))[1] > 0.2:
        rep.add("C-07", where, "near-black page + one saturated accent")
    if any(oklch(tuple(g["col"]))[1] > 0.10 for g in D["glow"]): rep.add("C-04", where, "saturated glow shadow")
    if D["stacked"]: rep.add("K-03", where, f"{D['stacked']} elements with hairline border + wide shadow")
    # radii
    r = D["radii"]
    if len(r) >= 8:
        top, n = Counter(r).most_common(1)[0]
        distinct = {x for x in r if x > 0}
        if n / len(r) > 0.8 and top >= 12: rep.add("K-02", where, f"radius {top}px on {n}/{len(r)} surfaces")
        elif len([k for k, v in Counter(r).items() if v >= 3]) > 2: rep.add("K-02", where, f"{len(distinct)} radius values in use")
    # contrast
    fails = []
    for t in D["contrast"]:
        if t["a"] < 0.99: continue
        cr = contrast(tuple(t["fg"]), tuple(t["bg"]))
        large = t["px"] >= 24 or (t["px"] >= 18.66 and t["bold"])
        need = 3.0 if large else 4.5
        if cr < need: fails.append(f"'{t['t']}' {cr:.2f}:1 (needs {need})")
    if fails: rep.add("Q-01", where, f"{len(fails)} text elements fail: " + "; ".join(fails[:3]))
    if D["hidden"]: rep.add("M-01", where, f"{D['hidden']} text elements invisible at rest")
    if data[375]["smallTargets"]: rep.add("Q-04", where, f"{data[375]['smallTargets']} targets under 24px at 375px")
    if D["brokenImgs"] or errors: rep.add("Q-12", where, f"{D['brokenImgs']} broken images; {len(errors)} script errors")
    rep.rendered = True

# ---------------------------------------------------------------- verdict
def verdict(rep, cfg):
    live = [f for f in rep.findings if not f["waived"]]
    by_cat = defaultdict(set)
    for f in live:
        if f["category"] in VISUAL_CATS and f["severity"] in ("P0", "P1"): by_cat[f["category"]].add(f["rule"])
    escalated = []
    for cat, ids in by_cat.items():
        if len(ids) >= 3:
            for f in live:
                if f["category"] == cat and f["severity"] == "P1": f["severity"] = "P0"; f["escalated"] = True
            escalated.append(cat)
    visual = {f["rule"] for f in live if f["category"] in VISUAL_CATS and f["severity"] in ("P0", "P1")}
    vs = len(visual); vlevel = "Low" if vs <= 1 else "Medium" if vs <= 3 else "High"
    copy_raw = sum(COPY_WEIGHTS.get(f["rule"], 0) for f in live if f["category"] == "copy")
    copy_score = min(100, round(copy_raw * 1000 / max(rep.words, 300))) if rep.words else 0
    p0 = [f for f in live if f["severity"] == "P0"]; p1 = [f for f in live if f["severity"] == "P1"]
    complete = getattr(rep, "rendered", False) and not rep.incomplete
    if p0 or p1 or vlevel != "Low" or copy_score >= 35: v = "HOLD"
    elif not complete: v = "HOLD (incomplete: " + ("; ".join(rep.incomplete) or "render not run") + ")"
    else: v = "SHIP (pending fresh-eyes J-rule review)"
    return {"verdict": v, "visual_tells": vs, "visual_level": vlevel, "copy_score": copy_score,
            "p0": len(p0), "p1": len(p1), "p2": len([f for f in live if f["severity"] == "P2"]),
            "waived": len([f for f in rep.findings if f["waived"]]), "clusters_escalated": escalated,
            "words_scanned": rep.words, "rendered": getattr(rep, "rendered", False), "incomplete": rep.incomplete}

def main():
    ap = argparse.ArgumentParser(description="deslop-web deterministic scanner")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--config", default=None, help="deslop.config.json (waivers, brand palette, fonts, custom patterns)")
    ap.add_argument("--render", default=None, help="URL or HTML file to render with Playwright")
    ap.add_argument("--out", default=".deslop", help="output dir for screenshots and report")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    cfg = {}
    cpath = a.config or ("deslop.config.json" if os.path.exists("deslop.config.json") else None)
    if cpath:
        with open(cpath) as fh: cfg = json.load(fh)
    pdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "presets")
    for name in cfg.get("presets", []):
        pf = os.path.join(pdir, f"{name}.json")
        if os.path.exists(pf):
            with open(pf) as fh: pre = json.load(fh)
            for k, v in pre.items():
                if isinstance(v, list): cfg[k] = list(cfg.get(k, [])) + v
                elif k not in cfg and not k.startswith("_"): cfg[k] = v
    rep = Report(cfg); para_bank = []
    if not a.paths and not a.render: ap.error("give a PATH and/or --render")
    for fp in iter_files(a.paths, cfg.get("ignore_paths", [])):
        try:
            with open(fp, encoding="utf-8", errors="ignore") as fh: raw = fh.read()
        except OSError: continue
        if len(raw) > 2_000_000: continue
        scan_static(fp, raw, rep, cfg, para_bank)
    finish_static(rep, cfg, para_bank)
    if a.render: scan_render(a.render, rep, cfg, a.out)
    else: rep.incomplete.append("render not run (R rules skipped)")
    # dedupe
    seen, uniq = set(), []
    for f in rep.findings:
        k = (f["rule"], f["where"], f["detail"])
        if k not in seen: seen.add(k); uniq.append(f)
    rep.findings = uniq
    summ = verdict(rep, cfg)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "scan.json"), "w") as fh: json.dump({"summary": summ, "findings": rep.findings}, fh, indent=1)
    if a.json:
        print(json.dumps({"summary": summ, "findings": rep.findings}, indent=1))
    else:
        print(f"\nVERDICT: {summ['verdict']}")
        print(f"Visual tells: {summ['visual_tells']} ({summ['visual_level']}) | Copy score: {summ['copy_score']}/100 | "
              f"P0 {summ['p0']} · P1 {summ['p1']} · P2 {summ['p2']} · waived {summ['waived']}")
        if summ["clusters_escalated"]: print("Clusters escalated to P0: " + ", ".join(summ["clusters_escalated"]))
        for inc in summ["incomplete"]: print("INCOMPLETE: " + inc)
        order = {"P0": 0, "P1": 1, "P2": 2}
        grouped = defaultdict(list)
        for f in sorted(rep.findings, key=lambda f: (order.get(f["severity"], 3), f["rule"])): grouped[f["category"]].append(f)
        for cat, fs in grouped.items():
            print(f"\n## {cat.upper()} ({len(fs)})")
            for f in fs[:40]:
                w = " [waived]" if f["waived"] else (" [escalated]" if f.get("escalated") else "")
                print(f"  {f['severity']} {f['rule']} {f['title']}{w}\n      {f['where']}  {f['detail']}")
            if len(fs) > 40: print(f"  … {len(fs)-40} more in {a.out}/scan.json")
    if summ["p0"] or summ["p1"] or summ["verdict"].startswith("HOLD") and not summ["incomplete"]:
        sys.exit(1)
    sys.exit(2 if summ["incomplete"] else 0)

if __name__ == "__main__":
    main()
