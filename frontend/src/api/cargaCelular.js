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

/** Datos para la página del enlace: tipo, vencimiento, fotos restantes y caso o solicitante. */
export function consultarEnlaceCarga(token) {
  return solicitar('GET', `/api/carga/${encodeURIComponent(token)}`)
}

/**
 * Sube una foto con el enlace; cada archivo va en su propia solicitud. La
 * persona afectada envía además que aceptó la declaración (CP-32).
 */
export function cargarConEnlace(token, archivo, declaracion = false) {
  const formulario = new FormData()
  formulario.append('archivo', archivo)
  if (declaracion) formulario.append('declaracion', 'true')
  return solicitar('POST', `/api/carga/${encodeURIComponent(token)}`, formulario)
}
