"""The older single-file review page for one reel, scene by scene, before the full edit. tools/beatreview.py is the
current review step.

usage: python tools/review.py <reel dir> [--mix final/mix.wav] [--no-render] [--round 1]
reads  edit/plan.json (scenes), edit/words.js (CAPWORDS), edit/notes.json (optional: reel title, id, keyword, summary,
       and per scene {what, real, changed}), the mix (voice, effects and bed from tools/mix.py)
writes review/draft.mp4 (the whole reel, draft quality, with the mix), review/scenes/NN_<id>.mp4 (one clip per scene),
       review/full.mp4 (the whole reel at review size, shown first with a jump button per scene and its own notes box),
       review/REVIEW.html: every clip embedded in the page itself (base64), so the one file plays wherever it is
       opened; under each clip the words said in it, what is on screen, the real material, and a notes box. Notes are
       kept in the browser while you type, and one button copies them all, by scene number, in one block.
"""
import argparse, base64, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('reel'); ap.add_argument('--mix', default=None); ap.add_argument('--no-render', action='store_true')
ap.add_argument('--round', type=int, default=1)
a = ap.parse_args()
R = a.reel
J = lambda *p: json.load(open(os.path.join(R, *p), encoding='utf-8'))
plan = J('edit', 'plan.json')
notes = J('edit', 'notes.json') if os.path.exists(os.path.join(R, 'edit', 'notes.json')) else {}
wj = open(os.path.join(R, 'edit', 'words.js'), encoding='utf-8').read()
cap = json.loads(re.search(r'window\.CAPWORDS=(.*?);\n', wj).group(1))
dur = plan['dur']
rv = os.path.join(R, 'review'); sd = os.path.join(rv, 'scenes')
os.makedirs(sd, exist_ok=True)
mix = a.mix or os.path.join(R, 'final', 'mix.wav')
if not os.path.isabs(mix) and not os.path.exists(mix): mix = os.path.join(R, mix)  # a relative --mix is the reel dir's
if not os.path.exists(mix): sys.exit(f'no mix at {mix}: run tools/mix.py first (a review without sound is never handed over)')
draft = os.path.join(rv, 'draft.mp4')

if not a.no_render:
    cmd = ['node', os.path.join(HERE, 'render.mjs'), os.path.join(R, 'edit'), '--from', '0', '--to', f'{dur:.3f}', '--out', draft, '--draft']
    cmd += ['--audio', mix]
    subprocess.run(cmd, check=True)

