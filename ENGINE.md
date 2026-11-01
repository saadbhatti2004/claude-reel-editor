# The Engine: how a reel gets edited

This file is the rulebook. Claude reads it before touching a reel. Every rule below came from real review rounds on
real reels, so treat them as defaults that have already been argued over. Your own taste wins: when you disagree with
a rule, change it here and it holds for every reel after that.

"The speaker" means the person on camera. "The take" means their raw recording.

The study behind the style is in [`study/GRAMMAR.md`](study/GRAMMAR.md).

## Founding principles
- **Blank slate.** The craft comes only from the reference creators you choose to study (`study/`).
- **No templates.** Every reel is different from the last in its whole structure. Small similarities are fine.
- **Real material, as much as possible.** Real details, real pages, real products, not decorative animation.
  Capture it from the screen, download it, get the data, get the references.
- **Understand the why.** A reference reel is decoded frame by frame: how it is built, why each element exists, how
  it relates to the viewer.

## Decisions
1. **One kit of parts, every reel composed from zero.** No structure, world, palette, metaphor, hook sentence or keyword
   is reused from recent reels.
2. **The constants stay** (GRAMMAR section 3): speech and motion from frame 0; graphic over face with a hard seam, full
   graphic, full face; hard cuts on sentence starts; one caption style; colour meaning; one heavy sans plus one mono; a
   bed whose drop lands on the turn; the keyword last, in quotes; no branding.
3. **Colours come from each reel's topic.** No branding inside the video, ever.
4. **The Claude character is Anthropic's own Claude Code mascot (Clawd)**, drawn by the kit.
5. **Facts are free.** Numbers, stories and examples may be made up; there is no fact-check step in this style. Real
   material (real logos, pages, talks, products) is still used as much as possible, because it looks real.
6. **Review first, step by step.** Every reel goes through Beat Review (rule 22) before the full-quality render.
7. **Pace.** The take is sped up on top of cutting the pauses. `tools/take.py` measures the words a minute once the
   pauses are cut and speeds the take toward a target, never past a cap and never slower than the speaker talked. A
   take already that fast stays at 1x.
   - The target is about **245 words a minute** with a cap of **1.22x**. Below about 240 tends to read slow and about
     250 is the top of the good range.
   - On a fast take, watch the multiplier, not only the target: around 1.2x and over reads too fast. There, fix it with
     `--speed 1.18`.
   - **No word cut off, every take.** Whisper's word times go wrong next to the speaker's own recording cuts (a word of
     zero length, a number stretched over a second), and the pause cut then takes real speech out. After `take.py`,
     check every removed stretch of the original for speech (loud frames inside a cut); re-time the words there with
     large-v3 on that stretch and cut again.
   - **No quiet start, every take.** Whisper often puts the first word at 0.00 when the speaker starts a quarter second
     in. Before `take.py`, measure the take's first half second (20 ms RMS); if it is silent, set the first word's start
     to its real onset and `--drop` the silence (keep about 0.02 s before the onset).
8. **The bed.** One track you have the rights to, picked per reel by measurement with `tools/beds.py`. It tries every
   beat entry of every track as the reel's turn and ranks them: a kick that comes back on the turn after a break, a
   steady rhythm after it with no hole, little energy where the voice is understood (1 to 4 kHz), and a usable tempo
   (the references run at 107 to 120 BPM). Check the top ones by ear. Mix it with `tools/mix.py`:
   - the bed stays in stereo, with a small dip at 1 to 4 kHz;
   - it ducks 3 dB while the speaker talks;
   - with `--pre-hp` it plays without its low end until the turn, so the bass and kick arrive on the turn;
   - the whole reel is set to -14 LUFS with a true peak of -1 dBTP (the references measure -14.6 LUFS).
9. **The self-review loop runs before you see anything.** Each loop renders, measures (`tools/selfcheck.py` against the
   references), critiques (critic agents briefed with `CRITIC-BRIEF.md`), builds the best changes, and repeats. Only
   when no scene falls short of the reference bar does the reel go to Beat Review.

