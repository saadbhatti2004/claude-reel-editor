"""Mix an educational reel's sound: the voice, the effects on their words (plan.json, written by render.mjs --plan),
and optionally a music bed placed so its drop lands on the story's turn.

usage: python mix.py <voice.wav> <plan.json> <out.wav> [--no-sfx] [--sound edit/sound.json]
                     [--bed <file> --bed-start <s in the track> --bed-at <s in the reel> --drop <reel s>]
                     [--under 18] [--under-after 11] [--duck 3] [--lufs -14] [--pre-hp 250]
                     [--ride ride.json]

Levels follow the study (GRAMMAR section 12): the voice stays dry on top; the bed sits about 18 dB under it before
the drop and rises to about 11 dB under it after; effects only mark state changes.
The bed keeps its stereo width, gets a small dip where speech is understood (1 to 4 kHz), and ducks a few dB while the speaker
talks. With --pre-hp the bed plays without its low end until the drop, so the kick and bass arrive on the turn (the
references' low band rises 14 to 35 dB there) even when the track itself has no quiet intro. The whole mix is then set to the references' loudness (about -14 LUFS, true peak under -1 dBTP).
With --ride the bed rides by section instead: a list of [t, dB under the voice, ramp s],
measured above 150 Hz against the speaking level, so it sits low on the face, higher on the graphics, drops before
the payoff and ends at its lowest on the call to action; the track keeps its own dynamics inside each section.
With --sound (written by tools/sound.py) the effects are the designed set: real recorded sounds in stereo, each panned
where its motion happens (a fly-in moves across), varied slightly in speed, high-passed by role so only impacts keep
their low end, levelled against the speaking level, and dipped up to 4 dB while the speaker talks so they never cover a word.
"""
import argparse, json, subprocess
import numpy as np

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument('voice'); ap.add_argument('plan'); ap.add_argument('out')
ap.add_argument('--no-sfx', action='store_true')
ap.add_argument('--sound', help="edit/sound.json from tools/sound.py: the designed effects (replaces the plan's old file cues)")
ap.add_argument('--sfx-trim', type=float, default=-4.0, help='global effects trim; -4 dB puts pops about 12 dB under the voice peak, as in the references')
ap.add_argument('--bed'); ap.add_argument('--bed-start', type=float, default=0.0); ap.add_argument('--bed-at', type=float, default=0.0)
ap.add_argument('--drop', type=float); ap.add_argument('--under', type=float, default=18.0); ap.add_argument('--under-after', type=float, default=11.0)
ap.add_argument('--duck', type=float, default=3.0, help='dB the bed dips while the speaker talks')
ap.add_argument('--pre-hp', type=float, default=0.0, help='high-pass (Hz) on the bed before the drop; 0 keeps it whole')
ap.add_argument('--lufs', type=float, default=-14.0, help='final integrated loudness; 0 leaves it as mixed')
ap.add_argument('--ride', help='JSON file: [[t, dB under the voice, ramp s], ...]; replaces --under, --under-after and --drop')
ap.add_argument('--stems', help='folder: also write the voice, effects and bed stems (before the final loudness gain) as .npy, for measuring')
a = ap.parse_args()


