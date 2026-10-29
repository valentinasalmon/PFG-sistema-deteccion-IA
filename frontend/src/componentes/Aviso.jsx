/**
 * Mensaje destacado para informar el resultado de una acción.
 *
 * Los errores usan role="alert" para que el lector de pantalla los lea de
 * inmediato; el resto usa role="status".
 *
 * Los avisos de éxito son flotantes (funcionalidad 022): aparecen abajo a la
 * derecha, se cierran solos a los 6 segundos o con su botón, y no desplazan
 * el contenido. Los errores y la información quedan junto a lo que los causó,
 * porque la persona necesita leerlos para corregir algo.
 *
 * Realiza: RNF10 (respuesta del sistema).
 *
 * Un aviso de éxito que trae instrucciones o enlaces (por ejemplo, la copia de
 * datos) se deja en su lugar con ``flotante={false}``.
 *
 * @param {{tipo?: 'exito' | 'error' | 'info' | 'alerta', flotante?: boolean, children: React.ReactNode}} props
 */
import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

export const DURACION_AVISO_FLOTANTE = 6000

/** Contenedor común de los avisos flotantes, para que se apilen. */
function contenedorDeAvisos() {
  let contenedor = document.getElementById('avisos-flotantes')
  if (!contenedor) {
    contenedor = document.createElement('div')
    contenedor.id = 'avisos-flotantes'
    contenedor.className = 'avisos-flotantes'
    document.body.appendChild(contenedor)
  }
  return contenedor
}

function AvisoFlotante({ children }) {
  const [visible, setVisible] = useState(true)
  const [anterior, setAnterior] = useState(children)
  // Un mensaje nuevo en el mismo lugar vuelve a mostrarse.
  if (anterior !== children) {
    setAnterior(children)
    setVisible(true)
  }

  useEffect(() => {
    if (!visible) return undefined
    const temporizador = setTimeout(() => setVisible(false), DURACION_AVISO_FLOTANTE)
    return () => clearTimeout(temporizador)
  }, [visible, anterior])

  if (!visible) return null
  return createPortal(
    <div className="aviso aviso--exito aviso--flotante" role="status">
      <span className="aviso__texto">{children}</span>
      <button type="button" className="aviso__cerrar" aria-label="Cerrar aviso" onClick={() => setVisible(false)}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>
    </div>,
    contenedorDeAvisos(),
  )
}

export default function Aviso({ tipo = 'info', flotante = tipo === 'exito', children }) {
  if (flotante) return <AvisoFlotante>{children}</AvisoFlotante>
  return (
    <div className={`aviso aviso--${tipo}`} role={tipo === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  )
}