## Rules from review
1. **Sound design follows the video itself: every motion gets the real sound of what it is.**
   - **Real recorded effects** from the Mixkit library (`tools/sfxlib.py`, free licence, no credit needed), in roles
     (`kit/sfx/POOLS.json`): air whooshes, UI zooms, real mouse clicks, keystrokes cut from real typing, bubble pops,
     glitches, marker strokes, paper crumples, short thumps, impacts, a sub drop, risers. No melodies or jingles,
     because a tune in an effect fights the bed and the voice: those titles are filtered out and every file passes a melody check.
   - **Driven by the motion:** the kit tags every motion it makes (fly-in, pop, stamp, shake, camera zoom, typing,
     counter, drawn mark); `render.mjs --plan` sweeps every frame and writes `edit/events.json`; `tools/sound.py` gives
     each visible motion its sound on its own frame. A fly-in's whoosh peaks as it lands and pans from where it came
     from; a pop is sized to its element; typing gets real keys; a counter ticks and slows with its number.
   - **Narrative moments are cued by role** in the composition (`window.SFX`, `{t, role}`): the ban, the error, the
     delete, the success, the record stop, a riser that stops dead into the turn and into the CTA, the drop.
   - **Never noise:** at most two sounds start inside 90 ms, never two of one family inside 60 ms (120 ms for low hits),
     at most four a half second outside typing; each file varies slightly in speed and level and never repeats back to
     back.
   - Hard cuts are silent; a whoosh on every cut is decoration.
   - Every file lands by its loudest point with a short pre-roll and a length cap per role, so a sound never peaks a
     second after its moment.
   - A small stamp gets a light tap, not a thump.
   - What Claude or a program prints gets soft ticks; only a person typing gets keystrokes.
   - One error buzzer is plenty (a sub, a glitch or a thump carries the other bad moments).
   - A scene can mute kinds of automatic sound or re-voice its runs (`snd` in the scene: a handful of files going into a
     bin is three crumples, not 26 pops).
   - The narrative peak is the loudest hit of its scene, and the drop the loudest of the reel; the next biggest reveal
     comes second. When the kit's automatic sound for plumbing (a card flying in, a camera move) would outshout the
     peak, the scene mutes that kind and cues it quieter. A run of tiny ticks under the voice is inaudible: give the
     moment one clear sound instead.
   - Most viewers hear the reel on a phone speaker, which loses everything under about 150 Hz. A peak carried only by a
     sub, a thump or an impact vanishes there while small clicks survive, so every narrative peak gets a bright layer
     too (a pop, a tick, paper), and the drop's bright layer is the loudest bright sound of the reel.
   - One sound per meaning across a reel: notif is a message, ring is a call, paper is a note, coin is money, error is
     a failure.
   - **Mixed under the voice:** stereo, high-passed by role so only impacts keep their low end, and dipped up to 4 dB
     while the speaker talks. The loudest effects sit about 10 dB under the speech.
2. **Motion at the references' pace.** Entries take 2 to 6 frames, pops 3 to 5, and zooms snap onto the word in 4 to 8
   frames. Something new happens every 0.3 to 0.5 s. Never one slow zoom held for a second.
3. **Real material gets layered graphics on top.** The footage or page keeps moving. Add the speaker's own words as a
   quote card with their face, hand-drawn circles, marker sweeps, name chips, a calendar or counter for any time or
   number, and camera snaps to each named thing.
4. **No generic movement.** Cards fly in with a tilt and overshoot, spotlight one item at a time, carry counters that
   climb, and get shakes on impacts. Each scene stages its own choreography for its own words.
5. **Face-only beats still move.** Punch-ins snap on the stressed words, and a headroom card above the head acts out
   the line.
6. **Nothing meaningful above y 150.** Instagram's Reels header covers the top of the frame. The references keep their
   top labels at y 148 or lower. The same goes for the caption band and the comment column on the right: payoffs live in
   the middle.
   - This holds during camera moves too: a zoom or a push must not carry a header into the top 150 px or a row into the
     caption band on any frame. Zoom about a point that keeps both edges in.
   - A label or overlay gets its own clear space; it never sits on the content it explains.
