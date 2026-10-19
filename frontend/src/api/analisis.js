/**
 * Operaciones sobre los análisis de un caso (funcionalidad 007).
 *
 * Realiza: RF38, RF43, RF46.
 */
import { solicitar } from './cliente.js'

const base = (idCaso) => `/api/casos/${idCaso}/analisis`

/** Pide el análisis de las imágenes elegidas; queda en cola (RF38). */
export function solicitarAnalisis(idCaso, idsImagenes) {
  return solicitar('POST', base(idCaso), { imagenes: idsImagenes })
}

/** Historial de análisis del caso, del más reciente al más antiguo. */
export async function listarAnalisis(idCaso) {
  const { analisis } = await solicitar('GET', base(idCaso))
  return analisis
}

/** Estado, progreso y resultados de cada capa por imagen (RF43, RF46). */
export async function obtenerAnalisis(idCaso, idAnalisis) {
  const { analisis } = await solicitar('GET', `${base(idCaso)}/${idAnalisis}`)
  return analisis
}
