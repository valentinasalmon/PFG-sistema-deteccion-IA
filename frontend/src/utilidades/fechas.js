/**
 * Formato de fechas para mostrar en la interfaz.
 *
 * El backend envía las fechas en UTC sin zona horaria (ISO 8601); acá se
 * interpretan como UTC y se muestran en la hora de Argentina.
 */
const ZONA_HORARIA = 'America/Argentina/Buenos_Aires'

function comoUtc(texto) {
  return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(texto) ? texto : `${texto}Z`)
}

/** Fecha en formato dd/mm/aaaa, o un guion si no hay fecha. */
export function formatearFecha(texto) {
  if (!texto) return '—'
  return comoUtc(texto).toLocaleDateString('es-AR', {
    timeZone: ZONA_HORARIA,
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

/**
 * Fecha calendario sin hora (por ejemplo, la fecha del hecho) en formato
 * dd/mm/aaaa. No se convierte de zona horaria: es el mismo día en todas.
 */
export function formatearDia(texto) {
  if (!texto) return '—'
  const [anio, mes, dia] = texto.slice(0, 10).split('-')
  return `${dia}/${mes}/${anio}`
}

/** Fecha de hoy en formato aaaa-mm-dd, en la hora de Argentina (para los campos de fecha). */
export function hoyIso() {
  return new Date().toLocaleDateString('en-CA', { timeZone: ZONA_HORARIA })
}
