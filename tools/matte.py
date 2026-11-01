"""A matte for every face frame, so the card layout can let the head rise out of the face card.

usage: python tools/matte.py <take dir> [--scale 0.5] [--ds 0.25]
  reads  <take dir>/frames/NNNNN.jpg (take.py's face frames, 1080 x 1920)
  writes <take dir>/matte/NNNNN.png  alpha only (RGB black), at --scale of the frame size; the kit stretches it back

RVM (Robust Video Matting, mobilenetv3, ONNX on the CPU) carries its recurrent state from frame to frame, so the edge
holds steady over time. The model lives in models/ at the repo root. A frame that already has its matte is skipped, so a stopped run resumes; the recurrent state
then restarts, which is fine after a few frames.
"""
import argparse, os, sys
import numpy as np, cv2, onnxruntime as ort

ap = argparse.ArgumentParser()
ap.add_argument('take')
ap.add_argument('--scale', type=float, default=0.5)
ap.add_argument('--ds', type=float, default=0.25, help='RVM downsample ratio (0.25 suits a 1080 x 1920 portrait)')
ap.add_argument('--model', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models', 'rvm_mobilenetv3_fp32.onnx'))
a = ap.parse_args()

src_dir = os.path.join(a.take, 'frames'); out_dir = os.path.join(a.take, 'matte')
os.makedirs(out_dir, exist_ok=True)
names = sorted(f for f in os.listdir(src_dir) if f.endswith('.jpg'))
rvm = ort.InferenceSession(a.model, providers=['CPUExecutionProvider'])
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
ds = np.array([a.ds], np.float32)
done = 0
for i, n in enumerate(names):
    out = os.path.join(out_dir, n[:-4] + '.png')
    if os.path.exists(out):
        rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
        continue
    im = cv2.imread(os.path.join(src_dir, n))[:, :, ::-1]
    src = (im.astype(np.float32) / 255).transpose(2, 0, 1)[None]
    _, pha, *rec = rvm.run([], {'src': src, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': ds})
    al = pha[0, 0]
    h, w = al.shape
    al = cv2.resize(al, (int(w * a.scale), int(h * a.scale)), interpolation=cv2.INTER_AREA)
    a8 = (np.clip(al, 0, 1) * 255).astype(np.uint8)
    rgba = np.zeros((a8.shape[0], a8.shape[1], 4), np.uint8); rgba[..., 3] = a8
    cv2.imwrite(out, rgba, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    done += 1
    if done % 100 == 0: print(f'{i + 1}/{len(names)}', flush=True)
print(f'matte: {done} new, {len(names)} frames in {out_dir}')
