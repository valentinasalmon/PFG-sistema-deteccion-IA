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

/** Indicadores agregados de la plataforma, con un rango opcional (RF21, funcionalidad 014). */
export async function obtenerTablero({ desde = '', hasta = '' } = {}) {
  const consulta = new URLSearchParams(Object.entries({ desde, hasta }).filter(([, v]) => v))
  const { tablero } = await solicitar('GET', `/api/administracion/tablero?${consulta}`)
  return tablero
}

/** Listado paginado de cuentas o de organizaciones, de solo lectura (RF22). */
export function listarParaAdministracion(recurso, filtros = {}) {
  const consulta = new URLSearchParams(Object.entries(filtros).filter(([, v]) => v))
  return solicitar('GET', `/api/administracion/${recurso}?${consulta}`)
}
