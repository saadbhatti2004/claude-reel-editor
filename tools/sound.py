"""Design an educational reel's sound effects from what actually moves on screen.

usage: python sound.py <edit dir> [--seed 1] [--report]

Reads edit/events.json (every kit motion on screen, written by render.mjs --plan), edit/plan.json (scenes, each
scene's sound options, and the reel's own narrative cues in window.SFX) and kit/sfx/POOLS.json (the real recorded
effects, by role). Writes edit/sound.json, which tools/mix.py places.

So:
  - every visible motion gets the sound of what it is: a card flying in gets a whoosh that peaks as it lands and pans
    from where it came from to where it lands; a pop gets a pop sized to its element; a big stamp lands on a thump and
    a small one on a light tap; a camera snap gets a zoom; a person typing gets real keystrokes, a machine printing
    gets soft ticks; a counter ticks and slows with its number; a drawn mark gets a marker stroke;
  - hard cuts stay silent (the references cut hard; GRAMMAR section 12);
  - the reel's narrative moments (a delete, an error, the turn, the CTA) are cued by role in the composition and win
    over the automatic ones; a scene can mute kinds of automatic sound or re-voice its runs (SCENES[].snd);
  - every file is placed by its loudest point (or its attack, or for risers its end), with only a short pre-roll and
    a length cap per role, so nothing rings or peaks far from its frame;
  - a density rule keeps it from turning into noise: no more than two sounds start inside 90 ms, never two of one
    family too close (120 ms for low hits), and at most four in half a second outside typing, ticks and runs;
  - variety: the same file is never used twice in a row for a role, and each hit varies slightly in speed and level.
"""
import argparse, json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('edit'); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--report', action='store_true')
a = ap.parse_args()

pools = json.load(open(os.path.join(HERE, '..', 'kit', 'sfx', 'POOLS.json'), encoding='utf-8'))
LIB = os.environ.get('SFX_LIB') or os.path.join(HERE, '..', pools['lib'])
meas = {str(m['id']): m for m in json.load(open(os.path.join(LIB, 'measured.json'), encoding='utf-8'))}
meas.update({m['id']: m for m in json.load(open(os.path.join(LIB, 'derived', 'measured.json'), encoding='utf-8'))})
plan = json.load(open(os.path.join(a.edit, 'plan.json'), encoding='utf-8'))
events = json.load(open(os.path.join(a.edit, 'events.json'), encoding='utf-8')) if os.path.exists(os.path.join(a.edit, 'events.json')) else []
rng = random.Random(a.seed)
W, H = 1080, 1920
SND = {s['id']: (s.get('snd') or {}) for s in plan['scenes']}


def files(role):
    r = pools['roles'][role]
    if 'derived' in r:
        ids = sorted(k for k in meas if k.startswith(r['derived'] + '_'))
        return [(os.path.join(LIB, 'derived', k + '.wav'), meas[k]) for k in ids]
    return [(os.path.join(LIB, 'wav', f'{i}.wav'), meas[str(i)]) for i in r['ids'] if str(i) in meas and not meas[str(i)]['melody']]


last = {}


def pick(role):
    fs = files(role)
    choices = [f for f in fs if f[0] != last.get(role)] or fs
    f = rng.choice(choices)
    last[role] = f[0]
    return f


def pan_of(x):
    return max(-0.7, min(0.7, (x - W / 2) / (W / 2) * 0.7))


cands = []


def add(t, role, prio, why, g=0.0, pan0=0.0, pan1=None, rate=None, fam=None, seq=False, dur=None, pre=None, cross=False, hp=None, file=None, peak=0.0):
    """t is the moment the sound's own anchor (its peak, attack or end) must land on. cross: a cue (a riser into a
    cut) may start before its scene; hp: a cue's own high-pass, overriding its role's. file + peak: a cue that names its
    own recording (a designed moment) and where its anchor sits in it; the role still sets the gain,
    the alignment and the density family."""
    cands.append(dict(t=t, role=role, prio=prio, why=why, g=g, pan0=pan0, pan1=pan0 if pan1 is None else pan1,
                      rate=rate, fam=fam or role, seq=seq, dur=dur, pre=pre, cross=cross, hp=hp, file=file, peak=peak))


def size(e):
    return max(0.0, min(1.0, (e.get('w', 0) * e.get('h', 0)) / (W * H)))


def onscreen(e):
    return e.get('vis', 1) >= 0.25 and -150 < e.get('x', W / 2) < W + 150 and -150 < e.get('y', H / 2) < H + 150


def eased_inverse(p, e):
    """the time share at which an eased counter shows the value share p (so ticks follow the number)"""
    if e == 'out':
        return 1 - (1 - p) ** (1 / 3)
    if e == 'inOut':
        return (p / 4) ** (1 / 3) if p < 0.5 else 1 - (2 * (1 - p)) ** (1 / 3) / 2
    return p


