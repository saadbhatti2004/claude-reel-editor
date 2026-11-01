# The educational style: what two top creators do

A study of how educational talking-head reels are built, from a large set of reels by two creators, the best of them decoded frame
by frame.

**How to read this.** **C1** and **C2** are the two creators. Short capitals (LIMIT, CLIPS) and codes (R01, R02) name individual
reels. Times are seconds inside the cited reel. "x median" is a reel's views divided by that creator's median views. Anything
that is inference is called a hypothesis: watch time and saves are not public, so every "why it worked" is grounded in counts,
not proof.

---

## 1. What an educational reel is

**Definition, from the evidence.** A talking-head reel of 25 to 60 seconds that teaches one real, named thing: a
tool, a repo, a feature, a release, a paper or an offer. The speaker talks from frame 0 to the last word. Every
sentence gets its own picture. Most pictures are designed motion graphics filled with the thing's real names,
numbers, commands, paths and logos. Real captures appear only where seeing the real thing is the proof. The reel ends
on one keyword the viewer comments to get the deliverable by DM.

**The three promises it makes to the viewer.**
1. **You will get it, even on mute.** Every line is acted out on screen. Headers restate the lesson in a fixed
   grammar ("Plan first, then code", C2 R01), and captions carry every word.
2. **It is real and you can check it.** The names, counts, commands and pages are the real ones (C2 R02's
   folder counts 36, 8 and 9 match the repo exactly; C1 TRADE zooms into the real "Star 111k").
3. **You can have it.** The keyword gets the link, the guide or the setup.

**What it is not.**
- Not a screen-recording tutorial. Neither creator ever runs a long recording with a moving cursor in a talking reel.
  C2's two decoded real clips last 2.84 s and 4.93 s.
- Not stock footage, and not memes inside a talking reel. Neither creator uses either.
- Not a slideshow. Something moves at least every 10 frames (C2); the picture is never still for more than about
  0.5 to 1.1 s, except a few holds such as the CTA (C1).
- Not self-branded. There is no logo, handle, lower third, progress bar or end screen (C2 23 of 23 in one scan).
  C1's only self-reference is his avatar inside the CTA mock.

---

## 2. How a reel is made, end to end (both creators)

Both run the same pipeline. Each step below has the evidence that proves it.

1. **Find the topic.**
   - Both hunt in other creators' outlier reels and rank them by how far they beat that creator's median.
   - Both also hunt on GitHub trending, Trendshift and launch news, and turn news around fast:
     - C1 LIMIT went out 5 days after Opus 5.5; MELTY the same day as the press coverage; GAMES 2 days after the
       browser GTA port went viral.
     - C2 covered Claude Code Mods 8 days after launch, and the $250 credit offer 3 days before its deadline.
   - Winners get recycled: C2 ran find-skills 3 times, Strix 3 times, and agency-agents twice.
2. **Read the source in full and copy the exact strings.** This means the README, the folder tree with its counts,
   the install command, the star count and the docs.
   - Five of R01's six phrases map onto sections of the official Claude Code best-practices page.
   - C1 lifts README claims one by one: the tagline becomes the feature list, the providers table becomes tool
     logos, and the "zero key" path becomes a $0 line.
3. **Write the script for the picture.** One claim per sentence, and every sentence carries a noun a scene can show.
   - The script exists before the edit. In C1 TRADE the captions follow the written text, not what he actually said.
   - In LIMIT the cards say "Fable" while he says "Opus 5.5": the graphics were built from an earlier draft.
4. **Record in one sitting.**
   - The camera is locked at eye level, chest-up, and looks into the lens (C2: scale 1.00 ± 0.02 across 18 jump cuts;
     C1: face scale 0.986 to 1.012).
   - Both hold a wireless mic in hand, usually with a fur windscreen.
   - Often there is a separate CTA take (C1 TOKENS, BOOK, REPOS). C1 REPOS was recorded one line per take.
5. **Cut the talking head first, at every pause.** Gaps end at 0.12 to 0.50 s.
6. **Lay the scenes on the cut points.**
   - C1 LIMIT: 9 of 10 cuts land within 2 frames of a sentence's first word.
   - C2: 10 of 14 panel changes land within 0 to 5 frames of a face cut (R01); in R02, 7 of its 18
     face cuts land on a scene change or within 1 to 4 frames of one.
7. **Build every scene as code.**
   - Both name Remotion ("Claude can animate") and HyperFrames ("HTML to MP4") in their own stack posts.
   - The templating is proven by the details:
     - frame-exact counters;
     - a stopwatch equal to the video clock (C1 TOKENS);
     - caption pills sized by a pixel rule (68 px plus 36 px per character, C1 FINDER);
     - headlines pixel-locked across scenes (C2);
     - modules reused with the same bugs (C1).
   - C2 renders the panel at about 1080x945 and full screens at 1080x1920.
8. **Time the state changes inside each scene to single words.** For example, a logo colours on the spoken brand
   name (C2 R02), and a slider maxes out on the word "limit" (C1 LIMIT 9.20).
9. **Caption.** Both use auto captions with hand fixes, and both leave errors on screen.
10. **Lay the sound.** One bed runs from frame 0, its drop sits on the story turn, and effects mark state changes.
11. **Export** at 1080x1920 and 30 fps (C2 29.97).
12. **Post.** The keyword goes on line 1 of the caption (C1) or line 2 (C2), and an automation sends the DM.

**What this means for us.** Every step except recording can be done by the engine. Recording is the speaker's part, and
this style asks little of it (section 17.J).

---

## 3. The constant layer

These are the things that hold in almost every reel of each creator. They are what makes a viewer recognise the
account. They are not a template: no composition, picture or sequence repeats.

| # | Constant | C1 | C2 | The shared rule |
|---|---|---|---|---|
| 1 | Start | Speech from frame 0 in 16 of 16; a full scene on frame 0 with no build-in | Speech from frame 0 in every talking reel; motion within 5 frames in 3 of 3, and in 11 of 12 recent reels | No greeting, no name, no intro. The payoff or claim is the first sentence (C2: 20/20, 18/18, 10/10, 20/20, 3/3 across batches) |
| 2 | End | The video ends 0.1 to 0.4 s after the last word (18 of 18 voiced reels) | Ends on a closed mouth, so the loop restarts on the hook (R01 48.05 to 48.28) | No outro, no end card |
| 3 | Layouts | Split A (seam y 768), Split B (seam y 920), full graphic, face plus headroom cards, face-anchored evidence, one faceless grid | SPLIT in 66 of 72 (seam y 943 to 945), GFX full graphic, FACE full frame | Three base layouts: graphic over face with a hard seam, full graphic, full face. The seam has no line, shadow or rounding. The face is the raw camera, never cut out or boxed |
| 4 | The face | Never away more than about 5.2 s in the 11 split reels; back every 3 to 4 s in TRADE | Visible 77% to 100% of the runtime | The face is the trust layer and comes back fast |
| 5 | Cuts | Hard cuts between layouts in 15 of 16; no whips, slides or speed ramps | Hard cuts carry almost everything; 1 to 3 effect transitions a reel (glitch, morph, wash) | Hard cuts. An effect transition is a rare accent, never the grammar |
| 6 | Cut placement | On the sentence's first word or inside its breath | Scenes laid on the face cuts | Cut where the sentence starts; hide jump cuts under graphic changes |
| 7 | Captions | Fixed position per layout; within 0 to 4 frames of the word | Fixed on the seam; 0.0 to 0.2 s after the word, never ahead | Every word captioned, 1 to 3 words a chunk, position never moves within a layout |
| 8 | Colour meaning | Red paid, limit, wrong; green free, done; orange Claude; blue the word that matters; grey inactive | Red bad, mint good, orange active; chapter colours; the second headline line coloured by mood | Colour carries the plot |
| 9 | Type | Heavy neo-grotesk (Inter or SF Pro class); a mono for labels and terminals; an italic serif for emphasis in 5 of 16 | Heavy tight grotesque headlines; IBM Plex or JetBrains Mono for code; a pixel font for small UI; serif in the earlier look | One heavy sans and one mono; one accent face at most |
| 10 | Cards | White rounded cards with soft shadows on a pale canvas (15 of 16) | Cream or white cards on one flat background per reel or chapter | Clean cards on a flat field |
| 11 | Sound | One bed under a dry, close, compressed voice | Same | The voice is on top and dry; the bed sits under it |
| 12 | CTA | The last sentence in 16 of 16; the keyword shown as UI | The last sentence in 69 of 72; the keyword title in 68 of 72 | One keyword, last, on screen, repeated in the post caption |
| 13 | Self-branding | None except the avatar in the CTA mock | None, 23 of 23 | No logo, handle, lower third or end screen |
| 14 | Set | One room, mic in hand, wardrobe per shoot | A few sets, mic in hand, wardrobe per batch | The set follows the filming batch, never the topic |