7. **One object carries the story.** The invented example is the same card everywhere it appears: planted, checked,
   wrong, fixed. Never a new look-alike, and never a contradiction, such as a check passing in one scene and failing two
   scenes later.
   - A payoff happens once: one price falling to zero, not two totals in a row. No scene gives away what the next scene
     spells out.
8. **Props are designed for the moment, never emoji.** Build each prop from the reel's own world: real UI (an analytics
   card, a session list, a comment box, a price tag), real logos and marks, and vector icons and shapes drawn in the
   reel's palette. This covers reactions, rewards and objects alike: a falling or rising sparkline instead of a thumb or
   a trophy, a drawn chain icon instead of a link emoji.
9. **Show what a tool achieves on real work, not on a mockup.** When a line says what a tool makes possible, record real,
   well-designed sites or products made with it (its showcase, award sites) in motion, labelled with their address. The
   invented example stays for the story (the problem and the payoff), not as the proof of quality.
10. **The first 3 to 4 seconds must stop the scroll.** The hook is designed first and judged on its own: would a stranger
    scrolling past stop on frame 0 and still be watching at 4 seconds?
    - It gets the reel's strongest visual, not a quiet setup: a full, moving scene on frame 0, a picture that makes the
      viewer ask a question, and a change every few frames until the 4-second mark.
    - **The hook shows the viewer's own pain, the way it really happens to them.** Stage the real moment in the real tool
      they use (their chat, their editor, their inbox), with the details they will recognise: the chat titled "final
      FINAL (v7)", the cheerful "Great idea!" that makes it worse, the hours on the clock, the message limit. A made up
      mockup or an abstract score never carries a hook.
11. **No stamps, ever.** A stamp is any label slammed in like a rubber stamp: bordered or tilted text dropping from big
    to small. The kit's `stampV` motion is not used on labels or badges. A verdict or a state change is shown the way
    modern software shows it, in the reel's own world: a status that changes in place, a check that draws itself, a meter
    or ring that fills, a toggle that switches, a glow, a colour that turns. Upright, smooth, on the element it describes.
12. **Never the speaker's own face in a small icon.** Avatars, call screens and profile icons use someone else (initials,
    a designed figure) or a designed icon, never a crop of the take.
13. **A recurring sound must be pleasant, modern, and used only at its key moments.** A sound that stands for an idea
    plays where that idea matters most, three or four times a reel at most, not every time the idea comes up.
14. **The camera never moves left or right.** It zooms and rises or falls only; the kit holds its focus on the centre
    line (`E.allowPan` is off). It holds still most of the time and moves only when the story needs it, a few times a
    scene at most. A scan or sweep passes once, smoothly, never in repeated jumps.
15. **Scenes connect.** The graphic zooms through every cut (the kit's link, 3 frames out and 4 in; the face never takes
    part).
16. **Every scene is its own world** (its own background, its own main object, its own kind of motion), acted out by the
    mascot (`E.clawd`, any colour, `dead` for forgetting) and packed with real details.
    - One dark terminal window in nearly every scene is the failure to avoid.
    - **Real websites, never a made up page.** When a story needs a worse version of a site, record the real site with
      the worse styles laid on (`tools/capture_smooth.mjs --css`), scrolling, so every version is the same real page.
    - Real sites play smoothly at their real speed (frame-exact recordings).
    - A "machine" prop (a press slamming down) reads as slop: show a process the way real software shows it (Claude Code's
      own "Compacting conversation" with the messages folding into the summary).
    - The opening is an idea that acts out the line, not the scene's main UI with the camera hopping between its parts.
    - A list of sites shown one after another, each in its window, is not a story. A list reel needs one acted idea
      running through it, not five showcases in a row.
17. **No decorative lines, a safe zone, no bangs.**
    - **No lines:** no marker underlines, strike-throughs, leader lines, arrows or connector lines. A state is shown by
      the element itself changing (colour, icon, check, glow).
    - **Safe zone:** tall phones crop the sides of a reel, so the kit draws every graphic at 0.86 of its size about its
      centre (`E.safe`, `window.SAFE`) and fills the margins with the scene's background (`window.BACKDROP` carries a
      canvas pattern, scaled and aligned). Nothing meaningful sits outside x 100 to 980.
    - **No bangs:** the drop is a riser swelling into a zoom whoosh on the cut with a soft sub under it; no impact, no
      crack, no white flash; error buzzers and shakes are replaced by soft slides.
    - **Real footage, fast:** a line about videos shows real reels playing, at doom-scroll speed.
    - **Show what the tool can really do:** when a line says a model makes something, the thing it makes is genuinely
      impressive.
