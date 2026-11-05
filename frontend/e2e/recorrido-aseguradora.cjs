// Recorrido real por la interfaz: registro de una aseguradora, pago, verificación, aprobación y uso.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [,, dir, buzon, navegador = 'chromium'] = process.argv;
const pw = require('playwright'); const B = 'http://localhost:5173';
const marca = Date.now(); const correo = `ref${marca}@aseg.com`; const clave = 'Segura12345';
let paso = 0; const log = (m) => console.log(`[${++paso}] ${m}`);
const ultimoToken = (desde) => {
  for (let i = 0; i < 40; i++) {
    const nuevos = fs.readdirSync(buzon).filter((f) => f.endsWith('.eml')).map((f) => path.join(buzon, f)).filter((f) => fs.statSync(f).mtimeMs > desde);
    for (const f of nuevos) { const t = fs.readFileSync(f, 'utf8').replace(/=\r?\n/g, '').replace(/=3D/g, '='); if (t.includes(correo)) { const m = t.match(/token=([\w.\-]+)/); if (m) return m[1]; } }
    require('child_process').execSync('sleep 0.3');
  }
  return null;
};
(async () => {
  const b = await pw[navegador].launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 860 } }); const p = await ctx.newPage();
  const errores = []; p.on('pageerror', (e) => errores.push(e.message)); p.on('console', (m) => m.type() === 'error' && errores.push(m.text()));
  const foto = (n) => p.screenshot({ path: `${dir}/${navegador}-${String(paso).padStart(2, '0')}-${n}.png`, fullPage: true });
  try {
    await p.goto(B + '/registro'); await p.locator('.camino').nth(2).click(); await p.getByRole('button', { name: 'Siguiente' }).click();
    log('camino Aseguradora elegido');
    await p.getByLabel('Nombre', { exact: true }).fill('Rita'); await p.getByLabel('Apellido').fill('Prueba');
    const buscar = p.getByLabel(/Buscá tu aseguradora/); await buscar.fill('SEGUROS'); await p.waitForTimeout(700);
    await p.locator('.opciones-tarjeta label').nth(3 + (marca % 5)).click(); await foto('datos');
    await p.getByRole('button', { name: 'Siguiente' }).click(); log('datos y aseguradora');
    await p.waitForTimeout(500); await foto('plan');
    if (await p.getByRole('button', { name: 'Siguiente' }).isVisible()) { await p.getByRole('radio').first().check({ force: true }).catch(() => {}); await p.getByRole('button', { name: 'Siguiente' }).click(); log('plan'); }
    await p.getByLabel('Correo electrónico').fill(correo); await p.getByLabel('Contraseña', { exact: true }).fill(clave);
    await p.getByRole('checkbox').check(); const antes = Date.now();
    await p.getByRole('button', { name: /Crear la cuenta/ }).click(); await p.waitForTimeout(1500); await foto('pago'); log('cuenta creada, en el pago');
    await p.getByRole('button', { name: /Simular/ }).click(); await p.waitForTimeout(2500); await foto('pago-acreditado'); log('pago simulado');
    const token = ultimoToken(antes - 5000); log('token de verificación ' + (token ? 'recibido' : 'NO RECIBIDO'));
    await p.goto(`${B}/verificar-correo?token=${token}`); await p.waitForTimeout(1500); await foto('verificado');
    await p.goto(B + '/iniciar-sesion'); await p.getByLabel('Correo electrónico').fill(correo); await p.getByLabel('Contraseña', { exact: true }).fill(clave);
    await p.getByRole('button', { name: 'Ingresar' }).click(); await p.waitForTimeout(2000); await foto('inicio-pendiente'); log('ingresó la aseguradora pendiente: ' + (await p.locator('h1').first().textContent()));
    await p.goto(B + '/organizaciones'); await p.waitForTimeout(1200); await p.locator('a[href^="/organizaciones/"]').first().click(); await p.waitForTimeout(1500); await foto('organizacion-pendiente');
    log('organización: ' + (await p.locator('.aviso').first().textContent().catch(() => 'sin aviso')).slice(0, 80));
    await p.getByRole('button', { name: 'Verificar mi identidad' }).click(); await p.waitForTimeout(1500); await foto('identidad');
    await p.getByRole('button', { name: 'Simular verificación aprobada' }).click(); await p.waitForTimeout(1200); await foto('identidad-aprobada');
    log('identidad: ' + (await p.locator('main, .registro-ancho').first().innerText()).replace(/\n/g, ' ').slice(0, 120));
    // Administrador
    const adm = await (await b.newContext({ viewport: { width: 1280, height: 860 } })).newPage();
    await adm.goto(B + '/iniciar-sesion'); await adm.getByLabel('Correo electrónico').fill('admin.1792121374009@ejemplo.com'); await adm.getByLabel('Contraseña', { exact: true }).fill('Prueba12345');
    await adm.getByRole('button', { name: 'Ingresar' }).click(); await adm.waitForTimeout(2000);
    await adm.goto(B + '/administracion'); await adm.waitForTimeout(2000); await adm.screenshot({ path: `${dir}/${navegador}-admin-pendientes.png`, fullPage: true });
    const tarjeta = adm.locator('li', { hasText: correo }); log('el admin ve la aseguradora pendiente: ' + (await tarjeta.count()));
    await tarjeta.getByRole('button', { name: 'Aprobar' }).click(); await adm.getByRole('dialog').getByRole('button', { name: 'Aprobar' }).click(); await adm.waitForTimeout(1500);
    await adm.screenshot({ path: `${dir}/${navegador}-admin-aprobada.png`, fullPage: true }); log('aprobada: ' + (await adm.locator('[role=status], .aviso').first().textContent().catch(() => '?')).slice(0, 80));
    await p.goto(B + '/'); await p.waitForTimeout(2000); await foto('inicio-activa');
    log('menú de la aseguradora: ' + (await p.locator('.encabezado__navegacion').innerText()).replace(/\n/g, ' | '));
    await p.goto(B + '/casos/nuevo'); await p.waitForTimeout(1500); log('alta: ' + (await p.locator('h1').first().textContent())); await foto('nuevo-siniestro');
  } catch (e) { log('ERROR: ' + e.message.split('\n')[0]); await foto('error'); }
  console.log('Errores de consola:', errores.slice(0, 5));
  await b.close();
})();
