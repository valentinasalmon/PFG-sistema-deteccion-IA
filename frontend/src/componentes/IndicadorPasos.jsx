/**
 * Indicador de avance de un formulario por pasos: texto "Paso N de M" y una
 * barra de progreso.
 *
 * El texto es el que leen los lectores de pantalla; la barra es decorativa
 * porque repite la misma información.
 *
 * Realiza: CA8 de la funcionalidad 020; RNF10.
 */
export default function IndicadorPasos({ actual, total }) {
  const porcentaje = Math.round((actual / total) * 100)
  return (
    <div className="indicador-pasos">
      <p className="indicador-pasos__texto">
        Paso {actual} de {total}
      </p>
      <div className="indicador-pasos__barra" aria-hidden="true">
        <div className="indicador-pasos__avance" style={{ width: `${porcentaje}%` }} />
      </div>
    </div>
  )
}
