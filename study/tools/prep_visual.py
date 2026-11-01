"""Per-reel VISUAL prep: every frame -> metrics (motion/zoom/blur/cuts), OCR text timeline, annotated frame sheets.
usage: python prep_visual.py <reel_dir>
"""
import sys, os, json, glob, subprocess, re
import numpy as np, cv2

D = sys.argv[1]
V = os.path.join(D, 'video.mp4')
fr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                     '-of', 'csv=p=0', V], capture_output=True, text=True).stdout.strip()
num, den = map(int, fr.split('/')); FPS = num / den
wh = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                     '-of', 'csv=p=0', V], capture_output=True, text=True).stdout.strip()
LAND = int(wh.split(',')[0]) > int(wh.split(',')[1])   # landscape reels keep their shape everywhere below
FW, FH = (640, 360) if LAND else (360, 640)            # analysis frames
OW, OH = (1920, 1080) if LAND else (1080, 1920)        # coordinates reported in output pixels

# ---- 1. every frame
FD = os.path.join(D, 'frames')
if not os.path.isdir(FD) or not os.listdir(FD):
    os.makedirs(FD, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', V, '-vf', f'scale={FW}:{FH}', '-q:v', '3', os.path.join(FD, '%05d.jpg')], check=True)
files = sorted(glob.glob(os.path.join(FD, '*.jpg')))
N = len(files)

# ---- 2. per-frame metrics
orb = cv2.ORB_create(1200); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
prev = None; prevF = None; rows = []
for i, f in enumerate(files):
    im = cv2.imread(f); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    sharp = float(cv2.Laplacian(g, cv2.CV_64F).var())
    r = dict(f=i, t=round(i / FPS, 3), bright=round(float(g.mean()), 1), sat=round(float(hsv[..., 1].mean()), 1), sharp=round(sharp, 1),
             rgb=[round(float(x), 1) for x in im.reshape(-1, 3).mean(0)[::-1]])
    kp, de = orb.detectAndCompute(g, None)
    if prev is not None:
        r['diff'] = round(float(np.mean(np.abs(g.astype(np.float32) - prev.astype(np.float32)))), 2)
        r['scale'] = r['tx'] = r['ty'] = r['rot'] = None; r['inl'] = 0
        if prevF[1] is not None and de is not None and len(prevF[0]) > 20 and len(kp) > 20:
            m = bf.match(prevF[1], de)
            if len(m) > 20:
                p1 = np.float32([prevF[0][x.queryIdx].pt for x in m]); p2 = np.float32([kp[x.trainIdx].pt for x in m])
                M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if M is not None:
                    r['inl'] = int(inl.sum()); r['scale'] = round(float(np.hypot(M[0, 0], M[0, 1])), 4)
                    r['rot'] = round(float(np.degrees(np.arctan2(M[1, 0], M[0, 0]))), 3)
                    r['tx'] = round(float(M[0, 2]), 2); r['ty'] = round(float(M[1, 2]), 2)
    rows.append(r); prev = g; prevF = (kp, de)

# cuts: big diff + broken feature continuity, relative to the local median
diffs = np.array([r.get('diff', 0) for r in rows])
cuts = [0]
for r in rows[1:]:
    i = r['f']; loc = np.median(diffs[max(1, i - 10):i + 10])
    if (r['diff'] > max(14, 3.0 * loc) and r['inl'] < 60) or (r['inl'] < 10 and r['diff'] > 9):
        if i - cuts[-1] > 2: cuts.append(i)
cuts.append(N)

shots = []
for a, b in zip(cuts, cuts[1:]):
    z = 1.0; traj = [1.0]; px = 0.0; py = 0.0; rot = 0.0; moves = []
    sharp = [rows[k]['sharp'] for k in range(a, b)]
    med = float(np.median(sharp)) if sharp else 0
    for k in range(a + 1, b):
        r = rows[k]
        if r.get('scale') and r['inl'] >= 25 and 0.85 < r['scale'] < 1.15:
            z *= r['scale']; px += r['tx'] or 0; py += r['ty'] or 0; rot += r['rot'] or 0
        traj.append(z)
    blur = [k for k in range(a, b) if med > 0 and rows[k]['sharp'] < 0.5 * med]
    shots.append(dict(start_f=a, end_f=b - 1, t0=round(a / FPS, 3), t1=round(b / FPS, 3), dur=round((b - a) / FPS, 3),
                      zoom_total=round(z, 4), zoom_curve=[round(traj[int(j * (len(traj) - 1) / 8)], 4) for j in range(9)],
                      pan_px=[round(px, 1), round(py, 1)], rot_deg=round(rot, 2), sharp_median=round(med, 1),
                      blur_frames=[blur[0], blur[-1]] if blur else None, blur_count=len(blur),
                      mean_rgb=[round(float(np.mean([rows[k]['rgb'][c] for k in range(a, b)])), 1) for c in range(3)]))

# smooth zoom/pan moves inside shots
moves = []
for s in shots:
    cur = None
    for k in range(s['start_f'] + 1, s['end_f'] + 1):
        r = rows[k]; zr = (r['scale'] - 1) if (r.get('scale') and r['inl'] >= 25) else 0
        if abs(zr) > 0.0025:
            if cur and k - cur['e'] <= 2 and np.sign(zr) == cur['sgn']:
                cur['e'] = k; cur['z'] *= (1 + zr); cur['peak'] = max(cur['peak'], abs(zr))
            else:
                if cur: moves.append(cur)
                cur = dict(s=k, e=k, sgn=float(np.sign(zr)), z=1 + zr, peak=abs(zr))
    if cur: moves.append(cur)
moves = [dict(t0=round(m['s'] / FPS, 3), t1=round((m['e'] + 1) / FPS, 3), dur=round((m['e'] - m['s'] + 1) / FPS, 3),
              kind='zoom_in' if m['z'] > 1 else 'zoom_out', amount_pct=round(abs(m['z'] - 1) * 100, 1), peak_per_frame_pct=round(m['peak'] * 100, 2))
         for m in moves if abs(m['z'] - 1) > 0.012]

# ---- 3. OCR text timeline (5 frames a second, plus every frame near cuts). OCR is the slow step: every 2nd frame
#      took 15+ minutes a reel with three reels in parallel. The sheets still show every frame, and an analyst reads
#      exact text from a full-resolution extract, so OCR only has to find WHEN text appears. OCR_STEP overrides.
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
STEP = int(os.environ.get('OCR_STEP') or max(1, round(FPS / 5)))
sample = sorted(set(list(range(0, N, STEP)) + [c + d for c in cuts[1:-1] for d in (-1, 0, 1) if 0 <= c + d < N]))
texts = {}
for k in sample:
    im = cv2.imread(files[k])
    BW, BH = FW * 2, FH * 2
    big = cv2.resize(im, (BW, BH))
    res, _ = ocr(big)
    items = []
    for box, txt, conf in (res or []):
        if float(conf) < 0.6 or not txt.strip(): continue
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        items.append(dict(text=txt.strip(), x=round(min(xs) * OW / BW), y=round(min(ys) * OH / BH),
                          w=round((max(xs) - min(xs)) * OW / BW), h=round((max(ys) - min(ys)) * OH / BH), conf=round(float(conf), 2)))
    texts[k] = items
# merge into on-screen text events (same text in roughly the same place)
events = []; open_ev = {}
for k in sample:
    seen = set()
    for it in texts[k]:
        key = (re.sub('[^a-z0-9]', '', it['text'].lower()), round(it['y'] / 120))
        seen.add(key)
        if key in open_ev: open_ev[key]['last_f'] = k; open_ev[key]['h_max'] = max(open_ev[key]['h_max'], it['h'])
        else: open_ev[key] = dict(text=it['text'], first_f=k, last_f=k, x=it['x'], y=it['y'], h_first=it['h'], h_max=it['h'])
    for key in list(open_ev):
        if key not in seen and k - open_ev[key]['last_f'] > STEP + 1:
            events.append(open_ev.pop(key))
events += list(open_ev.values())
for e in events:
    e['t_in'] = round(e['first_f'] / FPS, 3); e['t_out'] = round((e['last_f'] + 1) / FPS, 3)
    e['text_px_height'] = e.pop('h_max'); e.pop('h_first')
events.sort(key=lambda e: e['first_f'])

json.dump(dict(fps=FPS, frames=N, rows=rows), open(os.path.join(D, 'frame_metrics.json'), 'w'))
json.dump(dict(fps=FPS, frames=N, cuts=[round(c / FPS, 3) for c in cuts[1:-1]], cut_frames=cuts[1:-1], shots=shots, zoom_moves=moves,
               text_events=events), open(os.path.join(D, 'visual.json'), 'w'), indent=1)

# ---- 4. annotated sheets: EVERY frame, 40 per sheet (10 x 4), cut frames framed in red
from PIL import Image, ImageDraw, ImageFont
SD = os.path.join(D, 'sheets'); os.makedirs(SD, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 15)
W, H, cols, rws = (384, 216, 5, 8) if LAND else (216, 384, 10, 4); per = cols * rws
cutset = set(cuts[1:-1])
for p in range(0, N, per):
    sh = Image.new('RGB', (cols * W, rws * H), (0, 0, 0)); d = ImageDraw.Draw(sh)
    for j, k in enumerate(range(p, min(N, p + per))):
        im = Image.open(files[k]).resize((W, H)); x, y = (j % cols) * W, (j // cols) * H
        sh.paste(im, (x, y))
        d.rectangle([x, y, x + 92, y + 18], fill=(0, 0, 0)); d.text((x + 3, y + 1), f'{k} {k / FPS:.2f}', font=font, fill=(255, 230, 0))
        if k in cutset: d.rectangle([x, y, x + W - 1, y + H - 1], outline=(255, 40, 40), width=4)
    sh.save(os.path.join(SD, f'sheet_{p // per:03d}.jpg'), quality=82)
print(f'{D}: {N} frames @ {FPS:.3f} fps, {len(cuts) - 2} cuts, {len(moves)} zoom moves, {len(events)} text events')
