/**
 * Períodos rápidos del tablero de administración (funcionalidad 028).
 *
 * Realiza: RF21 (interfaz).
 */

const aIso = (fecha) =>
  `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`

/**
 * Rango de fechas de cada período rápido, hasta hoy inclusive.
 *
 * @param {'mes' | 'trimestre' | 'anio' | 'inicio'} periodo "inicio" es sin límites.
 * @param {Date} [hoy]
 * @returns {{desde: string, hasta: string}} fechas ISO (``AAAA-MM-DD``) o vacías.
 */
export function rangoDelPeriodo(periodo, hoy = new Date()) {
  const hasta = aIso(hoy)
  if (periodo === 'mes') return { desde: aIso(new Date(hoy.getFullYear(), hoy.getMonth(), 1)), hasta }
  if (periodo === 'trimestre') {
    return { desde: aIso(new Date(hoy.getFullYear(), hoy.getMonth() - 2, 1)), hasta }
  }
  if (periodo === 'anio') return { desde: aIso(new Date(hoy.getFullYear(), 0, 1)), hasta }
  return { desde: '', hasta: '' }
}
