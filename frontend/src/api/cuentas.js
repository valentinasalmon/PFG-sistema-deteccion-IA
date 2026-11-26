/**
 * Operaciones de cuenta que no requieren sesión: registro, verificación del
 * correo y recuperación de la contraseña.
 *
 * Los pedidos que cualquiera puede enviar llevan el token de reCAPTCHA (051).
 *
 * Realiza: RF01, RF02, RF05; 051.
 */
import { solicitar } from './cliente.js'
import { cabecerasRecaptcha } from './recaptcha.js'

/** Crea una cuenta pendiente de verificación (RF01). */
export async function registrarCuenta(datos) {
  return solicitar('POST', '/api/cuentas/registro', datos, await cabecerasRecaptcha('registro'))
}

/** Activa la cuenta con el token del enlace recibido por correo (RF02). */
export function verificarCorreo(token) {
  return solicitar('POST', '/api/cuentas/verificacion', { token })
}

/** Pide que se reenvíe el correo de verificación (RF02). */
export async function reenviarVerificacion(correo) {
  const cabeceras = await cabecerasRecaptcha('reenvio_verificacion')
  return solicitar('POST', '/api/cuentas/verificacion/reenvio', { correo }, cabeceras)
}

/** Pide el enlace para restablecer la contraseña (RF05). */
export async function solicitarRecuperacion(correo) {
  const cabeceras = await cabecerasRecaptcha('recuperacion')
  return solicitar('POST', '/api/cuentas/recuperacion', { correo }, cabeceras)
}

/** Define una contraseña nueva con el token del enlace de recuperación (RF05). */
export function restablecerContrasenia(token, contrasenia) {
  return solicitar('POST', '/api/cuentas/recuperacion/restablecer', { token, contrasenia })
}

/** Aseguradoras habilitadas por la SSN, para registrar una aseguradora (funcionalidad 021). */
export async function listarAseguradoras() {
  const { aseguradoras } = await solicitar('GET', '/api/catalogos/aseguradoras')
  return aseguradoras
}
