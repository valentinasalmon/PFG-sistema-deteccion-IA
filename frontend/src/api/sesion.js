/**
 * Inicio, consulta y cierre de la sesión.
 *
 * Realiza: RF03, RF04.
 */
import { definirTokenCsrf, ErrorApi, solicitar } from './cliente.js'

/**
 * Inicia sesión y guarda el token CSRF asociado a la sesión nueva.
 *
 * @returns {Promise<Object>} el usuario autenticado.
 */
export async function iniciarSesion(correo, contrasenia) {
  const { usuario, csrf } = await solicitar('POST', '/api/sesion', { correo, contrasenia })
  definirTokenCsrf(csrf)
  return usuario
}

/**
 * Devuelve el usuario de la sesión actual, o null si no hay sesión.
 */
export async function obtenerSesion() {
  try {
    const { usuario } = await solicitar('GET', '/api/sesion')
    return usuario
  } catch (error) {
    if (error instanceof ErrorApi && error.estado === 401) return null
    throw error
  }
}

/** Cierra la sesión; el token CSRF anterior deja de valer. */
export async function cerrarSesion() {
  try {
    await solicitar('DELETE', '/api/sesion')
  } finally {
    definirTokenCsrf(null)
  }
}
