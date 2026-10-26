/**
 * Panel principal (funcionalidad 013).
 *
 * Realiza: RF48.
 */
import { solicitar } from './cliente.js'

/** Resumen de casos, pendientes y actividad reciente del usuario. */
export async function obtenerPanel() {
  const { panel } = await solicitar('GET', '/api/panel')
  return panel
}
