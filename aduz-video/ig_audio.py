"""Instagram Reels audio for episodes 1–26: the episode's own mix (build/episodeN.wav) + the IG layer's sounds
(hook hit on frame 0, orange/lime cut whooshes, violet card ticks, result hit, identity letters, loop riser).
Usage: python3 ig_audio.py N   →  build/episodeN_ig.wav"""
import sys, wave, json, re
import numpy as np
import audio as A

def cfg(n):
    js = open('ig_config.js', encoding='utf-8').read()
    m = re.search(r'\n  %d: \{(.*?)\},?\n(?:  \d+:|\};)' % n, js, re.S)
    body = m.group(1)
    return {k: ('null' not in re.search(k + r': ([^\]]*?\]|null)', body).group(1)) for k in ('cut1', 'cut2', 'card', 'res')}

def cues(n, c=None):
    c = c or cfg(n); old = n <= 3          # 1–3 have no 8.5 / 18.5 hits of their own
    q = [(0.0, "sfx.boom_sub", 0.95, 0, 0.3, 0, "HOOK", None), (0.0, "sfx.bass_drop", 0.7, 0, 0.3, 0, "", None),
         (0.12, "sfx.bass_drop", 0.5, 0, 0.3, 0, "", 5), (0.25, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "", None),
         (1.45, "sfx.glitch_short", 0.4, 0, 0.15, 0, "", None), (1.5, "sfx.swipe", 0.3, 0, 0.15, 0, "", None)]
    if c['cut1']:
        q += [(8.45, "sfx.whoosh_low", 0.3, 0, 0.2, 0, "", None)]
        if old: q += [(8.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "", None), (8.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "", None)]
    if c['cut2']:
        q += [(18.45, "sfx.whoosh_low", 0.3, 0, 0.3, 0, "", None), (18.6, "sfx.thump", 0.4, 0, 0.25, 0, "", None)]
        if old: q += [(18.5, "sfx.boom_sub", 0.7, 0, 0.35, 0, "", None)]
    if c['card']:
        q += [(20.0, "sfx.shimmer", 0.22, 0, 0.3, 0.2, "", None)] + [(20.4 + i * .3, "sfx.tick_hi", 0.2, -0.3 + 0.3 * i, 0.25, 0.2, "", [0, 4, 7][i]) for i in range(3)]
        q += [(21.3, "sfx.pop_short", 0.25, 0, 0.3, 0.2, "", 7)]
    if c['res']:
        q += [(22.1, "sfx.bass_drop", 0.4, 0, 0.3, 0, "", 5), (22.1, "sfx.shimmer", 0.18, 0, 0.3, 0.2, "", None)]
    q += [(27.45 + i * .1, "sfx.thump", 0.26, -0.45 + 0.3 * i, 0.2, 0, "", None) for i in range(4)]
    q += [(27.8, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "", None), (28.0, "sfx.type_burst", 0.22, 0, 0.15, 0, "", None),
          (28.5, "sfx.bass_drop", 0.3, 0, 0.3, 0, "", 7), (30.8, "sfx.riser_click", 0.3, 0, 0, 0, "", None),
          (31.4, "sfx.whoosh_low", 0.3, 0, 0.2, 0, "", None), (31.4, "sfx.glitch_short", 0.25, 0, 0.15, 0, "", None)]
    return q

def main(n):
    with wave.open(f'build/episode{n}.wav') as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(float) / 32768
    M = A.MixerPro(120)
    A.render_cues(M, cues(n))
    o = M.render()[:len(x)]
    o = o / (np.max(np.abs(o)) + 1e-9) * 0.8
    y = x.copy(); y[:len(o)] += o
    y /= np.max(np.abs(y)) / 0.89
    y *= np.clip((len(y) / sr - np.arange(len(y)) / sr) / 0.02, 0, 1)[:, None]
    with wave.open(f'build/episode{n}_ig.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype(np.int16).tobytes())
    print('wrote', n)

if __name__ == '__main__':
    for n in map(int, sys.argv[1:]): main(n)
