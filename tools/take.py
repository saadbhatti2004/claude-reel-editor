"""Prepare a raw take for the educational edit: cut every pause short, speed the take up to the target pace, and remap
every word's time onto the new timeline.

usage: python take.py <take.mp4> <words.json> <out_dir> [--wpm 245] [--max-speed 1.22] [--speed X] [--keep 0.14] [--min-gap 0.18]
                     [--zones '[[from, to, speed, keep], ...]'] [--drop '[[from, to], ...]']

Zones (original take seconds): a stretch that should be slower or calmer gets its own speed and its own pause length;
every kept span plays at the speed of the zone its middle falls in, the rest at the take's speed.

Drop (original take seconds): a stretch cut out whole, words and all: a stumble or a false start the pause finder
cannot see because it is not quiet.

The speed: after the pauses are cut, the take is sped up until it runs at --wpm words a minute (ENGINE.md decision 7),
never past --max-speed and never slowed down. --speed fixes it instead.

out_dir gets:
  face.mp4        the cut and sped take, 1080x1920, 30 fps, with its voice (AAC)
  voice.wav       the same voice, 48 kHz mono
  timemap.json    kept spans of the original [orig_start, orig_end, new_start] and the speed
  words.json      the words with new times {w, s, e, os, oe}
  pauses.json     every pause found in the original and how long it became
  frames/         the face frames the renderer draws (00001.jpg on), straight from the take, near lossless

Pauses are found on the audio itself: inside every gap between words (and any long quiet run the transcript
stretched a word over), the quiet run under the take's speech level (p90) plus --floor-db is cut down to --keep
seconds, 60% after the last word and 40% before the next. A cut never goes inside a confident word.

Recording cuts (ENGINE.md rule 19): natural pauses inside a take keep the gentle trim above. Only where the speaker
stopped and restarted the recording is the silence removed completely: a join is a single frame where the picture jumps
(the pose changes) with steady frames on both sides, which fast hand movement never gives. At each join the cut runs from
just after the last word to just before the next one (--join-keep). The cut voice is then checked: no join may leave a gap
of 0.10 s or more (exit code 3).

Smooth picture: from 60 fps at a 1.2x speed, picking every 2.4th frame for 30 fps jerks in a 2, 3, 2, 3 rhythm. The
conversion to 30 fps blends neighbouring frames (ffmpeg framerate) so the motion stays even, and the face frames get a
light sharpen.
"""
import argparse, json, os, subprocess, sys, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('take'); ap.add_argument('words'); ap.add_argument('out')
ap.add_argument('--speed', type=float, default=None, help='a fixed speed instead of the target pace')
ap.add_argument('--wpm', type=float, default=245.0, help='target words a minute after the pauses are cut')
ap.add_argument('--max-speed', type=float, default=1.22)
ap.add_argument('--keep', type=float, default=0.14)
ap.add_argument('--min-gap', type=float, default=0.18)
ap.add_argument('--floor-db', type=float, default=-14.0, help='quiet threshold under the speech level (p90)')
ap.add_argument('--deep-db', type=float, default=None, help='a run this far under the speech level (p90) is cut even inside a stretched word')
ap.add_argument('--gap-db', type=float, default=-10.0, help='looser threshold inside a gap between words (breaths)')
ap.add_argument('--zones', default='[]', help='JSON [[from, to, speed, keep], ...] in original seconds')
ap.add_argument('--drop', default='[]', help='JSON [[from, to], ...] in original seconds, cut out whole')
ap.add_argument('--joins', default='auto', help="recording cuts: 'auto' (detect), 'none', or JSON [t, ...] in original seconds")
ap.add_argument('--join-keep', type=float, default=0.05, help='seconds kept across a join (a joint, not a pause)')
ap.add_argument('--fq', type=int, default=1, help='JPEG quality of the face frames (1 best; a long video can use 2)')
a = ap.parse_args()
ZONES = json.loads(a.zones)
zone = lambda t: next((z for z in ZONES if z[0] <= t < z[1]), None)
os.makedirs(a.out, exist_ok=True)