**What both creators keep fixed and what they let change.** Each kept the room, the mic in hand, the fast trimmed
delivery, a graphic on frame 0 and a free deliverable behind a one-word keyword through the whole span (C1). C2 kept
the split, the boxed seam captions, the keyword in quotes, the speech pace and the full-face ending.
Everything else changed reel to reel.

---

## 4. The bespoke layer: how every reel becomes its own

In both creators **every distinct element is derived from
the topic itself**. None is picked from a menu. Here is the chain:

| What changes | What decides it | C1 | C2 |
|---|---|---|---|
| **Structure** | The shape of the topic | A paid anchor exists, so the reel is built on the price contrast (CLIPS, BOOK). A system with parts gets a walkthrough that copies the product's own architecture (TRADE copies TradingAgents' org chart; MONTAGE copies OpenMontage's "orchestrator"). A list gets only a progress device (TOKENS, REPOS) | One tool with a process becomes a mechanism chain (R03: terminal, file, report, skills, editor, dashboard, toggle). Typed inputs become "input, then outcome" (R01). A package of role plugins becomes role chapters (R02). An offer becomes offer, deadline, why, how, proof |
| **World and metaphor** | The topic's own nouns and name | "dunks on" becomes a literal dunk (LIMIT); "built like a trading firm" becomes a building whose floors light up (TRADE); "decompiler" becomes a restaurant meal and its recipe (APP); a skills search becomes a bookshelf and a librarian (FINDER); a "video studio" becomes a film set (MONTAGE); "old rules pile up" becomes stickers piling onto the mascot (DELETE) | MiroFish becomes a fish swarm; a "clone" tool a blueprint grid; "free Claude Code" an arcade "FREE / ∞" screen; "taste" a wizard under a starry sky; an Anthropic offer kraft paper and serif; a skill that reads your sessions a "files being read" language |
| **Palette** | The subject's brand, or the story's chapters | TRADE runs market green and red; VOICE takes its pink from the VoiceStudio logo; CLAUDE gives each plugin card its brand colour; one reel reskinned in NVIDIA black and green | Cloudflare orange on dark; LinkedIn, Reddit and X each get their own colour slide; R03 goes blue, red, lavender, cream with its four story chapters; R01 stays one green because it has no chapters |
| **Material** | What exists to show | Games are visual, so GAMES is 64% real footage; audio cannot be played in this format, so VOICE is 0% real; a paper's own pages and figures prove HUMAN; real X posts of hype prove TRADE | Phrases have no UI, so R01 has 0% real footage; a one-paste install gets one real install clip (R02); a plugin gets its homepage hero (R03); visual output is shown for real (Runway, Luma) |
| **Devices** | The claim type | A number gets a count-up; speed a stopwatch; a cost a bills card or receipt; a before-and-after the same card twice | Scale a counter; "free" a strike or a $0.00 receipt; checking a magnifier or stamp; gaps a puzzle; speed race bars; an eligibility fact a word-by-word highlight on the real page |
| **Layout mix** | How much there is to explain, and how personal the line is | Lists stay face-full with overlays; a research breakdown keeps the face 100% so it vouches for each source; pure argument with no product goes faceless with a narrator mascot; mechanism-heavy reels spend 43% to 55% on full graphics | Abstract feature lists keep the split at 81% to 86%; visual output and documents meant to be read go full frame |
| **Length** | The item count | 25.9 to 39.7 s; list speedruns at 1.1 to 1.2 names a second | About 8 to 12 s per item, plus about 8 s for the hook and the CTA |
| **Hook formula** | The source of the news | A paid-tool clone gets "Someone built a free open source version of...". A launch gets a rivalry. A viral clip gets disbelief. A hype wave gets "X just killed Y. Well, that's what everyone's saying." A paper gets a visual statement. An authority gets "The man who built X says..." | A named company gets "[Company] just released". An unknown author gets "Someone has just built". A capability gets "You can now". A list gets "If you're using X, these are the N". Money gets "This X turns Y into $Z" |
| **The mascot's role** | The topic's verb | A convict with a katana for "this feels illegal" (APP); a hard hat, a searcher and a librarian (FINDER); banned for "don't use Claude Code until" (CLAUDE) | It reads and thinks (R03), clones and sleeps (R01), dresses for each job (R02) |
| **Deliverable and keyword** | The content | A repo gives the link; a setup gives the full guide; the keyword is the topic or its verb in one word | A repo gives the link; a workflow gives a guide or checklist; prompts give the prompts |

**Proof, in pairs: what each reel shares, and what makes it its own.**

| Reel | Shares the signature | Its own, because of its topic |
|---|---|---|
| C1 LIMIT (63.1x) | Split plus full-graphic alternation, typed CTA box | A launch-week rivalry staged as a dunk between the two CEOs' faces; a 7-day usage card that goes red and comes back green, because the pain is a weekly limit; the two CLAUDE.md lines typed live as the takeaway |
| C1 CLIPS (36.4x) | Split, serif emphasis, typed CTA | Paid vs Free OpusClip cards at frame 0, because the topic clones a known paid tool; the repo is never named, so the comment is the only way in (16.4% comments); a filmstrip, a viral-score board and a 7-slot week, the nouns of clipping |
| C1 MELTY (33.6x) | Split, mono seam chips, two-step CTA | A real viral gameplay clip at frame 0, because the claim is "this is real"; a Steam-like library of 12 famous covers, because the audience is gamers; a recipe, lock, binary and blueprint chain, because the story is about closed game code |
| C1 TRADE (14.8x) | Split, mono chip with a blue keyword | A cartoon Grok shooting real trading-app icons, because the hook borrows "Grok killed day trading"; the edit copies the repo's own org chart; real X hype posts plus a deleted "-92%" draft, because the story deflates the hype |
| C1 GAMES (14.6x) | Face, word captions | The face never leaves and evidence cards float on the wall, because every claim has a real thing behind it; source chips on every card; a news beat on the drop, because an evergreen list needed urgency |
| C1 HUMAN (1.1x) | Split, pill captions | A coded particle chart as both hook and payoff, because the finding is that AI writing clusters; the paper walked in reading order, because it is a research breakdown |
| C2 R03 (9.3x) | Split, seam captions, "You can now", full-face keyword | A "files being read" visual language, because the product reads your session files; one invented user's history drives every proof, so the opening prompts return as findings and a 4h 40m total; colour chapters mirror the story chapters |
| C2 R01 (2.0x) | Split for 90.8%, cream cards, numbered list | The typed prompt box is the hero of every item, because the subject is text you type; each item is a bespoke mini-demo; a single deep-green world with zero real footage, because phrases have no UI |
| C2 R02 (1.0x) | Split, "[Brand] just released", the same 107 BPM bed | Mascot characters dressed per job role with role-colour chapters, because the release is a set of role plugins; one fictional customer thread from research to the deal answer; the only decoded real app recording, because "just add the repo" is believable only as real footage |
| C2 R04 (6.2x) | Split, seam captions, keyword CTA | A black pixel-arcade "FREE / ∞" world, because the promise is free play; a token counter to 7.4 billion, because the claim is scale |
| C2 R05 (62.2x) | Split, keyword title | The real anthropic.com eligibility text highlighted word by word with his voice, and a salary counter to $85,000, because it is an official opportunity with rules |

**Why "no templates" is right, from their own numbers.** When either creator reused a whole composition, a sentence
or a topic, the result fell:
- C1: VOICE and BOOK reused CLIPS' template and opening sentence one day apart, after two other reels had opened on
  it too, and did 0.52x and 0.6x against CLIPS' 36.4x.
