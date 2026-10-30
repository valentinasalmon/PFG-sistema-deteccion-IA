/**
 * Carga de Microsoft Clarity para que la autora revise el uso real antes del
 * lanzamiento (mapas de calor y grabaciones de sesión).
 *
 * Solo se activa si al compilar se definió ``VITE_CLARITY_ID`` (en el
 * despliegue sale de la variable ``CLARITY_ID`` de GitHub). Sin ese valor no
 * se carga nada. Con él, todo el contenido de la página queda enmascarado
 * (``data-clarity-mask``): Clarity ve dónde se hace clic y cómo se recorre la
 * pantalla, pero no los textos, los datos de los casos ni las fotos (Ley
 * 25.326). No muestra nada a los usuarios.
 *
 * Realiza: CA8 de la funcionalidad 034; CP-33.
 */

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
export function iniciarClarity(id = import.meta.env.VITE_CLARITY_ID, documento = document) {
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