wav16 = os.path.join(a.out, 'a16.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.take, '-ac', '1', '-ar', '16000', wav16], check=True)
with wave.open(wav16) as w:
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
sr, hop = 16000, 160
n = len(x) // hop
rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
db = 20 * np.log10(rms)
speech = np.percentile(db, 90)
silent = db < speech + a.floor_db
dur = len(x) / sr

words = json.load(open(a.words, encoding='utf-8'))
if isinstance(words, dict):
    words = words['words']
DROP = json.loads(a.drop)
words = [w for w in words if not any(d0 <= w['s'] < d1 for d0, d1 in DROP)]          # a word that starts inside goes

# smooth the level over 30 ms, then find the quiet runs
sm = np.convolve(db, np.ones(3) / 3, mode='same')
quiet_strict = sm < speech + a.floor_db
quiet_gap = sm < speech + a.gap_db      # inside a gap between words, breaths count as quiet too
quiet = quiet_strict

def quiet_runs(lo, hi, min_len, mask=None):
    q = quiet if mask is None else mask
    i0, i1 = max(0, int(lo * 100)), min(n, int(hi * 100))
    out, i = [], i0
    while i < i1:
        if q[i]:
            j = i
            while j < i1 and q[j]:
                j += 1
            if (j - i) / 100 >= min_len:
                out.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    return out

# candidates: every gap between words, plus long quiet runs anywhere (the transcript sometimes stretches a word
# over a pause); a cut never goes inside a confident word's core
regions = []
for k in range(1, len(words)):
    if words[k]['s'] - words[k - 1]['e'] >= 0.12:
        regions.append((words[k - 1]['e'] - 0.03, words[k]['s'] + 0.03, quiet_gap))
for s, e in quiet_runs(0, dur, 0.30):
    regions.append((s, e, quiet_strict))
# --deep-db: a run this far under the speech level is a pause even where the transcript stretched a confident word over it
# (short pauses inside a word)
deep = sm < speech + a.deep_db if a.deep_db is not None else None
FORCED = set()
if deep is not None:
    for s, e in quiet_runs(0, dur, 0.20, deep):
        regions.append((s, e, deep)); FORCED.add((round(s, 2), round(e, 2)))
first, last = words[0]['s'], words[-1]['e']

# recording cuts: single-frame picture jumps with steady frames either side (hand movement blurs across several)
def find_joins():
    W, H = 108, 192
    pr = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.take, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True)
    fr = np.frombuffer(pr.stdout, np.uint8).reshape(-1, H, W).astype(np.float32)
    fps_src = len(fr) / dur
    dd = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    out = []
    for i in range(4, len(dd) - 4):
        nb = max(dd[i - 3:i].max(), dd[i + 1:i + 4].max())
        if dd[i] > 6 and dd[i] > 2.8 * nb:
            out.append(round((i + 1) / fps_src, 3))
    return out
JOINS = [] if a.joins == 'none' else find_joins() if a.joins == 'auto' else json.loads(a.joins)
JOINCUT = []
for j in JOINS:
    before = [w for w in words if w['e'] <= j + 0.08]
    after = [w for w in words if w['s'] >= j - 0.08]
    if not before or not after:
        continue
    b, c = max(before, key=lambda w: w['e']), min(after, key=lambda w: w['s'])
    cs, ce = b['e'] + a.join_keep * 0.6, c['s'] - a.join_keep * 0.4
    if ce > cs:
        JOINCUT.append((cs, ce, j, b['e'], c['s']))
print(f'recording cuts found: {len(JOINS)} {JOINS}', flush=True)

