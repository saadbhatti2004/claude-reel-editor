# Creator synthesis brief (educational style)

You turn everything learned about ONE reference creator into a single, complete account of their editing system.
The reader is building a new editing style from a blank slate: this document is what they and their
editing engine will know about this creator. Assume no house style and no rules of your own. Report only what the
evidence shows, and cite it.

## Inputs (paths given by the main session)
- Every full frame-by-frame decode of this creator's picked reels: `references/<creator>/<shortcode>.md`.
- Every profile scan of the creator's other reels: `references/<creator>/SCAN-*.md`.
- The post table with every scraped post and its views against the median: `references/<creator>/PROFILE-POSTS.md`.
- The reel folders in your work folder if you must check a frame yourself
  (`ffmpeg -v error -y -ss <t> -i video.mp4 -frames:v 1 <your scratch>/x.png`, then Read the png).

Read EVERY decode and EVERY scan in full before writing. Do not skim; the details are the point.

## Output: one document with exactly these sections
Cite reels by shortcode and time everywhere (for example "R01 9.20 s"). Give counts ("in 14 of 19 decoded
reels") instead of "often". Where decodes disagree, say so and say which evidence is stronger.

**1. Who and what**: the account, the audience, the offer behind the CTA, cadence, follower and view numbers, median,
the outliers.

**2. The production system, end to end**: how one reel gets made, step by step, with the evidence for each step:
how topics are found (and any visible pipeline), how the script is written (length, words per minute, structure),
how and where he records (camera, framing, mic, set, takes and hidden cuts), how the graphics are most likely built
(tools named on screen or in captions count as evidence), how captions are made, how sound is made, the export
format. Separate what is proven from what is inferred.

**3. The constant signature** (what makes any reel recognisably his): layouts with exact geometry; the design system
(every palette hex, type families and sizes, card styles, corner radii, shadows, backgrounds); each caption system
(font, size, position, chunking, emphasis); the motion vocabulary (entries, exits, transitions, easing, how long things
take); the sound palette (music, beat drops, effects and what they land on, levels); the CTA system (said, shown,
written). Counts for each.

**4. The variable layer: what changes reel to reel, and what in the topic decides it**: structure, material, metaphor,
palette, layout mix, length, devices, hook formula. For each, concrete pairs of reels and the reason.

**5. The material system** (the most important section): every kind of material that appears (real
captures, real data inside designed mocks, logos, photos, cut-outs, invented data, his own footage, other creators'
footage), with how often, how it is most likely obtained (URLs where known), how it is treated, and the principle
behind when he uses a real capture vs a designed mock filled with real data vs pure illustration. Then the full
sourcing workflow as a checklist someone could follow.

**6. The decision rules (the thought process)**: the rules this editor follows, each with the reels that show it:
when his face is on screen and when it leaves; when the split, when full screen; how literal each picture is; how
proof is shown; how colour carries meaning; what gets no graphic; how a list or a mechanism is staged; how hidden
cuts are placed.

**7. Story structures library**: every structure he uses (for example a paid-to-free reveal, a news drop, a pain then
cure, a list speedrun, a ranking, a research breakdown), each with its beats and typical times, the reels that use it,
and how each performed.

**8. Hook library**: every hook, verbatim (spoken, on-screen text, and what is on screen at frame 0), grouped by
formula, with each reel's result. What the strongest openings share and what the weakest share.

**9. Retention devices catalogue**: every device that holds attention (open questions, counters, before and after,
typed reveals, pattern breaks, beat drops, risers, callbacks), with where it is used.

**10. Motion and graphic device catalogue**: every distinct device as a recipe: name, what it looks like, exact
timing and parameters (frames, scales, speeds), what kind of line it serves, the reels and times it appears.

**11. CTA system**: wording, placement, timing, the on-screen widget, the caption template, how it changed over time,
and what the comment rates say about what works.

**12. Performance**: what the outliers share and what the flops share, with numbers (views against median, comment
rate, like rate, watch time where known). Separate evidence from hypothesis.

**13. Changes over time**: how the format, look, length, CTA and editing density evolved from the oldest to the
newest reel.

**14. Errors and weak spots**: mistakes, mismatches and shortcuts found in the reels (so they are never copied).

**15. How each reel is the same, yet distinct**: a final table, one row per decoded reel: what it shares with the
signature, and the 2 to 4 things that make it its own, each tied to what that reel is about.

Subagents cannot write report files here, so **return the full document as your final reply**: a 15-line summary
under the line `15-line summary:`, then the document starting with a line that begins `# PROFILE`. The main session
saves it.
