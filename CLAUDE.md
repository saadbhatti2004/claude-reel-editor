# Claude Reel Editor

This repo edits short-form talking-head reels. When the user asks to edit a video, or gives you a recording:

1. Read `ENGINE.md` in full before doing anything. It is the rulebook and the step by step workflow.
2. Skim `study/GRAMMAR.md`, sections 3 to 12, for the style.
3. Make a reel folder outside this repo (for example `../reels/<name>/`) and follow "How a reel is made" in `ENGINE.md`.
4. Run the self-review loop in `CRITIC-BRIEF.md`, then open Beat Review: `python tools/beatreview.py <reel dir>`.
   Add `--handle <name>` to show the user's Instagram name in the preview.
5. Work one reel at a time. Do not render the full-quality final until the reel is approved in Beat Review.

## Applying notes from Beat Review
When the user says "apply my notes" or similar:
1. Run `python tools/beatreview.py <reel dir> --notes`.
2. Change only what the notes ask for. Each note names its beat, its time and the words said there.
3. Run `python tools/beatreview.py <reel dir> --rerender <the beats you changed> --say "one plain line on what changed"`.
   If you changed the sound, run `tools/mix.py` first and add `--mix final/mix.wav`.
4. Never re-render the whole reel to fix one beat. A note on the whole video is closed with `--close <note id>` once done.

The dashboard picks up each new round by itself. When the user corrects an edit, ask whether to write that correction into
`ENGINE.md` so it holds for every later reel.

## First-time setup
When the user asks you to set this repo up, follow "Set up from scratch" in `README.md` from step 3 for them: run each command,
fix what fails, and finish by opening the demo in Beat Review. Create `.venv` and use it for every Python command. If a tool from
step 1 is missing, install it with their package manager after telling them what you are installing.
