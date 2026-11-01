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

## Set up from scratch
You need about 3 GB of free disk space. Tested on Windows 11 with Node 22 and Python 3.13.

**1. Install the tools.** Skip any you already have, then close the terminal and open a new one so they are on your PATH.

Windows (PowerShell):

```powershell
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.13
winget install Gyan.FFmpeg
```

Mac:

```bash
brew install git node python@3.13 ffmpeg
```

**2. Install Claude Code and log in.**

```bash
npm install -g @anthropic-ai/claude-code
claude
```

**3. Get this repo.** Copy the URL from the green Code button at the top of this page.

```bash
git clone <the URL you copied>
cd claude-reel-editor
npm install
python -m venv .venv
```

Turn the Python environment on. Do this every time you open a new terminal:

```bash
# Windows PowerShell
Set-ExecutionPolicy -Scope Process Bypass
.venv\Scripts\Activate.ps1

# Mac
source .venv/bin/activate
```

Then install the Python parts:

```bash
pip install -r requirements.txt
```

**4. Check it works.** The first run renders a short draft and opens the dashboard in your browser:

```bash
python tools/beatreview.py examples/demo-reel
```

**5. Build the sound effects library, once.** Free, from Mixkit, a few hundred MB:

```bash
python tools/sfxlib.py fetch sfx-library
python tools/sfxlib.py get sfx-library
python tools/sfxlib.py measure sfx-library
python tools/sfxlib.py derive sfx-library
```

**6. Get the face cutout model, once.** It powers the face card layout:

```bash
mkdir models
curl -L -o models/rvm_mobilenetv3_fp32.onnx https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx
```

The first transcription also downloads the speech model by itself.

Only if you want to decode other creators' reels (`study/README.md`): `pip install -r requirements-study.txt`. It pulls in PyTorch,
which is a large download, so skip it until you need it.

Or skip the typing: after step 2, clone the repo, open Claude Code inside it and say "set this up for me".

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
