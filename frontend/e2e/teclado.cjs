// Sensor de uso con teclado (043, RNF11): complementa al de accesibilidad, que no
// prueba la interacción. En computadora, recorre cada pantalla con Tab y falla si:
//   - un elemento recibe el foco sin un indicador visible (contorno o sombra),
//   - el foco cae en algo invisible o fuera de la pantalla,
//   - el foco queda atrapado (no avanza al apretar Tab).
// Además inicia sesión usando solo el teclado.
//
// Uso (con el entorno local levantado): node e2e/teclado.cjs [base]
// Variables: SENSOR_CORREO y SENSOR_CLAVE para las pantallas con sesión.
//
// Realiza: RNF11 (WCAG 2.1: 2.1.1 Teclado, 2.1.2 Sin trampas, 2.4.7 Foco visible).

const { chromium } = require('playwright')

const PANTALLAS = [
  { ruta: '/presentacion' },
  { ruta: '/iniciar-sesion' },
  { ruta: '/registro' },
  { ruta: '/verificar' },
  { ruta: '/', sesion: true },
  { ruta: '/casos', sesion: true },
  { ruta: '/casos/nuevo', sesion: true },
  { ruta: '/organizaciones', sesion: true },
  { ruta: '/perfil', sesion: true },
]
const MAXIMO_TABS = 60

/** Describe el elemento con foco y si su indicador se ve. */
function estadoDelFoco() {
  const el = document.activeElement
  if (!el || el === document.body) return null
  const estilo = getComputedStyle(el)
  const caja = el.getBoundingClientRect()
  const contorno = estilo.outlineStyle !== 'none' && parseFloat(estilo.outlineWidth) > 0
  const sombra = estilo.boxShadow && estilo.boxShadow !== 'none'
  const texto = (el.innerText || el.getAttribute('aria-label') || el.getAttribute('name') || '').trim().replace(/\s+/g, ' ').slice(0, 40)
  return {
    descripcion: `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''} «${texto}»`,
    visible: caja.width > 0 && caja.height > 0 && estilo.visibility !== 'hidden',
    indicador: contorno || sombra,
    clave: el.outerHTML.slice(0, 120) + `@${Math.round(caja.x)},${Math.round(caja.y)}`,
  }
}

async function recorrer(page, etiqueta) {
  const problemas = []
  const vistos = new Set()
  let anterior = null
  let repetidos = 0
  await page.evaluate(() => document.activeElement?.blur())
  for (let i = 0; i < MAXIMO_TABS; i += 1) {
    await page.keyboard.press('Tab')
    const foco = await page.evaluate(estadoDelFoco)
    if (!foco) continue
    if (foco.clave === anterior) {
      repetidos += 1
      // Un campo de fecha nativo usa Tab para pasar entre día, mes y año: hasta
      // cinco Tab seguidos en el mismo control no son una trampa.
      if (repetidos >= 6) {
        problemas.push(`foco atrapado en ${foco.descripcion}`)
        break
      }
      continue
    }
    repetidos = 0
    anterior = foco.clave
    if (vistos.has(foco.clave)) break // dio la vuelta: recorrió todo
    vistos.add(foco.clave)
    if (!foco.visible) problemas.push(`foco en un elemento invisible: ${foco.descripcion}`)
    else if (!foco.indicador) problemas.push(`foco sin indicador visible: ${foco.descripcion}`)
  }
  console.log(`${etiqueta}: ${vistos.size} elementos con foco${problemas.length ? '' : ', sin problemas'}`)
  problemas.forEach((p) => console.log(`    ERROR ${p}`))
  return problemas.length
}

async function iniciarSesionConTeclado(page, base, correo, clave) {
  await page.goto(`${base}/iniciar-sesion`)
  await page.waitForLoadState('networkidle')
  // Tab hasta el campo del correo, sin usar el mouse.
  for (let i = 0; i < MAXIMO_TABS; i += 1) {
    await page.keyboard.press('Tab')
    if (await page.evaluate(() => document.activeElement?.getAttribute('name') === 'correo')) break
  }
  await page.keyboard.type(correo)
  await page.keyboard.press('Tab')
  if (!(await page.evaluate(() => document.activeElement?.getAttribute('name') === 'contrasenia'))) {
    // Puede haber un control intermedio; se busca la contraseña con Tab.
    for (let i = 0; i < 5; i += 1) {
      await page.keyboard.press('Tab')
      if (await page.evaluate(() => document.activeElement?.getAttribute('name') === 'contrasenia')) break
    }
  }
  await page.keyboard.type(clave)
  await page.keyboard.press('Enter')
  await page.waitForURL((url) => !url.pathname.startsWith('/iniciar-sesion'), { timeout: 15000 })
}

async function principal() {
  const base = process.argv[2] || 'http://localhost:5173'
  const correo = process.env.SENSOR_CORREO
  const clave = process.env.SENSOR_CLAVE
  const navegador = await chromium.launch()
  const contexto = await navegador.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' })
  const page = await contexto.newPage()
  let errores = 0
  let conSesion = false
  for (const pantalla of PANTALLAS) {
    if (pantalla.sesion && !conSesion) {
      if (!correo || !clave) continue
      try {
        await iniciarSesionConTeclado(page, base, correo, clave)
        console.log('inicio de sesión solo con el teclado: ok')
      } catch (error) {
        console.log(`    ERROR no se pudo iniciar sesión solo con el teclado: ${error.message.split('\n')[0]}`)
        errores += 1
        break
      }
      conSesion = true
    }
    await page.goto(base + pantalla.ruta)
    await page.waitForLoadState('networkidle')
    errores += await recorrer(page, pantalla.ruta)
  }
  await navegador.close()
  console.log(errores ? `\n${errores} problemas de uso con teclado.` : '\nSin problemas de uso con teclado.')
  process.exitCode = errores ? 1 : 0
}

principal().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