pauses, cuts = [], []
seen = set()
for lo, hi, mask in sorted(regions, key=lambda r: r[0]):
    for s, e in quiet_runs(lo, hi, a.min_gap, mask):
        if (round(s, 2), round(e, 2)) in seen:
            continue
        seen.add((round(s, 2), round(e, 2)))
        core = any(w['s'] + 0.06 < x < w['e'] - 0.06 for w in words if (w.get('p') or 1) > 0.5 for x in (s + 0.05, e - 0.05))
        if core and (round(s, 2), round(e, 2)) not in FORCED and mask is not deep:
            continue
        if e <= first + 0.05:
            cuts.append((0.0, max(0.0, e - 0.05))); continue
        if s >= last - 0.05:
            cuts.append((s + 0.25, dur)); continue
        z = zone(s)
        keep = z[3] if z else a.keep
        cs, ce = s + keep * 0.6, e - keep * 0.4
        if ce > cs:
            cuts.append((cs, ce))
            pauses.append({'at': round(s, 3), 'len': round(e - s, 3), 'kept': keep})
if words[0]['s'] > 0.05 and not any(c[0] == 0.0 for c in cuts):
    cuts.append((0.0, max(0.0, words[0]['s'] - 0.05)))
if dur - last > 0.3 and not any(c[1] == dur for c in cuts):
    cuts.append((last + 0.25, dur))

cuts += [tuple(d) for d in DROP]
cuts += [(cs, ce) for cs, ce, *_ in JOINCUT]
# merge overlapping cuts
merged = []
for c in sorted(cuts):
    if merged and c[0] <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], c[1]))
    else:
        merged.append(c)
cuts = merged
cuts.sort()
spans, t = [], 0.0
for cs, ce in cuts:
    if cs > t:
        spans.append([round(t, 3), round(cs, 3)])
    t = max(t, ce)
if t < dur:
    spans.append([round(t, 3), round(dur, 3)])
spans = [s for s in spans if s[1] - s[0] > 0.02]
# every cut on the source's frame grid: the picture and the sound of a span are then exactly as long as each other, so
# the join pads nothing and the words keep their computed times to the end (unsnapped, the words drift)
num, den = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', a.take],
                          capture_output=True, text=True, check=True).stdout.strip().split('/')
FR = float(num) / float(den or 1)
snap = lambda t: round(round(t * FR) / FR, 6)
spans = [[snap(s), snap(e)] for s, e in spans if snap(e) > snap(s)]
# a span running across a zone edge is split there (on the frame grid), so each side gets its own speed
for edge in sorted(snap(x) for z in ZONES for x in z[:2]):
    spans = [part for s, e in spans for part in ([[s, edge], [edge, e]] if s + 0.05 < edge < e - 0.05 else [[s, e]])]

# the speed: the take's own pace once the pauses are cut, brought up to the target
kept = sum(e - s for s, e in spans)
wpm0 = len(words) / kept * 60
if a.speed is None:
    a.speed = round(min(a.max_speed, max(1.0, a.wpm / wpm0)), 3)
print(f'pace after the cuts {wpm0:.0f} wpm; speed {a.speed}x', flush=True)
new, acc = [], 0.0                                  # acc: seconds on the new timeline
for s, e in spans:
    z = zone((s + e) / 2)
    sp = z[2] if z else a.speed
    new.append([s, e, round(acc, 4), sp])
    acc += (e - s) / sp

def remap(t0):
    for s, e, ns, sp in new:
        if t0 < s:
            return ns
        if t0 <= e:
            return round(ns + (t0 - s) / sp, 3)
    return round(acc, 3)

out_words = [{'w': w['w'], 's': remap(w['s']), 'e': remap(w['e']), 'os': w['s'], 'oe': w['e'], 'p': w.get('p')} for w in words]

# one filter graph: trim every kept span, concat, speed, 30 fps
parts, labels = [], []
for k, (s, e, _, sp) in enumerate(new):
    parts.append(f'[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,'
                 f'afade=t=in:d=0.008,afade=t=out:st={max(0, e - s - 0.008):.3f}:d=0.008[a{k}]')
    labels.append(f'[v{k}][a{k}]')
graph = ';'.join(parts) + f";{''.join(labels)}concat=n={len(new)}:v=1:a=1[vc][ac];"
if not ZONES:
    graph += f'[vc]setpts=PTS/{a.speed},framerate=fps=30[vo];[ac]atempo={a.speed},aresample=48000[ao]'
