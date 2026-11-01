// Capture a real web page, logged out, as material for an educational reel.
// usage: node capture.mjs <url> <out.png> [--w 1080] [--h 1350] [--scale 2] [--dark] [--full] [--wait 2500]
//        [--hide "css selectors to hide, comma separated"] [--scroll 0]
// Writes the screenshot plus <out>.json with the page title and the boxes of its h1/h2 and links, so a scene can
// zoom to the exact words it needs.
import puppeteer from 'puppeteer';
import fs from 'node:fs';

const [url, out, ...rest] = process.argv.slice(2);
const opt = { w: 1080, h: 1350, scale: 2, wait: 2500, scroll: 0, hide: '' };
for (let i = 0; i < rest.length; i++) {
  const k = rest[i].replace(/^--/, '');
  if (k === 'dark' || k === 'full') opt[k] = true;
  else opt[k] = isNaN(+rest[i + 1]) ? rest[++i] : +rest[++i];
}

const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--hide-scrollbars'] });
const page = await browser.newPage();
await page.setViewport({ width: opt.w, height: opt.h, deviceScaleFactor: opt.scale });
await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0 Safari/537.36');
if (opt.dark) await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
await new Promise(r => setTimeout(r, opt.wait));
if (opt.hide) await page.addStyleTag({ content: `${opt.hide} { display: none !important; }` });
if (opt.scroll) await page.evaluate(y => window.scrollTo(0, y), opt.scroll);
await new Promise(r => setTimeout(r, 400));
await page.screenshot({ path: out, fullPage: !!opt.full });
const info = await page.evaluate(() => {
  const box = el => { const r = el.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y + window.scrollY), Math.round(r.width), Math.round(r.height)]; };
  return {
    title: document.title,
    headings: [...document.querySelectorAll('h1,h2,h3')].slice(0, 40).map(e => ({ tag: e.tagName, text: e.innerText.trim().slice(0, 140), box: box(e) })),
  };
});
// --find "phrase|another phrase": the line boxes of each phrase on the page (page pixels, before deviceScaleFactor)
if (opt.find) {
  info.found = await page.evaluate(phrases => phrases.map(ph => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const i = node.textContent.indexOf(ph.slice(0, 40));
      if (i < 0) continue;
      const r = document.createRange();
      r.setStart(node, i);
      let end = node, endOff = i + ph.length;
      if (endOff > node.textContent.length) endOff = node.textContent.length;
      r.setEnd(end, endOff);
      const rects = [...r.getClientRects()].map(q => [Math.round(q.x), Math.round(q.y + window.scrollY), Math.round(q.width), Math.round(q.height)]);
      return { phrase: ph, rects };
    }
    return { phrase: ph, rects: [] };
  }), String(opt.find).split('|'));
}
fs.writeFileSync(out.replace(/\.png$/, '.json'), JSON.stringify({ url, ...opt, ...info }, null, 1));
console.log(out, info.title);
await browser.close();
