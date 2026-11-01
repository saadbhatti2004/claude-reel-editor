#!/usr/bin/env python3
"""Beat Review: the local dashboard for one reel. The reel is split into numbered beats, you watch it the way Instagram
shows it, leave a note on any beat, and Claude re-renders only the beats you noted.

  python tools/beatreview.py <reel dir>                        open the dashboard (renders a draft first if there is none)
  python tools/beatreview.py <reel dir> --notes                print the open notes, for Claude to act on
  python tools/beatreview.py <reel dir> --rerender b03,b12 --say "what changed" [--mix final/mix.wav]
                                                               re-render only those beats and splice them in (a new round)
  python tools/beatreview.py <reel dir> --close n2,n5          mark notes done without a re-render (or --close all)

Options when opening: --video <file> (review an existing render), --mix <wav>, --handle <name> (the name shown in the
Instagram view), --port <n>, --no-open, --rebeat (split the beats again from the current plan).

Reads   edit/plan.json, edit/words.js, edit/notes.json (optional), edit/sound.json (optional)
Writes  review/beats.json (beats, notes, rounds: the one file Claude reads) and review/draft.mp4
Runs on 127.0.0.1 only. Nothing leaves the machine.
"""
import argparse, glob, http.server, json, os, re, socket, subprocess, sys, tempfile, threading, time, webbrowser
from urllib.parse import parse_qs, urlparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(HERE, 'beatreview')
FPS = 30  # the same frame rate as render.mjs
MAX_THUMB = 200_000


# ---------- files ----------
def replace_retry(src, dst):
    """os.replace, waiting out a reader on Windows (the browser may be streaming the file being swapped)."""
    for i in range(60):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == 59:
                raise
            time.sleep(0.5)


class Lock:
    """The server and the command line both write beats.json, so every read-modify-write takes this lock."""
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        for _ in range(400):
            try:
                os.close(os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.path) > 15:
                        os.remove(self.path)  # left behind by a crash
                except OSError:
                    pass
                time.sleep(0.025)
        raise TimeoutError('beats.json is locked')

    def __exit__(self, *a):
        try:
            os.remove(self.path)
        except OSError:
            pass


