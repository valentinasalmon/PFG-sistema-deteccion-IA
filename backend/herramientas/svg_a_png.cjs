// Convierte un diagrama SVG en PNG con el Chromium de Playwright (funcionalidad 039).
// Uso: node svg_a_png.cjs entrada.svg salida.png [escala]
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const [, , entrada, salida, escala] = process.argv;
  const svg = fs.readFileSync(entrada, 'utf8');
  const medidas = svg.match(/width="(\d+)" height="(\d+)"/);
  const ancho = Number(medidas[1]);
  const alto = Number(medidas[2]);
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({
    viewport: { width: ancho, height: alto },
    deviceScaleFactor: Number(escala || 2),
  });
  await pagina.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await pagina.screenshot({ path: salida, clip: { x: 0, y: 0, width: ancho, height: alto } });
  await navegador.close();
})();
