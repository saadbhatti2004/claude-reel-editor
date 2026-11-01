// Record a page that draws itself (window.__draw(t), options in window.__o) frame by frame, exactly (ENGINE.md rule 18).
// usage: node capture_draw.mjs <page.html> <outDir> [--w 1440] [--h 900] [--frames 90] [--fps 30] [--t0 0] [--scale 1]
//        [--q 88] [--opts '{"v":1}'] [--sweep key:from:to]   (sweep: the option runs from..to across the frames, t stays t0)
// Writes <outDir>/00001.jpg ... and <outDir>/clip.json.
import puppeteer from 'puppeteer';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [src, outDir, ...rest] = process.argv.slice(2);
const o = { w: 1440, h: 900, frames: 90, fps: 30, t0: 0, scale: 1, q: 88, opts: '{}', sweep: '' };
for (let i = 0; i < rest.length; i += 2) o[rest[i].replace(/^--/, '')] = isNaN(+rest[i + 1]) ? rest[i + 1] : +rest[i + 1];
fs.mkdirSync(outDir, { recursive: true });
const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--hide-scrollbars', '--allow-file-access-from-files'] });
const page = await browser.newPage();
await page.setViewport({ width: o.w, height: o.h, deviceScaleFactor: o.scale });
await page.goto(pathToFileURL(path.resolve(src)).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
const opts = JSON.parse(o.opts);
const [sk, sa, sb] = o.sweep ? o.sweep.split(':') : [];
for (let f = 0; f < o.frames; f++) {
  const k = o.frames > 1 ? f / (o.frames - 1) : 0;
  const op = Object.assign({}, opts, sk ? { [sk]: +sa + (+sb - +sa) * k } : {});
  const t = sk ? o.t0 : o.t0 + f / o.fps;
  await page.evaluate((op, t) => { window.__o = op; window.__draw(t); }, op, t);
  await page.screenshot({ path: path.join(outDir, String(f + 1).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: o.q });
}
fs.writeFileSync(path.join(outDir, 'clip.json'), JSON.stringify({ src, frames: o.frames, fps: o.fps, w: o.w, h: o.h, opts, sweep: o.sweep, t0: o.t0 }, null, 1));
await browser.close();
console.log(outDir, o.frames, 'frames');
