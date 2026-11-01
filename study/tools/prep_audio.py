"""Per-reel AUDIO prep (after demucs + transcription): SFX event detection & classification on the non-vocal stem,
music beat/level analysis, spectrogram strips with markers.
usage: python prep_audio.py <reel_dir>
"""
import sys, os, json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, stft

D = sys.argv[1]
st = os.path.join(D, 'stems')
nv, sr = sf.read(os.path.join(st, 'no_vocals.wav')); vo, _ = sf.read(os.path.join(st, 'vocals.wav'))
mix, _ = sf.read(os.path.join(D, 'audio.wav'))
nvm = nv.mean(1); vom = vo.mean(1)
vis = json.load(open(os.path.join(D, 'visual.json')))
words = json.load(open(os.path.join(D, 'words.json')))['words']
db = lambda x: 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9)

# ---- STFT on the non-vocal stem
nper = 2048; hop = 441                          # 10 ms hop
f, t, Z = stft(nvm, fs=sr, nperseg=nper, noverlap=nper - hop, boundary=None)
P = np.abs(Z) ** 2 + 1e-12
bands = {'sub': (20, 120), 'low': (120, 500), 'mid': (500, 2500), 'high': (2500, 8000), 'air': (8000, 18000)}
BE = {k: 10 * np.log10(P[(f >= a) & (f < b)].sum(0) + 1e-12) for k, (a, b) in bands.items()}
tot = 10 * np.log10(P.sum(0))
cent = (f[:, None] * P).sum(0) / P.sum(0)
# spectral flux novelty (log-magnitude, positive)
L = np.log(P + 1e-9); flux = np.maximum(0, np.diff(L, axis=1)).sum(0); flux = np.concatenate([[0], flux])
# per-band onset strength
def novelty(x, w=50):
    out = np.zeros_like(x)
    for i in range(len(x)):
        out[i] = x[i] - np.median(x[max(0, i - w):i + 1])
    return out
nov = novelty(tot); fn = (flux - np.median(flux)) / (np.std(flux) + 1e-9)

# music bed level (rolling 3 s median) to judge what stands out
bed = np.array([np.median(tot[max(0, i - 150):i + 150]) for i in range(len(tot))])

events = []; last = -999
for i in range(5, len(tot) - 5):
    rise = tot[i] - bed[i]
    if (fn[i] > 3.0 or rise > 5) and rise > 2.5 and tot[i] == tot[max(0, i - 4):i + 5].max() and i - last > 10:
        # find the event span: from where it left the bed to where it returned (within 2.5 s)
        a = i
        while a > 0 and tot[a] > bed[a] + 2 and i - a < 150: a -= 1
        b = i
        while b < len(tot) - 1 and tot[b] > bed[b] + 2 and b - i < 250: b += 1
        attack = (i - a) * 0.01; decay = (b - i) * 0.01; dur = attack + decay
        seg = slice(a, b + 1)
        bands_rel = {k: round(float(BE[k][i] - tot[i]), 1) for k in bands}
        c0, c1 = float(np.median(cent[a:i + 1])), float(np.median(cent[i:b + 1]))
        # tonal? peakiness of the spectrum at the peak
        spec = P[:, i]; tonal = float(10 * np.log10(spec.max() / (np.median(spec) + 1e-12)))
        if dur < 0.06: kind = 'tick/click'
        elif bands_rel['sub'] > -6 and decay > 0.25: kind = 'boom/impact (low)'
        elif bands_rel['sub'] > -10 and dur < 0.35: kind = 'thud/hit'
        elif attack > 0.45 and attack > decay: kind = 'riser'
        elif dur > 0.15 and tonal < 25 and (abs(c1 - c0) > 600 or attack > 0.08): kind = 'whoosh/swish' + (' (rising)' if c1 > c0 else ' (falling)')
        elif tonal > 30: kind = 'tonal hit / chime'
        elif bands_rel['high'] > -6 or bands_rel['air'] > -10: kind = 'bright transient (snap/shimmer)'
        else: kind = 'hit (mid)'
        tt = i * 0.01
        events.append(dict(t=round(tt, 2), start=round(a * 0.01, 2), end=round(b * 0.01, 2), attack_s=round(attack, 2), decay_s=round(decay, 2),
                           above_bed_db=round(float(rise), 1), peak_db=round(float(tot[i]), 1), centroid_hz=[round(c0), round(c1)],
                           tonality_db=round(tonal, 1), band_balance_db=bands_rel, kind=kind))
        last = i

# context: nearest cut, nearest text event start, word being spoken
cuts = vis['cuts']; tev = vis['text_events']
for e in events:
    t0 = e['t']
    nc = min(cuts, key=lambda c: abs(c - t0)) if cuts else None
    e['nearest_cut'] = None if nc is None else dict(t=nc, offset_s=round(t0 - nc, 2))
    nt = min(tev, key=lambda x: abs(x['t_in'] - t0)) if tev else None
    e['nearest_text_in'] = None if nt is None else dict(text=nt['text'], t=nt['t_in'], offset_s=round(t0 - nt['t_in'], 2))
    w = [x for x in words if x['s'] - 0.15 <= t0 <= x['e'] + 0.15]
    e['word'] = ' '.join(x['w'] for x in w) if w else None

