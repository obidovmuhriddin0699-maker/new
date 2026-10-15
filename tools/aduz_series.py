"""ADUZ seriya shabloni (28 qismlik ssenariy uchun) — Reels + karusel.
Tuzilish (rejissorlik ssenariysi bo'yicha):
  HOOK  — qism raqami + sarlavha (Words Up)
  MUAMMO — qorong'i, qizil chigal chiziqlar, xatolik chiplari, buzzer, tarang fon (Characters Down + Text Flicker)
  YECHIM — yorqin ADUZ bot interfeysi, yashil tasdiqlar, klik/swoosh (Color Bounce Up)
  NATIJA — o'sish grafigi, oltin nishon, cha-ching + ting, shior (Words Fade)
  CTA    — ADUZ, @Targetreklammabot, 'Izohga "BOT" deb yozing' (Text Flicker)
Ovoz: hammasi original sintez.
Ishlatish:
  python3 aduz_series.py config.json reel OUT.mp4      -> 1080x1920, 16 s
  python3 aduz_series.py config.json post OUT_DIR       -> 1080x1350 karusel, 5 slayd
Config: {"part": 1, "title": "...", "problem": "...", "problem_chips": [3 ta], "solution": "...",
         "ui_title": "...", "ui_rows": [[nom, izoh] x4], "result": "...", "tagline": "...", "cta": "..."}
"""
import sys, os, json, subprocess
import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import wavfile
from playwright.sync_api import sync_playwright

