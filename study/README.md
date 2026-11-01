# How a reference reel is studied

Pick the creators whose style you want to learn. Two depths, both run by `tools/prep_reel.py` (every step skips what already exists,
so a crash is resumed by running it again). Heavy files go to a work folder outside this repo.

## 1. Full decode (the reels you pick)
`python study/tools/prep_reel.py <work_root> <creator>/<shortcode> ... --workers 3`
- `video.mp4` + `video.info.json` (yt-dlp)
- `audio.wav`, `a16.wav`; `stems/vocals.wav` + `stems/no_vocals.wav` (demucs, voice apart from music and effects)
- `words.json` + `transcript.txt` (faster-whisper small.en, word times)
- `frames/` (every frame), `frame_metrics.json`, `visual.json` (cuts, zoom moves, on-screen text by OCR), `sheets/` (every frame, 40
  per sheet, labelled `frame time`, detected cuts outlined red)
- `audio_events.json` + `spectro/` (sound events on the music and effects stem, music level, 6 s spectrogram strips)

Then one analyst agent per reel, briefed with [`ANALYST-BRIEF.md`](ANALYST-BRIEF.md). `tools/reel_facts.py` prints the facts line each
analyst's prompt needs, and `tools/save_returned.py` saves each returned report.

## 2. Profile scan (every other video on the profile)
`python study/tools/prep_reel.py <work_root> <creator>/<shortcode> ... --light` gives each reel its video, transcript and contact sheets
(2 frames a second). Scan agents, briefed with [`PROFILE-SCAN-BRIEF.md`](PROFILE-SCAN-BRIEF.md), read them to find what every reel of a
creator shares and how each one differs. [`SYNTHESIS-BRIEF.md`](SYNTHESIS-BRIEF.md) turns the decodes into one document per creator.

## Traps
- The measurement data is a starting point only: OCR misreads, a "cut" can be fast motion, and sound labels are guesses. Analysts verify
  everything against the frames.
- Instagram reels are often 30 fps but some are cut at 25 and exported at 30 (a doubled frame every 6). Check before measuring speeds.
- On Windows, run Python with `PYTHONIOENCODING=utf-8` when captions hold emoji.
