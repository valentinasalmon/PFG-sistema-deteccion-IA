// Recorrido real del abogado: caso nuevo, fotos, análisis, informe y verificación pública.
const { revisarPagina } = require('./sensor-diseno.cjs');
const pw = require('playwright');
const [,, dir, imgs, modo = 'pc'] = process.argv; const B = 'http://localhost:5173';
// Cuenta de abogada sin rol de Administrador (el Administrador no crea casos).
const CORREO = process.env.RECORRIDO_CORREO || 'prueba@evidentia.local';
const CLAVE = process.env.RECORRIDO_CLAVE || 'Prueba12345';
let paso = 0; let fallo = false; const log = (m) => console.log(`[${++paso}] ${m}`);
(async () => {
  const b = await pw.chromium.launch();
  const ctx = await b.newContext(modo === 'cel' ? { ...pw.devices['iPhone 13'], acceptDownloads: true } : { viewport: { width: 1280, height: 860 }, acceptDownloads: true });
  const p = await ctx.newPage(); const errores = []; p.on('pageerror', (e) => errores.push(e.message));
  // Cada captura pasa también por el sensor de diseño (037): contenido cortado o escondido falla.
  const diseno = [];
  const foto = async (n) => { await p.screenshot({ path: `${dir}/abogado-${modo}-${String(paso).padStart(2, '0')}-${n}.png`, fullPage: true }); for (const x of await revisarPagina(p)) if (x.gravedad === 'error') diseno.push(`${n}: ${x.tipo} — ${x.detalle}`); };
  try {
    await p.goto(B + '/iniciar-sesion'); await p.getByLabel('Correo electrónico').fill(CORREO); await p.getByLabel('Contraseña', { exact: true }).fill(CLAVE);
    await p.getByRole('button', { name: 'Ingresar' }).click(); await p.waitForTimeout(1800); log('ingresó: ' + (await p.locator('h1').first().textContent()));
    await p.goto(B + '/casos/nuevo'); await p.waitForTimeout(1500);
    await p.locator('label', { hasText: 'Automovilístico' }).first().click();
    await p.getByLabel('Fecha del hecho').fill('2026-10-30'); await p.getByLabel('Lugar del hecho').fill('Av. Rivadavia 5000, CABA');
    await p.getByRole('button', { name: /Crear y cargar/ }).click(); await p.waitForTimeout(2000); await foto('caso-creado'); log('caso creado: ' + (await p.locator('h1').first().textContent()));
    await p.locator('input[type=file]').first().setInputFiles([`${imgs}/frente.jpg`, `${imgs}/editada.jpg`]); await p.waitForTimeout(4000); await foto('fotos'); log('fotos subidas: ' + (await p.locator('.galeria li, .tarjeta-imagen').count()));
    await p.getByRole('button', { name: /Analizar/ }).first().click(); log('análisis pedido');
    for (let i = 0; i < 40 && !(await p.getByText(/Análisis terminado|Generar el informe|Descargar el PDF/).first().isVisible().catch(() => false)); i++) await p.waitForTimeout(1500);
    await foto('analisis'); log('análisis: ' + ((await p.locator('.flujo-caso__pasos').innerText().catch(() => '')).replace(/\n/g, ' ')));
    const gen = p.getByRole('button', { name: 'Generar el informe' }); if (await gen.isVisible().catch(() => false)) { await gen.click(); await p.waitForTimeout(4000); log('informe generado'); }
    await p.goto(p.url().split('?')[0] + '?etapa=informe'); await p.waitForTimeout(2500); await foto('informe');
    const [descarga] = await Promise.all([p.waitForEvent('download', { timeout: 15000 }).catch(() => null), p.getByRole('button', { name: /Descargar el informe/ }).first().click().catch(() => {})]);
    if (descarga) { await descarga.saveAs(`${dir}/informe-${modo}.pdf`); log('PDF descargado'); } else { const pop = ctx.pages().length; log('descarga: sin evento (pestañas abiertas ' + pop + ')'); }
    const codigo = await p.locator('a[href^="/verificar/"]').first().getAttribute('href').catch(() => null);
    if (codigo) { const v = await ctx.newPage(); await v.goto(B + codigo); await v.waitForTimeout(2500); await v.screenshot({ path: `${dir}/abogado-${modo}-verificar.png`, fullPage: true }); log('verificación pública: ' + (await v.locator('main').innerText()).replace(/\n/g, ' ').slice(140, 420)); }
  } catch (e) { fallo = true; log('ERROR: ' + e.message.split('\n')[0]); await foto('error'); }
  console.log('Errores de la página:', errores.slice(0, 5));
  console.log(diseno.length ? `Problemas de diseño:\n  ${diseno.join('\n  ')}` : 'Sin problemas de diseño.'); await b.close();
  // 039: en la integración continua, un paso fallido o un problema de diseño dejan el recorrido en rojo.
  if (fallo || diseno.length || errores.length) process.exitCode = 1;
})();