CFG = json.load(open(sys.argv[1])); MODE = sys.argv[2]; OUT = sys.argv[3]
FPS = 30; DUR = 16.0
T = dict(hook=0.0, prob=1.4, sol=5.4, res=10.6, cta=13.4, end=DUR)
RED, GREEN, GOLD, TEAL = "#FF3B4E", "#22C55E", "#E8B85C", "#2AABEE"

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:var(--H);overflow:hidden;font-family:'Inter Display','Inter',sans-serif;color:#fff;background:#0B1016}
.sc{position:absolute;inset:0;display:none;overflow:hidden}
.lbl{position:absolute;left:80px;font-size:30px;font-weight:800;letter-spacing:.32em;display:flex;align-items:center;gap:18px}
.lbl i{width:16px;height:16px;border-radius:50%}
.big{font-weight:900;letter-spacing:-.03em;line-height:1.02}
.ch{display:inline-block;white-space:pre}
.wn{display:inline-block;white-space:nowrap}
.w{display:inline-block;margin-right:.24em}
#hook{background:radial-gradient(90% 60% at 50% 40%,#16303D,#0B1016)}
#prob{background:radial-gradient(80% 60% at 50% 45%,#2A0E14,#0A0A0D)}
#sol{background:linear-gradient(#F5F7FA,#E7ECF1);color:#0E1520}
#res{background:radial-gradient(80% 60% at 50% 45%,#1E2238,#0B0D18)}
#cta{background:radial-gradient(90% 60% at 50% 45%,#16303D,#0B1016)}
canvas{position:absolute;left:0;top:0}
.chip{position:absolute;left:80px;right:80px;display:flex;align-items:center;gap:22px;background:rgba(255,59,78,.12);border:2px solid rgba(255,59,78,.55);border-radius:26px;padding:28px 32px;font-size:40px;font-weight:700}
.chip b{flex:none;width:56px;height:56px;border-radius:50%;background:REDC;display:flex;align-items:center;justify-content:center;font-size:34px}
.phone{position:absolute;left:150px;width:780px;background:#fff;border-radius:56px;box-shadow:0 40px 90px rgba(14,21,32,.18),0 0 0 14px #0E1520}
.phone .hd{display:flex;align-items:center;gap:18px;padding:34px 38px;border-bottom:2px solid #EEF1F4}
.phone .av{width:76px;height:76px;border-radius:50%;background:TEALC;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:28px;color:#fff}
.phone .nm{font-size:34px;font-weight:800}.phone .sb{font-size:24px;color:#7A8594;font-weight:600}
.row{display:flex;align-items:center;gap:22px;margin:22px 30px;padding:24px 26px;border-radius:24px;background:#F3F6F9}
.row .ck{flex:none;width:60px;height:60px;border-radius:50%;background:GREENC;display:flex;align-items:center;justify-content:center}
.row .ck svg{width:34px;height:34px}
.row .t{font-size:34px;font-weight:800}.row .s{font-size:26px;color:#6B7684;font-weight:600;margin-top:4px}
.bar{height:20px;border-radius:10px;background:#E3E8EE;margin:12px 30px 34px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,GREENC,TEALC)}
#cur{position:absolute;width:70px;height:70px}
.badge{position:absolute;left:390px;width:300px;height:300px;border-radius:50%;border:10px solid GOLDC;display:flex;align-items:center;justify-content:center;box-shadow:0 0 80px rgba(232,184,92,.35)}
.badge svg{width:150px;height:150px}
.pill{display:inline-flex;align-items:center;justify-content:center;padding:28px 44px;border-radius:999px;font-size:44px;font-weight:800}
"""

CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHECKG = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="GOLDC" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
def chars(s):
    return " ".join('<span class="wn">' + "".join(f'<span class="ch">{esc(c)}</span>' for c in w) + '</span>'
                    for w in s.split(" "))
def words(s): return "".join(f'<span class="w">{esc(w)}</span>' for w in s.split())

C = CFG
rows = "".join(f'<div class="row"><div class="ck">{CHECK}</div><div><div class="t">{esc(a)}</div><div class="s">{esc(b)}</div></div></div>' for a, b in C["ui_rows"])
chips = "".join(f'<div class="chip"><b>✕</b>{esc(x)}</div>' for x in C["problem_chips"])

def reel_html():
    return f"""<html><head><meta charset="utf-8"><style>:root{{--H:1920px}}{CSS}</style></head><body>
<div class="sc" id="hook"><div class="lbl" style="top:700px;color:{TEAL}"><i style="background:{TEAL}"></i>ADUZ · {C['part']}-QISM</div>
 <div class="big" id="ht" style="position:absolute;left:80px;right:80px;top:780px;font-size:118px">{words(C['title'])}</div></div>
<div class="sc" id="prob"><canvas id="pc" width="1080" height="1920"></canvas>
 <div class="lbl" style="top:220px;color:{RED}"><i style="background:{RED}"></i>MUAMMO</div>
 <div class="big" id="pt" style="position:absolute;left:80px;right:80px;top:300px;font-size:96px">{chars(C['problem'])}</div>
 <div id="chips" style="position:absolute;left:0;right:0;top:980px">{chips}</div></div>
<div class="sc" id="sol"><div class="lbl" style="top:150px;color:#16A34A"><i style="background:{GREEN}"></i>YECHIM</div>
 <div class="big" id="st" style="position:absolute;left:80px;right:80px;top:220px;font-size:78px">{chars(C['solution'])}</div>
 <div class="phone" id="ph" style="top:560px"><div class="hd"><div class="av">AD</div><div><div class="nm">ADUZ</div><div class="sb">@Targetreklammabot · {esc(C['ui_title'])}</div></div></div>
  {rows}<div class="bar"><i id="bar"></i></div></div>
 <svg id="cur" viewBox="0 0 24 24"><path d="M3 2l7 19 2.5-7.5L20 11z" fill="#0E1520" stroke="#fff" stroke-width="1.5"/></svg></div>
<div class="sc" id="res"><canvas id="rc" width="1080" height="1920"></canvas>
 <div class="lbl" style="top:220px;color:{GOLD}"><i style="background:{GOLD}"></i>NATIJA</div>
 <div class="big" id="rt" style="position:absolute;left:80px;right:80px;top:300px;font-size:92px">{words(C['result'])}</div>
 <div class="badge" id="bd" style="top:1120px">{CHECKG}</div>
 <div class="big" id="tg" style="position:absolute;left:60px;right:60px;top:1500px;text-align:center;font-size:62px;color:{GOLD}">{words(C['tagline'])}</div></div>
<div class="sc" id="cta"><div class="big" id="logo" style="position:absolute;left:0;right:0;top:640px;text-align:center;font-size:260px;letter-spacing:-.04em">ADUZ</div>
 <div id="ctasub" style="position:absolute;left:0;right:0;top:930px;text-align:center;font-size:40px;font-weight:700;color:#A9C3D1;letter-spacing:.06em">Telegram Advertising Marketplace</div>
 <div id="ctabot" style="position:absolute;left:0;right:0;top:1080px;text-align:center"><span class="pill" style="background:{TEAL}">@Targetreklammabot</span></div>
 <div id="ctac" style="position:absolute;left:0;right:0;top:1250px;text-align:center;font-size:52px;font-weight:800">{esc(C['cta'])}</div></div>
<script>
const T={json.dumps(T)};
const ease=t=>t<0?0:t>1?1:(t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2);
const out=t=>{{t=Math.max(0,Math.min(1,t));return 1-Math.pow(1-t,3)}};
const back=t=>{{t=Math.max(0,Math.min(1,t));const a=2.0,b=a+1;return 1+b*Math.pow(t-1,3)+a*Math.pow(t-1,2)}};
const seg=(t,a,b)=>Math.max(0,Math.min(1,(t-a)/(b-a)));
const lerp=(a,b,k)=>a+(b-a)*k; const $=id=>document.getElementById(id);
const S=[['hook','hook','prob'],['prob','prob','sol'],['sol','sol','res'],['res','res','cta'],['cta','cta','end']];
// precomputed scribbles
let rs=1; const rnd=()=>{{rs=(rs*16807)%2147483647;return rs/2147483647}};
const scr=[]; for(let i=0;i<14;i++){{const p=[];let x=rnd()*1080,y=500+rnd()*1300;for(let k=0;k<7;k++){{x+=(rnd()-.5)*520;y+=(rnd()-.5)*420;p.push([x,y])}}scr.push(p)}}
function wordsAnim(el,u,mode){{[...el.children].forEach((w,i)=>{{const k=out(seg(u,i*.09,i*.09+.35));
 if(mode=='up'){{w.style.opacity=k;w.style.transform=`translateY(${{(1-k)*70}}px)`}}
 else if(mode=='fade'){{w.style.opacity=k;w.style.filter=`blur(${{(1-k)*14}}px)`}} }})}}
function charsAnim(el,u,mode,sp){{[...el.querySelectorAll(".ch")].forEach((c,i)=>{{const k=seg(u,i*sp,i*sp+.28);
 if(mode=='down'){{const e=out(k);c.style.opacity=e;c.style.transform=`translateY(${{(e-1)*80}}px)`}}
 else if(mode=='bounce'){{const e=back(k);c.style.opacity=Math.min(1,k*3);c.style.transform=`translateY(${{(1-e)*60}}px)`;c.style.color=k<1?'TEALC':''}} }})}}
window.render=function(t){{
 let cur='hook'; S.forEach(([id,a,b])=>{{const on=t>=T[a]&&t<T[b];$(id).style.display=on?'block':'none';if(on)cur=id}});
 if(cur=='hook'){{wordsAnim($('ht'),t-.15,'up')}}
 if(cur=='prob'){{const u=t-T.prob; const g=$('pc').getContext('2d'); g.clearRect(0,0,1080,1920);
   const prog=seg(u,0,3.2); g.lineWidth=5; g.lineCap='round';
   scr.forEach((p,i)=>{{const n=Math.floor(prog*p.length*1.4-i*.15); if(n<1)return; g.strokeStyle=`rgba(255,59,78,${{.25+.25*(i%3)/2}})`; g.beginPath(); g.moveTo(p[0][0],p[0][1]);
     for(let k=1;k<Math.min(n,p.length);k++){{const [x0,y0]=p[k-1],[x1,y1]=p[k];g.quadraticCurveTo(x0,y0,(x0+x1)/2,(y0+y1)/2)}} g.stroke()}});
   charsAnim($('pt'),u,'down',.025);
   const fl=(u>2.9&&u<3.3)?(Math.floor(u*30)%3?1:.25):1; $('pt').style.opacity=fl;
   [...$('chips').children].forEach((c,i)=>{{const a=.9+i*.6,k=back(seg(u,a,a+.35)); const sh=Math.sin(u*70)*Math.exp(-(u-a)*8)*14*(u>a?1:0);
     c.style.top=(i*170)+'px'; c.style.opacity=Math.min(1,k*2); c.style.transform=`translateX(${{(1-k)*-200+sh}}px)`}});
   document.body.style.transform=(u>2.95&&u<3.15)?`translate(${{(Math.random()-.5)*10}}px,0)`:'none'}}
 else document.body.style.transform='none';
 if(cur=='sol'){{const u=t-T.sol; charsAnim($('st'),u,'bounce',.02);
   const pk=out(seg(u,.4,1.1)); $('ph').style.opacity=pk; $('ph').style.transform=`translateY(${{(1-pk)*240}}px) scale(${{.92+.08*pk}})`;
   [...document.querySelectorAll('.row')].forEach((r,i)=>{{const a=1.2+i*.7,k=back(seg(u,a,a+.4)); r.style.opacity=Math.min(1,k*2); r.style.transform=`translateX(${{(1-k)*120}}px)`;
     const ck=r.querySelector('.ck'); const c2=back(seg(u,a+.25,a+.55)); ck.style.transform=`scale(${{c2}})`}});
   $('bar').style.width=(100*ease(seg(u,1.2,4.3)))+'%';
   const cx=lerp(900,600,ease(seg(u,3.9,4.5))), cy=lerp(1750,1520,ease(seg(u,3.9,4.5))); $('cur').style.left=cx+'px'; $('cur').style.top=cy+'px';
   $('cur').style.opacity=u>3.8?1:0; $('cur').style.transform=`scale(${{u>4.55&&u<4.7?.8:1}})`}}
 if(cur=='res'){{const u=t-T.res; wordsAnim($('rt'),u,'up'); const g=$('rc').getContext('2d'); g.clearRect(0,0,1080,1920);
   const k=ease(seg(u,.3,1.6)); const pts=[[90,1020],[260,960],[420,980],[580,860],[740,790],[900,620],[1000,560]];
   g.lineWidth=12;g.lineCap='round';g.lineJoin='round';g.strokeStyle='GOLDC';g.beginPath();
   const n=pts.length-1, end=k*n; g.moveTo(...pts[0]);
   for(let i=1;i<=Math.ceil(end);i++){{const f=Math.min(1,end-(i-1));g.lineTo(lerp(pts[i-1][0],pts[i][0],f),lerp(pts[i-1][1],pts[i][1],f))}} g.stroke();
   g.globalAlpha=.12;g.lineTo(lerp(pts[Math.max(0,Math.ceil(end)-1)][0],1000,0),1100);g.globalAlpha=1;
   const b=back(seg(u,1.2,1.6)); $('bd').style.transform=`scale(${{b}})`; $('bd').style.opacity=Math.min(1,b*2);
   wordsAnim($('tg'),u-1.6,'fade')}}
 if(cur=='cta'){{const u=t-T.cta; const l=out(seg(u,0,.5)); $('logo').style.opacity=l; $('logo').style.letterSpacing=lerp(.2,-.04,l)+'em';
   $('ctasub').style.opacity=seg(u,.35,.7); const p=back(seg(u,.6,1.0)); $('ctabot').style.transform=`scale(${{p}})`; $('ctabot').style.opacity=Math.min(1,p*2);
   const fl=u<1.1?0:(u<1.6?(Math.floor(u*24)%2?1:.15):1); $('ctac').style.opacity=fl}}
}}
</script></body></html>"""

def post_html(i):
    base = f"<html><head><meta charset='utf-8'><style>:root{{--H:1350px}}{CSS} .sc{{display:block}}</style></head><body>"
    foot = f"<div style='position:absolute;left:80px;right:80px;bottom:60px;display:flex;justify-content:space-between;font-size:26px;font-weight:700;opacity:.7'><span>ADUZ · {C['part']}-qism</span><span>{i+1} / 5</span></div>"
    if i == 0:
        body = f"""<div class="sc" id="hook"><div class="lbl" style="top:420px;color:{TEAL}"><i style="background:{TEAL}"></i>ADUZ · {C['part']}-QISM</div>
        <div class="big" style="position:absolute;left:80px;right:80px;top:500px;font-size:112px">{esc(C['title'])}</div>
        <div style="position:absolute;left:80px;top:1060px;font-size:34px;font-weight:700;color:#A9C3D1">Suring →</div>{foot}</div>"""
    elif i == 1:
        ch = "".join(f'<div class="chip" style="position:relative;left:0;right:0;margin:0 80px 26px"><b>✕</b>{esc(x)}</div>' for x in C["problem_chips"])
        body = f"""<div class="sc" id="prob"><div class="lbl" style="top:130px;color:{RED}"><i style="background:{RED}"></i>MUAMMO</div>
        <div class="big" style="position:absolute;left:80px;right:80px;top:200px;font-size:84px">{esc(C['problem'])}</div>
        <div style="position:absolute;left:0;right:0;top:640px">{ch}</div>{foot}</div>"""
    elif i == 2:
        body = f"""<div class="sc" id="sol"><div class="lbl" style="top:110px;color:#16A34A"><i style="background:{GREEN}"></i>YECHIM</div>
        <div class="big" style="position:absolute;left:80px;right:80px;top:170px;font-size:66px">{esc(C['solution'])}</div>
        <div class="phone" style="top:430px;transform:scale(.86);transform-origin:50% 0"><div class="hd"><div class="av">AD</div><div><div class="nm">ADUZ</div><div class="sb">@Targetreklammabot · {esc(C['ui_title'])}</div></div></div>{rows}<div class="bar"><i style="width:100%"></i></div></div>
        <div style="position:absolute;left:80px;right:80px;bottom:60px;display:flex;justify-content:space-between;font-size:26px;font-weight:700;color:#0E1520;opacity:.6"><span>ADUZ · {C['part']}-qism</span><span>3 / 5</span></div></div>"""
    elif i == 3:
        body = f"""<div class="sc" id="res"><div class="lbl" style="top:130px;color:{GOLD}"><i style="background:{GOLD}"></i>NATIJA</div>
        <div class="big" style="position:absolute;left:80px;right:80px;top:200px;font-size:86px">{esc(C['result'])}</div>
        <div class="badge" style="top:660px;width:260px;height:260px;left:410px">{CHECKG}</div>
        <div class="big" style="position:absolute;left:60px;right:60px;top:1000px;text-align:center;font-size:58px;color:{GOLD}">{esc(C['tagline'])}</div>{foot}</div>"""
    else:
        body = f"""<div class="sc" id="cta"><div class="big" style="position:absolute;left:0;right:0;top:330px;text-align:center;font-size:240px;letter-spacing:-.04em">ADUZ</div>
        <div style="position:absolute;left:0;right:0;top:600px;text-align:center;font-size:38px;font-weight:700;color:#A9C3D1">Telegram Advertising Marketplace</div>
        <div style="position:absolute;left:0;right:0;top:730px;text-align:center"><span class="pill" style="background:{TEAL}">@Targetreklammabot</span></div>
        <div style="position:absolute;left:0;right:0;top:900px;text-align:center;font-size:50px;font-weight:800">{esc(C['cta'])}</div>{foot}</div>"""
    return base + body + "</body></html>"

def fix(h): return h.replace("REDC", RED).replace("GREENC", GREEN).replace("GOLDC", GOLD).replace("TEALC", TEAL)

if MODE == "post":
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i in range(5):
            pg.set_content(fix(post_html(i))); pg.wait_for_timeout(200)
            pg.screenshot(path=f"{OUT}/slayd_{i+1}.jpg", type="jpeg", quality=92)
        b.close()
    print("done", OUT); sys.exit()

WORK = OUT + "_work"; os.makedirs(f"{WORK}/f", exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_content(fix(reel_html())); pg.wait_for_timeout(300)
    if errs: raise SystemExit("JS error: " + errs[0])
    for i in range(int(DUR * FPS)):
        pg.evaluate("t => window.render(t)", i / FPS)
        pg.screenshot(path=f"{WORK}/f/{i:05d}.jpg", type="jpeg", quality=90)
    b.close()

# ---------------- audio (original) ----------------
SR = 44100; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(31)
def lp(x, fc): bb, aa = butter(2, min(fc, SR / 2 - 100) / (SR / 2), 'low'); return lfilter(bb, aa, x)
def hp(x, fc): bb, aa = butter(2, fc / (SR / 2), 'high'); return lfilter(bb, aa, x)
def env(n, k): return np.exp(-np.arange(n) / SR * k)
def put(s, t0, g=1., pan=0.):
    i = int(t0 * SR); j = min(N, i + len(s))
    if i >= N or j <= i: return
    s = s[: j - i] * g; L[i:j] += s * (1 - pan * .5); R[i:j] += s * (1 + pan * .5)
def saw(f, n, det=(-.006, 0, .006)):
    t = np.arange(n) / SR; return sum(2 * ((t * f * (1 + d)) % 1) - 1 for d in det) / len(det)
midi = lambda m: 440 * 2 ** ((m - 69) / 12)
def sine(f, n): return np.sin(2 * np.pi * f * np.arange(n) / SR)
def kick(t0, g=.55):
    n = int(SR * .3); x = np.arange(n) / SR; f = 160 * np.exp(-x * 32) + 46; put(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 9), t0, g)
def hat(t0, g=.05): n = int(SR * .04); put(hp(rng.standard_normal(n), 8500) * env(n, 70), t0, g, .3)
def clap(t0, g=.14): n = int(SR * .16); put(hp(rng.standard_normal(n), 1400) * env(n, 22), t0, g)
def buzzer(t0, g=.16):
    n = int(SR * .28); x = np.arange(n) / SR; s = np.sign(np.sin(2 * np.pi * 110 * x)) + .5 * np.sign(np.sin(2 * np.pi * 116 * x))
    put(lp(s, 1800) * np.minimum(1, x * 60) * env(n, 4), t0, g)
def whoosh(t0, d=.45, g=.16):
    n = int(SR * d); x = rng.standard_normal(n); o = np.zeros(n); fc = np.linspace(500, 7000, n)
    for k in range(0, n, 256): o[k:k + 256] = lp(x[max(0, k - 1024):k + 256], fc[k])[-len(o[k:k + 256]):]
    put(o * np.sin(np.linspace(0, np.pi, n)) ** 2, t0 - d * .6, g)
def click(t0, g=.2): n = int(SR * .03); put(hp(rng.standard_normal(n), 2500) * env(n, 180), t0, g)
def pop(t0, f=900, g=.2):
    n = int(SR * .12); x = np.arange(n) / SR; fr = f * (1 + 1.5 * np.exp(-x * 60)); put(np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 38), t0, g)
def ting(t0, g=.18): n = int(SR * 1.2); put((sine(2093, n) + .5 * sine(3136, n) + .3 * sine(5274, n)) * env(n, 4), t0, g)
def chaching(t0, g=.22):
    for k, f in enumerate([2637, 3136, 3951]):
        n = int(SR * .5); put((sine(f, n) + .4 * sine(f * 2.01, n)) * env(n, 9), t0 + k * .06, g * .7)
    n = int(SR * .25); put(hp(rng.standard_normal(n), 5000) * env(n, 18), t0, g * .5)
def impact(t0, g=.45):
    n = int(SR * 1.2); x = np.arange(n) / SR; f = 70 * np.exp(-x * 4) + 38
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 2.8) + lp(rng.standard_normal(n), 900) * env(n, 6) * .5, t0, g)
def tick(t0, g=.05): n = int(SR * .02); put(hp(rng.standard_normal(n), 3500) * env(n, 250), t0, g, rng.uniform(-.5, .5))
# hook: soft pad + words ticks
n = int(SR * T["prob"]); put(lp(sum(saw(midi(m), n) for m in [57, 64, 69]) / 3, 900) * np.linspace(0, 1, n), 0, .1)
for k in range(len(C["title"].split())): pop(.15 + k * .09, 1300, .06)
# problem: tense low drone + heartbeat + buzzers + glitch
n = int(SR * (T["sol"] - T["prob"])); x = np.arange(n) / SR
put(lp(saw(midi(38), n) + saw(midi(39), n), 500) * (.6 + .4 * np.sin(x * 9)), T["prob"], .12)
for k in range(int((T["sol"] - T["prob"]) / .8)):
    kick(T["prob"] + k * .8, .4); kick(T["prob"] + k * .8 + .18, .25)
for i in range(len(C["problem"])):
    if i % 2 == 0: tick(T["prob"] + i * .025)
for i in range(3): buzzer(T["prob"] + .9 + i * .6)
whoosh(T["sol"] + .1, .5, .2)
# solution: bright 120 BPM groove + clicks/pops
B = .5
def groove(t0, t1, chords):
    for k in range(int((t1 - t0) / B)):
        tt = t0 + k * B; ch = chords[(k // 4) % len(chords)]
        kick(tt); hat(tt + B / 2, .06); hat(tt + B / 4, .035); hat(tt + 3 * B / 4, .035)
        if k % 2: clap(tt)
        n = int(SR * B); put(lp(sum(saw(midi(m), n) for m in ch) / 3, 3200) * (1 - .7 * env(n, 12)), tt, .085, -.2)
        n2 = int(SR * B * .4); put(lp(saw(midi(ch[0] - 24), n2, (0,)), 600) * env(n2, 7), tt + B / 2, .18)
groove(T["sol"], T["res"], [[60, 64, 67], [67, 71, 74], [69, 72, 76], [65, 69, 72]])
for i in range(4): pop(T["sol"] + 1.2 + i * .7, 700, .14); pop(T["sol"] + 1.45 + i * .7, 1250, .12)
click(T["sol"] + 4.6, .28)
# result: uplifting + cha-ching + ting
impact(T["res"], .4); groove(T["res"], T["cta"], [[65, 69, 72, 76], [67, 71, 74, 79]])
chaching(T["res"] + 1.25); ting(T["res"] + 1.7)
# cta
impact(T["cta"], .45)
n = int(SR * (DUR - T["cta"])); put(lp(sum(saw(midi(m), n) for m in [60, 64, 67, 72]) / 4, 2000) * env(n, .6), T["cta"], .12)
pop(T["cta"] + .65, 900, .2); ting(T["cta"] + 1.1, .12)
mix = np.stack([L, R], 1); fo = int(SR * 1.0); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.5); mix = mix / np.max(np.abs(mix)) * .9
wavfile.write(f"{WORK}/audio.wav", SR, (mix * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{WORK}/f/%05d.jpg", "-i", f"{WORK}/audio.wav",
                "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", OUT], check=True)
print("done", OUT)
