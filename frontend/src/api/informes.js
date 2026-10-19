/**
 * Operaciones sobre los informes PDF de un caso (funcionalidad 008).
 *
 * Realiza: RF44, RF45.
 */
import { abrirDescarga } from '../utilidades/archivos.js'
import { solicitar } from './cliente.js'

/** Informes del caso, del más reciente al más antiguo (RF45). */
export async function listarInformes(idCaso) {
  const { informes } = await solicitar('GET', `/api/casos/${idCaso}/informes`)
  return informes
}

/** Enlace firmado de 5 minutos para descargar el PDF (RF45 CA2). */
export async function enlaceDeInforme(idCaso, idInforme) {
  const { url } = await solicitar('GET', `/api/casos/${idCaso}/informes/${idInforme}/descarga`)
  return url
}

/** Vuelve a generar el informe de un análisis que no lo tiene. */
export function regenerarInforme(idCaso, idAnalisis) {
  return solicitar('POST', `/api/casos/${idCaso}/analisis/${idAnalisis}/informe`)
}

/** Pide el enlace firmado y abre la descarga del PDF. */
export async function descargarInforme(idCaso, idInforme) {
  abrirDescarga(await enlaceDeInforme(idCaso, idInforme))
}
