/**
 * Operaciones del Administrador de la plataforma (funcionalidad 021).
 *
 * Realiza: RN38 (aprobación de aseguradoras).
 */
import { solicitar } from './cliente.js'

/** Aseguradoras pendientes de aprobación, con su Referente. */
export async function listarAseguradorasPendientes() {
  const { aseguradoras } = await solicitar('GET', '/api/administracion/aseguradoras-pendientes')
  return aseguradoras
}

/** Aprueba una aseguradora pendiente. */
export function aprobarAseguradora(id) {
  return solicitar('POST', `/api/administracion/organizaciones/${id}/aprobacion`)
}

/** Rechaza una aseguradora pendiente indicando el motivo, que se informa a su Referente. */
export function rechazarAseguradora(id, motivo) {
  return solicitar('POST', `/api/administracion/organizaciones/${id}/rechazo`, { motivo })
}
