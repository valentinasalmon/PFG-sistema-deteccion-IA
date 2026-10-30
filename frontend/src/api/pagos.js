/**
 * Pago del plan por transferencia (funcionalidad 032).
 *
 * La página de pago no usa sesión: el token del enlace es la credencial,
 * porque el pago se hace al final del registro, antes de verificar el correo.
 * Mientras no esté la API de Cresium, la acreditación se simula.
 *
 * Realiza: RF20 (CA2); CP-34.
 */
import { solicitar } from './cliente.js'

/** Planes de las organizaciones con sus límites; precio vacío = «A confirmar». */
export function listarPlanes() {
  return solicitar('GET', '/api/catalogos/planes')
}

/** Plan, organización, CVU, alias, referencia y estado del cobro del enlace. */
export async function consultarCobro(token) {
  const { cobro } = await solicitar('GET', `/api/pagos/${encodeURIComponent(token)}`)
  return cobro
}

/** Simula la acreditación de la transferencia (pago simulado). */
export async function simularPago(token) {
  const { cobro } = await solicitar('POST', `/api/pagos/${encodeURIComponent(token)}/simulacion`)
  return cobro
}
