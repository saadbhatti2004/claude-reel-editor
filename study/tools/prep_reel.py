"""Prepare reference reels for study: download, split audio, separate voice from music and effects, transcribe,
measure every frame, detect sound events. Every step is skipped when its output already exists, so a crashed run
can simply be started again.

usage:
  python prep_reel.py <work_root> <creator>/<shortcode> [<creator>/<shortcode> ...] [--workers 3] [--light]

  <work_root>  heavy files live here, outside the repo
  --light      profile scan only: video, info, transcript, and a 2-frames-per-second contact sheet (no stems, no OCR)

per reel folder <work_root>/<creator>/<shortcode>/:
  video.mp4, video.info.json (caption, counts, date), audio.wav, a16.wav, stems/{vocals,no_vocals}.wav,
  words.json + transcript.txt, frames/ + sheets/ + frame_metrics.json + visual.json, audio_events.json + spectro/
"""
import json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def have(path):
    return os.path.exists(path) and (os.path.getsize(path) > 0 if os.path.isfile(path) else bool(os.listdir(path)))


def download(d, code):
    if have(os.path.join(d, 'video.mp4')):
        return
    url = f'https://www.instagram.com/p/{code}/'
    run(['yt-dlp', '-q', '--no-warnings', '--write-info-json', '-f', 'bv*+ba/b', '--merge-output-format', 'mp4',
         '-o', os.path.join(d, 'video.%(ext)s'), url])


def audio(d):
    v = os.path.join(d, 'video.mp4')
    if not have(os.path.join(d, 'audio.wav')):
        run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vn', '-ac', '2', '-ar', '44100', os.path.join(d, 'audio.wav')])
    if not have(os.path.join(d, 'a16.wav')):
        run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vn', '-ac', '1', '-ar', '16000', os.path.join(d, 'a16.wav')])


def stems(d):
    st = os.path.join(d, 'stems')
    if have(os.path.join(st, 'no_vocals.wav')):
        return
    sep = os.path.join(d, 'sepout')
    run(['demucs', '--two-stems=vocals', '-n', 'htdemucs', '-o', sep, os.path.join(d, 'audio.wav')],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.makedirs(st, exist_ok=True)
    src = os.path.join(sep, 'htdemucs', 'audio')
    for f in ('vocals.wav', 'no_vocals.wav'):
        shutil.move(os.path.join(src, f), os.path.join(st, f))
    shutil.rmtree(sep, ignore_errors=True)


def transcribe(d):
    if have(os.path.join(d, 'words.json')):
        return
    env = dict(os.environ, HF_HUB_OFFLINE='1')
    code = ('import json,os,sys\n'
            'from faster_whisper import WhisperModel\n'
            'd=sys.argv[1]\n'
            'm=WhisperModel("small.en",device="cpu",compute_type="float32")\n'
            'segs,_=m.transcribe(os.path.join(d,"a16.wav"),word_timestamps=True,vad_filter=False)\n'
            'W=[];L=[]\n'
            'for s in segs:\n'
            '    L.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")\n'
            '    W+=[{"w":w.word.strip(),"s":round(w.start,3),"e":round(w.end,3)} for w in s.words]\n'
            'json.dump({"words":W,"lines":L},open(os.path.join(d,"words.json"),"w"),indent=1)\n'
            'open(os.path.join(d,"transcript.txt"),"w",encoding="utf-8").write("\\n".join(L))\n')
    run([PY, '-c', code, d], env=env)


def light_sheet(d):
    """profile scan: one contact sheet of 2 frames a second, labelled with time"""
    out = os.path.join(d, 'contact.jpg')
    if have(out):
        return
    run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(d, 'video.mp4'), '-vf',
         "fps=2,scale=180:320,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='%{pts\\:hms}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x8",
         '-frames:v', '1', '-q:v', '3', out])
    # long reels need more than one 80-frame sheet
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                os.path.join(d, 'video.mp4')], capture_output=True, text=True).stdout.strip() or 0)
    k = 1
    while dur > 40 * k + 1:                     # a tail under a second gives the tile no frame (a longer reel failed)
        try:
            run(['ffmpeg', '-v', 'error', '-y', '-ss', str(40 * k), '-i', os.path.join(d, 'video.mp4'), '-vf',
                 f"fps=2,scale=180:320,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='%{{pts\\:hms}} +{40 * k}s':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x8",
                 '-frames:v', '1', '-q:v', '3', os.path.join(d, f'contact_{k}.jpg')])
        except subprocess.CalledProcessError as e:
            print(f'WARN {d}: contact sheet {k} failed ({e.returncode})', flush=True)
        k += 1


def prep(root, item, light):
    creator, code = item.split('/')
    d = os.path.join(root, creator, code)
    os.makedirs(d, exist_ok=True)
    try:
        download(d, code)
        audio(d)
        transcribe(d)
        if light:
            light_sheet(d)
        else:
            stems(d)
            if not have(os.path.join(d, 'visual.json')):
                run([PY, os.path.join(HERE, 'prep_visual.py'), d])
            if not have(os.path.join(d, 'audio_events.json')):
                run([PY, os.path.join(HERE, 'prep_audio.py'), d])
        print(f'OK   {item}', flush=True)
        return True
    except Exception as e:
        print(f'FAIL {item}: {e}', flush=True)
        return False


def main():
    args = sys.argv[1:]
    workers = 3
    if '--workers' in args:
        i = args.index('--workers'); workers = int(args[i + 1]); del args[i:i + 2]
    light = '--light' in args
    args = [a for a in args if a != '--light']
    root, items = args[0], args[1:]
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(lambda it: prep(root, it, light), items))
    print(f'done: {sum(res)} ok, {len(res) - sum(res)} failed')


if __name__ == '__main__':
    main()