18. **Websites as motion graphics, no fake effects on real pages.**
    - Footage of other creators comes from big public channels.
    - **A website is a motion graphic, not a slow slide:** the real page plays flat for its name, tips back on a plane and
      dims, and on each thing the speaker names, a real part of that site (a live demo recorded from it, or a crop of its
      page) lifts off into a deck in front; earlier parts step back in depth. Show the site's best parts, recorded from
      its real sub pages and demos.
    - **No random decoration:** no glows, halos or colour spills behind windows; every element shows something the speaker
      says.
    - **No faked effects on a real page:** when the story needs "what the AI made", it is a real page written the way AI
      writes them, recorded in a browser and building itself on screen (drawn per frame by `window.__draw(t)`), never
      styles painted onto someone's real site. The payoff shows the same page rebuilt well, in the same window as the hook.
    - **No chips and score cards as a payoff:** the result is shown as the real thing changing, not as a score, a sparkline
      or tags.
19. **No gap at the speaker's own cuts; never chop their natural pauses.**
    - **Recording cuts** are where the speaker stopped and restarted. `tools/take.py` finds them on the picture: a single
      frame where the pose jumps, with steady frames either side (fast hand movement blurs across several frames and is
      never taken for a join). Across each one the silence is removed completely, from just after the last word to just
      before the next (`--join-keep 0.05`), and the tool exits with code 3 if any join leaves a gap of 0.10 s or more.
    - **Natural pauses inside a take** keep the gentle trim (0.14 s kept, only pauses of 0.18 s or more). Cutting every
      pause makes the speaker look chopped.
    - **No stutter:** at a 1.2x pace from 60 fps, picking every 2.4th frame for 30 fps jerks in a 2, 3 rhythm. The conversion
      blends neighbouring frames (ffmpeg `framerate`). The face frames get a light sharpen (`unsharp 0.45`).
20. **The standard for every scene.**
    - **Act the line out as a small story with characters.** Each phrase becomes something that happens: a phrase about
      a lot of people is a crowd of mascots popping out in a wave, confusion is question marks rippling across them, a product
      name is the crowd rushing together into one big mascot, a new feature is that mascot powering up. Never a static screen with
      labels on it, never the camera hopping round a UI.
    - **A new beat on every phrase, three or four a second in the opening**, each one a transformation of what is already
      there (multiply, ripple, merge, power up, drop into place), so the picture keeps evolving instead of new boxes
      appearing.
    - **The mascot is the actor** (`E.clawd`: any colour for other agents, `dead` for forgetting, bob and blink), in crowds,
      alone, handing things over, reacting.
    - **One real detail anchors each beat**: the real command and its real output, the tool's own messages, real pages as
      motion graphics.
    - **Energy from inside the frame**: particles and sparks on a peak, a glow on a power-up, a wave or ripple across a
      group, objects flying into place. The camera holds still.
    - **Scenes hand over to each other through an object**: the big mascot drops into its corner as the terminal builds
      round it.
21. **The face card.** The kit's `card` layout: the graphic in the top half, a one or two word caption on y 1092, and the
    speaker small in a rounded card on the bottom edge (x 207 to 864, top y 1262, radius 30). The take sits in it at 0.66.
    - **The head rises out over the card's top edge:** `tools/matte.py <take dir>` writes a matte per face frame (RVM), and
      `E.init({ matteDir })` draws the matted head above the card.
    - **Full-face beats between the graphics** use the raw framing with jump-cut zooms on phrase starts; captions sit on the
      chest (y 1400).
    - What carries to every reel is the face card and the head rising out of it. The background, palette and animations
      belong to each reel (decision 1, rule 16).
    - **No scene sits still.** Every element added is part of what the speaker is saying, never decoration.
    - **Devices are real, never drawn.** A laptop or phone in a scene is a real photo or real footage (free stock works),
      and what its screen shows is keyed onto the real green screen.
    - **But real footage is not repeated.** One kind of shot appears once or twice a reel; the next time the idea comes up
      it is animated.
    - **The speaker talks on frame 0.** If the take opens on silence, cut it with `take.py --drop '[[0, <s>]]'` and check the
      voice level on the first frames of `voice.wav`.
