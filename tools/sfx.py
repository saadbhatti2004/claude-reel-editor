"""Synthesize the educational kit's sound effects, matched to the reference reels' measured effects
(the events logged in the decodes, measured on their separated music-and-effects stems):

  pop_up      rising pitched pop, ~520 to 690 Hz over 60 ms, 5 ms attack
  pop_up_hi   the same an octave-ish higher, for small chips
  hit         short tonal hit on a cut, ~350 Hz, 45 ms
  thud        low thud with a click, ~110 to 85 Hz
  boom        sub boom for stamps and punches, 130 to 86 Hz, 160 ms
  boop        soft low "boop" for a red X, ~172 Hz
  buzz        buzzy two-pulse error tone, ~172 to 215 Hz
  ok          two-tone success chime, ~1.17 kHz then a fifth up
  ding        bright bell ding, partials 1.16 / 2.7 / 4.3 kHz
  blip        tiny tonal blip, ~1.4 kHz, 15 to 40 ms
  tick        bright click, ~1.6 kHz with a transient
  swish       noise swell around 3 to 5 kHz, ~110 ms, for strikes
  impact      the CTA impact: low 129 to 86 Hz plus a bright transient
  riser       white-noise riser, brightening, stops dead
  zap         short electric crackle for cables wiring up
usage: python sfx.py <out dir>
"""
import os, sys, wave
import numpy as np

SR = 48000
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def sweep(f0, f1, dur, curve=3.0):
    t = t_(dur)
    k = (1 - np.exp(-curve * t / dur)) / (1 - np.exp(-curve))
    f = f0 + (f1 - f0) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR), t


def env(t, a, tau, hold=0.0):
    e = np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a - hold).clip(0) / tau))
    return e


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def hp(x, fc):
    return x - lp(x, fc)


def bp_noise(dur, f_lo, f_hi):
    n = rng.standard_normal(int(dur * SR))
    return hp(lp(n, f_hi), f_lo)


def click(dur=0.004, fc=4000):
    n = rng.standard_normal(int(dur * SR)) * np.linspace(1, 0, int(dur * SR))
    return hp(n, fc)


def fit(*parts):
    n = max(len(p) for p in parts)
    return sum(np.pad(p, (0, n - len(p))) for p in parts)


def save(name, x, room=True):
    if room:  # a very small room so it is not bone dry
        ir = rng.standard_normal(int(0.09 * SR)) * np.exp(-t_(0.09) / 0.025) * 0.06
        x = np.convolve(x, np.r_[1.0, np.zeros(int(0.004 * SR)), ir])[: len(x) + int(0.09 * SR)]
    fade = int(0.004 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    with wave.open(os.path.join(out, name + '.wav'), 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


# rising pitched pop
s, t = sweep(500, 700, 0.14, 4); s2, _ = sweep(1000, 1400, 0.14, 4)
save('pop_up', (s + 0.18 * s2) * env(t, 0.003, 0.018))
s, t = sweep(820, 1150, 0.12, 4); s2, _ = sweep(1640, 2300, 0.12, 4)
save('pop_up_hi', (s + 0.15 * s2) * env(t, 0.002, 0.015))
# tonal hit on a cut
s, t = sweep(390, 340, 0.22, 2); tri = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * np.cumsum(np.full(len(t), 345)) / SR))
save('hit', fit((0.7 * s + 0.4 * tri) * env(t, 0.004, 0.024), 0.12 * click(0.002, 3000)))
# low thud
s, t = sweep(115, 82, 0.18, 3)
save('thud', fit(s * env(t, 0.002, 0.03), 0.22 * click(0.003, 1200)))
# sub boom
s, t = sweep(132, 84, 0.5, 5)
b = np.tanh(1.6 * s * env(t, 0.002, 0.1))
save('boom', fit(b, 0.6 * lp(rng.standard_normal(int(0.03 * SR)) * np.exp(-t_(0.03) / 0.006), 1400)))
# soft low boop (red X)
s, t = sweep(185, 160, 0.3, 2); s3, _ = sweep(370, 320, 0.3, 2)
save('boop', (s + 0.12 * s3) * env(t, 0.018, 0.05))
# buzzy error, two pulses
def buzz_pulse(f, dur):
    tt = t_(dur); sq = np.sign(np.sin(2 * np.pi * f * tt)) * 0.6 + np.sin(2 * np.pi * f * tt)
    return lp(sq, 1600) * env(tt, 0.008, 0.05, 0.03)
save('buzz', np.r_[buzz_pulse(205, 0.11), np.zeros(int(0.035 * SR)), 0.75 * buzz_pulse(172, 0.14)])
# success chime: two bell tones a fifth apart
def bell(f, dur, tau):
    tt = t_(dur)
    return (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / (tau / 3)) + 0.15 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / (tau / 6))) * env(tt, 0.003, tau)
save('ok', fit(bell(1175, 0.5, 0.1), 0.55 * np.r_[np.zeros(int(0.085 * SR)), bell(1760, 0.5, 0.12)]))
save('ding', bell(1165, 0.5, 0.11))
# tiny blip and tick
tt = t_(0.06); save('blip', np.sin(2 * np.pi * 1420 * tt) * env(tt, 0.002, 0.012), room=False)
tt = t_(0.05); save('tick', fit(np.sin(2 * np.pi * 1640 * tt) * env(tt, 0.001, 0.008), 0.6 * click(0.002, 5000)), room=False)
# strike swish
n = bp_noise(0.2, 2600, 6000); tt = t_(0.2)
save('swish', n * np.where(tt < 0.09, (tt / 0.09) ** 2, np.exp(-(tt - 0.09) / 0.03)), room=False)
# CTA impact
s, t = sweep(130, 84, 0.6, 4)
save('impact', fit(np.tanh(1.8 * s * env(t, 0.002, 0.075)), 0.7 * hp(rng.standard_normal(int(0.03 * SR)) * np.exp(-t_(0.03) / 0.006), 1200)))
# white-noise riser that brightens, stops dead (made long; the mixer trims its start)
dur = 2.4; tt = t_(dur); n = rng.standard_normal(len(tt))
lo = lp(n, 900); hi = n - lp(n, 3000); k = (tt / dur) ** 2
save('riser', (lo * (1 - k) * 0.6 + hi * k) * (0.05 + 0.95 * (tt / dur) ** 2.2), room=False)
# electric zap for cables
tt = t_(0.18); n = rng.standard_normal(len(tt)); gate = (np.sin(2 * np.pi * 55 * tt) > 0.2).astype(float)
save('zap', hp(n, 1800) * gate * env(tt, 0.002, 0.05) + 0.4 * np.sign(np.sin(2 * np.pi * 110 * tt)) * env(tt, 0.002, 0.04))
print('sfx written to', out, sorted(os.listdir(out)))
