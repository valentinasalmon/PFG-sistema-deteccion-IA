/**
 * Botón para acciones que no se pueden deshacer, con confirmación en dos pasos.
 *
 * El primer clic muestra la pregunta y los botones "Confirmar" y "Cancelar"
 * en el mismo lugar, sin ventanas emergentes; el foco pasa a "Cancelar" para
 * que una pulsación accidental de Enter no confirme (RNF10).
 *
 * @param {{texto: string, pregunta: string, textoConfirmar?: string,
 *   onConfirmar: () => (void | Promise<void>), peligro?: boolean,
 *   deshabilitado?: boolean}} propiedades
 */
import { useEffect, useRef, useState } from 'react'

export default function BotonConfirmar({
  texto,
  pregunta,
  textoConfirmar = 'Confirmar',
  onConfirmar,
  peligro = false,
  deshabilitado = false,
}) {
  const [preguntando, setPreguntando] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const refCancelar = useRef(null)
  const claseAccion = peligro ? 'boton boton--peligro boton--chico' : 'boton boton--chico'

  useEffect(() => {
    if (preguntando) refCancelar.current?.focus()
  }, [preguntando])

  async function confirmar() {
    setEnviando(true)
    try {
      await onConfirmar()
    } finally {
      setEnviando(false)
      setPreguntando(false)
    }
  }

  if (!preguntando) {
    return (
      <button
        type="button"
        className={peligro ? 'boton boton--secundario-peligro boton--chico' : 'boton boton--secundario boton--chico'}
        onClick={() => setPreguntando(true)}
        disabled={deshabilitado}
      >
        {texto}
      </button>
    )
  }

  return (
    <span className="confirmacion" role="group" aria-label={pregunta}>
      <span className="confirmacion__pregunta">{pregunta}</span>
      <button type="button" className={claseAccion} onClick={confirmar} disabled={enviando}>
        {textoConfirmar}
      </button>
      <button
        type="button"
        ref={refCancelar}
        className="boton boton--secundario boton--chico"
        onClick={() => setPreguntando(false)}
        disabled={enviando}
      >
        Cancelar
      </button>
    </span>
  )
}