else:
    # the cut first (frame exact), then each run of spans at one speed is sped as a whole: speeding the spans one by
    # one padded every join a few milliseconds (atempo's flush)
    runs, c0 = [], 0.0
    for s, e, _, sp in new:
        if runs and runs[-1][2] == sp:
            runs[-1][1] = round(runs[-1][1] + e - s, 6)
        else:
            runs.append([round(c0, 6), round(c0 + e - s, 6), sp])
        c0 += e - s
    R = len(runs)
    graph += f"[vc]split={R}{''.join(f'[cv{i}]' for i in range(R))};[ac]asplit={R}{''.join(f'[ca{i}]' for i in range(R))};"
    graph += ';'.join(f'[cv{i}]trim={r0}:{r1},setpts=(PTS-STARTPTS)/{sp}[rv{i}];[ca{i}]atrim={r0}:{r1},asetpts=PTS-STARTPTS,atempo={sp}[ra{i}]'
                      for i, (r0, r1, sp) in enumerate(runs))
    graph += f";{''.join(f'[rv{i}][ra{i}]' for i in range(R))}concat=n={R}:v=1:a=1[vz][az];[vz]framerate=fps=30[vo];[az]aresample=48000[ao]"
gfile = os.path.join(a.out, 'graph.txt')
open(gfile, 'w').write(graph)
face = os.path.join(a.out, 'face.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.take, '-filter_complex_script', gfile, '-map', '[vo]', '-map', '[ao]',
                '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                face], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', face, '-vn', '-ac', '1', '-ar', '48000', os.path.join(a.out, 'voice.wav')], check=True)
# the face frames the renderer draws come straight from the take (not from face.mp4, which is one encode later), as
# near-lossless JPEGs with full colour (4:4:4) and the take's BT.709 colours converted the way a browser reads a JPEG
frames = os.path.join(a.out, 'frames')
os.makedirs(frames, exist_ok=True)
fgraph = os.path.join(a.out, 'graph_frames.txt')
open(fgraph, 'w').write(graph.replace('framerate=fps=30[vo]', 'framerate=fps=30,unsharp=5:5:0.45:5:5:0,scale=in_color_matrix=bt709:in_range=tv:out_color_matrix=bt601'
                                      ':out_range=pc:flags=lanczos+accurate_rnd+full_chroma_int,format=yuvj444p[vo]'))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.take, '-filter_complex_script', fgraph, '-map', '[vo]',
                '-q:v', str(a.fq), '-qmin', '1', os.path.join(frames, '%05d.jpg'), '-map', '[ao]', '-f', 'null', '-'], check=True)
os.remove(wav16)

json.dump({'speed': a.speed, 'keep': a.keep, 'zones': ZONES, 'drop': DROP, 'spans': new, 'orig_dur': round(dur, 3),
           'new_dur': round(acc, 3)}, open(os.path.join(a.out, 'timemap.json'), 'w'), indent=1)
json.dump(out_words, open(os.path.join(a.out, 'words.json'), 'w', encoding='utf-8'), indent=0)
json.dump(pauses, open(os.path.join(a.out, 'pauses.json'), 'w'), indent=0)
print(f'{len(new)} spans, {len(pauses)} pauses cut; {dur:.2f} s -> {acc:.2f} s at {a.speed}x '
      f'({len(words) / acc * 60:.0f} wpm)')

# the join check: across each recording cut the gap from the last word to the next must be a joint, not a pause
bad = []
for cs, ce, j, be, cst in JOINCUT:
    g = remap(cst) - remap(be)
    if g >= 0.10:
        bad.append((j, round(g, 3)))
json.dump({'joins': JOINS, 'cut': [[round(x, 3) for x in jc[:3]] for jc in JOINCUT], 'bad': bad}, open(os.path.join(a.out, 'joins.json'), 'w'))
if bad:
    print(f'JOIN CHECK FAILED: gaps left at recording cuts (join, seconds): {bad}')
    sys.exit(3)
print(f'join check: all {len(JOINCUT)} recording cuts are tight')
