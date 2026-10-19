/**
 * Cliente HTTP común para hablar con la API del backend.
 *
 * Centraliza tres cosas que todas las solicitudes necesitan:
 * - Enviar y recibir JSON, con la cookie de sesión incluida.
 * - Adjuntar el token CSRF en la cabecera X-CSRFToken a toda solicitud que
 *   modifica datos (RNF02 CA3). El token se pide una sola vez y se renueva si
 *   el backend lo rechaza.
 * - Convertir las respuestas de error en un ErrorApi con el mensaje en español
 *   que envía el backend, y avisar cuando la sesión venció (CA12, CA22).
 *
 * Realiza: RNF02 (CA3) y CA21, CA22 de la funcionalidad 002.
 */

const METODOS_QUE_MODIFICAN = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

let tokenCsrf = null
let alExpirarSesion = null

/** Error de la API con el detalle que devuelve el backend. */
export class ErrorApi extends Error {
  /**
   * @param {number} estado código HTTP.
   * @param {{mensaje?: string, codigo?: string, errores?: Object<string, string>}} cuerpo
   */
  constructor(estado, cuerpo = {}) {
    super(cuerpo.mensaje ?? 'Ocurrió un error inesperado. Intentá de nuevo.')
    this.name = 'ErrorApi'
    this.estado = estado
    this.codigo = cuerpo.codigo ?? 'error'
    this.errores = cuerpo.errores ?? {}
  }
}

/**
 * Registra la función que se ejecuta cuando una solicitud responde que la
 * sesión no existe o venció. La usa el proveedor de sesión para volver al
 * inicio de sesión.
 *
 * @param {(() => void) | null} funcion
 */
export function configurarAlExpirarSesion(funcion) {
  alExpirarSesion = funcion
}

/**
 * Guarda el token CSRF recibido (por ejemplo, en la respuesta del inicio de
 * sesión) o lo descarta con null para que se pida uno nuevo.
 *
 * @param {string | null} token
 */
export function definirTokenCsrf(token) {
  tokenCsrf = token
}

async function obtenerTokenCsrf() {
  if (!tokenCsrf) {
    const respuesta = await fetch('/api/sesion/csrf', { credentials: 'same-origin' })
    tokenCsrf = (await respuesta.json()).csrf
  }
  return tokenCsrf
}

async function leerCuerpo(respuesta) {
  try {
    return await respuesta.json()
  } catch {
    return {}
  }
}

async function enviar(metodo, ruta, datos) {
  const cabeceras = { Accept: 'application/json' }
  if (datos !== undefined) cabeceras['Content-Type'] = 'application/json'
  if (METODOS_QUE_MODIFICAN.has(metodo)) cabeceras['X-CSRFToken'] = await obtenerTokenCsrf()

  let respuesta
  try {
    respuesta = await fetch(ruta, {
      method: metodo,
      headers: cabeceras,
      credentials: 'same-origin',
      body: datos === undefined ? undefined : JSON.stringify(datos),
    })
  } catch {
    throw new ErrorApi(0, {
      mensaje: 'No se pudo conectar con el servidor. Revisá tu conexión.',
      codigo: 'sin_conexion',
    })
  }
  return { respuesta, cuerpo: await leerCuerpo(respuesta) }
}

/**
 * Realiza una solicitud a la API.
 *
 * @param {string} metodo GET, POST, PATCH o DELETE.
 * @param {string} ruta por ejemplo, '/api/sesion'.
 * @param {Object} [datos] cuerpo a enviar como JSON.
 * @returns {Promise<Object>} el cuerpo JSON de la respuesta.
 * @throws {ErrorApi} si la respuesta no es exitosa.
 */
export async function solicitar(metodo, ruta, datos) {
  let { respuesta, cuerpo } = await enviar(metodo, ruta, datos)

  // El token CSRF pudo vencer (por ejemplo, al cerrarse la sesión): se pide
  // uno nuevo y se reintenta una sola vez.
  if (respuesta.status === 400 && cuerpo.codigo === 'csrf_invalido') {
    tokenCsrf = null
    ;({ respuesta, cuerpo } = await enviar(metodo, ruta, datos))
  }

  if (!respuesta.ok) {
    if (respuesta.status === 401 && cuerpo.codigo === 'sesion_requerida' && alExpirarSesion) {
      alExpirarSesion()
    }
    throw new ErrorApi(respuesta.status, cuerpo)
  }
  return cuerpo
}
