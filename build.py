"""Build the public pages from the privacy policy markdown.

usage: python3 build.py ../summerquest/docs/store/privacy-policy.md .

Writes privacy/index.html and index.html. Shared styles live in style.css and the
Fredoka font in fonts/, so the pages load nothing from other websites.
"""
import html
import re
import sys

src = open(sys.argv[1]).read()
out_dir = sys.argv[2]
EMAIL = 'zaclements@gmail.com'


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w.])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)', r'<a href="mailto:\1">\1</a>', t)
    return t


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


# ── parse: a preamble (title, effective date, who we are), then ## sections of blocks ──
title = 'Privacy policy'
pre, sections = [], []  # blocks are ('p', text) or ('ul' | 'ol', [items])
cur = pre
para, lst = [], None


def flush():
    global para, lst
    if para:
        cur.append(('p', ' '.join(para)))
        para = []
    if lst:
        cur.append(lst)
        lst = None


for ln in src.split('\n'):
    s = ln.rstrip()
    m_ul = re.match(r'^- (.*)', s)
    m_ol = re.match(r'^\d+\. (.*)', s)
    if s.startswith('# '):
        flush(); title = s[2:]; continue
    if s.startswith('## '):
        flush(); cur = []; sections.append((s[3:], cur)); continue
    if m_ul or m_ol:
        if para: flush()
        kind = 'ul' if m_ul else 'ol'
        if lst and lst[0] != kind: flush()
        if not lst: lst = (kind, [])
        lst[1].append((m_ul or m_ol).group(1)); continue
    if s.startswith('  ') and lst:
        lst[1][-1] += ' ' + s.strip(); continue
    if not s:
        flush(); continue
    if lst: flush()
    para.append(s.strip())
flush()

# preamble lines like "**Effective date:** October 18, 2026" become the hero's facts
facts = []
for kind, text in pre:
    m = re.match(r'\*\*(.+?):\*\*\s*(.*)', text) if kind == 'p' else None
    if m:
        facts.append((m.group(1), m.group(2)))
effective = next((v for k, v in facts if k.lower().startswith('effective')), '')

SECTION_ICONS = [  # first keyword found in the heading picks the icon
    ('short', '☀️'), ('stays', '📱'), ("doesn't", '🛡️'), ('grown', '🔒'), ('rights', '🧑‍🧒'),
    ('children', '🧸'), ('changes', '📝'), ('questions', '💌'),
]
TILE_ICONS = [  # the "doesn't do" list, keyed on the bold lead
    ('account', '👤'), ('ads', '📢'), ('analytics', '📊'), ('tracking', '📊'), ('sdk', '🧩'),
    ('leaves', '📡'), ('purchase', '💳'), ('chat', '💬'), ('link', '🔗'), ('location', '📍'),
]


def pick(table, text, default):
    t = text.lower()
    return next((icon for key, icon in table if key in t), default)


def block_html(b, tiles=False):
    kind, val = b
    if kind == 'p':
        return f'<p>{inline(val)}</p>'
    if tiles and kind == 'ul':
        out = []
        for item in val:
            m = re.match(r'\*\*(.+?)\*\*\s*(.*)', item)
            head, rest = (m.group(1), m.group(2)) if m else ('', item)
            out.append(
                f'<li class="tile"><span class="tile-icon" aria-hidden="true">{pick(TILE_ICONS, head, "🚫")}</span>'
                f'<div><strong>{inline(head)}</strong> {inline(rest)}</div></li>'
            )
        return '<ul class="tiles">' + ''.join(out) + '</ul>'
    cls = ' class="steps"' if kind == 'ol' else ''
    return f'<{kind}{cls}>' + ''.join(f'<li>{inline(i)}</li>' for i in val) + f'</{kind}>'


toc, body = [], []
for i, (head, blocks) in enumerate(sections):
    sid = slug(head)
    icon = pick(SECTION_ICONS, head, '•')
    toc.append(f'<li><a href="#{sid}"><span aria-hidden="true">{icon}</span>{inline(head)}</a></li>')
    tiles = "doesn't" in head.lower()
    cls = 'card summary' if i == 0 else 'card'
    inner = ''.join(block_html(b, tiles) for b in blocks)
    body.append(
        f'<section class="{cls}" id="{sid}"><h2><span class="h-icon" aria-hidden="true">{icon}</span>'
        f'{inline(head)}<a class="anchor" href="#{sid}" aria-label="Link to this section">#</a></h2>{inner}</section>'
    )

