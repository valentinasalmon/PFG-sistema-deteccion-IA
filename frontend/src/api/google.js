/**
 * Inicio de sesión y registro con Google (funcionalidad 027).
 *
 * El inicio no es una llamada de la API: el navegador navega a
 * /api/google/inicio, que lo lleva a Google, y Google lo devuelve a la
 * plataforma. Las llamadas de acá son las del paso "completar el registro".
 *
 * Realiza: RF52.
 */
import { definirTokenCsrf, solicitar } from './cliente.js'

/** True si la plataforma tiene configurado el inicio con Google. */
export async function googleHabilitado() {
  const { habilitado } = await solicitar('GET', '/api/google/estado')
  return habilitado
}

/** Dirección que inicia el flujo; con una invitación, la conserva para el registro. */
export function urlInicioGoogle(invitacion) {
  const base = '/api/google/inicio'
  return invitacion ? `${base}?invitacion=${encodeURIComponent(invitacion)}` : base
}

/** Nombre, apellido y correo que informó Google, para completar el registro. */
export function obtenerRegistroGoogle() {
  return solicitar('GET', '/api/google/registro')
}

/**
 * Crea la cuenta con el perfil, la institución y los Términos aceptados, e
 * inicia sesión. Guarda el token CSRF de la sesión nueva.
 *
 * @returns {Promise<Object>} el usuario autenticado.
 */
export async function completarRegistroGoogle(datos) {
  const { usuario, csrf } = await solicitar('POST', '/api/google/registro', datos)
  definirTokenCsrf(csrf)
  return usuario
}
