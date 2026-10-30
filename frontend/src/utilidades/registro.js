/**
 * Pasos del registro según el camino elegido (funcionalidad 032).
 *
 * Realiza: RF01, RF10; RN01.
 */

/** Perfil de la cuenta según el camino elegido (RN01). */
export function perfilDelCamino(camino) {
  if (!camino) return ''
  return camino === 'aseguradora' ? 'aseguradora' : 'abogado'
}

/** True si el camino registra una organización que paga su plan. */
export function caminoConPago(camino) {
  return camino === 'estudio' || camino === 'aseguradora'
}

/** Nombre y detalle de cada paso, para el panel de la izquierda (frame 10a). */
export const DESCRIPCION_DE_PASOS = {
  perfil: { nombre: 'Cómo vas a usarla', detalle: 'Independiente, estudio o aseguradora' },
  datos: { nombre: 'Tus datos', detalle: 'Nombre y apellido' },
  institucion: { nombre: 'Tu institución', detalle: 'Colegio o aseguradora' },
  plan: { nombre: 'Plan', detalle: 'Básico o Profesional' },
  cuenta: { nombre: 'Tu cuenta', detalle: 'Correo, contraseña y términos' },
  terminos: { nombre: 'Términos', detalle: 'Términos de Uso y Privacidad' },
  pago: { nombre: 'Pago', detalle: 'Transferencia con Cresium' },
}