# ---- music: beat period from onset autocorrelation, voice/music levels, ducking
env = np.maximum(0, novelty(BE['low'] + 0.5 * BE['mid'], 30))
ac = np.correlate(env - env.mean(), env - env.mean(), 'full')[len(env) - 1:]
lo, hi = int(0.33 / 0.01), int(1.5 / 0.01)
lag = lo + int(np.argmax(ac[lo:hi])); bpm = 60 / (lag * 0.01)
win = int(0.5 * sr)
vlev = [db(vom[k:k + win]) for k in range(0, len(vom) - win, win)]
mlev = [db(nvm[k:k + win]) for k in range(0, len(nvm) - win, win)]
speech = [i for i, v in enumerate(vlev) if v > np.percentile(vlev, 40)]
gaps = [i for i, v in enumerate(vlev) if v < np.percentile(vlev, 15)]
music = dict(est_bpm=round(bpm, 1), voice_db_p75=round(float(np.percentile(vlev, 75)), 1),
             music_db_median=round(float(np.median(mlev)), 1),
             music_under_voice_db=round(float(np.percentile(vlev, 75) - np.median(mlev)), 1),
             music_during_speech_db=round(float(np.median([mlev[i] for i in speech])), 1) if speech else None,
             music_during_gaps_db=round(float(np.median([mlev[i] for i in gaps])), 1) if gaps else None,
             music_level_per_2s=[round(float(np.mean(mlev[i:i + 4])), 1) for i in range(0, len(mlev), 4)])
json.dump(dict(sfx_events=events, music=music), open(os.path.join(D, 'audio_events.json'), 'w'), indent=1)

# ---- spectrogram strips (6 s each): music/SFX stem on top, voice stem below, cut + event markers
from PIL import Image, ImageDraw, ImageFont
SD = os.path.join(D, 'spectro'); os.makedirs(SD, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 14)
def specimg(x, t0, t1, h):
    seg = x[int(t0 * sr):int(t1 * sr)]
    if len(seg) < nper: seg = np.pad(seg, (0, nper))
    ff, tt, ZZ = stft(seg, fs=sr, nperseg=1024, noverlap=1024 - 220, boundary=None)
    S = 10 * np.log10(np.abs(ZZ) ** 2 + 1e-10)
    # log-frequency rows 40 Hz .. 16 kHz
    rowsf = np.geomspace(40, 16000, h)[::-1]
    idx = np.clip(np.searchsorted(ff, rowsf), 0, len(ff) - 1)
    S = S[idx]; S = np.clip((S + 90) / 80, 0, 1)
    rgb = np.stack([np.clip(S * 2.2 - 0.6, 0, 1), np.clip(S * 1.8 - 0.9, 0, 1), np.clip(0.3 + S * 0.4 - S ** 3, 0, 1)], -1)
    return Image.fromarray((rgb * 255).astype(np.uint8))
dur = len(nvm) / sr; Wpx = 1500
for k, t0 in enumerate(np.arange(0, dur, 6.0)):
    t1 = min(dur, t0 + 6.0)
    a = specimg(nvm, t0, t1, 260).resize((int(Wpx * (t1 - t0) / 6), 260)); b = specimg(vom, t0, t1, 140).resize((a.width, 140))
    im = Image.new('RGB', (Wpx, 260 + 140 + 70), (0, 0, 0)); im.paste(a, (0, 0)); im.paste(b, (0, 262))
    d = ImageDraw.Draw(im)
    X = lambda tt: int((tt - t0) / 6.0 * Wpx)
    for s in np.arange(np.ceil(t0 * 2) / 2, t1, 0.5):
        d.line([X(s), 402, X(s), 410], fill=(200, 200, 200)); d.text((X(s) + 2, 404), f'{s:.1f}', font=font, fill=(200, 200, 200))
    for c in cuts:
        if t0 <= c < t1: d.line([X(c), 0, X(c), 400], fill=(255, 40, 40), width=2)
    for e in events:
        if t0 <= e['t'] < t1:
            d.line([X(e['t']), 0, X(e['t']), 12], fill=(0, 255, 120), width=3)
            d.text((X(e['t']) + 3, 420), e['kind'].split(' ')[0][:14], font=font, fill=(0, 255, 120))
    for w in words:
        if t0 <= w['s'] < t1: d.text((X(w['s']), 440 + (hash(w['w']) % 2) * 14), w['w'], font=font, fill=(255, 220, 120))
    d.text((4, 2), 'MUSIC+SFX stem (red = cut, green = detected event)', font=font, fill=(255, 255, 255))
    d.text((4, 264), 'VOICE stem', font=font, fill=(255, 255, 255))
    im.save(os.path.join(SD, f'spec_{k:02d}_{t0:05.1f}s.png'))
print(f'{D}: {len(events)} sfx events, bpm~{music["est_bpm"]}, music {music["music_under_voice_db"]} dB under voice')
