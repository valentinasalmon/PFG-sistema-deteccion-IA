/**
 * Textos y etiquetas del estado de la verificación de identidad (funcionalidad 035).
 *
 * Los usan la pantalla de la organización (Referente) y la de Administración.
 *
 * Realiza: RN41.
 */

/** Texto breve y tipo de etiqueta de cada estado de la verificación. */
export const ESTADOS_DE_IDENTIDAD = {
  sin_verificar: { texto: 'Identidad sin verificar', tipo: 'alerta' },
  pendiente: { texto: 'Verificación en curso', tipo: 'neutra' },
  aprobada: { texto: 'Identidad verificada', tipo: 'destacada' },
  rechazada: { texto: 'Verificación rechazada', tipo: 'alerta' },
}

/** Datos de la etiqueta para un estado; uno desconocido se muestra como sin verificar. */
export function etiquetaDeIdentidad(estado) {
  return ESTADOS_DE_IDENTIDAD[estado] ?? ESTADOS_DE_IDENTIDAD.sin_verificar
}

/** Redirección a la página del proveedor; un objeto para poder reemplazarla en las pruebas. */
export const navegador = {
  ir(url) {
    window.location.assign(url)
  },
}
