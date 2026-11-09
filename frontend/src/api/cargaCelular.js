/**
 * Carga de fotos con un enlace, sin iniciar sesión (funcionalidades 024 y 028).
 *
 * La computadora genera el enlace del celular (con su código QR) y lo
 * cancela; el celular lo usa sin iniciar sesión: el token del enlace es la
 * credencial. Desde la 028 también hay enlaces para que la persona afectada
 * suba sus propias fotos, que se crean, se listan y se anulan desde el caso.
 *
 * Realiza: RF53 (CA2); CP-32.
 */
import { solicitar } from './cliente.js'

/** Genera el enlace de carga del caso: URL, QR (data URI), vencimiento y máximo de fotos. */
export async function crearEnlaceCarga(idCaso) {
  const { enlace } = await solicitar('POST', `/api/casos/${idCaso}/enlace-carga`)
  return enlace
}

/** Cancela los enlaces de carga vigentes del usuario para el caso. */
export function cancelarEnlaceCarga(idCaso) {
  return solicitar('DELETE', `/api/casos/${idCaso}/enlace-carga`)
}

/** Enlaces vigentes para la persona afectada del caso y la vigencia máxima en días. */
export function listarEnlacesPersonaAfectada(idCaso) {
  return solicitar('GET', `/api/casos/${idCaso}/enlaces-persona-afectada`)
}

/** Crea un enlace para la persona afectada; la URL solo se recibe en este momento. */
export function crearEnlacePersonaAfectada(idCaso, dias, destinatario) {
  return solicitar('POST', `/api/casos/${idCaso}/enlaces-persona-afectada`, { dias, destinatario })
}

/** Anula un enlace para la persona afectada: deja de servir en el momento. */
export function anularEnlacePersonaAfectada(idCaso, idEnlace) {
  return solicitar('DELETE', `/api/casos/${idCaso}/enlaces-persona-afectada/${idEnlace}`)
}

/**
 * Clave del celular al que quedó atado el QR (038): el servidor la da con la
 * primera foto que sube y este celular la presenta en cada paso.
 * Se guarda solo durante la pestaña.
 */
function claveDe(token) {
  try {
    return sessionStorage.getItem(`evidentia.carga.${token}`)
  } catch {
    return null
  }
}

function guardarClave(token, clave) {
  try {
    sessionStorage.setItem(`evidentia.carga.${token}`, clave)
  } catch {
    // Sin almacenamiento: el enlace se puede usar mientras la página siga abierta.
  }
}

function cabecerasDe(token) {
  const clave = claveDe(token)
  return clave ? { 'X-Clave-Dispositivo': clave } : {}
}

/** Datos para la página del enlace: tipo, vencimiento, fotos restantes y caso o solicitante. */
export function consultarEnlaceCarga(token) {
  return solicitar('GET', `/api/carga/${encodeURIComponent(token)}`, undefined, cabecerasDe(token))
}

/** El celular terminó de subir fotos: el QR se cierra (038). */
export function terminarCargaConEnlace(token) {
  return solicitar('POST', `/api/carga/${encodeURIComponent(token)}/fin`, undefined, cabecerasDe(token))
}

/** Si el QR del caso sigue abierto o el celular ya terminó (038). */
export async function estadoEnlaceCarga(idCaso) {
  const { enlace } = await solicitar('GET', `/api/casos/${idCaso}/enlace-carga`)
  return enlace
}

/**
 * Sube una foto con el enlace; cada archivo va en su propia solicitud. La
 * persona afectada envía además que aceptó la declaración (CP-32).
 */
export async function cargarConEnlace(token, archivo, declaracion = false) {
  const formulario = new FormData()
  formulario.append('archivo', archivo)
  if (declaracion) formulario.append('declaracion', 'true')
  const respuesta = await solicitar('POST', `/api/carga/${encodeURIComponent(token)}`, formulario, cabecerasDe(token))
  if (respuesta.clave_dispositivo) guardarClave(token, respuesta.clave_dispositivo)
  return respuesta
}
