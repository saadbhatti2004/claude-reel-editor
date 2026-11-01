// Record a real web page in motion, frame-exact, for a reel (ENGINE.md rule 16: real sites play smoothly).
// capture_clip.mjs keeps the latest frame Chrome painted at each tick; headless Chrome often paints below 30 fps, so
// frames repeat and the page stutters. This tool steps the page's own clock (CDP virtual time) one frame at a time and
// screenshots every step, so each of the clip's frames is a real, distinct moment of the page's animation, and a
// scroll is one continuous eased move written frame by frame.
// usage: node capture_smooth.mjs <url> <outDir> [--w 1440] [--h 900] [--secs 8] [--fps 30] [--q 88] [--scale 1]
//        [--wait 2500] [--load] [--scroll 0] [--scrollFrom 0.6] [--scrollFor 0] [--scrollTo 0]
//        [--hide "css selectors"] [--css "a css block"] [--click "css selector"] [--dark]
//   --css         extra styles laid on the real page (a worse version of a real site)
//   --start       call the page's window.__start() once its clock is paused (a page that builds itself on frame 1)
//   --load        start stepping right after the page's first paint, so its entrance animation is in the clip
//   --scroll N    scroll N px over the clip, eased in and out, from --scrollFrom s for --scrollFor s (0: to the end)
// Writes <outDir>/00001.jpg ... and <outDir>/clip.json. Every page is opened logged out, in a fresh profile.
import puppeteer from 'puppeteer';
import fs from 'node:fs';
import path from 'node:path';

const [url, outDir, ...rest] = process.argv.slice(2);
const o = { scale: 1, w: 1440, h: 900, secs: 8, fps: 30, q: 88, wait: 2500, scroll: 0, scrollFrom: 0.6, scrollFor: 0, scrollTo: 0, hide: '', css: '', click: '' };
for (let i = 0; i < rest.length; i++) {
  const k = rest[i].replace(/^--/, '');
  if (['load', 'dark', 'start'].includes(k)) o[k] = true;
  else o[k] = isNaN(+rest[i + 1]) ? rest[++i] : +rest[++i];
}
fs.mkdirSync(outDir, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ease = k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);

const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
const page = await browser.newPage();
await page.setViewport({ width: o.w, height: o.h, deviceScaleFactor: o.scale });
await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0 Safari/537.36');
if (o.dark) await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
const cdp = await page.createCDPSession();

await page.goto(url, { waitUntil: o.load ? 'domcontentloaded' : 'networkidle2', timeout: 60000 }).catch(() => {});
if (!o.load) await sleep(o.wait);
if (o.hide) await page.addStyleTag({ content: `${o.hide} { display: none !important; }` }).catch(() => {});
if (o.css) { await page.addStyleTag({ content: o.css }).catch(() => {}); await sleep(400); }
if (o.click) await page.click(o.click).catch(() => {});
if (o.scrollTo) { await page.evaluate(y => window.scrollTo(0, y), o.scrollTo); await sleep(600); }
await page.mouse.move(o.w / 2, o.h * 0.75);

// from here the page's clock only moves when we step it
await cdp.send('Emulation.setVirtualTimePolicy', { policy: 'pause' });
// some pages never report the budget as spent (a busy main thread); after 4 s of real time the step goes on anyway
let stalls = 0;
const step = ms => new Promise(res => {
  const to = setTimeout(() => { stalls++; res(); }, 4000);
  cdp.once('Emulation.virtualTimeBudgetExpired', () => { clearTimeout(to); res(); });
  cdp.send('Emulation.setVirtualTimePolicy', { policy: 'advance', budget: ms }).catch(() => {});
});
// --start: one warm-up step first (a first step can stall while the page settles), then the page's clock starts
if (o.start) { await step(1000 / o.fps); stalls = 0; await page.evaluate(() => window.__start && window.__start()).catch(() => {}); }
const n = Math.round(o.secs * o.fps), y0 = o.scrollTo || 0;
const sFor = o.scrollFor || Math.max(0.1, o.secs - o.scrollFrom);
for (let k = 0; k < n; k++) {
  const t = k / o.fps;
  if (o.scroll) {
    const y = y0 + o.scroll * ease(Math.min(1, Math.max(0, (t - o.scrollFrom) / sFor)));
    await page.evaluate(y => { document.documentElement.style.scrollBehavior = 'auto'; window.scrollTo(0, y); }, y);
  }
  await step(1000 / o.fps);
  // a screenshot needs a fresh frame; if the paused page will not paint one in 6 s, let real time run briefly
  let shot = await Promise.race([cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: o.q }), sleep(6000).then(() => null)]);
  if (!shot) { stalls++; await cdp.send('Emulation.setVirtualTimePolicy', { policy: 'advance', budget: 1000 / o.fps }).catch(() => {}); shot = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: o.q }); }
  fs.writeFileSync(path.join(outDir, String(k + 1).padStart(5, '0') + '.jpg'), Buffer.from(shot.data, 'base64'));
  if (k % 30 === 29) console.error(`frame ${k + 1}/${n}${stalls ? `, ${stalls} stalled steps` : ''}`);
}
await browser.close();
fs.writeFileSync(path.join(outDir, 'clip.json'), JSON.stringify({ url, w: o.w, h: o.h, scale: o.scale, fps: o.fps, frames: n, stepped: true, stalls, scroll: o.scroll, captured: new Date().toISOString() }, null, 1));
console.log(`${outDir}: ${n} stepped frames${stalls ? `, ${stalls} stalled steps (not frame-exact there)` : ''} (${url})`);