def load(path, ss=0.0, dur=None, ch=1, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-i', path]
    if dur:
        cmd += ['-t', f'{dur:.3f}']
    if af:
        cmd += ['-af', af]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).copy()
    return x if ch == 1 else x[: len(x) // ch * ch].reshape(-1, ch)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-12)


voice = load(a.voice)
n = len(voice)
mix = voice.copy()
# speech level: RMS of the loud half of the voice, so pauses do not pull it down
fr = voice[: n // 480 * 480].reshape(-1, 480)
fr_db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
v_db = float(np.percentile(fr_db, 75))
v_peak = float(20 * np.log10(np.percentile(np.abs(voice), 99.9) + 1e-9))

plan = json.load(open(a.plan, encoding='utf-8'))
fx_bus = None
if a.sound and not a.no_sfx:
    fx_bus = np.zeros((n, 2), dtype=np.float32)
    for s in json.load(open(a.sound, encoding='utf-8'))['sounds']:
        af = [f"asetrate={int(SR * s['rate'])},aresample={SR}"] if abs(s['rate'] - 1) > 1e-3 else []
        if s.get('hp'):
            af.append(f"highpass=f={s['hp']}:p=2")
        x = load(s['f'], s['ss'], s['dur'] / max(s['rate'], 0.5) + 0.02, ch=2, af=','.join(af) or None)
        if len(x) < 32:
            continue
        w = int(0.05 * SR)                                         # level: its loudest 50 ms against the speech
        e = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(w) / w, mode='same')).max() + 1e-9
        x = x / e * 10 ** ((v_db + s['g']) / 20)
        fade = min(len(x) // 3, int(0.015 * SR)); x[-fade:] *= np.linspace(1, 0, fade)[:, None]
        fin = min(len(x) // 4, int(0.005 * SR)); x[:fin] *= np.linspace(0, 1, fin)[:, None]   # no click at the start
        m = x.mean(1); sd = (x[:, 0] - x[:, 1]) / 2                # equal-power pan of the centre, moving if pan0 != pan1
        p = np.linspace(s['pan0'], s['pan1'], len(x)).clip(-1, 1)
        th = (p + 1) * np.pi / 4
        x = np.stack([m * np.cos(th) * np.sqrt(2) + sd, m * np.sin(th) * np.sqrt(2) - sd], 1)
        i0 = int(round(s['t'] * SR)); j0 = max(0, -i0); i0 = max(0, i0)
        x = x[j0: j0 + max(0, n - i0)]
        fx_bus[i0:i0 + len(x)] += x
    # dip the effects while the speaker talks: up to 4 dB, 5 ms down, 120 ms back
    lv = np.repeat(np.clip((fr_db - (v_db - 14)) / 14, 0, 1), 480)[:n].astype(np.float32)
    lv = np.pad(lv, (0, n - len(lv)))
    sm = np.empty_like(lv); up, dn = 1 - np.exp(-48 / (0.005 * SR)), 1 - np.exp(-48 / (0.12 * SR)); y = 0.0
    for j in range(0, n, 48):
        tgt = lv[j]; y += (up if tgt > y else dn) * (tgt - y); sm[j:j + 48] = y
    fx_bus *= (10 ** (-4 * sm / 20))[:, None]
elif not a.no_sfx:
    for s in plan['sfx']:
        x = load(s['f'], s.get('ss', 0.0), s.get('dur'))
        if len(x) == 0:
            continue
        x = x / (np.abs(x).max() + 1e-9) * 10 ** ((v_peak + s['g'] + a.sfx_trim) / 20)   # g = dB relative to the voice's peak
        if s.get('dur'):
            fade = min(len(x), int(0.02 * SR)); x[-fade:] *= np.linspace(1, 0, fade)
        i0 = int(s['t'] * SR)
        if i0 >= n:
            continue
        x = x[: n - i0]
        mix[i0:i0 + len(x)] += x

mix = np.repeat(mix[:, None], 2, axis=1)
if fx_bus is not None:
    mix += fx_bus
if a.bed:
    eq = 'highpass=f=40,equalizer=f=2200:t=q:w=0.9:g=-3'
    bed = load(a.bed, a.bed_start, n / SR + 1, ch=2, af=eq)
    i0 = int(a.bed_at * SR)
    b = np.zeros((n, 2), dtype=np.float32)
    b[i0:i0 + len(bed[: n - i0])] = bed[: n - i0]
    drop = int((a.drop if a.drop is not None else n / SR / 2) * SR)
    if a.pre_hp > 0 and i0 < drop < n:                            # thin before the turn, whole from the kick on
        thin = load(a.bed, a.bed_start, n / SR + 1, ch=2, af=f'highpass=f={a.pre_hp}:p=2,highpass=f={a.pre_hp}:p=2,{eq}')
        t = np.zeros_like(b); t[i0:i0 + len(thin[: n - i0])] = thin[: n - i0]
        xf = int(0.012 * SR); c0 = max(i0, drop - xf)             # the switch ends just before the kick's attack
        w = np.ones(n, dtype=np.float32); w[c0:drop] = np.linspace(1, 0, drop - c0); w[drop:] = 0
        b = t * w[:, None] + b * (1 - w)[:, None]
    pre = b[i0:drop] if drop > i0 + SR else b[i0:]
    if i0 > 0:                                                    # a bed that starts late fades in, never clicks in
        fi = min(int(0.4 * SR), n - i0); b[i0:i0 + fi] *= np.linspace(0, 1, fi)[:, None]
    if a.ride:
        # one reference for the whole bed, measured above 150 Hz as a phone plays it; the ride sets dB under the voice
        keys = json.load(open(a.ride, encoding='utf-8'))
        ref = rms_db(load(a.bed, a.bed_start, n / SR + 1, ch=1, af='highpass=f=150:p=2')[: n - i0])
        under = np.full(n, float(keys[0][1]), dtype=np.float32)
        for k in keys[1:]:
            j = min(n, int(k[0] * SR)); r = max(1, int((k[2] if len(k) > 2 else 0.15) * SR))
            u0 = float(under[j - 1]) if j > 0 else float(k[1])
            m = min(r, n - j)
            under[j:j + m] = np.linspace(u0, k[1], r)[:m]; under[j + m:] = k[1]
        gain = (10 ** ((v_db - under - ref) / 20)).astype(np.float32)
        hpb = load(a.bed, a.bed_start, n / SR + 1, ch=1, af='highpass=f=150:p=2')
        hb = np.zeros(n, dtype=np.float32); hb[i0:i0 + len(hpb[: n - i0])] = hpb[: n - i0]
        for k, nk in zip(keys, keys[1:] + [[n / SR]]):
            s0, s1 = int(k[0] * SR), int(nk[0] * SR)
            if s1 - s0 > SR // 4:
                print(f'  bed {k[0]:6.2f} to {nk[0]:6.2f} s  set {k[1]:5.1f} dB under  measured {v_db - rms_db(hb[s0:s1] * gain[s0:s1]):5.1f}')
    else:
        g1 = 10 ** ((v_db - a.under - rms_db(pre)) / 20)
        # after the drop the bed is set to its own level, so every track rises the same on the turn (the references
        # rise 8 to 10 dB there), whether or not the track itself gets louder
        g2 = 10 ** ((v_db - a.under_after - rms_db(b[drop:])) / 20) if drop < n - SR else g1
        gain = np.full(n, g1, dtype=np.float32)
        ramp = int(0.03 * SR)
        gain[drop:] = g2
        gain[drop:drop + ramp] = np.linspace(g1, g2, min(ramp, n - drop))
    fo = int(0.15 * SR); gain[-fo:] *= np.linspace(1, 0, fo)
    if a.duck > 0:                                                # dip while the speaker talks: 30 ms down, 250 ms back up
        env = np.repeat(fr_db > v_db - 12, 480)[:n].astype(np.float32)
        env = np.pad(env, (0, n - len(env)))
        sm = np.empty_like(env); up, dn = 1 - np.exp(-1 / (0.03 * SR)), 1 - np.exp(-1 / (0.25 * SR)); y = 0.0
        for j in range(0, n, 48):                                 # 1 ms control rate is plenty for a bed duck
            tgt = env[j]; y += (up if tgt > y else dn) * 48 * (tgt - y); y = min(1.0, max(0.0, y)); sm[j:j + 48] = y
        gain *= 10 ** (-a.duck * sm / 20)
    mix += b * gain[:, None]
if a.stems:
    import os
    os.makedirs(a.stems, exist_ok=True)
    np.save(os.path.join(a.stems, 'voice.npy'), voice)
    np.save(os.path.join(a.stems, 'fx.npy'), fx_bus if fx_bus is not None else np.zeros((n, 2), np.float32))
    np.save(os.path.join(a.stems, 'bed.npy'), (b * gain[:, None]) if a.bed else np.zeros((n, 2), np.float32))

peak = np.abs(mix).max()
if peak > 0.97:
    mix *= 0.97 / peak
raw = mix.astype(np.float32).tobytes()
af = []
if a.lufs:                                                        # two passes, linear: one gain, no pumping
    r = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af',
                        f'loudnorm=I={a.lufs}:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'],
                       input=raw, capture_output=True)
    err = r.stderr.decode('utf-8', 'ignore')
    m = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
    af = ['-af', f"loudnorm=I={a.lufs}:TP=-1.0:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
                 f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample={SR}"]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', *af, '-c:a', 'pcm_s16le', a.out],
               input=raw, check=True)
print(a.out, f'{n / SR:.2f} s, voice {v_db:.1f} dB', 'bed on' if a.bed else '', f'set to {a.lufs} LUFS' if a.lufs else '')
