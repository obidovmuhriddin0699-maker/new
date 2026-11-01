"""Instagram audio for the "botga mos" versions (eps in IGBOT_EPS, ig_config.js): the episode's problem part
(score + its own cues before 10.9 s) is kept; from 10.95 s the cues follow the Target reklama bot demo
(igbot.js: screen slides, taps, typing, payment success, focus callouts, NATIJA card), then the IG layer
(ig_audio.cues). Eps 2–3 (v1 audio) keep their own wav up to 10.9 s and crossfade into a score_7 bed.
Usage: python3 bot_audio.py N   →  build/episodeN_ig.wav"""
import sys, wave, json, inspect, subprocess
import numpy as np
import audio as A
import ig_audio as IGA

CUT = 10.9

def config(n):
    js = "global.window={};require('./ig_config.js');process.stdout.write(JSON.stringify(window.IGCFG[%d]))" % n
    return json.loads(subprocess.check_output(['node', '-e', js]))

def C(at, name, gain, pan=0, verb=0.2, arg=None):
    return (round(at, 3), name, gain, pan, verb, 0, "", arg)

def bot_cues(cfg):
    B, q = cfg['bot'], [C(10.95, "sfx.whoosh_soft", 0.3), C(11.0, "ui.popup", 0.22)]
    seq = B['seq']
    for k, (name, a, b, o) in enumerate(seq):
        o = o or {}
        if k: q.append(C(a, "sfx.swipe", 0.18, 0.2 * (-1) ** k, 0.15))
        tap = lambda at, g=0.3: q.append(C(at, "ui.tap", g, 0, 0.1)) if a <= at < b else None
        if name == 'menu':
            tap(a + (b - a) * .55); q.append(C(a + (b - a) * .55 + .1, "sfx.notify_pop", 0.16))
        elif name in ('region', 'category'):
            q += [C(a + i * .05, "sfx.tick", 0.08, -0.4 + 0.16 * i, 0.1) for i in range(6)]
            tap(a + (b - a) * .6)
        elif name == 'channel':
            q.append(C(a + .05, "sfx.pop_swish", 0.18))
            chk = o.get('check', a + (b - a) * .45); ok = o.get('confirm', a + (b - a) * .8)
            if chk < b: tap(chk); q.append(C(chk + .05, "sfx.tick_hi", 0.18, 0.3, 0.2, 7))
            if ok < b: tap(ok, 0.34); q.append(C(ok + .05, "sfx.whoosh_soft", 0.18))
        elif name == 'create':
            steps = o.get('steps') or [1, 1, 1 if o.get('media') else 0]
            dt = (b - a) / (len(steps) + .3)
            for i, ans in enumerate(steps):
                qa, aa = a + i * dt, a + i * dt + dt * .5
                q.append(C(qa, "sfx.notify_pop", 0.15, -0.3))
                if ans and aa < b: q.append(C(aa, "sfx.pop_short", 0.14, 0.3) if (i == 2) else C(aa, "fx.type", 0.14, 0.3))
        elif name == 'preview':
            q.append(C(a + .05, "sfx.notify_pop", 0.18))
            ok = o.get('ok', b - .3)
            tap(ok)
        elif name == 'pay':
            click = o.get('click', a + (b - a) * .3); s2 = o.get('sched', click + (b - click) * .6)
            q.append(C(a + .05, "sfx.notify_pop", 0.16)); tap(click)
            q += [C(click + .25, "ui.success", 0.26), C(s2, "fx.ding", 0.2, 0.2)]
        elif name == 'campaigns':
            q += [C(a + .4, "sfx.notify_pop", 0.18), C(a + .45, "fx.tick", 0.12)]
        elif name == 'owner':
            t1, t2 = a + (b - a) * .3, a + (b - a) * .72
            q.append(C(a + .05, "sfx.notify_pop", 0.16)); tap(t1); q.append(C(t1 + .3, "sfx.notify_pop", 0.16)); tap(t2)
    for a, b, *_ in B.get('focus', []):
        q.append(C(a, "sfx.swoosh_text", 0.16, -0.2))
    # NATIJA card (igbot result)
    q += [C(23.0, "sfx.type_burst", 0.18), C(23.05, "sfx.thump", 0.34), C(23.1, "sfx.whoosh_soft", 0.2)]
    for i in range(3):
        q += [C(23.6 + i * .35, "fx.strike", 0.14, -0.3), C(23.8 + i * .35, "sfx.tick_hi", 0.18, 0.3, 0.2, [0, 4, 7][i])]
    q += [C(25.0, "sfx.shimmer", 0.2, 0, 0.3)] + [C(25.2 + i * .25, "sfx.pop_short", 0.2, -0.4 + 0.4 * i, 0.2, [0, 4, 7][i]) for i in range(3)]
    return q

def base_mix(n, extra):
    if n in A.V2:
        src = inspect.getsource(A.V2[n]).replace(f"render_cues(M, CUES_{n})", f"render_cues(M, [c for c in CUES_{n} if c[0] < {CUT}] + _BOT)")
        assert '_BOT' in src
        ns = dict(vars(A)); ns['_BOT'] = extra
        exec(src, ns)
        return ns[f'render_{n}']()
    with wave.open(f'build/episode{n}.wav') as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(float) / 32768
    M = A.MixerPro(120); M.width = [(0, 0.75), (32, 0.75)]
    A.score_7(M); A.render_cues(M, extra)
    bed = M.render()[:len(x)]
    bed *= np.clip((A.DUR - A.t[:len(bed)]) / 1.4, 0, 1)[:, None]
    i0, i1 = int(CUT * A.SR), int((CUT + .15) * A.SR)
    seg = slice(int(12 * A.SR), int(22 * A.SR))
    bed *= np.sqrt(np.mean(x[int(1.6 * A.SR):i0] ** 2) / (np.mean(bed[seg] ** 2) + 1e-12))
    f = np.clip((np.arange(len(x)) - i0) / (i1 - i0), 0, 1)[:, None]
    return x * (1 - f) + bed * f

def main(n):
    cfg = config(n)
    mix = base_mix(n, bot_cues(cfg))
    mix /= np.max(np.abs(mix)) / 0.89
    flags = {k: bool(cfg.get(k)) for k in ('cut1', 'cut2', 'card', 'res')}
    M = A.MixerPro(120)
    A.render_cues(M, IGA.cues(n, flags))
    o = M.render()[:len(mix)]
    o = o / (np.max(np.abs(o)) + 1e-9) * 0.8
    y = mix.copy(); y[:len(o)] += o
    y /= np.max(np.abs(y)) / 0.89
    sr = A.SR
    y *= np.clip((len(y) / sr - np.arange(len(y)) / sr) / 0.02, 0, 1)[:, None]
    with wave.open(f'build/episode{n}_ig.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype(np.int16).tobytes())
    print('wrote', n)

if __name__ == '__main__':
    for n in map(int, sys.argv[1:]): main(n)