esc = html.escape
LAY = {'card': 'Face card', 'split': 'Graphic over face', 'gfx': 'Full graphic', 'face': 'Full face', 'mixed': 'Mixed'}
line = lambda s: ' '.join(w['w'] for w in cap if s['from'] - 0.02 <= w['s'] < s['to'] - 0.02)
cards = []
for i, s in enumerate(plan['scenes']):
    a0, a1 = max(0.0, s['from']), min(s['to'], dur)
    clip = os.path.join(sd, f'{i + 1:02d}_{s["id"]}.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a0:.3f}', '-i', draft, '-t', f'{a1 - a0:.3f}', '-vf', 'scale=720:1280',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '25', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart', clip], check=True)
    b64 = base64.b64encode(open(clip, 'rb').read()).decode()
    n = notes.get('scenes', {}).get(s['id'], {})
    chg = f'<p class="chg"><b>Changed this round:</b> {esc(n["changed"])}</p>' if n.get('changed') else ''
    real = f'<p class="real"><b>Real:</b> {esc(n["real"])}</p>' if n.get('real') else ''
    cards.append(f'''<section class="sc{' changed' if n.get('changed') else ''}" id="s{i + 1}">
<div class="clip"><video controls playsinline preload="metadata" src="data:video/mp4;base64,{b64}"></video></div>
<div class="info"><div class="hd"><span class="num">{i + 1}</span><span class="id">{esc(s['id'])}</span>
<span class="tag">{esc(LAY.get(s['layout'], s['layout']))}</span><span class="time">{a0:.1f} to {a1:.1f} s ({a1 - a0:.1f} s)</span></div>
<p class="said">"{esc(line(s))}"</p>{chg}<p><b>On screen:</b> {esc(n.get('what', ''))}</p>{real}
<label>Your notes on scene {i + 1}<textarea data-n="{i + 1}" data-id="{esc(s['id'])}" placeholder="Leave empty if this scene is good"></textarea></label>
<div class="ok"><label><input type="checkbox" data-ok="{i + 1}"> Approved</label></div></div></section>''')

# the whole reel on top, every scene joined: one embedded clip, a jump button per scene, and a notes box for the whole flow
full = os.path.join(rv, 'full.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', draft, '-vf', 'scale=720:1280', '-c:v', 'libx264', '-preset', 'medium', '-crf', '26',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', full], check=True)
fb64 = base64.b64encode(open(full, 'rb').read()).decode()
jumps = ''.join(f'<button class="jump" data-t="{max(0.0, s["from"]) + 0.02:.2f}">{i + 1} · {esc(s["id"])}</button>' for i, s in enumerate(plan['scenes']))
fullsec = f'''<section class="sc full" id="s0">
<div class="clip"><video id="fullv" controls playsinline preload="metadata" src="data:video/mp4;base64,{fb64}"></video></div>
<div class="info"><div class="hd"><span class="num">▶</span><span class="id">The full reel</span><span class="tag">all {len(plan['scenes'])} scenes joined</span>
<span class="time">0.0 to {dur:.1f} s</span></div>
<p>Watch it straight through first: every scene hands its object to the next one. Jump to a scene:</p>
<div class="jumps">{jumps}</div>
<label>Your notes on the full reel (the flow, the joins, the pace)<textarea data-n="0" data-id="full reel" placeholder="Leave empty if it flows"></textarea></label>
<div class="ok"><label><input type="checkbox" data-ok="0"> Approved</label></div></div></section>'''

rr = notes.get('reel', {})
title = rr.get('title', os.path.basename(R))
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scene Review</title><style>
:root {{ --bg:#0B0B0C; --card:#151518; --ink:#F4F4F5; --sub:#A1A1AA; --line:#2A2A30; --acc:#22DF85; --chg:#F5B942; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 system-ui,Segoe UI,sans-serif; }}
main {{ max-width:1080px; margin:0 auto; padding:26px 16px 120px; }}
h1 {{ font-size:28px; margin:0 0 4px; }} p {{ color:var(--sub); margin:6px 0; }} b {{ color:var(--ink); }}
.sum {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:14px 18px; margin:16px 0 26px; }}
.sum li {{ color:var(--sub); margin:3px 0; }}
.sc {{ display:grid; grid-template-columns:300px 1fr; gap:22px; background:var(--card); border:1px solid var(--line); border-radius:16px; padding:16px; margin:0 0 18px; }}
.sc.changed {{ border-color:var(--chg); }}
video {{ width:100%; border-radius:12px; background:#000; display:block; }}
.hd {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:6px; }}
.num {{ background:var(--acc); color:#04140B; font-weight:900; border-radius:8px; padding:1px 10px; }}
.id {{ font-weight:800; font-size:18px; }} .tag {{ border:1px solid var(--line); border-radius:999px; padding:1px 10px; color:var(--sub); font-size:13px; }}
.time {{ color:var(--sub); font-size:13px; margin-left:auto; }}
.said {{ font-style:italic; }} .chg {{ color:var(--chg); }} .chg b {{ color:var(--chg); }} .real {{ color:#7FE3B0; font-size:14.5px; }}
label {{ display:block; color:var(--sub); font-size:14px; margin-top:12px; }}
textarea {{ width:100%; min-height:86px; margin-top:6px; background:#0F0F12; color:var(--ink); border:1px solid var(--line); border-radius:10px; padding:10px; font:15px system-ui; resize:vertical; }}
.ok label {{ display:inline-flex; gap:8px; align-items:center; color:var(--ink); }}
.bar {{ position:fixed; left:0; right:0; bottom:0; background:rgba(11,11,12,.94); border-top:1px solid var(--line); padding:12px 16px; display:flex; gap:12px; justify-content:center; align-items:center; }}
button {{ background:var(--acc); color:#04140B; border:0; border-radius:10px; padding:11px 20px; font-weight:800; cursor:pointer; font-size:15px; }}
#msg {{ color:var(--sub); font-size:14px; }}
h2 {{ font-size:20px; margin:28px 0 12px; }}
.sc.full {{ grid-template-columns:360px 1fr; border-color:var(--acc); }}
.jumps {{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 4px; }}
button.jump {{ background:#202026; color:var(--ink); border:1px solid var(--line); padding:7px 12px; font-weight:600; font-size:14px; }}
@media (max-width:760px) {{ .sc {{ grid-template-columns:1fr; }} .time {{ margin-left:0; }} }}
</style></head><body><main>
<h1>{esc(title)}</h1>
<p>{esc(rr.get('id', ''))}{(' · keyword ' + esc(rr['keyword'])) if rr.get('keyword') else ''} · round {a.round} · {len(plan['scenes'])} scenes, {dur:.1f} s</p>
{('<div class="sum"><ul>' + ''.join(f'<li>{esc(x)}</li>' for x in rr.get('summary', [])) + '</ul></div>') if rr.get('summary') else ''}
{fullsec}
<h2>Scene by scene</h2>
{''.join(cards)}
</main>
<div class="bar"><button id="copy">Copy all my notes</button><span id="msg">Notes stay in this browser while you type.</span></div>
<script>
const KEY = 'review:' + {json.dumps(os.path.basename(R))} + ':r{a.round}';
let saved = {{}}; try {{ saved = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch (e) {{}}
const tas = [...document.querySelectorAll('textarea[data-n]')], oks = [...document.querySelectorAll('input[data-ok]')];
tas.forEach(t => {{ t.value = saved['n' + t.dataset.n] || ''; }});
oks.forEach(c => {{ c.checked = !!saved['ok' + c.dataset.ok]; }});
// a clip that opens on a hand-off (a glitch, a blur) would show that frame as its picture: open each half a second in
document.querySelectorAll('section:not(.full) video').forEach(v => v.addEventListener('loadedmetadata', () => {{ if (v.currentTime === 0) v.currentTime = Math.min(0.5, v.duration / 2); }}, {{ once: true }}));
const fv = document.getElementById('fullv');
document.querySelectorAll('button.jump').forEach(b => b.onclick = () => {{ fv.currentTime = +b.dataset.t; fv.play(); }});
const save = () => {{ const o = {{}}; tas.forEach(t => o['n' + t.dataset.n] = t.value); oks.forEach(c => o['ok' + c.dataset.ok] = c.checked);
  try {{ localStorage.setItem(KEY, JSON.stringify(o)); }} catch (e) {{}} }};
tas.forEach(t => t.addEventListener('input', save)); oks.forEach(c => c.addEventListener('change', save));
document.getElementById('copy').onclick = () => {{
  const lines = [{json.dumps(title + ' notes (round ' + str(a.round) + '):')}];
  tas.forEach(t => {{ const ok = oks.find(c => c.dataset.ok === t.dataset.n).checked;
    const who = t.dataset.n === '0' ? 'Full reel' : 'Scene ' + t.dataset.n + ' (' + t.dataset.id + ')';
    if (t.value.trim()) lines.push(who + ': ' + t.value.trim());
    else if (ok) lines.push(who + ': approved'); }});
  const txt = lines.join('\\n');
  const done = () => document.getElementById('msg').textContent = 'Copied ' + (lines.length - 1) + ' scene notes.';
  if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, () => {{ prompt('Copy your notes:', txt); }}); else prompt('Copy your notes:', txt);
}};
</script></body></html>'''
out = os.path.join(rv, 'REVIEW.html')
open(out, 'w', encoding='utf-8').write(page)
print(out, f'{os.path.getsize(out) / 1e6:.1f} MB, the full reel and', len(cards), 'scenes embedded')
