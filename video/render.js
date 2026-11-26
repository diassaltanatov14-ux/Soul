const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS = +process.env.FPS || 30, ONLY = process.env.ONLY;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('console', m => console.log('page:', m.text())); p.on('pageerror', e => console.log('ERR', e));
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction('window.ready === true', null, { timeout: 60000 });
  const grab = async t => { const d = await p.evaluate(t => { renderAt(t); return document.querySelector('canvas').toDataURL('image/jpeg', 0.95); }, t); return Buffer.from(d.split(',')[1], 'base64'); };
  if (ONLY) { for (const t of ONLY.split(',')) require('fs').writeFileSync(`prev_${t}.jpg`, await grab(+t)); await b.close(); return; }
  const dur = await p.evaluate('DURATION'), n = Math.round(dur * FPS);
  const ff = spawn('ffmpeg', ['-y','-f','image2pipe','-framerate',String(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-movflags','+faststart','out.mp4'], { stdio: ['pipe','ignore','inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) { ff.stdin.write(await grab(i / FPS)); if (i % 60 == 0) console.log(i, '/', n, ((Date.now()-t0)/1000).toFixed(0)+'s'); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
