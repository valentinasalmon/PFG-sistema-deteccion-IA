/**
 * Carga de Microsoft Clarity para que la autora revise el uso real antes del
 * lanzamiento (mapas de calor y grabaciones de sesión).
 *
 * Se activa solo en la compilación de producción (la que se despliega en
 * AWS), con el proyecto de la autora (``ID_PROYECTO``); en desarrollo y en las
 * pruebas no se carga. ``VITE_CLARITY_ID`` permite compilar con otro
 * proyecto (vacía, sin Clarity). Todo el contenido de la página queda enmascarado
 * (``data-clarity-mask``): Clarity ve dónde se hace clic y cómo se recorre la
 * pantalla, pero no los textos, los datos de los casos ni las fotos (Ley
 * 25.326). No muestra nada a los usuarios.
 *
 * Realiza: CA8 de la funcionalidad 034; funcionalidad 031; CP-33.
 */

/** Proyecto de Clarity de evidentIA (no es secreto: queda a la vista en la página). */
export const ID_PROYECTO = 'z5vsmarsef'

/** Identificador que corresponde a esta compilación: ninguno fuera de producción. */
function idDeLaCompilacion() {
  if (!import.meta.env.PROD) return undefined
  return import.meta.env.VITE_CLARITY_ID ?? ID_PROYECTO
}

const ORIGEN = 'https://www.clarity.ms/tag/'

/** Identificador válido de un proyecto de Clarity: letras minúsculas y números. */
const FORMATO_ID = /^[a-z0-9]{6,20}$/

/**
 * Inyecta el script de Clarity si hay un identificador válido.
 *
 * @param {string | undefined} id identificador del proyecto; por defecto, el de la compilación.
 * @param {Document} documento documento donde se inyecta (para las pruebas).
 * @returns {boolean} si se cargó.
 */
export function iniciarClarity(id = idDeLaCompilacion(), documento = document) {
  if (!id || !FORMATO_ID.test(id)) return false
  if (documento.querySelector(`script[src="${ORIGEN}${id}"]`)) return true
  const ventana = documento.defaultView
  ventana.clarity =
    ventana.clarity ||
    function encolar(...argumentos) {
      ;(ventana.clarity.q = ventana.clarity.q || []).push(argumentos)
    }
  documento.body.setAttribute('data-clarity-mask', 'true')
  const script = documento.createElement('script')
  script.async = true
  script.src = `${ORIGEN}${id}`
  documento.head.appendChild(script)
  return true
}