# trains: three or more small pops or fly-ins of one scene, each within 0.2 s of the last (a list racing in, a row
# of checks) are one deliberate rhythm: kept as a sequence (thinned to 12 a second), rising in pitch, voiced by the
# scene's snd.train role (default: a soft tick)
small = [e for e in events if e['k'] in ('pop', 'fly') and 'x' in e and onscreen(e) and size(e) < 0.03]
small.sort(key=lambda e: (e['scene'], e['g0']))
run = []
for e in small + [None]:
    if e is not None and run and e['scene'] == run[-1]['scene'] and 0.02 <= e['g0'] - run[-1]['g0'] <= 0.2:
        run.append(e); continue
    if len(run) >= 3:
        step = max(1, math.ceil(len(run) / max(1.0, (run[-1]['g0'] - run[0]['g0']) * 12 + 1)))
        for j, r in enumerate(run):
            r['_train'] = (j % step == 0, j / max(1, len(run) - 1))
    run = [e] if e is not None else []

for e in events:
    k, t0, dur = e['k'], e['g0'], e.get('dur', 0) or 0
    opt = SND.get(e.get('scene'), {})
    if opt.get('mute') == 'all':
        continue
    # a run is its own sound (muted only by 'train'), even where single pops or fly-ins are muted
    if '_train' in e:
        keep, p = e['_train']
        if keep and 'train' not in opt.get('mute', []):
            role = opt.get('train', 'tick')
            add(t0 + (dur * 0.6 if k == 'fly' else 0), role, 35, 'a run of items', (-1 if role == 'tick' else -4) - 2 * p, pan_of(e.get('x', W / 2)), rate=1.0 + 0.4 * p, seq=True, fam='train')
        continue
    if k in opt.get('mute', []):
        continue
    if 'x' in e and not onscreen(e):
        continue
    ar, x = size(e), e.get('x', W / 2)
    lvl = max(-4, min(4, 3 * math.log10(max(ar, 1e-4) / 0.05)))          # bigger things sound bigger
    if k == 'fly':
        d = math.hypot(e.get('dx', 0), e.get('dy', 0))
        if d >= 200 and ar >= 0.01:
            add(t0 + dur * 0.55, 'whoosh_m' if ar >= 0.12 else 'whoosh_s', 55, 'fly-in', lvl, pan_of(x + e.get('dx', 0)), pan_of(x), fam='air')
        elif ar >= 0.004:
            add(t0, 'pop', 45, 'small fly-in', lvl - 2, pan_of(x), rate=1.08 if ar < 0.02 else 0.95)
    elif k == 'pop':
        if ar >= 0.003:
            add(t0, 'pop', 45, 'pop', lvl, pan_of(x), rate=1.12 if ar < 0.015 else (0.9 if ar > 0.12 else 1.0))
    elif k == 'in':
        if ar >= 0.2:
            add(t0 + dur, 'whoosh_s', 15, 'big entry', lvl - 8, pan_of(x), fam='air')
    elif k == 'stamp':
        if ar < 0.012:
            add(t0 + dur, 'click', 70, 'small stamp', 0, pan_of(x), rate=1.05)
        else:
            add(t0 + dur, 'thump', 80, 'stamp lands', lvl - (4 if ar < 0.04 else 0), pan_of(x), fam='low')
    elif k == 'shake':
        if e.get('amp', 0) >= 10:
            add(t0, 'thump', 60, 'shake', 0, 0.0, fam='low')
    elif k == 'punch':
        if e.get('amt', 0) >= 0.15 and ar >= 0.05:
            add(t0, 'pop', 30, 'punch', lvl - 5, pan_of(x), rate=0.8)
    elif k == 'out':
        if ar >= 0.15:
            add(t0 + dur * 0.5, 'whoosh_s', 10, 'big exit', lvl - 6, pan_of(x), fam='air')
    elif k == 'cam':
        z = abs(math.log(max(e['s1'], 1e-3) / max(e['s0'], 1e-3)))
        if z >= 0.12:
            add(t0 + dur * 0.45, 'zoom' if e['s1'] > e['s0'] else 'whoosh_s', 60, 'camera zoom', max(-6, min(3, 6 * (z - 0.4))), 0.0, fam='air')
        elif e.get('d', 0) >= 300:
            add(t0 + dur * 0.45, 'whoosh_s', 50, 'camera move', -4, 0.0, fam='air')
    elif k == 'type':
        n, cps = int(e['n']), float(e['cps'])
        if e.get('machine'):                                   # a program printing: a soft tick stream
            step = max(1, math.ceil(cps / 10))
            for i in range(0, n, step):
                add(t0 + i / cps, 'tick', 18, 'machine printing', -5 + rng.uniform(-2, 0), rng.uniform(-0.1, 0.1), seq=True, fam='tick', rate=1.15)
        else:
            step = max(1, math.ceil(cps / 16))
            for i in range(0, n, step):
                add(t0 + i / cps, 'key', 20, 'typing', rng.uniform(-3.5, 0), rng.uniform(-0.15, 0.15), seq=True, fam='key')
    elif k == 'count':
        nt = max(3, min(6, round(dur * 10)))
        for i in range(nt):
            p = i / nt
            add(t0 + dur * eased_inverse(p, e.get('e', 'out')), 'tick', 25, 'counter', -3 - 1.5 * p, 0.0, rate=1.0 + 0.1 * (1 - p), seq=True, fam='tick')
    elif k == 'draw':
        add(t0 + 0.03, 'marker', 40, 'drawn mark', 0, pan_of(x))

