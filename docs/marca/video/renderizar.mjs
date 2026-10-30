// Renderiza teaser.html fotograma por fotograma y lo codifica con ffmpeg.
// Uso: node renderizar.mjs <ancho> <alto> <salida.mp4> [--muestras t1,t2,...]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import path from 'node:path';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');

const [ancho, alto, salida, bandera, lista] = process.argv.slice(2);
const dir = path.dirname(new URL(import.meta.url).pathname);
const navegador = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' + (process.env.CHROMIUM_SUFIJO ?? ''), args: ['--allow-file-access-from-files'] }).catch(() => chromium.launch({ args: ['--allow-file-access-from-files'] }));
const pagina = await navegador.newPage({ viewport: { width: +ancho, height: +alto } });
await pagina.goto('file://' + path.join(dir, 'teaser.html'));
await pagina.evaluate(() => window.listo);

if (bandera === '--muestras') {
  for (const t of lista.split(',')) {
    await pagina.evaluate(x => window.render(x), +t);
    await pagina.screenshot({ path: `${salida}-${t}.png` });
  }
} else {
  const fps = 30;
  const duracion = await pagina.evaluate(() => window.DURACION);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', salida], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(duracion * fps);
  for (let f = 0; f < total; f++) {
    await pagina.evaluate(x => window.render(x), f / fps);
    const cuadro = await pagina.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(cuadro)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`fotograma ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await navegador.close();
