# Claude Reel Editor

Edit short-form talking-head reels from inside Claude Code. No CapCut, no Premiere.

You give Claude a raw recording. It cuts the pauses, builds every scene as code, designs the sound, and hands you a dashboard
where the reel is split into numbered beats. You leave a note on any beat, and Claude re-renders **only that beat**. Every other
frame stays exactly as it was.

## What is in here
| | |
|---|---|
| `ENGINE.md` | The rulebook Claude follows: pace, sound, motion, hooks, layouts, and the step by step workflow |
| `CRITIC-BRIEF.md` | The brief for the self-review loop, where critic agents judge each scene before you see it |
| `kit/` | The constant layer: captions, layouts, motion, counters, typewriter, the mascot |
| `tools/` | Transcribe, cut the take, capture real websites, render frame by frame, design sound, mix, Beat Review |
| `study/` | A long study of how top educational reels are built, plus the method to decode your own references |
| `examples/demo-reel/` | A tiny reel with no footage, so you can try Beat Review in a minute |

## Beat Review
A local dashboard for one reel. It runs on your own machine and nothing leaves it.

- **The reel, as Instagram shows it.** The header, the like column and the caption sit on top, so you see what they cover. Press
  `I` to turn that off.
- **Every beat, numbered.** A new beat at every scene cut, sentence end and real pause. Click one to play it.
- **A note on any beat.** Pause, press `N`, type, press Enter. The note keeps its frame, its time and its beat.
- **Rounds.** After a re-render the page updates by itself, and the changed beats are flagged so you only re-watch those.
- **Checks.** Length, frame size, frame rate, clipping, words covered, open notes.
- **Sound.** Every cue with its time, level and reason. Click one to hear it in place, or leave a note on it.

Keys: `Space` play, `Left` `Right` one frame, `Up` `Down` one beat, `N` note, `Shift N` note on the whole video, `L` loop the
beat, `I` Instagram view, `M` mute, `S` speed.

## Set up
You need [Claude Code](https://claude.com/claude-code), Node 18 or newer, Python 3.10 or newer, and
[ffmpeg](https://ffmpeg.org) on your PATH.

```bash
npm install
pip install -r requirements.txt
```

Try the dashboard on the demo. The first run renders a short draft:

```bash
python tools/beatreview.py examples/demo-reel
```

To edit a real reel, build the sound effects library once (free, from Mixkit, a few hundred MB):

```bash
python tools/sfxlib.py fetch sfx-library
python tools/sfxlib.py get sfx-library
python tools/sfxlib.py measure sfx-library
python tools/sfxlib.py derive sfx-library
```

For the face card layout, put the [Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting) ONNX model
(`rvm_mobilenetv3_fp32.onnx`) in `models/`.

## Use it
Open Claude Code in this folder and say:

> Edit this reel: path/to/my-recording.mp4

Claude follows `ENGINE.md`, builds the reel and opens Beat Review. Leave your notes, then tell Claude "apply my notes". When it
looks right, press Approve and Claude renders the final at full quality.

You can also just prompt Claude normally about any beat: "change b33, make the card land on the word 'free'".

## Make it yours
Everything in `ENGINE.md` is a default. Every time you correct an edit, ask Claude to write that correction into `ENGINE.md`, and
it holds for every reel after that. That loop is how these rules got here.

To copy the style of creators you like, follow `study/README.md`.

## Credits
Fonts: Inter, JetBrains Mono and Familjen Grotesk, under the SIL Open Font License. Sound effects are downloaded from
[Mixkit](https://mixkit.co/license/) under its own free licence. Use music and footage you have the rights to.
