"""Self-review, the measuring half: score how alive the graphics are, the same way for our scenes and for the
reference reels, so "fast enough" is a number, not a feeling.

usage:
  python selfcheck.py refs  <study root> <out.json>                    measure the decoded reference reels once
  python selfcheck.py reel  <review/scenes dir> <refs.json> <out.json> measure every scene of a reel against them

Measured on the top 720 px of the frame (the graphic area in every layout, clear of the caption band), downscaled to
108x72 grey: per-frame change; events = change onsets (local rises above a threshold, 3 frames apart);
longest still = longest run of frames with almost no change; active = share of frames that move.
"""
import json, os, subprocess, sys
import numpy as np

W, H = 108, 192


def frames(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps=30,scale={W}:{H},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W)[:, :72, :].astype(np.float32)


def measure(path, ev_thr=1.6, still_thr=0.35):
    f = frames(path)
    if len(f) < 3:
        return None
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    ev, last = 0, -9
    for i in range(1, len(d)):
        if d[i] > ev_thr and d[i] > d[i - 1] * 1.5 and i - last >= 3:
            ev += 1; last = i
    still = run = 0
    for v in d:
        run = run + 1 if v < still_thr else 0
        still = max(still, run)
    dur = len(f) / 30
    return {'dur': round(dur, 2), 'events_per_s': round(ev / dur, 2), 'longest_still_s': round(still / 30, 2),
            'active': round(float((d >= still_thr).mean()), 2), 'mean_change': round(float(d.mean()), 2)}


if sys.argv[1] == 'refs':
    root, out = sys.argv[2], sys.argv[3]
    res = {}
    for creator in sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))):  # one folder per reference creator
        refdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'study', 'references', creator)
        picks = [f[:-3] for f in os.listdir(refdir) if f.startswith('D') and f.endswith('.md')]
        for code in picks:
            v = os.path.join(root, creator, code, 'video.mp4')
            if os.path.exists(v):
                m = measure(v)
                if m:
                    res[f'{creator}/{code}'] = m
    vals = lambda k: [m[k] for m in res.values()]
    res['_summary'] = {k: {'median': float(np.median(vals(k))), 'p25': float(np.percentile(vals(k), 25)), 'p75': float(np.percentile(vals(k), 75))}
                       for k in ('events_per_s', 'longest_still_s', 'active', 'mean_change')}
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps(res['_summary'], indent=1))
else:
    sdir, refs, out = sys.argv[2], sys.argv[3], sys.argv[4]
    ref = json.load(open(refs))['_summary']
    rows = {}
    for f in sorted(os.listdir(sdir)):
        if f.endswith('.mp4'):
            m = measure(os.path.join(sdir, f))
            # a held picture is not a fault; the faults are busy cuts of motion and
            # pictures that change before they can be seen. The old "few events / sits still / low motion" flags
            # pushed every edit into constant motion and are retired.
            flags = []
            if m['events_per_s'] > ref['events_per_s']['p75']:
                flags.append('busy')
            m['flags'] = flags
            rows[f[:-4]] = m
    json.dump({'reference': ref, 'scenes': rows}, open(out, 'w'), indent=1)
    print(f"reference: events/s {ref['events_per_s']['median']:.2f} (p25 {ref['events_per_s']['p25']:.2f}), "
          f"longest still {ref['longest_still_s']['median']:.2f}s, active {ref['active']['median']:.2f}")
    for k, m in rows.items():
        print(f"{k:24s} ev/s {m['events_per_s']:5.2f}  still {m['longest_still_s']:4.2f}s  active {m['active']:.2f}  {', '.join(m['flags'])}")
