/**
 * Comparador deslizable entre la foto y su mapa de niveles de error
 * (funcionalidad 034).
 *
 * Las dos imágenes se superponen en el mismo lugar y un control deslizante
 * corre el corte: a la izquierda se ve la foto y a la derecha el mapa. Así se
 * ubica qué parte de la foto corresponde a cada zona clara del mapa sin ir y
 * venir entre dos imágenes. El control es un ``input`` de rango: se usa con el
 * mouse, el dedo o las flechas del teclado (RNF10).
 *
 * Realiza: CA9 de la funcionalidad 034; CA4 de la 011 (presentación); RNF10.
 *
 * @param {{original: string, mapa: string, nombre: string}} props
 */
import { useId, useState } from 'react'

export default function ComparadorMapa({ original, mapa, nombre }) {
  const [corte, setCorte] = useState(50)
  const idControl = useId()

  return (
    <div className="comparador">
      <div className="comparador__lienzo" style={{ '--corte': `${corte}%` }}>
        <img src={original} alt={`Foto ${nombre}`} className="comparador__foto" loading="lazy" />
        <img src={mapa} alt={`Mapa de niveles de error de ${nombre}`} className="comparador__mapa" loading="lazy" />
        <span className="comparador__linea" aria-hidden="true" />
        <span className="comparador__rotulo comparador__rotulo--foto" aria-hidden="true">
          Foto
        </span>
        <span className="comparador__rotulo comparador__rotulo--mapa" aria-hidden="true">
          Mapa de error
        </span>
        <input
          id={idControl}
          type="range"
          min="0"
          max="100"
          value={corte}
          onChange={(evento) => setCorte(Number(evento.target.value))}
          className="comparador__control"
          aria-label="Comparar la foto con su mapa de error"
          aria-valuetext={`${corte} % de foto, ${100 - corte} % de mapa`}
        />
      </div>
      <p className="nota comparador__ayuda">Deslizá para comparar la foto con su mapa de error.</p>
    </div>
  )
}
