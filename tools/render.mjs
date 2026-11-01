// Render an educational reel's composition (edit/index.html) frame by frame in headless Chrome.
// usage:
//   node render.mjs <editDir> --stills 0.5,3.2,... --outdir <dir>        one PNG per time (review sheets)
//   node render.mjs <editDir> --from 0 --to 5.1 --out <file.mp4> [--audio <wav>] [--crf 12] [--draft]
//     final quality by default: lossless PNG frames, x264 slow at CRF 12, BT.709 TV-range colour tags;
//     --draft is for review samples (JPEG frames, CRF 17, faster)
//   node render.mjs <editDir> --plan                                     write edit/plan.json (scenes + sound cues) and
//                                                                        edit/events.json (every motion on screen, for tools/sound.py)
// Every frame is a pure function of time (EDU.seek), so any range renders alone.
import puppeteer from 'puppeteer';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [editDir, ...rest] = process.argv.slice(2);
const o = {};
for (let i = 0; i < rest.length; i++) { const k = rest[i].replace(/^--/, ''); const v = rest[i + 1]; if (v === undefined || v.startsWith('--')) o[k] = true; else { o[k] = v; i++; } }
const FPS = 30;

const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--allow-file-access-from-files', '--disable-web-security'] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
await page.goto(pathToFileURL(path.join(editDir, 'index.html')).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
// a composition can set its own frame (a landscape video is 1920x1080); reels stay 1080x1920
const FR = await page.evaluate(() => window.FRAME || { w: 1080, h: 1920 });
if (FR.w !== 1080 || FR.h !== 1920) await page.setViewport({ width: FR.w, height: FR.h, deviceScaleFactor: 1 });
if (errors.length) { console.error('page errors:\n' + errors.join('\n')); await browser.close(); process.exit(1); }

const plan = await page.evaluate(() => ({ scenes: window.SCENES, sfx: window.SFX, dur: window.DUR }));
fs.writeFileSync(path.join(editDir, 'plan.json'), JSON.stringify(plan, null, 1));
const seek = async t => { await page.evaluate(t => window.EDU.seek(t), t); if (errors.length) throw new Error(errors.join('\n')); };
if (o.plan) {
  // the sound sweep: every frame once, recording each kit motion that is on screen (kit.js E.SND), for tools/sound.py
  await page.evaluate(() => { window.EDU.SND.on = true; window.EDU.SND.ev.clear(); window.EDU.cur = null; });
  const nf = Math.floor(plan.dur * FPS);
  for (let f = 0; f <= nf; f++) await seek(f / FPS);
  const ev = await page.evaluate(() => { const E = window.EDU; E.SND.on = false; E.cur = null; return [...E.SND.ev.values()]; });
  ev.sort((a, b) => a.g0 - b.g0);
  fs.writeFileSync(path.join(editDir, 'events.json'), '[\n' + ev.map(e => JSON.stringify(e)).join(',\n') + '\n]\n');
  console.log('plan written', plan.scenes.length, 'scenes,', ev.length, 'motion events');
  await browser.close(); process.exit(0);
}

if (o.stills) {
  fs.mkdirSync(o.outdir, { recursive: true });
  for (const s of String(o.stills).split(',')) {
    const t = +s; await seek(t);
    await page.screenshot({ path: path.join(o.outdir, `t${t.toFixed(2).padStart(6, '0')}.png`) });
  }
  console.log('stills written to', o.outdir);
} else {
  const from = +o.from, to = +o.to, n = Math.round((to - from) * FPS);
  const draft = !!o.draft;
  const args = ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', draft ? 'mjpeg' : 'png', '-i', '-'];
  if (o.audio) args.push('-ss', from.toFixed(3), '-t', (n / FPS).toFixed(3), '-i', o.audio);
  args.push('-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int',
    '-c:v', 'libx264', '-preset', draft ? 'medium' : 'slow', '-crf', String(o.crf || (draft ? 17 : 12)), '-profile:v', 'high',
    '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
    '-r', String(FPS));
  if (o.audio) args.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
  args.push('-movflags', '+faststart', o.out);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const write = buf => new Promise(res => (ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res)));
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await seek(from + i / FPS);
    await write(await page.screenshot(draft ? { type: 'jpeg', quality: 92 } : { type: 'png' }));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log(`${o.out}: ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}
await browser.close();
