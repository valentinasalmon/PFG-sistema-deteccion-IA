/**
 * Huella SHA-256 abreviada, con un botón para copiarla entera (funcionalidad 037).
 *
 * Una huella de 64 caracteres ocupaba cuatro renglones y apretaba el botón de
 * descarga. Se muestran el principio y el final, que alcanzan para comparar a
 * simple vista; la huella completa queda para los lectores de pantalla, en el
 * título y en el portapapeles.
 *
 * Realiza: RF44 (interfaz); RNF10.
 */
import { useState } from 'react'
import { abreviarHuella } from '../utilidades/archivos.js'

export default function HuellaCorta({ huella }) {
  const [copiada, setCopiada] = useState(false)

  async function copiar() {
    try {
      await navigator.clipboard.writeText(huella)
      setCopiada(true)
    } catch {
      setCopiada(false)
    }
  }

  return (
    <span className="huella-corta">
      <span className="solo-lectores">{huella}</span>
      <code aria-hidden="true" title={huella}>
        {abreviarHuella(huella)}
      </code>
      <button type="button" className="boton-enlace" onClick={copiar} aria-label="Copiar la huella completa">
        {copiada ? 'Copiada' : 'Copiar'}
      </button>
    </span>
  )
}
