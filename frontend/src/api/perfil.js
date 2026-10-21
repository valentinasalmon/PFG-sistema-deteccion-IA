/**
 * Operaciones sobre el perfil propio.
 *
 * Realiza: RF06 a RF09.
 */
import { definirTokenCsrf, solicitar } from './cliente.js'

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

/** Genera los enlaces de descarga de la copia de mis datos (RF09). */
export function solicitarCopiaDeDatos() {
  return solicitar('POST', '/api/perfil/copia')
}

/** Casos y organizaciones que hay que resolver antes de eliminar la cuenta (RF08). */
export function situacionParaBaja() {
  return solicitar('GET', '/api/perfil/baja')
}

/**
 * Elimina la cuenta propia confirmando con la contraseña (RF08). El servidor
 * cierra la sesión, así que se descarta el token CSRF de esa sesión.
 */
export async function eliminarCuenta(contrasenia) {
  const respuesta = await solicitar('DELETE', '/api/perfil', { contrasenia })
  definirTokenCsrf(null)
  return respuesta
}

/** Plan y consumo del espacio personal (RF20, funcionalidad 014). */
export async function obtenerPlanPersonal() {
  const { plan } = await solicitar('GET', '/api/perfil/plan')
  return plan
}
