/**
 * Página pública de la verificación de identidad (funcionalidad 035).
 *
 * No usa sesión: el token del enlace es la credencial, como en el pago. Mientras
 * no esté conectado Identik, el resultado se simula desde esa página.
 *
 * Realiza: RN41; CP-35.
 */
import { solicitar } from './cliente.js'

/** Aseguradora, estado y si la verificación del enlace es simulada. */
export async function consultarVerificacion(token) {
  const { verificacion } = await solicitar('GET', `/api/identidad/${encodeURIComponent(token)}`)
  return verificacion
}

/** Registra un resultado simulado: «aprobada» o «rechazada». */
export async function simularVerificacion(token, resultado) {
  const { verificacion } = await solicitar(
    'POST',
    `/api/identidad/${encodeURIComponent(token)}/simulacion`,
    { resultado },
  )
  return verificacion
}
