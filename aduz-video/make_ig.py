"""Generates episodeN_ig.html (Instagram Reels version, 28-qism design) for episodes 1–26 from episodeN.html.
The episode's own script runs unchanged; reel.js + ig_config.js + igwrap.js are appended after it."""
import re, sys

RENAME = {16: [('MONO', 'MONO16'), ('mono', 'mono16')], 22: [('card', 'card22')]}

def build(n):
    s = open(f'episode{n}.html', encoding='utf-8').read()
    for a, b in RENAME.get(n, []):
        s = re.sub(r'(?<![\w.$])' + a + r'(?![\w$])', b, s)
    s = s.replace(f'<title>ADUZ {n}-qism</title>', f'<title>ADUZ {n}-qism — Instagram</title>')
    tail = ''
    if 'src="reel.js"' not in s:
        tail += '<script src="reel.js"></script>\n'
    tail += f'<script>window.IG_EP = {n}; window.IG_CAPTIONS = CAPTIONS.slice(); CAPTIONS.length = 0;</script>\n<script src="ig_config.js"></script>\n<script src="igbot.js"></script>\n<script src="igwrap.js"></script>\n'
    s = s.replace('</body>', tail + '</body>', 1)
    open(f'episode{n}_ig.html', 'w', encoding='utf-8').write(s)

for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else range(1, 27)):
    build(n)
    print('built', n)
