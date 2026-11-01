"""Pick a reel's bed by measurement (ENGINE.md decision 8).

For every track in a folder, every place where its beat comes in is tried as the reel's turn: the track is started so
that its first kick after a break lands on the turn's first word, and the reel's whole length is measured as it would
play. A good bed has an audible, calmer part before the turn, a clear kick entry on it, a steady rhythm after it with
no break of its own, and little energy where the voice lives.

usage: python beds.py <tracks dir> <tracks.json> --turn 20.0 --dur 45.0 --out <ranking.json> [--top 12]

tracks.json is a list of {id, title}; audio files are <tracks dir>/<id>.*
Each result gives bed_start (seconds into the track where the reel starts) and bed_at (seconds into the reel where
the bed starts; 0 unless the track's own intro is too short), ready for mix.py --bed-start / --bed-at / --drop.
"""
import argparse, glob, json, os, subprocess
import numpy as np

SR = 22050
HOP = 256                      # 11.6 ms
NFFT = 2048

ap = argparse.ArgumentParser()
ap.add_argument('dir'); ap.add_argument('tracks')
ap.add_argument('--turn', type=float, required=True); ap.add_argument('--dur', type=float, required=True)
ap.add_argument('--out', required=True); ap.add_argument('--top', type=int, default=12)
ap.add_argument('--skip', default='Slowed,Sped Up,SPED UP', help='title words that rule a track out')
a = ap.parse_args()


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def stft_mag(x):
    n = 1 + (len(x) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    win = np.hanning(NFFT).astype(np.float32)
    out = np.empty((n, NFFT // 2 + 1), dtype=np.float32)
    for i in range(0, n, 4096):                                   # in blocks, to keep memory small
        out[i:i + 4096] = np.abs(np.fft.rfft(x[idx[i:i + 4096]] * win, axis=1))
    return out


def db(p):
    return 10 * np.log10(p + 1e-10)


def smooth(v, sec):
    k = max(1, int(sec * SR / HOP))
    return np.convolve(v, np.ones(k) / k, mode='same')


def tempo_and_clarity(flux):
    """Beats per minute and how clearly the onsets repeat (autocorrelation peak, 0..1)."""
    f = flux - flux.mean()
    if f.std() < 1e-9:
        return 0.0, 0.0
    ac = np.correlate(f, f, mode='full')[len(f) - 1:]
    ac /= ac[0]
    fps = SR / HOP
    lo, hi = int(fps * 60 / 160), int(fps * 60 / 80)     # fold to 80..160 BPM, so a busy hi-hat is not the tempo
    lag = lo + int(np.argmax(ac[lo:hi]))
    return 60 * fps / lag, float(ac[lag])


def first_kick(low_db, low_flux, i_from, i_to):
    """Index of the kick that starts the beat: the first frame from which the low band stays near its level after the
    entry (a lone hit inside a break does not count), moved onto the nearest low-band onset."""
    post = np.median(low_db[i_to:i_to + int(3 * SR / HOP)]) if i_to < len(low_db) else low_db[i_from:i_to].max()
    w = max(2, int(0.25 * SR / HOP))
    for j in range(i_from, i_to):
        if np.mean(low_db[j:j + w]) >= post - 4:
            r = int(0.06 * SR / HOP)
            a0, a1 = max(0, j - r), min(len(low_flux), j + r + 1)
            return a0 + int(np.argmax(low_flux[a0:a1]))
    return i_from


tracks = json.load(open(a.tracks, encoding='utf-8'))
skip = [s.strip().lower() for s in a.skip.split(',') if s.strip()]
fps = SR / HOP
pre_need, post_need = a.turn, a.dur - a.turn
results = []
for t in tracks:
    if any(s in t['title'].lower() for s in skip):
        continue
    files = glob.glob(os.path.join(a.dir, t['id'] + '.*'))
    if not files:
        continue
    x = load(files[0])
    if len(x) < SR * (a.dur + 5):
        continue
    S = stft_mag(x) ** 2
    f = np.fft.rfftfreq(NFFT, 1 / SR)
    low = S[:, (f > 35) & (f < 130)].sum(1)
    voice = S[:, (f > 1000) & (f < 4000)].sum(1)            # where speech is understood
    full = S.sum(1)
    logS = np.log1p(S[:, f < 8000] * 1e3)
    flux = np.maximum(np.diff(logS, axis=0, prepend=logS[:1]), 0).sum(1)
    llog = np.log1p(S[:, (f > 35) & (f < 130)] * 1e3)
    low_flux = np.maximum(np.diff(llog, axis=0, prepend=llog[:1]), 0).sum(1)
    low_s = smooth(db(low), 1.0)
    full_s = smooth(db(full), 1.0)
    n = len(full)
    # candidate entries: where the low band jumps up against the 6 s before it
    cands = []
    step = int(0.25 * fps)
    for i in range(int(6 * fps), n - int(4 * fps), step):
        jump = low_s[i + int(0.5 * fps):i + int(3 * fps)].mean() - low_s[i - int(6 * fps):i - int(0.5 * fps)].mean()
        cands.append((jump, i))
    cands.sort(reverse=True)
    picked = []
    for jump, i in cands:
        if jump < 4:
            break
        if all(abs(i - j) > 6 * fps for _, j in picked):
            picked.append((jump, i))
        if len(picked) == 5:
            break
    best = None
    for jump, i in picked:
        k = first_kick(db(low), low_flux, i - int(1.0 * fps), i + int(1.5 * fps))
        d = k / fps                                             # the kick, in track seconds
        bed_start = d - pre_need
        bed_at = 0.0
        if bed_start < 0:
            if bed_start < -2.0:                                 # the reel would open on more than 2 s of silence
                continue
            bed_at, bed_start = -bed_start, 0.0
        if d + post_need > n / fps:
            continue
        p0, p1 = int(bed_start * fps), k
        q0, q1 = k, int((d + post_need) * fps)
        pre_db = db(full[p0:p1].mean()) if p1 - p0 > fps else -99
        post_db = db(full[q0:q1].mean())
        rise = post_db - pre_db
        low_rise = db(low[q0:q1].mean()) - (db(low[p0:p1].mean()) if p1 - p0 > fps else -99)
        bpm, clarity = tempo_and_clarity(flux[q0:q1])
        # a break inside the post part: the quietest 1 s against the part's median
        post_curve = full_s[q0:q1]
        hole = float(min(30.0, np.median(post_curve) - post_curve.min()))
        pre_curve = full_s[p0:p1] if p1 - p0 > fps else np.array([-99.0])
        pre_hole = float(np.median(pre_curve) - pre_curve.min()) if p1 - p0 > fps else 0.0
        vshare = float(voice[q0:q1].sum() / (full[q0:q1].sum() + 1e-12))
        # the entry itself: the low band in the 2 s after the kick against the 2 s before it (a break that ends on the
        # turn); the long build is shaped in the mix (mix.py --pre-hp), so this is what the track must bring
        w2 = int(2 * fps)
        entry = float(db(low[k:k + w2].mean()) - db(low[max(0, k - w2):k].mean()))
        # score: kick entry, steady rhythm, no breaks, calmer but audible intro, room for the voice, a usable tempo
        tempo_fit = 1.0 - min(1.0, abs(min(bpm, 2 * bpm if bpm < 80 else bpm) - 110) / 40)
        intro_fit = 1.0 - min(1.0, abs(min(rise, 20) - 8) / 10) if pre_db > -99 else 0.3
        score = (min(max(entry, 0), 20) / 20 * 3.0 + min(max(low_rise, 0), 25) / 25 * 1.0 + clarity * 3.0
                 + tempo_fit * 1.0 + intro_fit * 0.5 - min(hole, 15) / 15 * 2.0 - min(pre_hole, 20) / 20 * 0.3
                 - vshare * 4.0)
        d, bed_start, bed_at, bpm, clarity, low_rise, rise, score, entry = map(float, (d, bed_start, bed_at, bpm, clarity, low_rise, rise, score, entry))
        r = dict(id=t['id'], title=t['title'], kick=round(d, 3), bed_start=round(bed_start, 3), bed_at=round(bed_at, 3),
                 bpm=round(bpm, 1), clarity=round(clarity, 3), entry=round(entry, 1), low_rise=round(low_rise, 1), rise=round(rise, 1),
                 post_hole=round(hole, 1), pre_hole=round(pre_hole, 1), voice_share=round(vshare, 3),
                 score=round(score, 3))
        if best is None or r['score'] > best['score']:
            best = r
    if best:
        results.append(best)
    print(f"{t['title'][:44]:44s} " + (f"kick {best['kick']:6.2f}  bpm {best['bpm']:5.1f}  clar {best['clarity']:.2f}  entry+{best['entry']:4.1f}  "
          f"low+{best['low_rise']:4.1f}  hole {best['post_hole']:4.1f}  voice {best['voice_share']:.2f}  "
          f"score {best['score']:.2f}" if best else 'no usable entry'), flush=True)

results.sort(key=lambda r: -r['score'])
json.dump(dict(turn=a.turn, dur=a.dur, ranking=results), open(a.out, 'w', encoding='utf-8'), indent=1)
print('\nTOP')
for r in results[:a.top]:
    print(f"{r['score']:5.2f}  {r['title'][:44]:44s} start {r['bed_start']:6.2f} at {r['bed_at']:.2f}  bpm {r['bpm']}")
