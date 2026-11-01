# Transcribe a take with word timings for take.py: faster-whisper small.en, float32.
# python tools/transcribe.py <take.mp4> <out stem>  ->  <stem>.json (w, s, e, p per word) and <stem>.txt
import json, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', '16000', out + '.a16.wav'], check=True)
m = WhisperModel('small.en', device='cpu', compute_type='float32')
segs, _ = m.transcribe(out + '.a16.wav', word_timestamps=True, beam_size=5, vad_filter=False, condition_on_previous_text=False)
words = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 3)} for s in segs for w in s.words]
json.dump(words, open(out + '.json', 'w', encoding='utf-8'), indent=0)
open(out + '.txt', 'w', encoding='utf-8').write(' '.join(w['w'] for w in words))
os.remove(out + '.a16.wav')
print(len(words), 'words'); print(' '.join(w['w'] for w in words))