- C1: the 40-repo sequel did 1.3x against the 32-repo original's 15.8x.
- C1: CLIPS2 reused CLIPS' keyword 25 days later and got 5.2% comments against 16.4%.
- C2: the identical hook, word for word, did 13.6x (R06) and then 1.1x (R07).
- C1: the reused modules carried their bugs into each reuse (the Gmail logo on Google One in VOICE and BOOK; stale
  follower stats in three CTAs).

What both reused safely was the **kit**: small parts like the card, the counter, the typewriter, the cursor, the
stamp and the comment box. These were recomposed fresh each time. The decay came from reusing **compositions**, not
parts. So the rule is: one kit of parts, every reel composed from zero.

---

## 5. The material system: how real references are used

### 5.1 The one question asked of every line
Both creators answer one question per line: **what must the viewer see for this line to be believed or understood?**
The answer puts each line in one of four tiers.

| Tier | Use it when | Examples |
|---|---|---|
| **A. Real capture** (the real pixels) | The thing itself is the evidence, and a mock would look fake or be doubted | Visual outputs: a CoD sniper inside Minecraft (C1 MELTY 0.00); blurry vs sharp GT4 (C1 GAMES 20.23); GTA V running in Chrome (C1 GAMES 22.53); Runway output (C2). A real page's own number is the argument: "Star 111k" zoomed and glowing (C1 TRADE 4.10 to 5.43); "61,608 stories" highlighted on arXiv (C1 HUMAN 10.43). Hype that must be seen to be debunked: two real X posts (C1 TRADE 22.57). "It is official": the anthropic.com eligibility text (C2 R05); the real plugin site (C2 R03 36.37). "It is easy": one real install clip (C2 R02 53.29 to 58.22). Authority when there is no product: an HBR headline, a Google AI Overview salary (C2 R08) |
| **B. A designed mock filled with real data** | The line says what the tool contains or does, or what the viewer must do (install, type, run, cancel, pick, comment) | Exact skill-folder names and counts, 11 real slash commands (C2 R02); SKILL.md, spec.md, package.json, schema.sql, auth.ts, bcrypt, date-fns (C2 R01); the real session path `~/.claude/projects/<session-uuid>.jsonl` (C2 R03 8.47); GitHub API data rebuilt as legible cards (C1 TOKENS); real prices from pricing pages (C1: Calendly $10 a seat, ElevenLabs Creator $22); the real CLAUDE.md lines typed in time with the voice (C1 LIMIT 19.87) |
| **C. Pure illustration or metaphor** | A number, a feeling, or a mechanism that has no screen | A race for "10x" (C2 R01 3.17); a sleeping mascot for "without you" (40.87); a router diagram for model routing (C1 LIMIT 10.97); a voice dot blocked from the cloud for privacy (C1 VOICE 18.53); a fish swarm as a pun on MiroFish (C2) |
| **D. Invented data** | The worked example only: something personal that needs a story | One fictional user or customer per reel, whose numbers reconcile: in C2 R03 about 25 streamed prompts come back as findings, and five task times sum exactly to 4h 40m; Acme Corp, Dana Lee and a $48k deal run from research to the answer (C2 R02); one booking universe in C1 BOOK; "lost signal" through every scene of C1 MONTAGE. It is never shown as a source |

Why tier B wins most lines:
- **Timing.** In a mock, typing lands on the spoken words (21 to 22 characters a second in C1 LIMIT).
- **Clarity.** A mock has no cluttered real editor.
- **Control.** One consistent universe runs through the whole reel.
- **Legibility.** It reads at phone size.
- **Truth.** It still reads as true, because the real layer is the vocabulary: "the real layer here is the
  vocabulary, not captured footage" (C2 R01 decode).

### 5.2 How real material is treated so it reads on a phone
- **Zoom to the word.** The page scales 1.6x to 2.5x inside a fixed card, in 4 to 12 frames, onto the exact name or
  number as it is said:
  - C1 TRADE 2.2x push, a pan, a glow, a pull-out;
  - GAMES 2.1x in 4 frames;
  - CLAUDE 2.18x in 7 frames;
  - HUMAN 1.6x and 2.3x in 12 frames.
