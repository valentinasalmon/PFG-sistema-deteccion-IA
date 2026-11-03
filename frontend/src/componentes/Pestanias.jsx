/**
 * Pestañas accesibles. La pestaña elegida suele guardarse en la dirección de
 * la página con ``usePestaniaElegida`` (hooks/usePestaniaElegida.js).
 *
 * Sigue el patrón de pestañas de WAI-ARIA: ``tablist`` con ``tab`` y un
 * ``tabpanel``; las flechas izquierda y derecha pasan de una pestaña a otra
 * y solo la elegida entra en el orden del tabulador.
 *
 * Lo usan Mi perfil (028) y la organización (034, cuarta tanda).
 *
 * Realiza: RNF10 (accesibilidad y navegación con teclado).
 */

/**
 * @param {object} props
 * @param {string} props.etiqueta Nombre accesible de la lista de pestañas.
 * @param {{id: string, texto: string}[]} props.pestanias Pestañas, en orden.
 * @param {string} props.actual Identificador de la pestaña elegida.
 * @param {(id: string) => void} props.alElegir Se llama al elegir otra pestaña.
 * @param {React.ReactNode} props.children Contenido de la pestaña elegida.
 */
export default function Pestanias({ etiqueta, pestanias, actual, alElegir, children }) {
  /** Flechas izquierda y derecha entre pestañas. */
  function alPresionar(evento, indice) {
    const paso = { ArrowRight: 1, ArrowLeft: -1 }[evento.key]
    if (!paso) return
    const siguiente = pestanias[(indice + paso + pestanias.length) % pestanias.length]
    alElegir(siguiente.id)
    document.getElementById(`pestania-${siguiente.id}`)?.focus()
  }

  return (
    <>
      <div className="pestanias" role="tablist" aria-label={etiqueta}>
        {pestanias.map(({ id, texto }, indice) => (
          <button
            key={id}
            id={`pestania-${id}`}
            type="button"
            role="tab"
            className="pestanias__pestania"
            aria-selected={actual === id}
            aria-controls={`panel-${id}`}
            tabIndex={actual === id ? 0 : -1}
            onClick={() => alElegir(id)}
            onKeyDown={(evento) => alPresionar(evento, indice)}
          >
            {texto}
          </button>
        ))}
      </div>
      <div
        id={`panel-${actual}`}
        role="tabpanel"
        aria-labelledby={`pestania-${actual}`}
        className="pestanias__panel"
      >
        {children}
      </div>
    </>
  )
}
