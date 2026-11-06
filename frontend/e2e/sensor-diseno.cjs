// Sensor de diseño (arnés, 037): recorre pantallas en computadora y en celular y
// falla si encuentra problemas de maquetación que una persona notaría a simple vista.
//
// Qué detecta, en cada pantalla y en cada ancho:
//   - desplazamiento horizontal de la página (algo más ancho que la pantalla);
//   - contenido cortado: un elemento cuyo texto o hijos se salen de su caja
//     (por ejemplo, un nombre largo que se sale de un resumen);
//   - contenido escondido: un contenedor con desplazamiento propio que oculta
//     más de un tercio de lo que tiene (por ejemplo, un pago dentro de una
//     tarjeta de alto fijo, con el botón principal fuera de la vista);
//   - controles fuera de la pantalla (botones o enlaces que empiezan o terminan
//     fuera del ancho visible);
//   - botones o campos de menos de 40 px de alto (objetivo táctil).
//
// Uso (con el entorno local levantado):
//   node sensor-diseno.cjs [base] [archivo de pantallas]
// Variables opcionales: SENSOR_CORREO y SENSOR_CLAVE para las pantallas con
// sesión. El archivo de pantallas es un JSON con [{ "ruta": "/...", "sesion": true }].
// También se puede importar `revisarPagina(page)` desde otros recorridos.
//
// Sale con código 1 si hay errores (las advertencias no lo hacen fallar).

const ANCHOS = [
  { nombre: 'pc', width: 1440, height: 900 },
  { nombre: 'cel', width: 390, height: 844 },
]

const PANTALLAS_POR_DEFECTO = [
  { ruta: '/' },
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
  { ruta: '/perfil', sesion: true },
]

/** Revisa la página abierta y devuelve la lista de problemas encontrados. */
async function revisarPagina(page) {
  return page.evaluate(() => {
    const problemas = []
    const anchoVista = document.documentElement.clientWidth
    const describir = (el) => {
      const clase = typeof el.className === 'string' && el.className ? `.${el.className.trim().split(/\s+/).slice(0, 2).join('.')}` : ''
      const texto = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 50)
      return `${el.tagName.toLowerCase()}${clase}${texto ? ` «${texto}»` : ''}`
    }
    const visible = (el) => {
      const estilo = getComputedStyle(el)
      if (estilo.display === 'none' || estilo.visibility === 'hidden' || el.closest('[hidden], .solo-lectores')) return false
      const caja = el.getBoundingClientRect()
      // Los textos solo para lectores de pantalla miden 1 px a propósito.
      const soloLectores = estilo.clip !== 'auto' || estilo.clipPath !== 'none' || caja.width <= 4 || caja.height <= 4
      return caja.width > 0 && caja.height > 0 && !soloLectores
    }

    if (document.documentElement.scrollWidth > anchoVista + 1) {
      problemas.push({ gravedad: 'error', tipo: 'desplazamiento-horizontal', detalle: `la página mide ${document.documentElement.scrollWidth}px de ancho en una pantalla de ${anchoVista}px` })
    }

    for (const el of document.querySelectorAll('body *')) {
      if (!visible(el) || ['svg', 'path', 'img', 'canvas', 'input', 'textarea', 'select', 'option', 'pre', 'code'].includes(el.tagName.toLowerCase())) continue
      const estilo = getComputedStyle(el)
      const desplazable = (valor) => valor === 'auto' || valor === 'scroll'

      // Contenido escondido en un contenedor con desplazamiento propio.
      if (desplazable(estilo.overflowY) && el.scrollHeight > el.clientHeight * 1.34 && el.clientHeight > 120 && !el.matches('[role="listbox"], [role="dialog"], .combo__lista, table, .tabla-contenedor')) {
        problemas.push({ gravedad: 'error', tipo: 'contenido-escondido', detalle: `${describir(el)} muestra ${el.clientHeight}px de ${el.scrollHeight}px` })
      }

      // Contenido cortado: se sale de su caja sin poder desplazarse.
      if (!desplazable(estilo.overflowX) && el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0 && estilo.textOverflow !== 'ellipsis') {
        const hijos = [...el.children].filter(visible)
        const caja = el.getBoundingClientRect()
        const sale = hijos.some((hijo) => hijo.getBoundingClientRect().right > caja.right + 2) || (!hijos.length && el.scrollWidth > el.clientWidth + 2)
        if (sale && estilo.overflowX === 'hidden') {
          problemas.push({ gravedad: 'error', tipo: 'contenido-cortado', detalle: `${describir(el)}: ${el.scrollWidth}px de contenido en ${el.clientWidth}px` })
        }
      }

      // Controles fuera de la pantalla o demasiado chicos.
      if (el.matches('button, a.boton, [role="button"], input:not([type="checkbox"]):not([type="radio"]):not([type="file"]), select')) {
        const caja = el.getBoundingClientRect()
        if (caja.right > anchoVista + 1 || caja.left < -1) {
          problemas.push({ gravedad: 'error', tipo: 'control-fuera-de-pantalla', detalle: `${describir(el)} va de ${Math.round(caja.left)} a ${Math.round(caja.right)}px` })
        }
        if (caja.height < 40 && !el.matches('.boton-enlace, .pie a, [class*="copiar"], .combo__limpiar')) {
          problemas.push({ gravedad: 'advertencia', tipo: 'objetivo-tactil-chico', detalle: `${describir(el)} mide ${Math.round(caja.height)}px de alto` })
        }
      }
    }
    return problemas
  })
}

async function principal() {
  const { chromium } = require('playwright')
  const [,, base = 'http://localhost:5173', archivo] = process.argv
  const pantallas = archivo ? JSON.parse(require('fs').readFileSync(archivo, 'utf8')) : PANTALLAS_POR_DEFECTO
  const correo = process.env.SENSOR_CORREO
  const clave = process.env.SENSOR_CLAVE
  const navegador = await chromium.launch()
  let errores = 0
  for (const ancho of ANCHOS) {
    for (const conSesion of [false, true]) {
      const lista = pantallas.filter((p) => Boolean(p.sesion) === conSesion)
      if (!lista.length || (conSesion && !correo)) continue
      const contexto = await navegador.newContext({ viewport: { width: ancho.width, height: ancho.height } })
      const page = await contexto.newPage()
      if (conSesion) {
        await page.goto(`${base}/iniciar-sesion`)
        await page.fill('input[name=correo]', correo)
        await page.fill('input[name=contrasenia]', clave)
        await page.click('button[type=submit]')
        await page.waitForTimeout(1500)
      }
      for (const pantalla of lista) {
        await page.goto(base + pantalla.ruta)
        await page.waitForLoadState('networkidle').catch(() => {})
        await page.waitForTimeout(600)
        const problemas = await revisarPagina(page)
        const propios = problemas.filter((p) => p.gravedad === 'error')
        errores += propios.length
        const marca = propios.length ? 'FALLA' : 'ok   '
        console.log(`${marca} ${ancho.nombre.padEnd(3)} ${pantalla.ruta}${conSesion ? ' (con sesión)' : ''}`)
        for (const problema of problemas) console.log(`      ${problema.gravedad === 'error' ? '✗' : '·'} ${problema.tipo}: ${problema.detalle}`)
      }
      await contexto.close()
    }
  }
  await navegador.close()
  console.log(errores ? `\n${errores} problemas de diseño.` : '\nSin problemas de diseño.')
  process.exit(errores ? 1 : 0)
}

module.exports = { revisarPagina }
if (require.main === module) principal()