class Reel:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.review = os.path.join(self.root, 'review')
        self.edit = os.path.join(self.root, 'edit')
        self.state_path = os.path.join(self.review, 'beats.json')
        self.lock = Lock(self.state_path + '.lock')
        if not os.path.exists(os.path.join(self.edit, 'plan.json')):
            sys.exit(f'no edit/plan.json in {self.root}: run "node tools/render.mjs <edit dir> --plan" first')
        os.makedirs(self.review, exist_ok=True)

    def read_json(self, *p, default=None):
        path = os.path.join(self.root, *p)
        if not os.path.exists(path):
            return default
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def plan(self):
        return self.read_json('edit', 'plan.json')

    def words(self):
        path = os.path.join(self.edit, 'words.js')
        if not os.path.exists(path):
            return []
        src = open(path, encoding='utf-8').read()
        for name in ('CAPWORDS', 'WORDS'):
            m = re.search(r'window\.' + name + r'\s*=\s*', src)
            if m:
                try:
                    return json.JSONDecoder().raw_decode(src[m.end():])[0]
                except ValueError:  # an alias such as CAPWORDS = WORDS: use the next name
                    continue
        return []

    def load(self):
        if not os.path.exists(self.state_path):
            return None
        with open(self.state_path, encoding='utf-8') as f:
            return json.load(f)

    def save(self, st):
        st['version'] = st.get('version', 0) + 1
        fd, tmp = tempfile.mkstemp(dir=self.review, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(st, f, ensure_ascii=False, indent=1)
        replace_retry(tmp, self.state_path)

    def edit_state(self, fn):
        with self.lock:
            st = self.load()
            result = fn(st)
            self.save(st)
            return result


# ---------- beats ----------
def snap(t):
    return round(round(t * FPS) / FPS, 3)


def build_beats(plan, words):
    """A new beat at every scene cut, every sentence end, every real pause, and before a line gets too long to note on."""
    dur = plan['dur']
    scenes = sorted(plan['scenes'], key=lambda s: s['from'])

    def scene_i(t):
        i = 0
        for k, s in enumerate(scenes):
            if s['from'] <= t + 0.02:
                i = k
        return i

    groups, cur = [], []
    for w in words:
        if w['s'] >= dur:
            continue
        if cur:
            p = cur[-1]
            end = p['w'].rstrip('"\')')[-1:]
            if (scene_i(w['s']) != scene_i(cur[0]['s']) or end in ('.', '?', '!') or w['s'] - p['e'] >= 0.35
                    or len(cur) >= 13 or (len(cur) >= 8 and end in (',', ';', ':'))):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)

    starts = []
    seen_scene = set()
    for g in groups:
        i = scene_i(g[0]['s'])
        t = max(0.0, scenes[i]['from']) if i not in seen_scene else g[0]['s']
        seen_scene.add(i)
        starts.append((t, i, ' '.join(w['w'] for w in g)))
    for i, s in enumerate(scenes):  # a scene with no speech still gets its own beat
        if i not in seen_scene and s['from'] < dur:
            starts.append((max(0.0, s['from']), i, ''))
    starts.sort(key=lambda x: x[0])
    if not starts:
        starts = [(0.0, 0, '')]
    starts[0] = (0.0, starts[0][1], starts[0][2])

    raw = []
    for k, (t, i, text) in enumerate(starts):
        a, b = snap(t), snap(starts[k + 1][0]) if k + 1 < len(starts) else snap(dur)
        if b <= a:
            continue
        if raw and b - a < 0.3 and raw[-1]['scene_i'] == i:  # too short to note on its own
            raw[-1]['to'] = b
            raw[-1]['text'] = (raw[-1]['text'] + ' ' + text).strip()
            continue
        raw.append({'from': a, 'to': b, 'text': text, 'scene_i': i})
    width = max(2, len(str(len(raw))))
    out = []
    for k, r in enumerate(raw):
        s = scenes[r['scene_i']]
        out.append({'id': f'b{k + 1:0{width}d}', 'n': k + 1, 'from': r['from'], 'to': r['to'], 'text': r['text'],
                    'scene': s.get('id', ''), 'layout': s.get('layout', ''), 'changed': 1})
    return out


def sounds_of(reel, plan, beats):
    """The cue list, with file names cut down to their stem: no local path ever reaches the page."""
    data = reel.read_json('edit', 'sound.json', default=None)
    src = data['sounds'] if data and data.get('sounds') else plan.get('sfx', [])
    out = []
    for c in sorted(src, key=lambda x: x.get('t', 0)):
        t = float(c.get('t', 0))
        stem = os.path.splitext(re.split(r'[\\/]', c.get('f', ''))[-1])[0] if c.get('f') else ''
        beat = next((b['id'] for b in beats if b['from'] <= t < b['to']), beats[-1]['id'])
        out.append({'t': round(t, 3), 'role': c.get('role', 'cue'), 'file': stem, 'db': c.get('g'), 'why': c.get('why', ''), 'beat': beat})
    return out


def new_state(reel, plan, handle):
    beats = build_beats(plan, reel.words())
    return {'version': 0, 'plan_dur': plan['dur'], 'handle': handle, 'video': None, 'mix': None, 'round': 1, 'approved': False,
            'beats': beats, 'notes': [], 'next_note': 1, 'stale': [],
            'rounds': [{'n': 1, 'at': int(time.time()), 'beats': [], 'say': 'First cut'}]}


# ---------- video ----------
def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate:format=duration', '-of', 'json', path],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next((s for s in d['streams'] if s['codec_type'] == 'video'), {})
    num, den = (v.get('r_frame_rate') or '0/1').split('/')
    return {'dur': float(d['format']['duration']), 'w': v.get('width'), 'h': v.get('height'), 'fps': float(num) / max(1.0, float(den)),
            'audio': any(s['codec_type'] == 'audio' for s in d['streams'])}


