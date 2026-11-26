/**
 * reCAPTCHA de Google en los formularios públicos (funcionalidad 051).
 *
 * La clave del sitio no se compila en el frontend: se pide al backend
 * (``/api/recaptcha/configuracion``) la primera vez que hace falta, y recién
 * entonces se carga el script de Google, así la portada y el resto de la
 * plataforma no lo descargan. Sin reCAPTCHA configurado no se carga nada.
 *
 * El token se pide justo al enviar el formulario (vence a los dos minutos y
 * sirve una sola vez) y viaja en la cabecera ``X-Recaptcha``.
 *
 * Realiza: RNF02; 051.
 */
import { solicitar } from './cliente.js'

const URL_SCRIPT = 'https://www.google.com/recaptcha/enterprise.js'

let configuracion = null
let script = null

function cargarScript(clave) {
  if (!script) {
    script = new Promise((resolver, rechazar) => {
      const etiqueta = document.createElement('script')
      etiqueta.src = `${URL_SCRIPT}?render=${encodeURIComponent(clave)}`
      etiqueta.async = true
      etiqueta.onload = () => window.grecaptcha.enterprise.ready(resolver)
      etiqueta.onerror = () => {
        script = null
        rechazar(new Error('No se pudo cargar reCAPTCHA.'))
      }
      document.head.appendChild(etiqueta)
    })
  }
  return script
}

/**
 * Cabeceras con el token de reCAPTCHA para la acción, o vacías si está
 * desactivado o no se pudo obtener (el backend responde con un mensaje claro).
 *
 * @param {'registro'|'inicio_sesion'|'recuperacion'|'reenvio_verificacion'} accion
 * @returns {Promise<Object<string, string>>}
 */
export async function cabecerasRecaptcha(accion) {
  try {
    configuracion ??= solicitar('GET', '/api/recaptcha/configuracion')
    const { habilitado, clave_sitio: clave } = await configuracion
    if (!habilitado || !clave) return {}
    await cargarScript(clave)
    const token = await window.grecaptcha.enterprise.execute(clave, { action: accion })
    return { 'X-Recaptcha': token }
  } catch {
    configuracion = null
    return {}
  }
}

/** Solo para las pruebas: olvida la configuración y el script cargados. */
export function reiniciarRecaptcha() {
  configuracion = null
  script = null
}
