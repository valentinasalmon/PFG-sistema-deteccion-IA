// Sensor de accesibilidad (041, RNF11): recorre las pantallas en computadora y
// en celular y las revisa con axe-core contra las reglas de WCAG 2.1 nivel A y AA
// (contraste, nombres accesibles de botones y campos, estructura de títulos,
// idioma, regiones y uso de ARIA).
//
// Uso (con el entorno local levantado y axe-core instalado sin guardarlo:
// `npm install --no-save axe-core@4.10.3`):
//   node e2e/accesibilidad.cjs [base] [archivo de pantallas]
// El archivo de pantallas es un JSON con [{ "ruta": "/...", "sesion": true }]
// (por ejemplo, para revisar un caso con su análisis o Administración).
// Variables opcionales: SENSOR_CORREO y SENSOR_CLAVE para las pantallas con sesión.
//
// Sale con código 1 si encuentra infracciones de impacto serio o crítico; las
// moderadas y menores se informan sin hacerlo fallar.
//
// Realiza: RNF11 (accesibilidad WCAG 2.1 AA).

const { chromium } = require('playwright')
const axe = require('axe-core')

const ANCHOS = [
  { nombre: 'pc', width: 1440, height: 900 },
  { nombre: 'cel', width: 390, height: 844 },
]

const PANTALLAS_POR_DEFECTO = [
  { ruta: '/presentacion' },
  { ruta: '/iniciar-sesion' },
  { ruta: '/registro' },
  { ruta: '/recuperar-contrasenia' },
  { ruta: '/verificar' },
  { ruta: '/estado' },
  { ruta: '/terminos' },
  { ruta: '/privacidad' },
  { ruta: '/', sesion: true },
  { ruta: '/casos', sesion: true },
  { ruta: '/casos/nuevo', sesion: true },
  { ruta: '/organizaciones', sesion: true },
  { ruta: '/organizaciones/nueva', sesion: true },
  { ruta: '/perfil', sesion: true },
]

const GRAVES = new Set(['serious', 'critical'])

async function revisar(page) {
  await page.addScriptTag({ content: axe.source })
  return page.evaluate(async () => {
    const resultado = await window.axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] },
    })
    return resultado.violations.map((v) => ({
      regla: v.id,
      impacto: v.impact,
      ayuda: v.help,
      nodos: v.nodes.slice(0, 3).map((n) => n.target.join(' ')),
      cantidad: v.nodes.length,
    }))
  })
}

async function principal() {
  const base = process.argv[2] || 'http://localhost:5173'
  const correo = process.env.SENSOR_CORREO
  const clave = process.env.SENSOR_CLAVE
  const PANTALLAS = process.argv[3]
    ? JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'))
    : PANTALLAS_POR_DEFECTO
  const navegador = await chromium.launch()
  let graves = 0
  for (const ancho of ANCHOS) {
    // Sin animaciones: las que aparecen al desplazarse dan falsos problemas de contraste.
    const contexto = await navegador.newContext({
      viewport: { width: ancho.width, height: ancho.height },
      reducedMotion: 'reduce',
    })
    const page = await contexto.newPage()
    let conSesion = false
    for (const pantalla of PANTALLAS) {
      if (pantalla.sesion && !conSesion) {
        if (!correo || !clave) continue
        await page.goto(`${base}/iniciar-sesion`)
        await page.fill('input[name=correo]', correo)
        await page.fill('input[name=contrasenia]', clave)
        await page.click('button[type=submit]')
        await page.waitForURL((url) => !url.pathname.startsWith('/iniciar-sesion'), { timeout: 15000 })
        conSesion = true
      }
      await page.goto(base + pantalla.ruta)
      await page.waitForLoadState('networkidle')
      const infracciones = await revisar(page)
      const etiqueta = `[${ancho.nombre}] ${pantalla.ruta}`
      if (infracciones.length === 0) {
        console.log(`${etiqueta}: sin infracciones`)
        continue
      }
      for (const inf of infracciones) {
        const grave = GRAVES.has(inf.impacto)
        if (grave) graves += 1
        console.log(`${etiqueta}: ${grave ? 'ERROR' : 'aviso'} ${inf.regla} (${inf.impacto}, ${inf.cantidad}) — ${inf.ayuda}`)
        for (const nodo of inf.nodos) console.log(`    ${nodo}`)
      }
    }
    await contexto.close()
  }
  await navegador.close()
  console.log(graves ? `\n${graves} infracciones graves.` : '\nSin infracciones graves.')
  process.exitCode = graves ? 1 : 0
}

principal().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
