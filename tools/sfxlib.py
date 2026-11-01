"""Build the educational engine's sound effects library from Mixkit (free licence: commercial use, social media, no
credit needed, no sign-up; mixkit.co/license). Real recorded and produced effects.

  python sfxlib.py fetch   <lib dir>     list every effect in the categories below (catalog.json)
  python sfxlib.py get     <lib dir>     download the full-quality WAV of every listed effect that passes the filter
  python sfxlib.py measure <lib dir>     measure each file (length, attack, peak time, brightness, tonality, melody)

Effects carry no tune, so they never fight the bed or the voice. Titles that name instruments, melodies or jingles are skipped, and the
measure step flags any file whose pitch moves through several stable notes (a melody), which the planner never uses.
"""
import html, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

CATS = ['whoosh', 'woosh', 'swoosh', 'swish', 'transition', 'zoom', 'slide', 'sweep', 'swell', 'click', 'mouse',
        'interface', 'tap', 'pop', 'bubbles', 'keyboard', 'type', 'typewriter', 'glitch', 'static', 'hit', 'impact',
        'thud', 'punch', 'boom', 'drop', 'notification', 'correct', 'error', 'wrong', 'beep', 'bleep', 'camera',
        'paper', 'page', 'write', 'clock', 'countdown', 'coin', 'money', 'laptop', 'phone', 'high-tech', 'technology',
        'electricity', 'lock', 'rewind', 'tape-machine', 'cinematic', 'sparkle', 'white-noise',
        'stomp', 'whip', 'spin', 'squeak', 'office', 'ding']
# skipped: anything with a tune, and anything that would not belong in a professional edit
SKIP = re.compile(r'music|melod|jingle|piano|guitar|flute|violin|orchestr|choir|brass|synth|drum|cymbal|bass\b|'
                  r'fanfare|harp|song|sing|vocal|voice|laugh|scream|game ?over|win\b|winning|lose|casino|slot|'
                  r'trumpet|bell|chime|xylophone|marimba|ukulele|organ|beat|rhythm|tune|arcade|retro game|'
                  r'horror|scary|monster|gun|shot|explosion|bomb|war|battle|fart|kiss|moan|baby|crying|animal', re.I)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def parse(page):
    out = []
    for m in re.finditer(r'data-audio-player-item-id-value="(\d+)"', page):
        tail = page[m.end(): m.end() + 6000]
        t = re.search(r'item-grid-card__title">\s*(.*?)\s*</h2>', tail, re.S)
        tags = re.findall(r'href="/free-sound-effects/([a-z0-9-]+)/"', tail[:4000])
        if t:
            out.append({'id': int(m.group(1)), 'title': html.unescape(t.group(1).strip()), 'tags': sorted(set(tags))})
    return out


def fetch(lib):
    cat = {}
    for c in CATS:
        for p in range(1, 9):
            url = f'https://mixkit.co/free-sound-effects/{c}/' + (f'?page={p}' if p > 1 else '')
            try:
                items = parse(get(url).decode('utf-8', 'replace'))
            except Exception:
                break
            new = 0
            for it in items:
                if it['id'] not in cat:
                    cat[it['id']] = dict(it, cats=[c]); new += 1
                elif c not in cat[it['id']]['cats']:
                    cat[it['id']]['cats'].append(c)
            if not items or new == 0 and p > 1:
                break
        print(f'{c:18s} {len(cat):5d} total', flush=True)
    json.dump(sorted(cat.values(), key=lambda x: x['id']), open(os.path.join(lib, 'catalog.json'), 'w', encoding='utf-8'), indent=0)


def download(lib):
    cat = json.load(open(os.path.join(lib, 'catalog.json'), encoding='utf-8'))
    os.makedirs(os.path.join(lib, 'wav'), exist_ok=True)
    keep = [c for c in cat if not SKIP.search(c['title'] + ' ' + ' '.join(c['tags']))]
    print(len(cat), 'listed,', len(keep), 'pass the title filter')

    def one(c):
        p = os.path.join(lib, 'wav', f"{c['id']}.wav")
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return 0
        try:
            open(p, 'wb').write(get(f"https://assets.mixkit.co/active_storage/sfx/{c['id']}/{c['id']}.wav"))
            return 1
        except Exception:
            return 0
    with ThreadPoolExecutor(6) as ex:
        n = sum(ex.map(one, keep))
    print(n, 'downloaded')


