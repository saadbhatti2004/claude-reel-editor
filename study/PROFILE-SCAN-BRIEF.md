# Profile scan brief (educational style)

You scan a batch of one creator's reels to find **how all of this creator's videos are the same, yet each one is
completely distinct**. The reader is building a new editing style from a blank slate; assume no
house style and no rules of your own. Separately, a few of this creator's reels get a full frame-by-frame decode; your
job is the wide view across many reels.

## Inputs (paths given by the main session)
- The creator's post table `PROFILE-POSTS.md`: every scraped post with date, views, views against the profile median,
  likes, comments and the caption's first line.
- For each reel in your batch, a folder `<work_root>/<creator>/<shortcode>/` with `video.mp4`, `video.info.json`
  (the caption), `transcript.txt`, and `contact.jpg` (+ `contact_1.jpg` and so on for long reels): 2 frames a second,
  80 per sheet, each labelled with its time.
- When a contact sheet is not enough to read something (a repo name, a headline, a UI label), extract a full frame:
  `ffmpeg -v error -y -ss <t> -i video.mp4 -frames:v 1 <folder>/x_<t>.png`, crop to zoom in, and read it.
- Web search and web fetch (load with ToolSearch, `select:WebSearch,WebFetch`) to identify the real tools, repos,
  products and stories shown when they are not obvious.

## Method
Look at EVERY contact sheet of every reel in your batch and read every transcript and caption. Do not skim.

## Output: one report with these sections

**1. One row per reel**: shortcode | date | views and x median | the real thing it is about (named) | the spoken hook
(first sentence, verbatim) | the hook text on screen (verbatim) | the structure in beats (for example: claim, what it
is, 3 features shown on screen, who it is for, CTA) | the real material shown (named: which site, repo, app, post,
clip, chart) | layouts used (face full, face over screen, split, material full screen, face cut out over material,
graphic) | anything unusual in this reel (a device, a format, a shot, a sound) | the CTA keyword and what it promises.

**2. What is constant** across the batch (the creator's signature): layouts and their positions, how the face is
framed and placed, captions (font, size, colour, highlight), hook text style, music and effects, pacing, length,
the CTA (said and shown), the caption template. Count how many reels follow each constant.

**3. What changes, and why**: for each axis (structure, material, layout mix, devices, length, hook formula), how it
varies across reels and what in the TOPIC decides it. Give concrete pairs: "reel A (a GitHub repo) shows X because…;
reel B (a news story) shows Y because…".

**4. Material and sourcing patterns**: what kinds of real material appear and how often (screen recordings of sites
and apps, GitHub pages, demo videos, posts, news, charts, clips, memes, stock, AI images, his own camera); how the
creator most likely gets each kind; how material is treated (crops, zooms, cards, highlights, scrolls).

**5. Topics and hooks**: the topic families, the hook formulas (verbatim examples), and which ones the strongest
reels (highest x median) share versus the weakest.

**6. Changes over time**: anything that shifts from the oldest to the newest reel in your batch (format, length,
layout, CTA, editing density).

Be concrete: shortcodes and times everywhere. Subagents cannot write report files here, so **return the full report
as your final reply**: a 10-line summary under the line `10-line summary:`, then the report starting with a line that
begins `# SCAN`. The main session saves it.
