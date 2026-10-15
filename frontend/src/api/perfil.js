/**
 * Operaciones sobre el perfil propio.
 *
 * Realiza: RF06, RF07.
 */
import { solicitar } from './cliente.js'

/** Actualiza nombre, apellido y colegio o empresa (RF07). */
export async function actualizarPerfil(cambios) {
  const { usuario } = await solicitar('PATCH', '/api/perfil', cambios)
  return usuario
}

/** Cambia la contraseña indicando la actual (RF06). */
export function cambiarContrasenia(contraseniaActual, contraseniaNueva) {
  return solicitar('POST', '/api/perfil/contrasenia', {
    contrasenia_actual: contraseniaActual,
    contrasenia_nueva: contraseniaNueva,
  })
}

/** Pide el cambio de correo; se confirma desde la dirección nueva (RF07). */
export function solicitarCambioCorreo(correoNuevo, contrasenia) {
  return solicitar('POST', '/api/perfil/correo', { correo_nuevo: correoNuevo, contrasenia })
}

/** Confirma el correo nuevo con el token del enlace recibido. */
export function confirmarCambioCorreo(token) {
  return solicitar('POST', '/api/perfil/correo/confirmacion', { token })
}