def measure(lib):
    import numpy as np, subprocess
    SR = 48000
    cat = {c['id']: c for c in json.load(open(os.path.join(lib, 'catalog.json'), encoding='utf-8'))}
    rows = []
    for f in sorted(os.listdir(os.path.join(lib, 'wav'))):
        i = int(f.split('.')[0]); p = os.path.join(lib, 'wav', f)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
        if len(x) < 200:
            continue
        m = x.mean(1); a = np.abs(m)
        hop = 240; fr = a[: len(a) // hop * hop].reshape(-1, hop); env = np.sqrt((fr ** 2).mean(1) + 1e-12)
        edb = 20 * np.log10(env / env.max() + 1e-9)
        on = int(np.argmax(edb > -30)); pk = int(np.argmax(env)); act = np.where(edb > -40)[0]
        end = int(act[-1]) if len(act) else len(env) - 1
        # spectrum: brightness and tonality (peakiness of the long-term spectrum)
        seg = m[on * hop: (end + 1) * hop]
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) if len(seg) > 64 else np.zeros(2)
        fq = np.fft.rfftfreq(len(seg), 1 / SR) if len(seg) > 64 else np.zeros(2)
        cen = float((spec * fq).sum() / (spec.sum() + 1e-9))
        flat = float(np.exp(np.mean(np.log(spec + 1e-9))) / (spec.mean() + 1e-9))
        low = float((spec[fq < 150] ** 2).sum() / ((spec ** 2).sum() + 1e-9))
        # melody check: dominant pitch per 40 ms frame; a melody holds 3+ distinct stable notes
        notes = []
        w = 1920
        for k in range(on * hop, (end + 1) * hop - w, w):
            fr_ = m[k:k + w] * np.hanning(w); s = np.abs(np.fft.rfft(fr_)); ff = np.fft.rfftfreq(w, 1 / SR)
            band = (ff > 120) & (ff < 2000)
            if s[band].max() > 8 * np.median(s[band]) and np.sqrt((fr_ ** 2).mean()) > env.max() * 0.08:
                notes.append(round(12 * np.log2(ff[band][np.argmax(s[band])] / 440)))
            else:
                notes.append(None)
        stable = []
        for k in range(1, len(notes)):
            if notes[k] is not None and notes[k] == notes[k - 1] and (not stable or stable[-1] != notes[k]):
                stable.append(notes[k])
        side = float(np.sqrt(((x[:, 0] - x[:, 1]) ** 2).mean()) / (np.sqrt((m ** 2).mean()) + 1e-9))
        c = cat.get(i, {'title': '?', 'tags': [], 'cats': []})
        rows.append({'id': i, 'title': c['title'], 'tags': c['tags'], 'cats': c['cats'], 'dur': round(len(m) / SR, 3),
                     'on': round(on * hop / SR, 3), 'peak': round(pk * hop / SR, 3), 'end': round(end * hop / SR, 3),
                     'centroid': round(cen), 'flat': round(flat, 3), 'low': round(low, 3), 'stereo': round(side, 3),
                     'notes': len(set(stable)), 'melody': len(set(stable)) >= 3})
    json.dump(rows, open(os.path.join(lib, 'measured.json'), 'w', encoding='utf-8'), indent=0)
    print(len(rows), 'measured,', sum(r['melody'] for r in rows), 'flagged as melodic')


