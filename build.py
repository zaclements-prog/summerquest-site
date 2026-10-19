import re, html, sys
src = open(sys.argv[1]).read()
out_dir = sys.argv[2]

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w.])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)', r'<a href="mailto:\1">\1</a>', t)
    return t

lines = src.split('\n')
body, para, lst = [], [], None
def flush():
    global para, lst
    if para: body.append('<p>' + inline(' '.join(para)) + '</p>'); para = []
    if lst: body.append(f'<{lst[0]}>' + ''.join(f'<li>{inline(i)}</li>' for i in lst[1]) + f'</{lst[0]}>'); lst = None
title = 'Privacy policy'
for ln in lines:
    s = ln.rstrip()
    m_ul = re.match(r'^- (.*)', s); m_ol = re.match(r'^\d+\. (.*)', s)
    if s.startswith('# '):
        flush(); title = s[2:]; continue
    if s.startswith('## '):
        flush(); body.append('<h2>' + inline(s[3:]) + '</h2>'); continue
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

CSS = """
:root{--bg:#fff8ec;--card:#fffdf8;--ink:#3a2c38;--soft:#6b5a66;--line:#ead9c0;--accent:#c2453b}
@media (prefers-color-scheme: dark){:root{--bg:#1f1a1e;--card:#2a2328;--ink:#f3e9df;--soft:#c9b9c3;--line:#463b42;--accent:#ff8a7a}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:720px;margin:0 auto;padding:32px 16px 64px}
header{display:flex;align-items:center;gap:14px;margin-bottom:8px}
header img{width:56px;height:56px;border-radius:14px}
h1{font-size:1.9rem;line-height:1.2;margin:0}h2{font-size:1.25rem;margin:2rem 0 .5rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:8px 24px 16px;margin-top:16px}
a{color:var(--accent)}li{margin:.35rem 0}footer{margin-top:32px;color:var(--soft);font-size:.9rem}
"""
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SummerQuest Privacy Policy</title><meta name="description" content="Privacy policy for SummerQuest, a learning game for children aged 7 to 9. Nothing leaves the tablet.">
<link rel="icon" href="../icon.png"><style>{CSS}</style></head><body><main>
<header><img src="../icon.png" alt=""><h1>{html.escape(title)}</h1></header>
<div class="card">{''.join(body)}</div>
<footer><a href="../">SummerQuest</a></footer>
</main></body></html>
"""
open(f'{out_dir}/privacy/index.html','w').write(page)
index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SummerQuest</title><meta name="description" content="SummerQuest: a summer learning island for kids finishing 2nd, 3rd or 4th grade.">
<link rel="icon" href="icon.png"><style>{CSS}</style></head><body><main>
<header><img src="icon.png" alt=""><h1>SummerQuest</h1></header>
<div class="card"><p>A summer learning island for kids finishing 2nd, 3rd or 4th grade: short spoken lessons with moving pictures, then math, reading, writing and science games.</p>
<p>No ads, no in-app purchases, no accounts, and no internet needed. Everything stays on the tablet.</p>
<ul><li><a href="privacy/">Privacy policy</a></li><li>Contact: <a href="mailto:zaclements@gmail.com">zaclements@gmail.com</a></li></ul></div>
</main></body></html>
"""
open(f'{out_dir}/index.html','w').write(index)
print('built', len(body), 'blocks')
