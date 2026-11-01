// The educational kit: the constant layer and the small parts every reel recomposes.
// A reel's composition (its own scenes.js) registers scenes; the renderer calls EDU.seek(t) for every frame.
// Every visual is a pure function of time, so any frame can be rendered alone and in any order.
(function () {
  const E = (window.EDU = { W: (window.FRAME || {}).w || 1080, H: (window.FRAME || {}).h || 1920, FPS: 30, scenes: [], words: [], chunks: [], cur: null });

  // ---------- math ----------
  E.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  E.lerp = (a, b, k) => a + (b - a) * k;
  E.ease = {
    lin: t => t,
    out: t => 1 - Math.pow(1 - t, 3),
    out5: t => 1 - Math.pow(1 - t, 5),
    inOut: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    in: t => t * t * t,
    back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    backBig: t => { const c1 = 2.8, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  };
  // progress of t through [a, a+dur], eased
  E.p = (t, a, dur, e = 'out') => E.ease[e](E.clamp((t - a) / Math.max(1e-6, dur)));

  // ---------- DOM ----------
  E.el = (tag, cls, parent, css, html) => {
    const d = document.createElement(tag);
    if (cls) d.className = cls;
    if (css) Object.assign(d.style, css);
    if (html != null) d.innerHTML = html;
    if (parent) parent.appendChild(d);
    return d;
  };
  E.svgNS = 'http://www.w3.org/2000/svg';
  E.svg = (parent, w, h, css, inner = '') => {
    const s = document.createElementNS(E.svgNS, 'svg');
    s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`);
    s.style.position = 'absolute'; s.style.overflow = 'visible';
    if (css) Object.assign(s.style, css);
    s.innerHTML = inner;
    if (parent) parent.appendChild(s);
    return s;
  };
  // ---------- sound events ----------
  // Every kit motion tags the value it returns with what it is ({k: 'fly', t0, dur, ...}). During the renderer's
  // sound sweep (E.SND.on) E.apply records each tagged motion once, with where its element lands on screen, so
  // tools/sound.py can give every visible motion its own sound, on its own frame, panned where it happens.
  E.SND = { on: false, ev: new Map(), n: 0 };
  E.now = 0; E.lt = 0; E.sFrom = 0; E.sId = '';
  const visible = el => {
    let a = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      a *= +cs.opacity;
    }
    return a;
  };
  E.rec = (key, ev, el) => {
    if (!E.SND.on) return;
    key = E.sId + '|' + key;
    const cur = E.SND.ev.get(key);
    const land = ev.t0 + (ev.dur || 0);
    if (cur && (cur.done || E.lt > land + 0.04)) return;
    if (!cur && E.lt > land + 0.07) return;          // a motion that finished before its element was drawn
    const o = { ...ev, g0: E.sFrom + ev.t0, scene: E.sId };
    if (el) {
      const r = el.getBoundingClientRect();
      o.x = r.x + r.width / 2; o.y = r.y + r.height / 2; o.w = r.width; o.h = r.height; o.vis = visible(el);
    }
    o.done = E.lt >= land - 1e-6;
    E.SND.ev.set(key, Object.assign(cur || {}, o));
  };
  const elId = el => el.__sid || (el.__sid = ++E.SND.n);
  E.tag = (v, k, t0, extra = {}) => { v._ev = [...(v._ev || []), { k, t0, ...extra }]; return v; };

  // apply a motion value {o, x, y, s, sx, sy, r, blur} to an element
  E.apply = (el, v) => {
    if (E.SND.on && v._ev) v._ev.forEach(ev => E.rec(`${ev.k}|${elId(el)}|${ev.t0.toFixed(3)}`, ev, el));
    const o = v.o == null ? 1 : v.o;
    el.style.opacity = o;
    el.style.visibility = o <= 0.001 ? 'hidden' : 'visible';
    const p3 = v.rx || v.ry ? `perspective(1400px) rotateX(${v.rx || 0}deg) rotateY(${v.ry || 0}deg) ` : '';
    el.style.transform = `translate(${v.x || 0}px, ${v.y || 0}px) ${p3}rotate(${v.r || 0}deg) scale(${(v.s == null ? 1 : v.s) * (v.sx || 1)}, ${(v.s == null ? 1 : v.s) * (v.sy || 1)})`;
    el.style.filter = v.blur ? `blur(${v.blur}px)` : 'none';
  };
  E.mix = (...vs) => vs.reduce((a, v) => ({
    o: (a.o == null ? 1 : a.o) * (v.o == null ? 1 : v.o), x: (a.x || 0) + (v.x || 0), y: (a.y || 0) + (v.y || 0),
    s: (a.s == null ? 1 : a.s) * (v.s == null ? 1 : v.s), r: (a.r || 0) + (v.r || 0), blur: (a.blur || 0) + (v.blur || 0),
    sx: (a.sx || 1) * (v.sx || 1), sy: (a.sy || 1) * (v.sy || 1), rx: (a.rx || 0) + (v.rx || 0), ry: (a.ry || 0) + (v.ry || 0),
    ...(a._ev || v._ev ? { _ev: [...(a._ev || []), ...(v._ev || [])] } : {}),
  }), {});

  // ---------- motion values (the kit's measured timings, GRAMMAR section 10) ----------
  // ghost-in: from ~30% opacity with blur and a small rise, 2 to 6 frames
  E.inV = (t, t0, { dur = 0.12, dy = 30, blur = 10, s0 = 0.96 } = {}) => {
    if (t < t0) return { o: 0 };
    const k = E.p(t, t0, dur);
    return E.tag({ o: 0.3 + 0.7 * k, y: (1 - k) * dy, blur: (1 - k) * blur, s: E.lerp(s0, 1, k) }, 'in', t0, { dur });
  };
  // spring pop: overshoot then settle
  E.popV = (t, t0, { dur = 0.16, s0 = 0.5 } = {}) => {
    if (t < t0) return { o: 0 };
    const k = E.clamp((t - t0) / dur);
    return E.tag({ o: E.clamp(k * 3), s: E.lerp(s0, 1, E.ease.back(k)) }, 'pop', t0, { dur, s0 });
  };
  // stamp: large and faint down to size, rotated
  E.stampV = (t, t0, { r = -7, dur = 0.08, s0 = 1.9 } = {}) => {
    if (t < t0) return { o: 0 };
    const k = E.p(t, t0, dur, 'out5');
    return E.tag({ o: E.clamp(0.25 + k), s: E.lerp(s0, 1, k), r }, 'stamp', t0, { dur, s0 });
  };
  // out: fade and drop away
  E.outV = (t, t0, { dur = 0.12, dy = -18 } = {}) => {
    if (t < t0) return {};
    const k = E.p(t, t0, dur);
    return E.tag({ o: 1 - k, y: k * dy }, 'out', t0, { dur });
  };
  // fly in from an offset with a tilt, landing with a small overshoot (card in from top right, 4 frames)
  E.flyV = (t, t0, { x = 0, y = 0, r = 0, rx = 0, ry = 0, s0 = 0.6, dur = 0.14 } = {}) => {
    if (t < t0) return { o: 0 };
    const k = E.clamp((t - t0) / dur), e = E.ease.back(k), q = 1 - E.ease.out5(k);
    return E.tag({ o: E.clamp(k * 4), x: x * q, y: y * q, r: r * q, rx: rx * q, ry: ry * q, s: E.lerp(s0, 1, e) }, 'fly', t0, { dur, dx: x, dy: y, s0 });
  };
  // screen shake that dies away (impacts, slams)
  E.shakeV = (t, t0, { dur = 0.22, amp = 12 } = {}) => {
    if (t < t0 || t > t0 + dur) return {};
    const k = 1 - (t - t0) / dur, ph = (t - t0) * 60;
    return E.tag({ x: Math.sin(ph * 1.7) * amp * k, y: Math.cos(ph * 2.3) * amp * k * 0.7, r: Math.sin(ph * 1.1) * 0.6 * k }, 'shake', t0, { dur: 0, amp });
  };
  // punch: a quick scale bump on a word (125 to 140% for 1 to 2 frames, back in about 3)
  E.punchV = (t, t0, { amt = 0.18, dur = 0.14 } = {}) => {
    if (t < t0 || t > t0 + dur) return {};
    const k = (t - t0) / dur;
    return E.tag({ s: 1 + amt * (k < 0.25 ? k / 0.25 : 1 - E.ease.out((k - 0.25) / 0.75)) }, 'punch', t0, { dur: 0.03, amt });
  };
  // camera: keyframes [time, dur, {s, fx, fy}] put the focus point (content px) at the viewport point (cx, cy)
  E.camAt = (t, keys, { cx = 540, cy = 470 } = {}) => {
    let cur = Object.assign({ s: 1, fx: cx, fy: cy }, keys[0][2]);
    for (let i = 1; i < keys.length; i++) {
      const [t0, dur, tgt] = keys[i]; if (t < t0) break;
      const k = dur > 0 ? E.p(t, t0, dur, keys[i][3] || 'out5') : (t >= t0 ? 1 : 0);
      const nxt = Object.assign({}, cur, tgt);
      if (E.SND.on && !(keys.__quiet)) E.rec(`cam|${t0.toFixed(3)}|${JSON.stringify(tgt)}`, { k: 'cam', t0, dur, s0: cur.s, s1: nxt.s, d: Math.hypot((nxt.fx - cur.fx) * nxt.s, (nxt.fy - cur.fy) * nxt.s), x: cx }, null);
      cur = { s: E.lerp(cur.s, nxt.s, k), fx: E.lerp(cur.fx, nxt.fx, k), fy: E.lerp(cur.fy, nxt.fy, k) };
    }
    // never a sideways move: the camera only zooms and rises or falls, its focus held on the frame's centre line
    if (!E.allowPan) cur.fx = cx;
    // where a content point (X, Y) sits on screen, relative to the camera's box
    cur.at = (X, Y) => [cx + (X - cur.fx) * cur.s, cy + (Y - cur.fy) * cur.s];
    return cur;
  };
  E.camV = (t, keys, o = {}) => {
    const { cx = 540, cy = 470 } = o, c = E.camAt(t, keys, o);
    return `translate(${cx - c.fx * c.s}px, ${cy - c.fy * c.s}px) scale(${c.s})`;
  };
  // a hand-drawn ellipse that draws itself (blue loop around the number, 6 to 8 frames)
  E.scribble = (parent, cx, cy, rx, ry, { color = '#4A9EE7', width = 7, seed = 1 } = {}) => {
    // the svg sits on the ellipse's own box, so its position (and the sound's pan) is where the ring is drawn
    const pad = width + 6, ox = cx - rx * 1.1 - pad, oy = cy - ry * 1.1 - pad;
    const s = E.svg(parent, Math.round(rx * 2.2 + pad * 2), Math.round(ry * 2.2 + pad * 2), { left: ox + 'px', top: oy + 'px', overflow: 'visible' });
    let d = '';
    for (let i = 0; i <= 40; i++) {
      const a = -Math.PI * 0.6 + (i / 40) * Math.PI * 2.15, w = 1 + 0.06 * Math.sin(i * 1.7 + seed);
      d += (i ? 'L' : 'M') + (cx - ox + Math.cos(a) * rx * w).toFixed(1) + ' ' + (cy - oy + Math.sin(a) * ry * w).toFixed(1);
    }
    s.innerHTML = `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
    const p = s.firstChild, L = p.getTotalLength();
    p.setAttribute('stroke-dasharray', `${L} ${L}`); p.setAttribute('stroke-dashoffset', String(L));
    return { el: s, draw: k => { if (k > 0 && k < 1) E.rec(`draw|${elId(s)}`, { k: 'draw', t0: E.lt, dur: 0, len: L }, s); p.setAttribute('stroke-dashoffset', String(L * (1 - E.clamp(k)))); } };
  };
  // a headline whose words land one by one on their spoken words (each a quick pop)
  E.slamLine = (parent, words, css) => {
    const d = E.el('div', 'abs', parent, css);
    const spans = words.map(w => E.el('span', '', d, { display: 'inline-block', marginRight: '0.22em', transformOrigin: '50% 80%' }, w));
    return { el: d, tick: (t, times) => spans.forEach((sp, i) => E.apply(sp, E.inV(t, times[i], { dur: 0.3, dy: 12 }))) };
  };

  // idle drift so a still is never still (cards rise ~10 px a shot, scale 0.3% a second)
  E.driftV = (t, { px = 10, len = 3, zoom = 0.004 } = {}) => ({ y: -px * E.clamp(t / len), s: 1 + zoom * t });
  E.bob = (t, amp = 4, hz = 1.4, ph = 0) => Math.sin((t * hz + ph) * Math.PI * 2) * amp;

  // ---------- text ----------
  // o.machine: Claude or a program printing (soft ticks, not a person's keystrokes); o.silent: no sound
  E.type = (t, t0, text, cps = 22, o = {}) => {
    if (t >= t0 && E.SND.on && text.length > 1 && !o.silent) E.rec(`type|${t0.toFixed(3)}|${text.slice(0, 24)}`, { k: 'type', t0, dur: text.length / cps, n: text.length, cps, machine: !!o.machine }, null);
    return t < t0 ? '' : text.slice(0, Math.floor((t - t0) * cps));
  };
  E.typed = (t, t0, text, cps = 22) => t >= t0 + text.length / cps;
  E.num = (t, t0, dur, a, b, e = 'out') => {
    if (t >= t0 && E.SND.on && a !== b) E.rec(`count|${t0.toFixed(3)}|${a}|${b}`, { k: 'count', t0, dur, a, b, e }, null);
    return E.lerp(a, b, E.p(t, t0, dur, e));
  };
  E.fmt = n => Math.round(n).toLocaleString('en-US');
  E.caretOn = (t, hz = 2.2) => Math.floor(t * hz * 2) % 2 === 0;

  // ---------- pixel sprites ----------
  // rows of characters; pal maps a character to a colour; each cell is uw x uh units
  E.sprite = (rows, pal, uw = 1, uh = 1) => {
    let r = '';
    rows.forEach((row, y) => [...row].forEach((c, x) => {
      if (pal[c]) r += `<rect x="${x * uw}" y="${y * uh}" width="${uw + 0.02}" height="${uh + 0.02}" fill="${pal[c]}"/>`;
    }));
    return { inner: r, w: rows[0].length * uw, h: rows.length * uh };
  };
  // Clawd, the Claude Code mascot, from its terminal block art (quadrant cells are 1 wide, 2 tall)
  E.CLAWD = ['...############...', '...##E######E##...', '.################.', '...############...', '....#.#....#.#....'];
  E.CLAWD_BLINK = ['...############...', '...############...', '.################.', '...############...', '....#.#....#.#....'];
  E.clawd = (parent, { x = 0, y = 0, w = 180, color = '#D77757', eye = '#141413', css = {} } = {}) => {
    const sp = E.sprite(E.CLAWD, { '#': color, E: eye }, 1, 2);
    const blink = E.sprite(E.CLAWD_BLINK, { '#': color }, 1, 2);
    const h = (w * sp.h) / sp.w;
    const wrap = E.el('div', 'abs', parent, Object.assign({ left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px' }, css));
    const s = E.svg(wrap, w, h, { left: 0, top: 0 });
    s.setAttribute('viewBox', `0 0 ${sp.w} ${sp.h}`); s.setAttribute('class', 'px');
    const xe = (cx) => `<path d="M${cx - 0.75} 1.9 L${cx + 0.75} 4.1 M${cx + 0.75} 1.9 L${cx - 0.75} 4.1" stroke="${eye}" stroke-width="0.45" stroke-linecap="round"/>`;
    s.innerHTML = `<g class="open">${sp.inner}</g><g class="shut" style="display:none">${blink.inner}</g><g class="dead" style="display:none">${blink.inner}${xe(5.5)}${xe(12.5)}</g>`;
    return {
      el: wrap, w, h,
      // blink every ~2.6 s for 2 frames (phase per mascot), bob a little
      tick(t, { bob = 3, ph = 0, blinkEvery = 2.6, dead = false } = {}) {
        const cyc = ((t + ph) % blinkEvery + blinkEvery) % blinkEvery;
        const shut = cyc < 0.07 && !dead;
        s.querySelector('.open').style.display = shut || dead ? 'none' : '';
        s.querySelector('.shut').style.display = shut ? '' : 'none';
        s.querySelector('.dead').style.display = dead ? '' : 'none';
        if (dead) return {};
        return { y: E.bob(t, bob, 1.1, ph) };
      },
    };
  };
  E.SPRITES = {
    bug: ['..#....#..', '...#..#...', '.########.', '#.#EE#EE.#', '..######..', '#.######.#', '..######..', '.#.####.#.', '#...##...#'],
    magnifier: ['...####....', '..#....#...', '.#......#..', '.#......#..', '.#......#..', '..#....#...', '...####.#..', '........#..', '.........#.', '..........#'],
    toolbox: ['....######....', '....#....#....', '##############', '#............#', '#....####....#', '##############', '#............#', '#............#', '##############'],
    note: ['#########', '#.......#', '#.#####.#', '#.......#', '#.####..#', '#.......#', '#.#####.#', '#.......#', '#########'],
  };
  E.pix = (parent, name, { x = 0, y = 0, cell = 10, pal = {}, css = {} } = {}) => {
    const sp = E.sprite(E.SPRITES[name], pal, 1, 1);
    const s = E.svg(parent, sp.w * cell, sp.h * cell, Object.assign({ left: x + 'px', top: y + 'px' }, css));
    s.setAttribute('viewBox', `0 0 ${sp.w} ${sp.h}`); s.setAttribute('class', 'px');
    s.innerHTML = sp.inner;
    return s;
  };

  // ---------- icons ----------
  E.ICON = {
    check: (c = '#fff', bg = '#2E9B5B') => `<svg viewBox="0 0 40 40" width="100%" height="100%"><circle cx="20" cy="20" r="20" fill="${bg}"/><path d="M11 20.5l6 6 12-13" stroke="${c}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    cross: (c = '#fff', bg = '#D6453D') => `<svg viewBox="0 0 40 40" width="100%" height="100%"><circle cx="20" cy="20" r="20" fill="${bg}"/><path d="M13 13l14 14M27 13l-14 14" stroke="${c}" stroke-width="5" stroke-linecap="round"/></svg>`,
    box: (c = '#141413') => `<svg viewBox="0 0 40 40" width="100%" height="100%"><rect x="3" y="3" width="34" height="34" rx="8" fill="none" stroke="${c}" stroke-width="4"/></svg>`,
    cursor: () => `<svg viewBox="0 0 28 40" width="100%" height="100%"><path d="M2 2 L2 32 L9.5 25 L14.5 37 L19.5 35 L14.5 23.5 L25 23.5 Z" fill="#111" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/></svg>`,
    folder: (c = '#D9A441') => `<svg viewBox="0 0 48 40" width="100%" height="100%"><path d="M2 8a4 4 0 0 1 4-4h12l5 5h19a4 4 0 0 1 4 4v21a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4z" fill="${c}"/><path d="M2 14h44v19a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4z" fill="${c}" opacity=".75"/></svg>`,
    file: (c = '#fff', fold = '#ddd') => `<svg viewBox="0 0 36 44" width="100%" height="100%"><path d="M2 4a3 3 0 0 1 3-3h18l11 11v29a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3z" fill="${c}"/><path d="M23 1v11h11" fill="${fold}"/></svg>`,
  };

  // ---------- captions (constant 2: one style, one place per layout) ----------
  // chunks: [{text, s, e}] built from the reel's corrected words: 1 to 3 words, short, broken at punctuation
  E.buildChunks = (words, { maxWords = 3, maxChars = 16, maxDur = 0.62 } = {}) => {
    const out = []; let cur = null;
    words.forEach((w, i) => {
      const brk = cur && (cur.n >= maxWords || (cur.text + ' ' + w.w).length > maxChars || w.e - cur.s > maxDur || /[.,?!:]$/.test(cur.text) || w.s - cur.e > 0.25 || w.newChunk);
      if (!cur || brk) { if (cur) out.push(cur); cur = { text: w.w, s: w.s, e: w.e, n: 1 }; }
      else { cur.text += ' ' + w.w; cur.e = w.e; cur.n++; }
    });
    if (cur) out.push(cur);
    out.forEach((c, i) => { const nx = out[i + 1]; c.until = nx ? Math.min(nx.s, c.e + 0.6) : c.e + 0.5; });
    return out;
  };

  // ---------- the frame ----------
  E.init = ({ faceDir, nFace, words, capWords, splitShift = 470, seam = 945, card = null, matteDir = null }) => {
    E.faceDir = faceDir; E.nFace = nFace; E.words = capWords || words; E.splitShift = splitShift; E.seam = seam;
    // the card layout: the graphic owns the top of a dark canvas
    // and the speaker sits small in a rounded card on the bottom edge, the head rising out over the card's top edge
    // (tools/matte.py gives the matte). Card x 207 to 864, top y 1262, corner radius 30;
    // the take sits in it at 0.66.
    E.card = Object.assign({ x: 207, y: 1262, w: 657, r: 30, s: 0.66, ox: 151, oy: 839 }, card || {});
    E.matteDir = matteDir;
    E.capY = Object.assign({ card: 1090, gfx: 1484, face: 1484 }, window.CAPY || {});
    E.chunks = E.buildChunks(capWords || words, window.CHUNKS || {});
    const f = E.el('div', '', document.body); f.id = 'frame';
    E.face = E.el('img', '', f); E.face.id = 'face';
    // the safe zone: tall phones crop the sides of a reel, so the graphic is drawn at E.safe of its
    // size about its centre and the backdrop (the scene's colour, or window.BACKDROP) fills the margins
    E.safe = window.SAFE == null ? 0.86 : window.SAFE;
    E.back = E.el('div', '', f, { position: 'absolute', left: '0', top: '0', width: '1080px' });
    E.stage = E.el('div', '', f); E.stage.id = 'stage';
    E.over = E.el('div', '', f); E.over.id = 'over';
    // the cinematic finish over the graphic: a soft vignette and a fine grain that changes every frame
    E.fx = E.el('div', '', f); E.fx.id = 'fx';
    // a reel on a light canvas sets window.FINISH = { vig: 0.12 }: the dark vignette reads as grey corners on cream
    const fin = Object.assign({ vig: 0.42, grain: 0.07 }, window.FINISH || {});
    E.vig = E.el('div', '', E.fx, { position: 'absolute', inset: '0', background: `radial-gradient(ellipse 75% 70% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,${fin.vig}) 100%)` });
    const gc = document.createElement('canvas'); gc.width = gc.height = 256;
    const g = gc.getContext('2d'), id = g.createImageData(256, 256);
    let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (rnd() - 0.5) * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    g.putImageData(id, 0, 0);
    E.grain = E.el('div', '', E.fx, { position: 'absolute', inset: '0', backgroundImage: `url(${gc.toDataURL()})`, opacity: String(fin.grain), mixBlendMode: 'overlay' });
    // the face card: one canvas over the graphic (the card, then the matted head where it rises above the card)
    E.cardCv = E.el('canvas', '', f, { position: 'absolute', left: '0', top: '0', display: 'none' });
    E.cardCv.width = E.W; E.cardCv.height = E.H; E.cardCv.id = 'card';
    E.popCv = document.createElement('canvas'); E.popCv.width = E.W; E.popCv.height = E.H;
    E.matte = new Image();
    E.cap = E.el('div', '', f); E.cap.id = 'cap';
  };

  // draw the face card for this frame: fx {blur, o, dy} lets a scene blur it through a transition
  E.drawCard = (fx = {}) => {
    const C = E.card, ctx = E.cardCv.getContext('2d'), fw = E.W * C.s, fh = E.H * C.s, oy = C.oy + (fx.dy || 0), y = C.y + (fx.dy || 0);
    ctx.clearRect(0, 0, E.W, E.H);
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(C.x, E.H + 40); ctx.lineTo(C.x, y + C.r); ctx.arcTo(C.x, y, C.x + C.r, y, C.r);
    ctx.lineTo(C.x + C.w - C.r, y); ctx.arcTo(C.x + C.w, y, C.x + C.w, y + C.r, C.r); ctx.lineTo(C.x + C.w, E.H + 40); ctx.closePath();
    ctx.clip();
    ctx.drawImage(E.face, C.ox, oy, fw, fh);
    ctx.restore();
    if (E.matteDir && E.matte.complete && E.matte.naturalWidth) {
      const p = E.popCv.getContext('2d');
      p.globalCompositeOperation = 'source-over'; p.clearRect(0, 0, E.W, E.H);
      p.drawImage(E.face, C.ox, oy, fw, fh);
      p.globalCompositeOperation = 'destination-in';
      p.drawImage(E.matte, C.ox, oy, fw, fh);
      p.globalCompositeOperation = 'source-over';
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, E.W, y + C.r + 2); ctx.clip();
      ctx.drawImage(E.popCv, 0, 0);
      ctx.restore();
    }
    E.cardCv.style.opacity = fx.o == null ? 1 : fx.o;
    E.cardCv.style.filter = fx.blur ? `blur(${fx.blur.toFixed(1)}px)` : '';
  };

  // scene: {id, from, to, layout: 'split'|'gfx'|'face', bg, build(stage, S) -> refs, tick(refs, t, S), faceScale}
  E.scene = def => {
    const S = Object.assign({ layout: 'split', bg: '#000' }, def);
    // local time of the n-th spoken word matching `w` inside this scene (or the whole reel if not inside)
    S.w = (w, n = 1) => {
      const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
      const hits = E.words.filter(x => norm(x.w) === norm(w) && x.s >= S.from - 0.05 && x.s < S.to);
      const h = hits[n - 1] || hits[0];
      if (!h) throw new Error(`scene ${S.id}: word "${w}" not found`);
      return h.s - S.from;
    };
    S.we = (w, n = 1) => { const st = S.w(w, n) + S.from; const h = E.words.find(x => Math.abs(x.s - st) < 1e-6); return h.e - S.from; };
    E.scenes.push(S);
    return S;
  };

  E.layoutAt = (S, lt) => (typeof S.layout === 'function' ? S.layout(lt) : S.layout);

  E.seek = async t => {
    E.now = t;
    const fi = E.clamp(Math.round(t * E.FPS) + 1, 1, E.nFace);
    // E.faceSrc (optional): a composition that cuts one take into variants maps its frame numbers to the take's
    const src = E.faceSrc ? E.faceSrc(fi) : `${E.faceDir}/${String(fi).padStart(5, '0')}.jpg`;
    if (E.face.getAttribute('src') !== src && !E.SND.on) { E.face.src = src; await E.face.decode().catch(() => {}); }
    const S = E.scenes.find(s => t >= s.from && t < s.to) || E.scenes[E.scenes.length - 1];
    if (E.cur !== S) {
      E.stage.innerHTML = ''; E.over.innerHTML = '';
      E.stage.style.background = S.bg;
      S.refs = S.build ? S.build(E.stage, S, E.over) : {};
      E.cur = S;
    }
    const lt = t - S.from;
    const L = E.layoutAt(S, lt);
    E.cardCv.style.display = L === 'card' ? '' : 'none';
    if (L === 'card') {
      E.face.style.display = 'none';
      if (E.matteDir && !E.SND.on) {
        const ms = `${E.matteDir}/${String(fi).padStart(5, '0')}.png`;
        if (E.matte.getAttribute('src') !== ms) { E.matte.src = ms; await E.matte.decode().catch(() => {}); }
      }
      Object.assign(E.stage.style, { display: '', top: '0px', height: E.H + 'px' });
      if (!E.SND.on) E.drawCard(S.cardFx ? S.cardFx(lt) : {});
    } else if (L === 'split') {
      E.face.style.display = '';
      E.face.style.transform = `translateY(${E.splitShift}px)`;
      Object.assign(E.stage.style, { display: '', top: '0px', height: E.seam + 'px' });
    } else if (L === 'gfx') {
      E.face.style.display = 'none';
      Object.assign(E.stage.style, { display: '', top: '0px', height: E.H + 'px' });
    } else {
      E.face.style.display = '';
      const fs = typeof S.faceScale === 'function' ? S.faceScale(lt) : (S.faceScale || 1.1);
      E.face.style.transform = `scale(${fs})`;
      Object.assign(E.stage.style, { display: 'none' });
    }
    E.face.style.filter = S.faceFilter ? S.faceFilter(lt) : '';
    // the finish covers the graphic only (the face is real camera footage and already has its own texture)
    const fxH = L === 'split' ? E.seam : L === 'gfx' || L === 'card' ? E.H : 0;
    Object.assign(E.fx.style, { display: fxH && !S.noFinish ? '' : 'none', height: fxH + 'px' });
    const fi2 = Math.round(t * E.FPS);
    E.grain.style.backgroundPosition = `${(fi2 * 97) % 256}px ${(fi2 * 151) % 256}px`;
    E.lt = lt; E.sFrom = S.from; E.sId = S.id;
    if (S.tick) S.tick(S.refs, lt, S, L);
    // scenes connect: the graphic zooms through
    // each cut, pushing in over the last 3 frames of a scene and settling over the first 4 of the next; the face, the
    // real camera, never takes part. A reel turns it off with E.noLink.
    const nx = E.scenes[E.scenes.indexOf(S) + 1];
    const tOut = nx ? S.to - t : 9, tIn = lt;
    let zs = 1, zb = 0;
    if (!E.noLink && !S.noLink && tOut < 3 / E.FPS && nx) { const k = 1 - tOut / (3 / E.FPS); zs = 1 + 0.07 * k * k; zb = 7 * k; }
    else if (!E.noLink && !S.noLink && E.scenes.indexOf(S) > 0 && tIn < 4 / E.FPS) { const k = 1 - tIn / (4 / E.FPS); zs = 1 - 0.05 * k * k; zb = 6 * k; }
    E.stage.style.transformOrigin = L === 'split' ? `540px ${E.seam / 2}px` : L === 'card' ? '540px 600px' : '540px 960px';
    const sz = zs * E.safe;
    E.stage.style.transform = sz === 1 ? '' : `scale(${sz.toFixed(4)})`;
    Object.assign(E.back.style, { display: L === 'face' ? 'none' : '', height: (L === 'split' ? E.seam : E.H) + 'px', background: S.bg });
    if (window.BACKDROP) Object.assign(E.back.style, window.BACKDROP);
    E.stage.style.filter = zb ? `blur(${zb.toFixed(1)}px)` : '';
    // captions
    const c = E.chunks.find(c => t >= c.s - 0.02 && t < c.until);
    if (c && !(S.noCaptions)) {
      E.cap.style.display = 'block';
      E.cap.textContent = c.text;
      E.cap.style.top = (L === 'split' ? E.seam : E.capY[L] || 1484) + 'px';
    } else E.cap.style.display = 'none';
    await Promise.all([...document.querySelectorAll('#stage img, #over img')].map(i => (i.complete ? null : i.decode().catch(() => {}))));
  };
})();