def render_range(reel, a, b, out, audio=None):
    cmd = ['node', os.path.join(HERE, 'render.mjs'), reel.edit, '--from', f'{a:.3f}', '--to', f'{b:.3f}', '--out', out, '--draft']
    if audio:
        cmd += ['--audio', audio]
    subprocess.run(cmd, check=True)


def resolve_mix(reel, given):
    for m in (given, os.path.join(reel.root, 'final', 'mix.wav')):
        if not m:
            continue
        for p in (m, os.path.join(reel.root, m)):
            if os.path.exists(p):
                return os.path.abspath(p)
        if m == given:
            sys.exit(f'no mix at {given}')
    return None


def find_video(reel, st, given, mix):
    if given:
        if not os.path.exists(given):
            sys.exit(f'no video at {given}')
        return os.path.abspath(given)
    if st.get('video') and os.path.exists(st['video']):
        return st['video']
    for p in [os.path.join(reel.review, 'draft.mp4'), os.path.join(reel.review, 'full.mp4')] + sorted(
            glob.glob(os.path.join(reel.root, 'final', '*.mp4')), key=os.path.getmtime, reverse=True):
        if os.path.exists(p):
            return p
    if os.path.exists(os.path.join(reel.edit, 'index.html')):
        out = os.path.join(reel.review, 'draft.mp4')
        print('No draft yet, rendering one...')
        render_range(reel, 0.0, st['plan_dur'], out, mix)
        return out
    sys.exit('no video to review: pass --video <file>')


def rerender(reel, ids, say, mix):
    st = reel.load()
    if not st:
        sys.exit('open the dashboard once first, so the beats exist')
    by_id = {b['id']: b for b in st['beats']}
    bad = [i for i in ids if i not in by_id]
    if bad:
        sys.exit('unknown beats: ' + ', '.join(bad))
    if not os.path.exists(os.path.join(reel.edit, 'index.html')):
        sys.exit('no edit/index.html, so this reel cannot be re-rendered')
    base = st.get('video')
    if not base or not os.path.exists(base):
        sys.exit('no base video recorded: open the dashboard first')
    info = probe(base)
    mix = resolve_mix(reel, mix) if mix else None

    # neighbouring beats render as one range: fewer browser launches, and no seam between them
    chosen = sorted((by_id[i] for i in set(ids)), key=lambda b: b['from'])
    ranges = []
    for b in chosen:
        if ranges and abs(ranges[-1][1] - b['from']) < 1e-3:
            ranges[-1][1] = b['to']
        else:
            ranges.append([b['from'], b['to']])

    seg_dir = os.path.join(reel.review, 'beats')
    os.makedirs(seg_dir, exist_ok=True)
    segs = []
    for k, (a, b) in enumerate(ranges):
        out = os.path.join(seg_dir, f'seg{k}.mp4')
        print(f'Rendering {a:.2f} to {b:.2f} s')
        render_range(reel, a, b, out)
        segs.append((out, a))

    # lay each new range over the old picture at its exact frame; everything else stays untouched
    inputs = ['-i', base]
    graph, last = [], '[0:v]'
    for k, (path, a) in enumerate(segs):
        inputs += ['-i', path]
        graph.append(f'[{k + 1}:v]scale={info["w"]}:{info["h"]},setpts=PTS-STARTPTS+{a:.3f}/TB[s{k}]')
        graph.append(f'{last}[s{k}]overlay=0:0:eof_action=pass:repeatlast=0[v{k}]')
        last = f'[v{k}]'
    audio_map = []
    if mix:
        inputs += ['-i', mix]
        audio_map = ['-map', f'{len(segs) + 1}:a']
    elif info['audio']:
        audio_map = ['-map', '0:a']
    tmp = os.path.join(reel.review, 'draft.next.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(graph), '-map', last] + audio_map +
                   ['-t', f'{info["dur"]:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', tmp], check=True)
    target = os.path.join(reel.review, 'draft.mp4')
    replace_retry(tmp, target)  # a --video source file is never overwritten: the new cut always lands in review/draft.mp4
    for path, _ in segs:
        os.remove(path)

    def apply(s):
        s['round'] += 1
        n = s['round']
        s['video'] = target
        done_ids = sorted(b['id'] for b in chosen)
        for b in s['beats']:
            if b['id'] in done_ids:
                b['changed'] = n
        for note in s['notes']:
            if note['status'] == 'open' and note.get('beat') in done_ids:
                note['status'] = 'done'
                note['done_round'] = n
        s['stale'] = [] if mix else sorted(set(s.get('stale', [])) | set(done_ids))
        s['approved'] = False
        s['rounds'].append({'n': n, 'at': int(time.time()), 'beats': done_ids, 'say': say or ''})
        return n
    n = reel.edit_state(apply)
    print(f'Round {n} ready: {", ".join(sorted(b["id"] for b in chosen))}. The dashboard updates by itself.')


