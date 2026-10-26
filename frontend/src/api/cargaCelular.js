/**
 * Carga de fotos desde el celular con un enlace de un solo uso (funcionalidad 024).
 *
 * La computadora genera el enlace (con su código QR) y lo cancela; el celular
 * lo usa sin iniciar sesión: el token del enlace es la credencial.
 *
 * Realiza: RF53 (CA2).
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

/** Datos para la página del celular: número de caso, vencimiento y fotos restantes. */
export function consultarEnlaceCarga(token) {
  return solicitar('GET', `/api/carga/${encodeURIComponent(token)}`)
}

/** Sube una foto con el enlace; cada archivo va en su propia solicitud. */
export function cargarConEnlace(token, archivo) {
  const formulario = new FormData()
  formulario.append('archivo', archivo)
  return solicitar('POST', `/api/carga/${encodeURIComponent(token)}`, formulario)
}