def derive(lib):
    """Cut single keystrokes and counter ticks out of real recordings, and build the sub drop and the risers.
    Writes lib/derived/<role>_NN.wav and lib/derived/measured.json (same fields as measured.json)."""
    import numpy as np, subprocess, wave
    SR = 48000
    out = os.path.join(lib, 'derived'); os.makedirs(out, exist_ok=True)

    def load(i, ss=0.0, dur=None):
        cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', os.path.join(lib, 'wav', f'{i}.wav')]
        cmd += (['-t', str(dur)] if dur else []) + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
        return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, dtype=np.float32).reshape(-1, 2).copy()

    def save(name, x):
        x = x / (np.abs(x).max() + 1e-9) * 0.89
        with wave.open(os.path.join(out, name + '.wav'), 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())

    def slices(ids, win, gap, keep, prefix):
        got = []
        for i in ids:
            x = load(i); m = x.mean(1)
            hp = np.diff(m, prepend=0)                                    # attack lives in the highs
            hop = 96; e = np.sqrt((hp[: len(hp) // hop * hop].reshape(-1, hop) ** 2).mean(1) + 1e-12)
            edb = 20 * np.log10(e / e.max() + 1e-9)
            flux = np.diff(edb, prepend=edb[0])
            ons = [k for k in range(1, len(e) - 1) if flux[k] > 9 and edb[k] > -26 and edb[k] >= edb[k + 1] - 3]
            ons = [k for j, k in enumerate(ons) if (j == 0 or k - ons[j - 1] > gap * SR / hop) and (j == len(ons) - 1 or ons[j + 1] - k > gap * SR / hop)]
            for k in ons:
                a = max(0, k * hop - int(0.004 * SR)); b = a + int(win * SR)
                if b > len(x):
                    continue
                s = x[a:b].copy(); f = int(0.02 * SR); s[-f:] *= np.linspace(1, 0, f)[:, None]
                got.append((float(edb[k]), s))
        got.sort(key=lambda g: -g[0])
        lv = np.median([g[0] for g in got]) if got else 0
        pick = [s for l, s in got if abs(l - lv) < 6][:keep]
        for n, s in enumerate(pick):
            save(f'{prefix}_{n:02d}', s)
        return len(pick)

    nk = slices([2537, 2531, 1386, 2532, 1391], 0.075, 0.06, 28, 'key')
    nt = slices([1054, 1053, 1056], 0.05, 0.05, 16, 'tick')
    # sub drop: a falling sine with its harmonics, so a phone speaker (no real sub) still hears the weight
    t = np.arange(int(1.3 * SR)) / SR
    f = 32 + 46 * np.exp(-t / 0.18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(t / 0.004, 1) * np.exp(-t / 0.42)
    sub = (np.sin(ph) + 0.35 * np.tanh(2.5 * np.sin(ph)) + 0.12 * np.sin(2 * ph)) * env
    hit = load(774)[: len(t)].mean(1) if os.path.exists(os.path.join(lib, 'wav', '774.wav')) else 0
    save('sub_00', np.repeat((sub + 0.25 * hit)[:, None], 2, axis=1))
    save('sub_01', np.repeat(sub[:, None], 2, axis=1))
    # risers: the real swells, trimmed so each ends at its loudest point (they are placed by their end)
    for n, (i, end, length) in enumerate([(2634, 1.85, 1.6), (790, 2.49, 1.9)]):
        x = load(i, max(0, end - length), length)
        f = int(0.01 * SR); x[:f] *= np.linspace(0, 1, f)[:, None]
        save(f'riser_{n:02d}', x)
    print(nk, 'keystrokes,', nt, 'ticks, 2 subs, 2 risers')
    # measure the derived files with the same fields
    rows = []
    for fn in sorted(os.listdir(out)):
        if not fn.endswith('.wav'):
            continue
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(out, fn), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        m = np.abs(np.frombuffer(raw, dtype=np.float32)); hop = 240
        e = np.sqrt((m[: len(m) // hop * hop].reshape(-1, hop) ** 2).mean(1) + 1e-12); edb = 20 * np.log10(e / e.max() + 1e-9)
        act = np.where(edb > -40)[0]
        rows.append({'id': fn[:-4], 'title': fn[:-4], 'dur': round(len(m) / SR, 3), 'on': round(int(np.argmax(edb > -30)) * hop / SR, 3),
                     'peak': round(int(np.argmax(e)) * hop / SR, 3), 'end': round(int(act[-1]) * hop / SR, 3) if len(act) else 0, 'melody': False})
    json.dump(rows, open(os.path.join(out, 'measured.json'), 'w'), indent=0)


if __name__ == '__main__':
    cmd, lib = sys.argv[1], sys.argv[2]
    os.makedirs(lib, exist_ok=True)
    {'fetch': fetch, 'get': download, 'measure': measure, 'derive': derive}[cmd](lib)