- **Highlight what is said.**
  - A yellow marker sweep (the #FCD94D family) over 3 to 24 frames.
  - A hand-drawn blue ellipse drawn in 6 to 8 frames around a stat said aloud (C1 HUMAN).
  - A coral highlight moving word by word with the voice over a real page (C2 R05).
- **Overlay, don't replace.** Designed graphics sit on top of the real thing rather than in its place: a counter on
  the dimmed repo page, a FREE stamp over the screenshot, a chip highlight morphing into code over a real motherboard
  photo, a thought bubble over gameplay (C1 GAMES).
- **Credit it.**
  - A "via @handle" or "via cal.com" chip on third-party video.
  - Source chips on every evidence card (C1 GAMES).
  - Creative Commons credits printed on photos (C1 HUMAN).
- **Frame it cleanly.**
  - C1: a rounded card, the page captured logged out (GitHub's marketing nav is visible), usually dark mode, no
    cursor, no scroll.
  - C2: full width in the panel, no device frame and no highlight box; the real cursor guides the eye; the clip is
    retimed to the voice.
- **Give stills life.** A linear 11.1% push over 84 frames on a static capture (C2 R03), a slow scroll, or a
  moving cursor.
- **Cut people and products out as stickers.** The CEOs' heads with a 5 px white outline (C1 LIMIT); PS5 and PS2 cut-outs
  (C1 GAMES).
- **Stop before the result in a real demo,** so the deliverable stays gated. C2 hovers on Send without clicking
  (R02 57.79).

### 5.3 Where real material sits in the story
- **Right after the hook, as social proof:**
  - C1 TRADE's real repo page at 2.8 to 5.9 s; GAMES at 3.2 to 8 s.
  - C2 at 0.5 s (R09), 2 to 6 s and 3.5 to 9 s.
- **At frame 0, when the claim is "this is real"** (C1 MELTY).
- **At the setup step, when the claim is "it is easy"**, 81% to 96% of the way through (C2 R03 and
  R02).
- **As a debunk:** the hype shown, then deflated (C1 TRADE).

### 5.4 Real pixels do not buy reach, but missing proof costs trust
- The two biggest C1 reels (LIMIT, CLIPS) contain no third-party capture at all. The most "real" one (GAMES, 64%)
  did 14.6x.
- C2 went from real captures in about half his talking reels (earlier months) to almost none (recent), while keeping
  every real name. The mocks replaced real pixels while keeping the real names.
- But every decode that lacked proof of the core output named that as the reel's biggest weakness:
  - no cloned voice is ever heard in C1 VOICE;
  - no generated video is shown in C1 MONTAGE;
  - the ready demos on the tool's own site went unused in C1 APP.

**How to use real material.** Both creators under-use the real thing exactly where it matters
most: the proof of what the tool produces. So the standard for us is:
1. Every frame carries maximum real material: the real logos, pages, talks, products, file names and commands
   wherever a real one exists, because real things look real. Numbers and examples are free to make up.
2. Real pixels appear at every point where they are the proof, above all the real output of the tool. Use the real
   generated clip, the real cloned voice, the real page with its real number.
3. Designed mocks carry the rest, because they are clearer, faster and legible, but they are filled only with real
   vocabulary.
4. Invented numbers stay consistent inside the reel, so later scenes pay off earlier ones.

So the motion design is the delivery, and the substance is
real.

### 5.5 What neither creator uses
- **Both:** no stock footage, and no memes inside talking reels.
- **C1:** no news headlines, no clips of other talking creators, no AI-generated images (except one sponsor reel), and
  no real screen recordings with a moving cursor (except the sponsor reel and some August phone-filmed screens).
- **C2:** no news clips, no tweets and no real charts from data sources in 94 videos. AI images appear only as hook
  metaphors or slides in a few scanned reels.

### 5.6 The sourcing checklist (both creators' steps merged, plus the fixes their errors call for)
1. **Pick one named, real, checkable thing.** That means a repo, plugin, feature, release, paper or offer. Prefer a
   gain anyone would want: free, money, time, limits.
2. **Read the source in full,** logged out: the README, the folder tree with names and counts, feature tables, the
   install command, the star count (`stargazers_count` from the GitHub API), the official docs and the launch post.
   Copy the exact strings.
3. **Find the one visual proof of the result,** the real output above all. Look for an official demo GIF in the
   README, the tool's own demo, a viral clip on X or a repost, a comparison video, or the paper's own figures.
4. **Capture the real pages:** one full-width screenshot logged out (header, tabs, star count, About panel), plus a
   scroll or zoom path to the exact word the line will say.
5. **Collect numbers for the cards:** prices from pricing pages, plan prices, benchmarks, install commands.
6. **Download the brand assets:** product logos from brand or press pages, the GitHub mark, emoji from an open set
   (C1 uses Microsoft Fluent 3D emoji), and the reel's character in its pose set.
7. **Invent freely where the reel needs it:** one fictional user, plausible, and
   consistent within the reel, so that later numbers reuse and reconcile with earlier ones.
8. **Credit every third-party clip or photo on screen.** Credit the original creator, not a reposter (C1 MELTY got
   this wrong).
9. **Save every source in the reel's material list:** the URL and what was taken from it, for the credits.

---

## 6. The thought process: the decision rules both follow

1. **One sentence, one scene.** The cut lands on the sentence's first word or inside its breath.
   - C1 LIMIT has 11 sentences and 11 scenes, and 9 of its 10 cuts land within 2 frames of a first word. In C1 VOICE
     every pause over 0.15 s hosts a cut.
   - C2 lays panel changes on the face cuts.
2. **Every line gets a picture.** Only pain, caveat, opinion, personal and ask lines get the face alone.
   - C2 R01 has no line without a panel picture until the caveat at 43.88.
   - C2 R03 gives only the pain lines (13.88 to 18.45) and the CTA to the face.
   - C1 gives one "breather" line per reel to the face only, in 3 reels (CLIPS 23.83, CLIPS2 4.87, VOICE 20.33).
3. **Connector words get no new visual.** "And", "so", "because" ride the previous scene; the change lands on the
   next content word (C2 R03 rule 8; C1 LIMIT 1.30, CLIPS 15.00).
4. **Be literal to the word, and move the thing being said, on the word.**
   - C2: a session is a terminal; "saved as a file" is the terminal shrinking into a .jsonl card; "nobody looks at it"
     is a column of "Never"; "automate" is a toggle turning green; research is a magnifier filling fields;
     reconciliation is two columns matched to $0.00.
   - C1: the slider maxes out on "limit" (LIMIT 9.20); the bar grows on "stronger" (GAMES 18.03); "halfway" becomes
     50% (REPOS 7.57).
5. **Input before outcome.** Show the exact phrase typed into the prompt box, then a demo of what it does (C2
   R01, 6 of 6 items; C1 LIMIT types the two CLAUDE.md lines).
6. **Before before after, in the same window, with one variable changed.**
   - C2 shows the "GUESSING" stamp before "never guessing", even though the sentence says it the other way around
     (R02 44.34). The window is kept while the text morphs.
   - C1 shows the same card twice: the week red at 9.20 and green at 34.77 (LIMIT). DELETE, BOOK, VOICE and REPOS do
     the same.
7. **Show the mistake before the fix.**
   - C1 LIMIT sends the easy task to the wrong model, the card turns red (14.00 to 16.23), and the routing is fixed
     later (28.13).
   - C2 R01: the cursor clicks the bad row, it turns pink, a strike draws, and the text retypes to bcrypt.
8. **Place the face by the line's job.**
   - **Split** for facts and mechanism.
   - **Full graphic** for:
     - named reveals and escalations (C2 R03 20.92, 29.36);
     - dense reading (C2 R02 9.84);
     - processes that need a source and a destination in one frame (C1 FINDER, MONTAGE's 2x2 crew grid);
     - big emotional beats (C1 TRADE's hook and fight).
   - **Full face** for pain, caveat, the "So..." opinion lines, personal proof and the ask.
9. **Change the layout rhythmically, and bring the face back fast.**
   - C1's alternators change layout on every sentence and never repeat the same layout on two shots in a row; the face
     never stays away more than about 5 s.
   - C2's recent decodes keep the split for 61% to 91% of the runtime and change the panel instead.
   - Both hold the same principle: something big changes on every sentence.
10. **Colour carries the plot,** at three levels:
    - chapter backgrounds (C2 R03 blue, red, lavender, cream);
    - verdict states (red bad, green good, orange active, grey not yet);
    - one accent for the word that matters (C1 blue).
11. **Use a metaphor only for numbers, feelings, or mechanisms with no screen.** Use one extended metaphor at most,
    planted early and paid off late:
    - the FINDER bookshelf (0.00) returns as the librarian (21.43);
    - HUMAN's particle ball (0.67) returns reshaped (31.20);
    - LIMIT's red week returns green.
12. **A list shows its length and your place in it.** Show all the slots empty first, reveal each item on its word,
    keep progress visible, and save the best for last.
    - C1: TOKENS' 20 empty slots at frame 0; CLAUDE's "0/4"; REPOS' 10 dots and its "Best" badge.
    - C2: six blurred rows plus a six-dot tracker; "MOD 01 / 05"; "?" tiles; the spoken signpost "The last one".
13. **Every number animates** and eases out at its final value. C2 has counters in 15 of 20 talking reels in one
    batch; C1 in at least 9 of 16. The spoken number and the shown number must match. C1 APP says 40,000 while its
    counter runs to the real 265,849, and the decode flags the clash.
14. **Proof is tool output, a moving number, a real page highlighted, or the same object before and after.** It is
    never a testimonial and never a long recording. Personal proof appears only as the creator's own numbers: C2's
    489 vs 233 lines test (R10); C1's "I swapped mine over in about 10 minutes" with a timer (BOOK 19.57).
15. **Hide the jump cuts:**
    - under a panel swap or layout switch;
    - under a glitch (C2 R03 6.07);
    - inside a face-only block;
    - behind a ±8% punch toggle per item (C1 REPOS);
    - or as a same-framing jump while the graphic keeps moving (19 cuts in C2 R01).
16. **Never still.** Something moves at least every 10 frames (C2). Scenes idle with:
    - cards drifting up 9 to 12 px a shot;
    - a full-screen card scaling 96% to 100%;
    - a 0.4° per second 3D float;
    - a grid drifting 2.3 px a second;
    - a panel push of 0.3% to 0.45% a second.
17. **Graphics land on the word, or lead it.**
    - Captions land 0 to 4 frames from the word.
    - In C2 R02 graphics lead the voice by 0.4 to 1.0 s, so the eye arrives before the ear.
    - A spotlight on a list item leads its spoken name by 0.4 to 0.5 s.
18. **Headers restate the lesson in a fixed grammar,** so a muted viewer gets the reel from the titles alone ("Plan
    first, then code", "Check first, then build", C2 R01).
19. **Show the keyword before or as "comment" is said, and hold it to the end.** C1 LIMIT types it at 36.13 to 36.60
    and says it at 37.68; C2 R01 shows it 1.6 s early.
20. **Gate the deliverable.**
    - Even when the resource is visible, stop before the result (C2 hovers on Send).
    - Naming the answer early in a comment-gated reel lowers comments: C1 BOOK shows the replacement's logo at 1.33 s
      and gets 0.9%; MONTAGE shows the URL at 4.2 s.
21. **Design every panel with a clear caption band.** C2 R01 hid three payoffs behind its caption box.

---

## 7. Story structures: the library, chosen by topic

Under almost every structure runs one spine:
1. the claim in sentence one;
2. the thing named;
3. how it works;
4. the turn ("So instead of...");
5. an escalator ("And what's even more insane...");
6. the setup ("To set it up, you just...");
7. the keyword.

**The music drop sits on the turn.** C2's "So instead of" line falls at 40% to 75% of the runtime in one batch, and
his drop lands at 18.8 s (31% to 42% of his decoded reels). C1's drop lands at 22.8 s in every reel, which is 57% to
88% of the runtime, because his house track is fixed and his reels vary in length. So the turn's position varies;
what holds is that the drop marks it.

| Structure | Use it when the topic is | Beats | Best evidence |
|---|---|---|---|
| **Paid-to-free reveal** | A free version of something people pay for | Paid vs Free cards with a known brand at frame 0 and a strike on "free"; the objection killed ("still does the part people actually pay for"); how it works; the money pain (a bills pile); proof (name plus stars); why it's free ("runs on your own computer"); the outcome; keyword | C1 CLIPS 36.4x (name withheld); C1 R11 5.7x. C2 versions: "$20 plan into the $100 plan" R12 5.6x; "$18,000" struck to "$0" R13 3.9x |
| **Launch rivalry plus tip** | A big launch that fixes a common pain | Rivalry picture; news unboxing; unnamed problem; the problem in the viewer's words; cause; one action; how it works after the drop; payoff mirrors the problem; keyword | C1 LIMIT 63.1x |
| **Capability through a personal-data chain** | A tool that works on the viewer's own data | "One command" hook; insider fact; pain on the face; turn plus drop; full-screen named reveal; three proofs; "even more insane" with a shock number; before and after; real install; keyword | C2 R03 9.3x |
| **Brand news or offer drop** | An official opportunity, offer or deadline | Offer; name; what it is; requirements; why it matters; how to claim; personal proof on the face; keyword | C2 R05 62.2x |
| **Multi-model team** | Combining tools into one setup | "X just got 10 times better"; one tool's blind spots; roles per tool; "an entire AI team"; "basically free" kicker; keyword | C2 R14 27.7x |
| **Viral-clip explainer** | A visual result people have already seen | Disbelief plus the real clip at frame 0; the claim on a shelf the viewer owns; name slam; proof clip again; "So how is that even possible?"; why it was impossible; "But now"; the mechanism; terms; keyword | C1 MELTY 33.6x |
| **Hype then deflate** | A wave of hype claims | A borrowed violent claim; a hedge on the face; the real proof page; the walkthrough; "You've probably seen the screenshots" on the drop; the survivorship twist; the safe step; the CTA loops back to the hook | C1 TRADE 14.8x |
| **Find plus explainer plus news** | An evergreen tool that needs urgency | Benefit plus a written news line; real page plus count; chapter "Here's how X works"; mechanism with real photos; objection killer; bonus; "This week..." news on the drop | C1 GAMES 14.6x |
| **"Someone has just built X, free"** | A new repo from an unknown author | Discovery; stars as social proof in the first 10 s; name; how it works; "instead of"; "the craziest part is it's free"; reframe; keyword | C2 median 1.1x; R06 13.6x |
| **Pain-first tool with your own test** | A measurable fix | Pain; name and promise; mechanism checklist; your own A/B numbers; payoff on the face; cost angle; "took me about a minute"; keyword | C2 R10 4.3x |
| **List speedrun** | Many items, each needing one line | Title plus an empty numbered grid plus a pacing device at frame 0; names at about 1.1 to 1.2 a second; the full grid held about 2 s; hard cut to the CTA | C1 TOKENS 3.9x; the 32-repo list 15.8x |
| **Numbered list, input then outcome** | A set of things you type | A loss hook with the count and blurred answers; N items of 4.4 to 7.5 s, each "The Nth is [phrase]" typed, then demoed; "The last one"; caveat; keyword | C2 R01 2.0x |
| **Ranked countdown, best last** | Several items of rising value | "N things, best last"; an open loop on who is best; items every 2.3 to 6 s with ordinal signposts; personal proof mid-way; the payoff with a badge; keyword | C1 CLAUDE 1.7x, REPOS 0.7x |
| **Role or use-case tour** | One release that serves many jobs | News, number and "free" with a roll-call highlight; trust stamp; what it is; pain counter then relief; roles x tasks; second benefit; wrong vs right number; "there's even one for..."; real install; keyword | C2 R02 1.0x |
| **Authority contrarian** | A famous builder's surprising rule | "The man who built X says [rule]"; "but he's kind of right"; credential; why; relief; 2 to 3 steps; the exception; payoff on the drop | C1 DELETE 2.2x |
| **Taboo plus analogy** | A powerful tool that needs translating | "This feels illegal" plus a mascot action; name plus stars; scope; an everyday analogy across 4 to 5 scenes (about 37% of the runtime); payoff | C1 APP 1.1x |
| **Research breakdown** | A paper or a study | A visual statement of the finding; the myth staged and busted; institutions; scale; the headline result; the mechanism; one relatable stat circled; the flaw in a familiar tool; the product; a callback to the hook | C1 HUMAN 1.1x |
| **Process story of one repo** | A pipeline with clear stages | Input; step 1; step 2; output; "So instead of one AI..." | C2 0.6x to 0.9x |
| **Setup tutorial** | "The correct way to set up X" | Promise; why setup matters; N numbered steps, each shown; one worked life example; payoff; keyword. The longest form (59.5 to 81.8 s), with face breathers | C2 0.9x to 1.3x |
| **Risk or warning** | A threat to the viewer's work | Fear question or accusation; scenario, then "tell your AI to..." three times; urgency; reassurance | C2 0.7x to 0.9x |
| **Versus or side-by-side test** | Two tools compared | VS card; A's strengths; B's strengths; "the debate is pointless"; "use both" | C2 0.6x; C1 0.8x |
| **Silent save-bait list** | A list worth saving | One title over b-roll or flipping cards; the list in the frame or the caption; the keyword in the caption; 6 to 15 s | C2 72.0x, 61.3x, 34.4x; C1 32.2x, 23.9x |
| **Silent POV skit** | A relatable pain | A POV line over escalating shot sizes; tips in the caption | C2 R15 430.7x (pinned) |

---

## 8. Hooks

**Formulas by source.**

| Formula | Fits when | Result |
|---|---|---|
| "Someone built a free open source version of [paid brand], and it still does the part people actually pay for" | A free clone of a known paid tool | 36.4x, but 0.52x and 0.6x when reused |
| "[Brand] just [violent or news verb]" | A launch or a rivalry | 63.1x |
| "[Brand] just announced / is giving away" | Official news or an offer | 62.2x |
| "[Tool] just got 10 times better, because..." | A combination of tools | 27.7x |
| Disbelief: "I can't believe this is real" | A viral visual result | 33.6x |
| "X just killed Y. Well, that's what everyone's saying." | A hype wave to deflate | 14.8x |
| "You can now / Claude can now..." | A new capability | 9.3x; 14.6x. Across C2's 10 reliable ones, 0.4x to 9.3x |
| "Someone has just built..." | A new repo by an unknown author | 13.6x, then 1.1x word for word |
| Money or stakes | A price change | 5.6x |
| Pain first | A cost or a waste | 4.3x |
| "If you're using X, [N things / a loss]" | A list for current users | 2.0x to 3.0x |
| "The man who built X says..." | An authority's rule | 2.2x |
| Number or format first | A list | 3.9x |
| "Did you know" / "Most people" / story openers | | Weak |

**What the strongest openings share (both creators).**
1. **A wide desire, stated in sentence one.** That means the usage limit, a free version of a paid tool, games,
   money, a career, or "improve itself". C2's spoken hooks with "free" have a median of 1.26x over 15 reels, against
   0.93x over 45 without.
2. **A picture of a conflict or a contrast, with recognisable entities, at frame 0.** CEO faces and logos, a paid
   brand against Free, famous game covers, the Claude Code splash.
3. **A number or a visible change in the first second:**
   - C1: the dunk at 1.03, the strike at 0.93;
   - C2: a counter racing to 1,284, "$18,000" struck to "$0", "10" ticking to "11" on frame 5.
4. **Motion on frame 0.**
5. **An open question that keeps working:** "the biggest problem", the never-named repo, "how is that possible", "is
   the hype real".

**What the weakest share.**
1. A narrow job: LinkedIn growth, a YouTube channel, app cloning, meta ads (C2 0.2x to 0.7x, though often with 10%+
   comment rates).
2. A number with no result ("69,000 stars", C1 MONTAGE).
3. A false or abstract paradox ("nobody's actually using it", "the shape of writing").
4. A sentence the audience saw days before.
5. A pale, small or unreadable first frame (C1 APP, FINDER, HUMAN).
6. The answer given away in the first 1.3 to 4.3 s.
7. A promise the body breaks (C2 R17 says 15 and shows 5).

**Three cautions.**
- **The formula is not the cause.** The identical hook scored 13.6x and then 1.1x, and "You can now" reels range from
  0.4x to 9.3x. The topic and the moment decide.
- **A face at frame 0 does not predict reach.** C1 LIMIT and TRADE open with no face; C1 FINDER and MONTAGE open on the
  face and flopped.
- **What is spoken and what is written are often different hooks.** The caption line is often a second hook.

---

## 9. Retention devices

| Device | How it works | C1 | C2 |
|---|---|---|---|
| Motion on frame 0 | Something resolves or ticks within 5 frames | A full scene on frame 0 in 16 of 16 | Pixel resolve over frames 0 to 6; "10" to "11" on frame 5 |
| Racing counter that eases out | The viewer waits to see where it stops | Stars, money ($1,000 to $100,000), files (412 to 6), consoles (0 to 58) | 1,284 sessions; 4h 40m; 7.4 billion tokens |
| An open question left unnamed | The question works until it is paid off | "the biggest problem" 3.97 to 9.20 (LIMIT); "So how is that even possible?" (MELTY 7.13) | A typed URL cut off unfinished (R02 9.0 to 9.84); "I couldn't fit all 15" (R17) |
| A withheld name or answer | The comment is the only way in | CLIPS never names the repo (16.4% comments) | The guide is behind the keyword even when the URL is visible |
| A curiosity gap with a visible length | The answers are blurred and the count shown | Empty 20-slot grid (TOKENS) | Six blurred rows (R01 1.94); "?" tiles |
| Visible progress | The viewer always knows how far in they are | "NN / 20"; 0/4 to 4/4; 10 dots | Six dots; "MOD 01 / 05"; role checklists filling |
| Ranked loop, best last | A crown planted early, paid late | CLAUDE crown 7.06, paid 25.20 | "The last one" signpost |
| Same object before and after | Same window, wrong vs right | The LIMIT week card red, then green | "$40k?" vs a sourced "$48,000" (R02 44.34 to 47.35) |
| Mistake then fix | Red first, green after | LIMIT 14.00 to 16.23, then 28.13 | Bad call struck and retyped (R01 16.9 to 18.65) |
| Typed reveal, read-along | The exact words appear as they are said | The CLAUDE.md lines (LIMIT 19.87) | Every phrase typed (R01) |
| Self-identification roll call | One tile lifts while the rest dim: "is my job on the list?" | | R02 3.0 to 6.0 |
| The viewer's own data or habit | Prompts they have typed; their own files; their own habit acted out | The habit of grabbing skills from reels (FINDER) | Streamed prompts; a "Never opened" column (R03) |
| A checkable insider fact | A real path or number the viewer can verify | "61,608 stories" highlighted | `~/.claude/projects/<session-uuid>.jsonl` (8.47) |
| A pattern break | Colour, layout, face out or face back, a glitch | Paper to black at 1.93 (LIMIT); face only at 23.83 (CLIPS) | Face for the pain (13.88), full graphic for the reveal (20.92); glitch at 6.07 |
| A second hook mid-reel | "And what's even more insane" plus a colour change and a shock number | "This week..." news on the drop (GAMES) | R03 29.36 to 31.40 |
| An objection pre-empted | Kill the doubt before it forms | "it still does the part people actually pay for" | "which sounds like it can't be done" |
| An honesty or caveat beat | Trust before the ask | "Nobody posts the ones that lose" with a "-92%" draft deleted (TRADE) | "So just be careful what you point it at" (R01) |
| The beat drop at the turn | The kick enters on the story turn | 22.79 to 22.91 s in 12 of 16 | 18.78 to 18.79 s in 2 of 3 |
| A riser or silence into the CTA | Tension, then a dead stop on the cut | Riser in 12 of 16; silence in 3 | The music never changes at the CTA |
| A callback to the hook | The opening picture returns at the end | HUMAN's particle scene; FINDER's bookshelf to the librarian | |
| Recognisable big brands | Famous covers, logos, faces | 12 Steam covers; MrBeast and Hormozi thumbnails | Logos turning from grey to colour on each spoken name |
| Small jokes | The mascot falls asleep, peeks, gets banned | Banned mascot (CLAUDE); convict with a katana (APP) | The mascot falls asleep (R01 40.87) |
| A loop-friendly end | A closed mouth, no end card | Ends 0.1 to 0.4 s after the last word | R01 48.05 |

---

## 10. The kit: motion and graphic recipes with their timings

These are the small parts both creators recompose in every reel. With their measured timings, they are the
**allowed constant** for our engine. They are parts, never compositions. Frame counts are at 30 fps.

**Entries and exits**
- **Ghost-in:** a new element appears at about 30% opacity, often blurred, and resolves in 2 to 6 frames, with a
  10 to 30 px rise or a 95% to 100% scale (C1, every scene entry).
- **Panel scale-in:** from 92% in 2 frames (C2), or a card from 75% to 80% up to 100% in 6 to 8 frames with ease-out
  (C1 CLAUDE).
- **Spring pop:** an overshoot, then settle in 3 to 5 frames (85% to 105% to 100%); a whole stage 87% to 113% to
  100% in 9 frames (C1 MONTAGE frame 0).
- **Overshoot pill pop:** past 100%, tilted about -5°, over 5 frames (C2 "free").
- **Masked rise:** the title revealed from below in 3 to 4 frames (C2).
- **Word-by-word headline:** each word fades from grey or blur to solid in 4 to 6 frames, leading the voice by 0.5 to
  1.0 s (C2 R02).
- **Title morph to header:** the hook title shrinks to about 45% and slides to the top-left in 6 frames, linking the
  hook to the body (C2).
- **Clear and rebuild:** a hard cut to an empty panel for 6 frames, then a build over 12 to 15 frames (C2 item
  changes).
- **Exit rule:** the incoming element animates and the outgoing one just cuts away (C1 BOOK's decode).

**Text and input**
- **Typewriter at five speeds:**
  - about 10.5 characters a second, human speed, for a command the viewer must memorise (C2);
  - 15 to 22 cps, synced to speech, for words to copy (C1 LIMIT 21 to 22; C2 2 frames a character);
  - 26 to 30 cps for a tool cue or a terminal;
  - 50 to 57 cps for a session happening or a prompt running ahead of speech;
  - about 110 cps for the machine writing.
  - Monospace, with a blinking bar or a block cursor.
- **Enter press:** the return key turns red and the card gets an outline, in 8 to 10 frames (C2).
- **Synthetic cursor:** a macOS arrow on an eased path, gliding in 10 to 12 frames (or 0.67 s with ease-out), then
  a dwell and a click with a ripple or state change. It covers "install", "open", "pick", "follow" and "send" (C1 14
  of 16).
- **Tap ring:** a ring on a chip, and the chip turns orange with a check, about once every 0.9 s (C2 quiz feel).

**Numbers and states**
- **Count-up:** interpolated every frame, easing out over 18 to 47 frames. C2 R03 goes 1, 2, 5, 8, 14, 22 and
  31 over frames 8 to 20, then lands on 1,284 at 3.07 s.
- **Slot ticker:** one digit changes with a slot-machine feel ("10" to "11" on frame 5).
- **Stopwatch pill:** a fast timer that freezes and turns mint (C2), or a stopwatch equal to the video clock (C1
  TOKENS).
- **Colour state flip:** a pill or bar goes red, brown, green (or orange to red) in 2 to 3 frames.
- **Stamp:** large and faint down to final size, rotated -5° to -10°, in 2 to 4 frames, with a sub boom. Used for
  FREE, Approved, GUESSING, Never opened, NON-COMPLIANT and the prohibition sign.
- **Strike draw:** a red line drawn left to right in 3 to 6 frames, with rows 2 frames apart. Used for "Paid", "pay
  for API" and a deleted setup.
- **Strike to price:** "$18,000" struck, then "$0" (C2); a receipt itemised to "TOTAL $0.00" (both).
- **Progress to READY:** a bar fills to "READY ✓" in about 2 s (C2).
- **Toggle:** it turns green, the pill changes text, and an "✓ Automated" chip lands (C2).

**Real material**
- **Zoom to the word:** 1.6x to 2.5x in 4 to 12 frames inside a fixed card; a pan; a glow; a pull-out (section 5.2).
- **Highlighter sweep:** yellow, 3 to 24 frames. **Hand-drawn ellipse:** blue, 6 to 8 frames. **Synced word
  highlight** moving with the voice.
- **Linear push on a still:** 100% to 111.1% over 84 frames (C2).
- **Sticker cut-out:** a 5 px white outline on a cut-out head or product (C1).

**Structures inside a scene**
- **Item light-up:** inactive items sit at 30% to 35% opacity and each lights on its clause in 2 to 4 frames (C1).
- **Spotlight roll call:** one tile lifts to about 110% and tilts, the rest fade to 35%, and the label swaps, leading
  the spoken word by 0.4 to 0.5 s (C2).
- **Grid pop:** tiles scale up from 50% row by row, about 2 frames apart (C2); covers stagger about one a frame (C1).
- **Blurred list:** rows staggered every 3 frames, the text Gaussian-blurred (C2).
- **Card-to-checklist drop:** a finished card shrinks into its checklist row in about 6 frames, and the next card
  scales in (C2).
- **Magnifier sweep:** about 0.3 s per row; the matching card changes state (C2).
- **Hub wiring:** dotted cables extend clockwise and tiles go from grey to colour on each spoken name, all 8 in about
  1.3 s (C2).
- **Race bars:** one sprints to 100% in about 1 s while the other crawls to 12% (C2 "10x slower").
- **Report reveal:** rows reveal one by one while the stack reflows, flexbox style (C2).

**Transformations**
- **Card flip:** 2D, squeezing to a sliver in 2 frames and reopening in 5 (C2); 3D on the Y axis in 4 to 6 frames (C2,
  C1 MELTY).
- **Morph:** a terminal collapses into a .jsonl card in about 8 frames (C2); a highlight square grows into a code
  window in 10 frames (C1 GAMES); a chat stack squashes into a file card with a chime (C2).
- **Window-kept morph:** the old text blurs out, the background dissolves and the window stays, over about 10 frames
  (C2 fair before and after).
- **Canvas pan:** the whole canvas pans to the next card in 4 to 8 frames (C2).
- **Page peel:** a diagonal fold over 19 frames reveals the replacement page underneath (C1 BOOK).
- **Crack and dissolve; particle morph; puzzle assembly; gravity stack; tile burst; katana slash.** These are one-off
  metaphor devices, each built for the topic that needed it.

**Accents and life**
- **Colour wash:** the background washes to a new chapter colour in about 3 frames (C2).
- **Punch accent:** a word jumps to 125% to 140% for 1 to 2 frames, landing 0.06 to 0.1 s after the spoken word (C1
  DELETE).
- **Glitch:** an RGB split with pixel blocks for 5 frames, plus a hiss; it hides a jump cut (C2).
- **Pink wash:** 1 to 2 frames on entering a full graphic (C2).
- **Shake:** ±3° over 7 frames on "blew up" (C1).
- **Idle drift:** a 9 to 12 px rise per shot, a 96% to 100% scale, a 0.4° per second float, a 2.3 px per second grid,
  or a 0.3% to 0.45% per second push.
- **Hearts float** from the send button in about 1 s (C1 CTA).

---

## 11. Captions

| | C1 | C2 |
|---|---|---|
| System | **One style per layout.** On graphics: near-black heavy sans, 85 to 120 px, no box, centred under the card at y about 1000 to 1110, 1 to 2 words. On the face: white heavy sans at y about 1490 to 1663, 1 to 2 words. On the seam: white mono caps on a charcoal chip (63 to 88 px tall) or white lowercase in a translucent grey pill, 2 to 4 words | **One style everywhere.** White heavy sans, 55 to 70 px, in a dark rounded box at 70% to 75% opacity (radius 10 to 12, padding 20 to 25, height 86 to 108), on the seam at y about 884 to 992; on full face and full graphic at about 77% of the height |
| Chunking | The chunk grows a word, then resets ("If" > "If you're" > "like" > "like me") | Mean 1.8 words, never more than 3; 0.40 to 0.46 s a chunk; 108 to 132 chunks a reel |
| Emphasis | Value words switch to italic serif (earlier) or blue (recent); red for negation, orange for Claude, yellow for numbers | None |
| At the CTA | Removed in 14 of 15; only the keyword stays | Kept on every frame |
| Timing | Within 0 to 4 frames of the word | 0.0 to 0.2 s after the word, never ahead |

**Shared.** The position is fixed per layout. Captions land on the word. They are heavy sans in white or black. On
the split, the caption box doubles as the divider.

**Shared errors.** Auto-transcript slips get burned in: C1 "form rules" for "reels" and "AGENTSREACH,"; C2 "it out" for
"it at" and "slowerthan". Every caption must be checked against the script and the take.

---

## 12. Sound

**Shared.**
- One bed runs from frame 0 under a dry, close, compressed voice. C2 R01 measures -14.6 LUFS integrated, a
  loudness range of 3.1 LU and a true peak of -0.2 dBFS.
- **The drop marks the turn.** The kick enters on the story turn:
  - C1: 22.79 to 22.91 s at about 118 to 120 BPM in 12 of 16 reels. It is one house track, so the script's turn is
    built to land at 22.8 s. The bed then rises 8 to 10 dB, and the low band by 14 to 35 dB.
  - C2: 18.78 to 18.79 s at 107 BPM in 2 of 3. A structural turn sits 0.3 to 0.6 s before the first kick.
- Typing sounds are rare (none in 15 of C1's 16; quiet blips in one C2 reel), and so are whooshes on cuts.

**Different.**
- **C1 designs sound:**
  - a noise riser of 0.5 to 2.3 s into the CTA cut, stopped dead on the cut (12 of 16), or silence instead (3);
  - pitched "pops" of about 300 to 650 Hz, 9 to 19 dB over the bed, on reveals and state changes (13 of 16);
  - tonal hits on cuts that need weight;
  - impacts and sub booms on negations and slams;
  - narrative effects only where the metaphor calls for them (hammer thuds, a katana "shing", a notification ding, a
    success chime).
  - Bed level: 5 to 23 dB under the voice, median about 14.
- **C2 is mostly voice:**
  - the bed sits 8 to 38 dB under the voice, sometimes inaudible on a phone;
  - effects are few or none (R02 has none, checked band by band);
  - a sub boom marks the key reveal (R03 1.16 and 11.54);
  - the music never changes at the CTA.

**What this means for us.** The bed is a structural tool: its drop marks the turn. A fixed house track forces every
script's turn to the same second, which works against "every reel different". The better version is to pick and trim
the bed per reel, so its drop lands on that reel's own turn. Effects should only mark state changes, never
decorate.

---

## 13. The CTA

**Shared.**
- The ask is the last sentence and carries one keyword: the topic or its verb, in one word.
- The deliverable is named: "the link", "the full guide", "the complete setup", "all six as full prompts".
- The keyword is on screen and repeated in the post caption, and an automation sends the DM.
- Spoken templates:
  - C1: "[Make sure you're following / Save this video] and comment [KEYWORD] and I'll send you [the link / the GitHub
    repo / the full guide]."
  - C2: "If you comment [KEYWORD], I'll send you [the link and a full setup guide]."
- Timing:
  - C1: the last 1.87 to 5.0 s, after a hard cut.
  - C2: the ask starts at 94% to 96% of the runtime and lasts 2.4 to 4.4 s.

**The widgets.**
- **C1:** the keyword is typed into a mock Instagram comment box with his avatar, then "Post" turns into a check and
  hearts float. Later it became a two-step card ("1 Follow", clicked to "Following"; "2 Add a comment"
  typed). Later versions were a mock profile card and a static giant keyword.
- **C2:** the keyword in white curly quotes over the wall above his head, on a hard cut into a 1.13x to 1.185x
  full-face punch-in, with a defocus to sharp in R02. Before recent he used a one-frame light-leak flash
  into the uncropped frame. There are no arrows, URLs or end cards.

**What the comment rates say.**
1. **Withholding the thing drives comments.**
   - C1 CLIPS never names the repo: 16.4% comments.
   - C2's "the link" beats "the prompts you already saw": 3.9% to 4.7% against 1.9% (R01 shows all six
     phrases, then offers them).
2. **A setup tied to money or a big outcome pulls comments even with the repo visible:** C1 TRADE 8.6%, a YouTube
   agent setup 13.4%, a leads setup 18%.
3. **Narrow topics convert the few viewers they get:** C2 has 10% to 20% comment rates on 0.4x to 0.9x reels.
4. **The full payload on screen kills comments:** C1 TOKENS 0.85% (all 20 names shown), BOOK 0.9%, LIMIT 0.61%.
5. **Reusing a keyword lowers the rate:** CLIPS2 5.2% against CLIPS 16.4%.
6. **A mismatch splits the response:** C1 DELETE's voice says "Claude" while the screen says DELETE, and 9 of 15
   comments say "Claude".
7. **A late CTA is missed.** C1 LIMIT's ask starts at 35.27 s against a 24.6 s average watch.
8. **No keyword, no comments:** C2's reels without a keyword got 0 to 12 comments; a silent list with a caption
   keyword got 6,822.

**Our constraint.** No handle and no branding inside any video. So a CTA widget that shows a handle or a profile card
(C1's later versions) is out. C2's keyword title, or a comment box with no handle, fits.

---

## 14. Performance: what decides results

1. **The topic decides reach.**
   - Reels that promise a desire wider than the niche lead both accounts: the usage limit, free versions of paid
     tools, games, trading money, a career or a fellowship, "improve itself".
   - Narrow jobs flop on views: LinkedIn growth, YouTube channels, app cloning, deck design, meta ads.
2. **It must read in big type at frame 0, with recognisable brands.** That holds in all six of C2's top talking
   reels and C1's five biggest.
3. **Fresh news travels.** C1's three news reels rode stories under a week old.
4. **Craft holds viewers but does not create reach.**
   - C2's richest build (R18, 100% simulated UI) did 0.7x.
   - R02 had an above-median like rate at 1.0x.
   - In C1's reels, speech rate, event density and the share of real material do not separate hits from flops.
5. **Reuse decays.** Templates, hooks, keywords and topics all lose on the second run (section 4).
6. **Posting 2 to 3 a day splits the push.**
   - Six posts in four days sit at 0.4x to 1.1x.
   - Their like and comment rates were at or above his medians, so the people who saw them reacted normally. The
     failure was distribution.
7. **Silent save-bait lists are the biggest outliers for the least effort.**
   - C2: 72.0x, 61.3x and 34.4x; C1: 32.2x and 23.9x.
   - With a caption keyword they produce DMs.
8. **Reach and comments are separate outcomes.** C1 LIMIT reached the most people with the second-lowest comment rate.

**What this means for us.** The educational edit makes a reel understood and trusted. It does not make it travel. The
topic and the hook do. Topic choice lives upstream, in your scripting. This engine's
job is to make the best possible reel of the topic it is given.

---

## 15. Mistakes never to copy (each becomes a check in our engine)

Wrong or stale facts are left out on purpose: facts are free in this style.

**Craft**
- The voice and the picture disagree:
  - C1: "Opus 5.5" said while the cards say "Fable"; "all 40" said over a list of 32; the spoken keyword differs from
    the shown one.
  - C2: two different commands in one reel (R03 5.34 vs 40.24).
- Payoffs hidden behind the caption box (C2 R01 11.45, 19.09, 25.53).
- Caption typos left on screen (both).
- Bugs in reused modules:
  - a wrong logo (Gmail on Google One);
  - text overflowing its box;
  - a stray black dot;
  - a highlight 40 px off its target;
  - a black strip on the first frame of a switch;
  - an empty glyph square;
  - a card arriving 10 frames late (all C1).
- A visible one-frame jump in a retimed recording (C2 R02).
- Someone else's account visible in a recording (C2 R19).
- Real logos for some brands and letter placeholders for others in the same grid (C2 R02).
- A list item that never gets its highlight (C2 R02, Legal).

**Strategy**
- Giving the name or the answer away early in a comment-gated reel (C1 BOOK 1.33 s, MONTAGE 4.2 s).
- Showing the whole payload, then offering it (C2 R01, C1 TOKENS).
- Repeating a template within 24 hours (C1 VOICE then BOOK).
- Reusing keywords and topics.
- Posting 3 a day.
- A CTA that starts after the average viewer has left.
- Never showing the core output (C1 VOICE, MONTAGE, APP).
- An uncredited clip, or crediting a reposter instead of the original creator (C1 CLIPS2, MELTY).

---

## 16. C1 vs C2: the real differences, and what each choice buys

| Dimension | C1 | C2 | What it buys, and when |
|---|---|---|---|
| Length | 26 to 40 s | 44 to 60 s (up to 82) | Short for one idea; long for several items or a setup. Length should follow the item count, never a target |
| Layout rhythm | Strict alternation: the layout changes every sentence | Split dominant (61% to 91% in the decodes), with the panel changing inside it | Alternation gives pattern breaks; a dominant split keeps the face's trust and a steady reading place. Choose by how much there is to show per line |
| Captions | A style per layout, emphasis words, gone at the CTA | One style, no emphasis, always on | Emphasis guides the eye to the value word; one style is calmer and never fights the panel |
| Sound | Designed: riser, pops, impacts | Mostly voice | Designed sound marks state changes and builds into the ask; voice-only keeps it intimate. Both drop the kick on the turn |
| Real material | Uses third-party clips, posts, papers and photos where they prove | Almost none by recent; real names inside mocks | C1's GAMES and TRADE show real material holding a reel up; C2 shows mocks can carry a 9.3x reel when the vocabulary is real |
| World per reel | Several kits running side by side in one week | One world per reel from its name or brand | C2's per-reel world is the purer form of "every reel different" |
| Invented example | Scenario-level props | One fictional user whose numbers reconcile across the whole reel | C2's reconciled user makes the proofs pay off the setup |
| CTA widget | Typed comment box, later with Follow | Keyword in quotes above the head | C2's fits our no-handle rule as it is |
| Density | 1.3 to 3.5 graphic events a second | A panel change every 0.2 to 0.5 s; 23 to 29 edit points a minute | Both are dense; neither lets a scene sit |
| Cadence | Up to 3 a day, and it hurt | About 1 every 2 days | Fewer, better reels |

---

## 17. What this means for the engine

From the study, it needs these parts:

**A. A material pack per reel.**
- The real things the reel can show: logos, pages, talks, products, file formats, the real output of the tool.
- Every source URL kept for the credits. Facts themselves are free, so there is no fact check.

**B. A script check for the picture.** It runs before or after recording. It checks that:
- every sentence carries a noun a scene can show;
- there is a clear turn for the drop to land on;
- the keyword is the last sentence;
- the deliverable is not given away on screen;
- the numbers on screen match the numbers said.

**C. An edit plan per reel: the bespoke layer, derived, never picked.**
- The structure follows the topic's shape.
- The world and metaphor come from its nouns and name, the palette from its brand or chapters.
- Each line gets a material tier (A to D, section 5.1), a device chosen by its claim type, and a layout chosen by
  its job.
- The plan also fixes the frame 0 picture, where the turn and the drop land, and the CTA.
- **A novelty ledger** keeps what the recent reels used (structures, worlds, palettes, metaphors, hook sentences,
  keywords), so nothing is reused.

**D. A renderer that builds scenes as code.**
- Scenes are written in HTML, CSS and JS or React, and rendered frame-exact to 1080x1920 video.
- The kit of small parts (section 10) comes with its measured timings as defaults.
- Every composition is written fresh for its reel.
- Which renderer to use (Remotion, HyperFrames or our own capture of HTML) is chosen at design time, after checking
  its licence and how well it fits.

**E. Real material tools.**
- Logged-out page captures with scripted scroll and zoom-to-word paths.
- GitHub API and README fetches for exact names and counts.
- The official demo GIF or video, and clip downloads with a credit chip.
- Brand logos from press pages.
- A short real screen recording when "it is easy" must be believed.
- The real output of the tool wherever it exists: the generated clip, the cloned voice.

**F. Timing from the take.**
- Word timings come from the recording, and every pause is cut.
- Scenes sit on the cut points, and state changes sit on single words.

**G. Captions.** Built from the word timings, corrected against the script, sitting in a fixed band that every panel
leaves clear.

**H. Sound.**
- A bed picked per reel, with its drop placed on the turn.
- A small set of effects for state changes only.
- One loudness target for the voice.

**I. Quality checks.** Section 15 becomes automatic checks, plus a frame-by-frame read of the render:
- spoken against shown (numbers, names, the keyword);
- the keyword the same everywhere;
- the caption band clear;
- credits present;
- nothing still for more than 10 frames;
- no layer bugs on first frames.

**J. What it asks of the speaker when recording.**
- **No prompter needed.** One sitting, line by line if you like, because every pause is cut.
- **Framing:** chest-up, eyes a little below the middle of the frame, camera locked. That one framing works for the
  split, the full face and the full graphic, since the split only hides the top of the frame.
- **A separate take for the CTA** is fine and common.
- Both reference creators hold a mic in hand on camera. That is a look, not a need.