# the effective date is a pill; longer facts ("Who we are") read as a line under it
pills = [(k, v) for k, v in facts if len(v) <= 40]
lines = [(k, v) for k, v in facts if len(v) > 40]
fact_html = ''.join(f'<li><span>{inline(k)}</span>{inline(v)}</li>' for k, v in pills)
lede_html = ''.join(f'<p class="who"><strong>{inline(k)}:</strong> {inline(v)}</p>' for k, v in lines)

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="icon" href="{root}icon.png"><link rel="stylesheet" href="{root}style.css">
<link rel="preload" href="{root}fonts/fredoka-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
</head><body>"""

SKY = """<div class="sky" aria-hidden="true"><span class="sun"></span><span class="cloud c1"></span><span class="cloud c2"></span><span class="cloud c3"></span></div>"""
WAVE = """<svg class="wave" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true"><path d="M0 48C180 8 360 8 540 36s360 44 540 20 270-40 360-28v104H0z"/></svg>"""

page = HEAD.format(
    title='SummerQuest Privacy Policy', root='../',
    desc='Privacy policy for SummerQuest, a learning game for elementary-school children. Nothing leaves the tablet.',
) + f"""
<header class="hero">{SKY}
  <div class="hero-in">
    <a class="brand" href="../"><img src="../icon.png" alt="" width="40" height="40">SummerQuest</a>
    <h1>{html.escape(title)}</h1>
    <ul class="facts">{fact_html}</ul>{lede_html}
  </div>{WAVE}
</header>
<div class="layout">
  <nav class="toc" aria-label="On this page"><details open><summary>On this page</summary><ol>{''.join(toc)}</ol></details></nav>
  <main class="sections">{''.join(body)}</main>
</div>
<footer class="foot"><div>
  <a class="btn" href="../">← Back to SummerQuest</a>
  <p>{('Effective ' + html.escape(effective) + ' · ') if effective else ''}Questions? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p class="small">This page loads nothing from other websites and sets no cookies.</p>
</div></footer>
<script>
// highlight the section being read in the contents list
(function () {{
  var links = {{}}; document.querySelectorAll('.toc a').forEach(function (a) {{ links[a.hash.slice(1)] = a }})
  if (!('IntersectionObserver' in window)) return
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (!e.isIntersecting) return
      for (var k in links) links[k].classList.toggle('on', k === e.target.id)
    }})
  }}, {{ rootMargin: '-30% 0px -60% 0px' }})
  document.querySelectorAll('.sections section').forEach(function (s) {{ io.observe(s) }})
  if (window.matchMedia('(max-width: 979px)').matches) document.querySelector('.toc details').removeAttribute('open')
}})()
</script>
</body></html>
"""
open(f'{out_dir}/privacy/index.html', 'w').write(page)

SHOTS = [
    ('01-world', 'The island world, with houses, paths and a pet fox'),
    ('02-lesson-fractions', 'A spoken lesson: one out of four equal pizza slices'),
    ('08-k-listen-play', 'Kindergarten Listen and Play'),
    ('10-g5-long-division', 'Fifth-grade long division'),
]
shots = ''.join(
    f'<figure><img src="img/{f}.jpg" alt="{html.escape(a)}" width="960" height="600" loading="lazy"></figure>' for f, a in SHOTS
)
index = HEAD.format(
    title='SummerQuest', root='',
    desc='SummerQuest: a summer learning island for kids from kindergarten to 5th grade.',
) + f"""
<header class="hero home">{SKY}
  <div class="hero-in">
    <img class="app-icon" src="icon.png" alt="" width="96" height="96">
    <h1 class="logo">SummerQuest</h1>
    <p class="lede">A summer learning island for kids from kindergarten to 5th grade: short spoken lessons with moving pictures, then math, reading, writing and science games.</p>
    <ul class="chips"><li>No accounts</li><li>No internet needed</li><li>No ads</li><li>Everything stays on the tablet</li></ul>
  </div>{WAVE}
</header>
<main class="home-main">
  <div class="shots">{shots}</div>
  <div class="card links">
    <a class="btn" href="privacy/">Privacy policy →</a>
    <p>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </div>
</main>
</body></html>
"""
open(f'{out_dir}/index.html', 'w').write(index)
print('built', len(sections), 'sections')