def print_notes(reel):
    st = reel.load()
    if not st:
        sys.exit('no review yet: open the dashboard first')
    by_id = {b['id']: b for b in st['beats']}
    open_notes = [n for n in st['notes'] if n['status'] == 'open']
    print(f'Round {st["round"]}, {"APPROVED" if st["approved"] else "not approved yet"}, {len(open_notes)} open note(s)')
    for n in open_notes:
        b = by_id.get(n.get('beat'))
        where = f'{b["id"]} ({b["from"]:.2f} to {b["to"]:.2f} s, scene {b["scene"]}), said: "{b["text"]}"' if b else 'WHOLE VIDEO'
        print(f'\n{n["id"]} at {n["t"]:.2f} s, {where}\n  {n["text"]}')


# ---------- checks ----------
def run_checks(reel, st):
    out = []
    add = lambda state, name, detail='': out.append({'state': state, 'name': name, 'detail': detail})
    path = st.get('video')
    try:
        info = probe(path)
    except Exception:
        return [{'state': 'fail', 'name': 'The video opens', 'detail': 'ffprobe could not read it'}]
    diff = abs(info['dur'] - st['plan_dur'])
    add('pass' if diff <= 0.1 else 'fail', 'Video length matches the edit', f'{info["dur"]:.2f} s against {st["plan_dur"]:.2f} s')
    add('pass' if (info['w'], info['h']) == (1080, 1920) else 'warn', 'Frame is 1080 x 1920', f'{info["w"]} x {info["h"]}')
    add('pass' if abs(info['fps'] - FPS) < 0.5 else 'warn', f'{FPS} frames a second', f'{info["fps"]:.2f}')
    if info['audio']:
        r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        m = re.search(r'max_volume: (-?[\d.]+) dB', r.stderr)
        if m:
            add('pass' if float(m.group(1)) <= -0.5 else 'warn', 'Sound does not clip', f'peak {m.group(1)} dB')
    else:
        add('warn', 'The video has sound', 'no audio track yet')
    beats, gaps = st['beats'], 0
    for a, b in zip(beats, beats[1:]):
        gaps += abs(a['to'] - b['from']) > 1e-3
    add('pass' if not gaps and beats[0]['from'] == 0 else 'fail', 'Beats cover the whole reel', f'{len(beats)} beats')
    words = reel.words()
    if words:
        said = sum(len(b['text'].split()) for b in beats)
        heard = sum(1 for w in words if w['s'] < st['plan_dur'])
        add('pass' if said == heard else 'warn', 'Every spoken word sits in a beat', f'{said} of {heard}')
    open_n = sum(1 for n in st['notes'] if n['status'] == 'open')
    add('pass' if not open_n else 'warn', 'No notes left open', f'{open_n} open' if open_n else '')
    stale = st.get('stale', [])
    add('pass' if not stale else 'warn', 'Sound is in step with the picture', 'remix needed for ' + ', '.join(stale) if stale else '')
    return out


