/**
 * Operaciones de cuenta que no requieren sesión: registro, verificación del
 * correo y recuperación de la contraseña.
 *
 * Realiza: RF01, RF02, RF05.
 */
import { solicitar } from './cliente.js'

/** Crea una cuenta pendiente de verificación (RF01). */
export function registrarCuenta(datos) {
  return solicitar('POST', '/api/cuentas/registro', datos)
}

/** Activa la cuenta con el token del enlace recibido por correo (RF02). */
export function verificarCorreo(token) {
  return solicitar('POST', '/api/cuentas/verificacion', { token })
}

/** Pide que se reenvíe el correo de verificación (RF02). */
export function reenviarVerificacion(correo) {
  return solicitar('POST', '/api/cuentas/verificacion/reenvio', { correo })
}

/** Pide el enlace para restablecer la contraseña (RF05). */
export function solicitarRecuperacion(correo) {
  return solicitar('POST', '/api/cuentas/recuperacion', { correo })
}

/** Define una contraseña nueva con el token del enlace de recuperación (RF05). */
export function restablecerContrasenia(token, contrasenia) {
  return solicitar('POST', '/api/cuentas/recuperacion/restablecer', { token, contrasenia })
}
