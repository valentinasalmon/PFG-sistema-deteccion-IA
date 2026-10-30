/**
 * Botón para acciones que no se pueden deshacer, con confirmación.
 *
 * Desde la funcionalidad 034 la pregunta se hace en un diálogo centrado con
 * X, Esc y clic afuera para cancelar. El foco empieza en «Cancelar», para que
 * una pulsación accidental de Enter no confirme (RNF10).
 *
 * @param {{texto: string, pregunta: string, textoConfirmar?: string,
 *   onConfirmar: () => (void | Promise<void>), peligro?: boolean,
 *   deshabilitado?: boolean, detalle?: string}} propiedades
 */
import { useState } from 'react'
import Dialogo from './Dialogo.jsx'

export default function BotonConfirmar({
  texto,
  pregunta,
  textoConfirmar = 'Confirmar',
  onConfirmar,
  peligro = false,
  deshabilitado = false,
  detalle,
}) {
  const [preguntando, setPreguntando] = useState(false)
  const [enviando, setEnviando] = useState(false)

  async function confirmar() {
    setEnviando(true)
    try {
      await onConfirmar()
    } finally {
      setEnviando(false)
      setPreguntando(false)
    }
  }

  return (
    <>
      <button
        type="button"
        className={
          peligro ? 'boton boton--secundario-peligro boton--chico' : 'boton boton--secundario boton--chico'
        }
        onClick={() => setPreguntando(true)}
        disabled={deshabilitado}
      >
        {texto}
      </button>
      {preguntando && (
        <Dialogo
          titulo={pregunta}
          bajada={detalle}
          alCerrar={() => !enviando && setPreguntando(false)}
          acciones={
            <>
              <button
                type="button"
                className="boton boton--secundario"
                data-foco-inicial
                onClick={() => setPreguntando(false)}
                disabled={enviando}
              >
                Cancelar
              </button>
              <button
                type="button"
                className={peligro ? 'boton boton--peligro' : 'boton'}
                onClick={confirmar}
                disabled={enviando}
              >
                {enviando ? 'Un momento…' : textoConfirmar}
              </button>
            </>
          }
        />
      )}
    </>
  )
}
