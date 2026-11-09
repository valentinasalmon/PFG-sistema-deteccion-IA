/**
 * Disposición de las páginas legales (Términos y Privacidad) en computadora:
 * un índice de las secciones a la izquierda, fijo al desplazarse, y el texto
 * a la derecha con un largo de línea cómodo para leer (038, pedido de la
 * autora: la tarjeta más ancha tenía que aprovecharse, no dejar media vacía).
 *
 * El índice se arma solo con los títulos de nivel 2 del texto, así agregar o
 * renombrar una sección no exige tocarlo. En el celular se oculta.
 *
 * Realiza: RNF10 (legibilidad e identidad visual).
 */
import { useEffect, useRef, useState } from 'react'

/** Convierte un título en un identificador para el enlace del índice. */
function identificadorDe(texto, indice) {
  const base = texto
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
  return base || `seccion-${indice + 1}`
}

export default function DisposicionLegal({ className = '', children }) {
  const articulo = useRef(null)
  const [secciones, setSecciones] = useState([])

  useEffect(() => {
    const titulos = [...(articulo.current?.querySelectorAll('h2') ?? [])]
    titulos.forEach((titulo, indice) => {
      if (!titulo.id) titulo.id = identificadorDe(titulo.textContent, indice)
    })
    setSecciones(titulos.map((titulo) => ({ id: titulo.id, texto: titulo.textContent })))
  }, [])

  return (
    <div className="legal">
      {secciones.length > 0 && (
        <nav className="legal__indice" aria-label="Secciones">
          <p className="legal__indice-titulo">En esta página</p>
          <ol>
            {secciones.map((seccion) => (
              <li key={seccion.id}>
                <a href={`#${seccion.id}`}>{seccion.texto}</a>
              </li>
            ))}
          </ol>
        </nav>
      )}
      <article ref={articulo} className={`texto-legal ${className}`.trim()}>
        {children}
      </article>
    </div>
  )
}
