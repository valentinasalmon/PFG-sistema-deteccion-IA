/**
 * Ventana de diálogo centrada en la pantalla (funcionalidad 034).
 *
 * Se cierra con la X, con Esc o tocando afuera. Al abrirse, el foco pasa al
 * primer control (o al indicado con ``data-foco-inicial``) y queda atrapado
 * dentro; al cerrarse vuelve a donde estaba. El resto de la página no se
 * desplaza mientras está abierta.
 *
 * Realiza: RNF10 (accesibilidad y respuesta del sistema); CA3 de la 034.
 *
 * @param {{titulo: string, bajada?: string, alCerrar: () => void,
 *   acciones?: React.ReactNode, ancho?: boolean, children?: React.ReactNode}} props
 */
import { useEffect, useId, useRef } from 'react'
import { createPortal } from 'react-dom'

const ENFOCABLES =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

export default function Dialogo({ titulo, bajada, alCerrar, acciones, ancho = false, children }) {
  const refDialogo = useRef(null)
  const refCerrar = useRef(alCerrar)
  const idTitulo = useId()
  const idBajada = useId()

  useEffect(() => {
    refCerrar.current = alCerrar
  }, [alCerrar])

  useEffect(() => {
    const anterior = document.activeElement
    const dialogo = refDialogo.current
    const inicial = dialogo.querySelector('[data-foco-inicial]') ?? dialogo.querySelector(ENFOCABLES)
    inicial?.focus()

    function alTeclear(evento) {
      if (evento.key === 'Escape') {
        evento.stopPropagation()
        refCerrar.current()
        return
      }
      if (evento.key !== 'Tab') return
      const controles = [...dialogo.querySelectorAll(ENFOCABLES)]
      if (controles.length === 0) return
      const primero = controles[0]
      const ultimo = controles[controles.length - 1]
      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault()
        ultimo.focus()
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault()
        primero.focus()
      }
    }

    document.addEventListener('keydown', alTeclear)
    return () => {
      document.removeEventListener('keydown', alTeclear)
      if (anterior instanceof HTMLElement) anterior.focus()
    }
  }, [])

  return createPortal(
    <div
      className="dialogo-velo"
      onMouseDown={(evento) => {
        if (evento.target === evento.currentTarget) alCerrar()
      }}
    >
      <div
        ref={refDialogo}
        className={`dialogo${ancho ? ' dialogo--ancho' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
        aria-describedby={bajada ? idBajada : undefined}
      >
        <div className="dialogo__cabecera">
          <div>
            <h2 id={idTitulo}>{titulo}</h2>
            {bajada && (
              <p id={idBajada} className="dialogo__bajada">
                {bajada}
              </p>
            )}
          </div>
          <button type="button" className="dialogo__cerrar" aria-label="Cerrar la ventana" onClick={alCerrar}>
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              aria-hidden="true"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
        {children}
        {acciones && <div className="dialogo__acciones">{acciones}</div>}
      </div>
    </div>,
    document.body,
  )
}