22. **Review beat by beat before the full edit, every reel.**
    - `python tools/beatreview.py <reel dir>` opens Beat Review: the reel in an Instagram view, every beat numbered, a note
      box tied to each beat, checks, rounds and the sound cues. See [the README](README.md) for what is on screen.
    - The full-quality edit comes only after the reel is approved there.
    - **Change one beat, render one beat.** Read the notes with `python tools/beatreview.py <reel dir> --notes`, change only
      what they ask for, then `python tools/beatreview.py <reel dir> --rerender b03,b12 --say "what changed"`. Only those
      frames are rendered and spliced in; every other frame stays exactly as it was. If the sound changed, run `tools/mix.py`
      first and add `--mix final/mix.wav`. Never re-render the whole reel to fix one beat.
    - **Every cut hands the object on screen to the next scene:** the thing the last scene ended on travels into the next
      one and becomes its object. A scene never starts on an empty ground and builds from nothing. Check frames across every
      join in the rendered reel.
    - `tools/review.py` is the older, single-file version of this step: every scene clip embedded in one HTML page.

## How a reel is made
Each reel gets its own folder (the "reel dir"), kept outside this repo.

1. **`take/`:** transcribe first with `python tools/transcribe.py <take.mp4> take/words`, then
   `python tools/take.py <take.mp4> take/words.json take`. That gives `face.mp4`, `voice.wav`, `words.json` on the new
   clock, and `frames/`: the face frames, as near-lossless JPEGs. For the card layout (rule 21), then
   `python tools/matte.py take` writes `take/matte/`.
2. **`assets/`:** the real material for this topic: pages via `capture.mjs`, pages in motion via `capture_clip.mjs`, a page
   that draws itself via `capture_draw.mjs`, talk clips via yt-dlp, slide crops, logos from each site's own header.
3. **`edit/`:** `index.html` (loads `kit/kit.css` and `kit/kit.js`), `words.js` (words, corrected caption words, sentence
   starts), `scenes.js` (this reel's composition, written from zero), `notes.json` (what and why per scene; it feeds Beat
   Review).
4. **Plan and sound.** `node tools/render.mjs edit --plan` (plan plus the motion sweep), then stills (`--stills`) to check
   the look. Sound: `python tools/sound.py edit --report`, then
   `python tools/mix.py take/voice.wav edit/plan.json <out> --sound edit/sound.json [--bed ...]`.
5. **Beat Review** (rule 22). `python tools/beatreview.py <reel dir> --mix final/mix.wav`.
6. **The full edit, at full quality.** Render 0 to the end in one pass without `--draft`: lossless PNG frames, x264 slow at
   CRF 12, BT.709 TV-range colour tags. That is about 10 Mbps (15 on close-ups), so Instagram's re-encode starts from a clean
   copy. Mux the mix onto it (AAC 256k). Check the final against the approved beats frame by frame.
7. **Clean up after delivery.** Delete the reel's `take/`, `assets/`, `review/` and `final/`, and the edit's backups. Keep the
   delivered final, the raw take and `edit/` (a few hundred KB, so a later change can be re-rendered).

## Layout
```
kit/      the constant layer only: kit.css (frame, captions, type), kit.js (layouts, seek, motion values, typewriter,
          counters, the mascot and pixel sprites, icons), fonts/. Colours and worlds never live here.
tools/    transcribe.py, take.py, matte.py, capture*.mjs, render.mjs, sfxlib.py, sound.py, beds.py, mix.py, selfcheck.py,
          beatreview.py (the dashboard), review.py (the older single-file review)
study/    GRAMMAR.md (the style, as a study of two reference creators), the briefs for decoding your own references, tools/
```
