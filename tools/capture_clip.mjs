// Record a real web page in motion (its load animation, its scroll) as a frame sequence a reel can play.
// usage: node capture_clip.mjs <url> <outDir> [--w 1440] [--h 900] [--secs 5] [--fps 30] [--q 88]
//        [--load] [--wait 1500] [--wheel 0] [--wheelEvery 0.12] [--wheelFrom 0.5] [--scrollTo 0]
//        [--hide "css selectors"] [--click "css selector"] [--dark] [--scale 1]
//   --load        start recording before the page loads, so its entrance animation is in the clip
//   --wheel N     send a mouse-wheel step of N px every --wheelEvery s from --wheelFrom s (smooth-scroll libraries
//                 such as Lenis only ease real wheel input, so this records the scroll the way a visitor sees it)
// Writes <outDir>/00001.jpg ... at a steady fps (the latest painted frame at each tick) and <outDir>/clip.json.
// Every page is opened logged out, in a fresh profile.
import puppeteer from 'puppeteer';
import fs from 'node:fs';
import path from 'node:path';

const [url, outDir, ...rest] = process.argv.slice(2);
const o = { scale: 1, w: 1440, h: 900, secs: 5, fps: 30, q: 88, wait: 1500, wheel: 0, wheelEvery: 0.12, wheelFrom: 0.5, scrollTo: 0, hide: '', click: '' };
for (let i = 0; i < rest.length; i++) {
  const k = rest[i].replace(/^--/, '');
  if (['load', 'dark'].includes(k)) o[k] = true;
  else o[k] = isNaN(+rest[i + 1]) ? rest[++i] : +rest[++i];
}
fs.mkdirSync(outDir, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
const page = await browser.newPage();
await page.setViewport({ width: o.w, height: o.h, deviceScaleFactor: o.scale });
await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0 Safari/537.36');
if (o.dark) await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
const cdp = await page.createCDPSession();
const frames = [];
cdp.on('Page.screencastFrame', async f => {
  frames.push({ ts: f.metadata.timestamp, data: f.data });
  try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch {}
});
const start = () => cdp.send('Page.startScreencast', { format: 'jpeg', quality: o.q, maxWidth: o.w * o.scale, maxHeight: o.h * o.scale, everyNthFrame: 1 });

let t0;
if (o.load) { await start(); t0 = Date.now() / 1000; }
await page.goto(url, { waitUntil: o.load ? 'domcontentloaded' : 'networkidle2', timeout: 60000 }).catch(() => {});
if (!o.load) {
  await sleep(o.wait);
  if (o.hide) await page.addStyleTag({ content: `${o.hide} { display: none !important; }` });
  if (o.click) await page.click(o.click).catch(() => {});
  if (o.scrollTo) { await page.evaluate(y => window.scrollTo(0, y), o.scrollTo); await sleep(600); }
  await page.mouse.move(o.w / 2, o.h / 2);
  await start(); t0 = Date.now() / 1000;
} else if (o.hide) await page.addStyleTag({ content: `${o.hide} { display: none !important; }` }).catch(() => {});

// drive the wheel while recording
const end = t0 + o.secs;
if (o.wheel) {
  await sleep(o.wheelFrom * 1000);
  while (Date.now() / 1000 < end) { await page.mouse.wheel({ deltaY: o.wheel }); await sleep(o.wheelEvery * 1000); }
} else await sleep(o.secs * 1000);
await sleep(150);
await cdp.send('Page.stopScreencast');
await browser.close();

// resample to a steady fps: at each tick, the latest frame painted at or before it
if (!frames.length) { console.error('no frames recorded'); process.exit(1); }
frames.sort((a, b) => a.ts - b.ts);
const base = Math.max(frames[0].ts, t0 - 0.05);
const n = Math.round(o.secs * o.fps);
let j = 0;
for (let k = 0; k < n; k++) {
  const tk = base + k / o.fps;
  while (j + 1 < frames.length && frames[j + 1].ts <= tk) j++;
  fs.writeFileSync(path.join(outDir, String(k + 1).padStart(5, '0') + '.jpg'), Buffer.from(frames[j].data, 'base64'));
}
fs.writeFileSync(path.join(outDir, 'clip.json'), JSON.stringify({ url, w: o.w, h: o.h, scale: o.scale, fps: o.fps, frames: n, painted: frames.length, captured: new Date().toISOString() }, null, 1));
console.log(`${outDir}: ${n} frames from ${frames.length} painted (${url})`);
