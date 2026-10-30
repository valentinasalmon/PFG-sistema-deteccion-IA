/**
 * Pasos del registro con su nombre, en el panel verde de la izquierda
 * (funcionalidad 032, frame 10a).
 *
 * Se dibuja dentro del panel de marca de las pantallas de acceso con un
 * portal; en el celular ese panel es una banda corta y los pasos se ven en la
 * barra de avance de la tarjeta.
 *
 * Realiza: RNF10.
 */
import { useContext } from 'react'
import { createPortal } from 'react-dom'
import { ContextoAcceso } from '../contextos/contextoAcceso.js'
import { DESCRIPCION_DE_PASOS } from '../utilidades/registro.js'

export default function PanelPasos({ pasos, actual, titulo = 'Creá tu cuenta', bajada }) {
  const destino = useContext(ContextoAcceso)
  if (!destino) return null
  return createPortal(
    <nav className="panel-pasos" aria-label="Pasos del registro">
      <p className="panel-pasos__titulo">{titulo}</p>
      {bajada && <p className="panel-pasos__bajada">{bajada}</p>}
      <ol className="panel-pasos__lista">
        {pasos.map((paso, indice) => {
          const situacion = indice < actual ? 'hecho' : indice === actual ? 'actual' : 'pendiente'
          const { nombre, detalle } = DESCRIPCION_DE_PASOS[paso]
          return (
            <li
              key={paso}
              className={`panel-pasos__paso panel-pasos__paso--${situacion}`}
              aria-current={situacion === 'actual' ? 'step' : undefined}
            >
              <span className="panel-pasos__numero" aria-hidden="true">
                {situacion === 'hecho' ? '✓' : indice + 1}
              </span>
              <span>
                <strong>{nombre}</strong>
                <span className="panel-pasos__detalle">{detalle}</span>
              </span>
            </li>
          )
        })}
      </ol>
    </nav>,
    destino,
  )
}
