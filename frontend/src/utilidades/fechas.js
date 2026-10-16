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
