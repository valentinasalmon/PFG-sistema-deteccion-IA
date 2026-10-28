/**
 * Etiqueta del estado de un caso (funcionalidad 028).
 *
 * Los colores avanzan de gris a azul y a verde a medida que el caso avanza
 * (Borrador → En análisis → Analizado → Cerrado); Archivado va con borde
 * punteado. El nombre siempre va escrito, así el color no es la única señal
 * (RNF10). Es el estado del trámite: nunca dice nada sobre la autenticidad.
 *
 * @param {{estado: string, children: import('react').ReactNode}} propiedades
 */
export default function EtiquetaEstado({ estado, children }) {
  return (
    <span className={`estado-caso estado-caso--${estado}`}>
      <span className="estado-caso__punto" aria-hidden="true" />
      {children}
    </span>
  )
}
