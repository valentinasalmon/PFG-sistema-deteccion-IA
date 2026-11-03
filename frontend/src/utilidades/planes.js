/**
 * Utilidades de los planes de las organizaciones (funcionalidad 032).
 *
 * Realiza: RF20.
 */

/** Texto del precio de un plan: «A confirmar» mientras no esté definido. */
export function textoDelPrecio(precio) {
  return precio ?? 'A confirmar'
}

/** Nombre corto de un plan de organización a partir de su código. */
export const NOMBRES_DE_PLAN = { basico: 'Básico', profesional: 'Profesional' }