# ---------- server ----------
def make_handler(reel):
    checks_cache = {}
    fonts = {'FamiljenGrotesk.ttf': os.path.join(UI, 'fonts', 'FamiljenGrotesk.ttf'),
             'JetBrainsMono.woff2': os.path.join(HERE, '..', 'kit', 'fonts', 'JetBrainsMono-latin.woff2')}

    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, *a):
            pass

        def send_bytes(self, body, ctype, status=200):
            self.send_response(status)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, obj, status=200):
            self.send_bytes(json.dumps(obj, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8', status)

        def local_only(self):
            host = (self.headers.get('Host') or '').split(':')[0]
            if host in ('127.0.0.1', 'localhost'):
                return True
            self.send_bytes(b'forbidden', 'text/plain', 403)
            return False

        def public_state(self):
            st = reel.load()
            pub = {k: v for k, v in st.items() if k not in ('video', 'mix')}
            notes = reel.read_json('edit', 'notes.json', default={}) or {}
            info = notes.get('reel', {})
            pub['title'] = info.get('title') or os.path.basename(reel.root)
            pub['reel_id'] = info.get('id') or os.path.basename(reel.root)
            whats = notes.get('scenes', {})
            pub['what'] = {k: v.get('what', '') for k, v in whats.items()}
            plan = reel.plan()
            pub['sounds'] = sounds_of(reel, plan, st['beats'])
            pub['fps'] = FPS
            return pub

        def do_GET(self):
            try:
                if not self.local_only():
                    return
                u = urlparse(self.path)
                if u.path == '/':
                    with open(os.path.join(UI, 'index.html'), 'rb') as f:
                        return self.send_bytes(f.read(), 'text/html; charset=utf-8')
                if u.path.startswith('/fonts/'):
                    p = fonts.get(u.path[7:])
                    if not p or not os.path.exists(p):
                        return self.send_bytes(b'', 'text/plain', 404)
                    with open(p, 'rb') as f:
                        return self.send_bytes(f.read(), 'font/ttf' if p.endswith('ttf') else 'font/woff2')
                if u.path == '/api/state':
                    since = parse_qs(u.query).get('since', [''])[0]
                    st = reel.load()
                    if since and since == str(st['version']):
                        return self.send_json({'unchanged': True})
                    return self.send_json(self.public_state())
                if u.path == '/api/checks':
                    st = reel.load()
                    key = (st['version'], os.path.getmtime(st['video']))
                    if checks_cache.get('key') != key:
                        checks_cache.update(key=key, value=run_checks(reel, st))
                    return self.send_json(checks_cache['value'])
                if u.path == '/video':
                    return self.send_video(reel.load()['video'])
                self.send_bytes(b'', 'text/plain', 404)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                pass

        def send_video(self, path):
            size = os.path.getsize(path)
            start, end, status = 0, size - 1, 200
            m = re.match(r'bytes=(\d*)-(\d*)', self.headers.get('Range') or '')
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    start = int(m.group(1))
                    end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
                else:
                    start = max(0, size - int(m.group(2)))
                status = 206
            if start >= size:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            self.send_response(status)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(end - start + 1))
            if status == 206:
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.end_headers()
            with open(path, 'rb') as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)

        def do_POST(self):
            try:
                if not self.local_only():
                    return
                if (self.headers.get('Content-Type') or '').split(';')[0] != 'application/json':
                    return self.send_json({'error': 'json only'}, 415)
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
                route = urlparse(self.path).path
                if route == '/api/note':
                    def add(st):
                        beat = body.get('beat')
                        if beat is not None and beat not in {b['id'] for b in st['beats']}:
                            raise ValueError('unknown beat')
                        thumb = body.get('thumb') or ''
                        if not thumb.startswith('data:image/jpeg;base64,') or len(thumb) > MAX_THUMB:
                            thumb = ''
                        note = {'id': f'n{st["next_note"]}', 'beat': beat, 't': round(float(body.get('t', 0)), 3), 'text': str(body.get('text', '')).strip(),
                                'thumb': thumb, 'status': 'open', 'round': st['round'], 'at': int(time.time())}
                        st['next_note'] += 1
                        st['notes'].append(note)
                        return note['id']
                    return self.send_json({'id': reel.edit_state(add)})
                if route == '/api/note/update':
                    def upd(st):
                        n = next(x for x in st['notes'] if x['id'] == body['id'])
                        if 'text' in body:
                            n['text'] = str(body['text']).strip()
                        if body.get('status') in ('open', 'done'):
                            n['status'] = body['status']
                            n['done_round'] = st['round'] if body['status'] == 'done' else None
                    reel.edit_state(upd)
                    return self.send_json({'ok': True})
                if route == '/api/note/delete':
                    def rm(st):
                        st['notes'] = [x for x in st['notes'] if x['id'] != body['id']]
                    reel.edit_state(rm)
                    return self.send_json({'ok': True})
                if route == '/api/approve':
                    def app(st):
                        st['approved'] = bool(body.get('approved'))
                    reel.edit_state(app)
                    return self.send_json({'ok': True})
                self.send_json({'error': 'not found'}, 404)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                pass
            except (KeyError, ValueError, StopIteration, TypeError) as e:
                self.send_json({'error': str(e)}, 400)

    return H