# the composition's own cues: {t, role, g?, why?}, always kept
for c in plan.get('sfx', []):
    if 'role' in c:
        add(c['t'], c['role'], 100, c.get('why', 'cue'), c.get('g', 0), c.get('pan', 0.0), c.get('pan1'), c.get('rate'), fam=c.get('fam'), dur=c.get('dur'), pre=c.get('pre'),
            cross=c.get('cross', False), hp=c.get('hp'), file=c.get('file'), peak=c.get('peak', 0.0))

# density: highest priority first, then thin out what would pile up
GAP = {'low': 0.12}
cands.sort(key=lambda c: (-c['prio'], c['t']))
kept = []
for c in cands:
    near = [k for k in kept if abs(k['t'] - c['t']) < 0.09 and not k['seq']]
    if c['prio'] < 100:
        if not c['seq'] and len(near) >= 2:
            continue
        if any(k['fam'] == c['fam'] and abs(k['t'] - c['t']) < (0.045 if c['seq'] else GAP.get(c['fam'], 0.06)) for k in kept):
            continue
        if not c['seq'] and sum(1 for k in kept if not k['seq'] and abs(k['t'] - c['t']) < 0.5) >= 4:
            continue
    kept.append(c)
kept.sort(key=lambda c: c['t'])

out = []
for c in kept:
    if c.get('file'):
        path, m = c['file'], {'on': c['peak'], 'peak': c['peak'], 'end': c['peak'] + (c['dur'] or 1.0), 'dur': c['peak'] + (c['dur'] or 1.0)}
    else:
        path, m = pick(c['role'])
    r = pools['roles'][c['role']]
    rate = c['rate'] or rng.uniform(0.95, 1.05)
    on, pk, end = m.get('on', 0.0), m.get('peak', m.get('on', 0.0)), m.get('end', m['dur'])
    if r['align'] == 'end':                                   # risers: placed by their end, cut to the cue's length
        anchor = end
        ss = max(0.0, end - (c['dur'] or end))
        dur = anchor - ss
    else:
        anchor = pk if r['align'] == 'peak' else on
        ss = max(0.0, anchor - (c['pre'] if c['pre'] is not None else r.get('pre', 0.03)))
        dur = c['dur'] or min(end - ss + 0.05, r.get('maxdur') or 2.5)
    t = c['t'] - (anchor - ss) / rate
    sc_from = max([s['from'] for s in plan['scenes'] if s['from'] <= c['t'] + 1e-6] or [0.0])
    if t < sc_from - 1e-6 and not c.get('cross'):
        cut = (sc_from - t) * rate
        if dur - cut < 0.03:
            continue
        ss += cut; dur -= cut; t = sc_from
    out.append({'t': round(t, 4), 'f': path, 'ss': round(ss, 4), 'dur': round(max(0.03, dur), 4), 'rate': round(rate, 4),
                'g': round(r['gain'] + c['g'] + rng.uniform(-1, 1), 2), 'pan0': round(c['pan0'], 3), 'pan1': round(c['pan1'], 3),
                'hp': c['hp'] if c.get('hp') is not None else r.get('hp', 0), 'role': c['role'], 'why': c['why'], 'at': round(c['t'], 4)})
json.dump({'sounds': out}, open(os.path.join(a.edit, 'sound.json'), 'w', encoding='utf-8'), indent=0)
print(f'{len(events)} motion events, {len(cands)} candidate sounds, {len(out)} placed '
      f'({sum(1 for c in kept if c["seq"])} keystrokes, ticks and runs) over {plan["dur"]:.1f} s')
if a.report:
    from collections import Counter
    print(Counter(o['role'] for o in out).most_common())
    for s in plan['scenes']:
        n = [o for o in out if s['from'] <= o['at'] < s['to'] and o['role'] not in ('key', 'tick')]
        print(f"  {s['id']:16s} {len(n):3d} sounds  {len(n) / max(0.1, s['to'] - s['from']):.1f}/s  " + ' '.join(sorted(set(o['role'] for o in n))))