def free_port(start):
    for p in range(start, start + 40):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', p))
                return p
            except OSError:
                continue
    sys.exit('no free port')


def main():
    ap = argparse.ArgumentParser(description='Beat Review: the local dashboard for one reel')
    ap.add_argument('reel')
    ap.add_argument('--notes', action='store_true')
    ap.add_argument('--rerender')
    ap.add_argument('--close')
    ap.add_argument('--say', default='')
    ap.add_argument('--mix')
    ap.add_argument('--video')
    ap.add_argument('--handle')
    ap.add_argument('--port', type=int, default=4750)
    ap.add_argument('--no-open', action='store_true')
    ap.add_argument('--rebeat', action='store_true')
    a = ap.parse_args()
    reel = Reel(a.reel)

    if a.notes:
        return print_notes(reel)
    if a.rerender:
        return rerender(reel, [x.strip() for x in a.rerender.split(',') if x.strip()], a.say, a.mix)
    if a.close:
        def close(st):
            ids = None if a.close == 'all' else {x.strip() for x in a.close.split(',')}
            k = 0
            for n in st['notes']:
                if n['status'] == 'open' and (ids is None or n['id'] in ids):
                    n['status'], n['done_round'] = 'done', st['round']
                    k += 1
            return k
        return print(reel.edit_state(close), 'note(s) closed')

    plan = reel.plan()
    info = reel.read_json('edit', 'notes.json', default={}) or {}
    handle = a.handle or info.get('reel', {}).get('handle')
    with reel.lock:
        st = reel.load()
        if st is None:
            st = new_state(reel, plan, handle or 'your_handle')
        elif a.rebeat or abs(st['plan_dur'] - plan['dur']) > 0.02:
            if not a.rebeat:
                print('The plan changed length, so the beats were split again.')
            st['beats'] = build_beats(plan, reel.words())
            st['plan_dur'] = plan['dur']
        if handle:
            st['handle'] = handle
        reel.save(st)
    mix = resolve_mix(reel, a.mix)
    video = find_video(reel, st, a.video, mix)

    def set_video(s):
        s['video'] = video
        s['mix'] = mix
    reel.edit_state(set_video)

    port = free_port(a.port)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), make_handler(reel))
    url = f'http://127.0.0.1:{port}/'
    print(f'Beat Review is open at {url}\nPress Ctrl+C to stop it.')
    if not a.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
