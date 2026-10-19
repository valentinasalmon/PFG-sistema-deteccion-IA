/**
 * Buscador para elegir la aseguradora del catálogo de la SSN.
 *
 * Filtra por parte de la denominación (sin distinguir mayúsculas ni tildes)
 * o del CUIT y muestra hasta 8 resultados como opciones grandes. La
 * cantidad de resultados se anuncia a los lectores de pantalla.
 *
 * Realiza: CA2 de la funcionalidad 021; RNF10.
 *
 * @param {{aseguradoras: Array<{id: number, denominacion: string, cuit: string, actividad: string}>,
 *   elegida: number | null, onElegir: (id: number) => void, error?: string}} propiedades
 */
import { useId, useState } from 'react'
import { filtrarAseguradoras } from '../utilidades/aseguradoras.js'
import OpcionTarjeta from './OpcionTarjeta.jsx'

const MAXIMO_RESULTADOS = 8

export default function SelectorAseguradora({ aseguradoras, elegida, onElegir, error }) {
  const id = useId()
  const [busqueda, setBusqueda] = useState('')
  const coincidencias = filtrarAseguradoras(aseguradoras, busqueda)
  const visibles = coincidencias.slice(0, MAXIMO_RESULTADOS)
  const seleccionada = aseguradoras.find((aseguradora) => aseguradora.id === elegida)
  // La elegida sigue visible aunque cambie la búsqueda.
  if (seleccionada && !visibles.includes(seleccionada)) visibles.unshift(seleccionada)

  let estado = 'Escribí al menos una parte del nombre o del CUIT.'
  if (busqueda.trim() && coincidencias.length === 0) {
    estado = 'No encontramos ninguna aseguradora con ese nombre o CUIT.'
  } else if (coincidencias.length > MAXIMO_RESULTADOS) {
    estado = `Hay ${coincidencias.length} resultados: mostramos los primeros ${MAXIMO_RESULTADOS}. Escribí más para acotar.`
  } else if (coincidencias.length > 0) {
    estado = `${coincidencias.length} ${coincidencias.length === 1 ? 'resultado' : 'resultados'}.`
  }

  return (
    <div className="selector-aseguradora">
      <div className="campo">
        <label htmlFor={`${id}-busqueda`} className="campo__etiqueta">
          Buscá tu aseguradora
        </label>
        <input
          id={`${id}-busqueda`}
          type="search"
          className={error ? 'campo__control campo__control--error' : 'campo__control'}
          value={busqueda}
          onChange={(evento) => setBusqueda(evento.target.value)}
          aria-describedby={`${id}-estado${error ? ` ${id}-error` : ''}`}
          aria-invalid={error ? 'true' : undefined}
          autoComplete="off"
        />
        <p id={`${id}-estado`} className="campo__ayuda" aria-live="polite">
          {estado}
        </p>
        {error && (
          <p id={`${id}-error`} className="campo__error">
            {error}
          </p>
        )}
      </div>
      {visibles.length > 0 && (
        <fieldset className="opciones-tarjeta">
          <legend className="solo-lectores">Aseguradoras encontradas</legend>
          {visibles.map((aseguradora) => (
            <OpcionTarjeta
              key={aseguradora.id}
              nombre="id_aseguradora"
              valor={String(aseguradora.id)}
              seleccionada={aseguradora.id === elegida}
              onChange={() => onElegir(aseguradora.id)}
              titulo={aseguradora.denominacion}
              descripcion={`CUIT ${aseguradora.cuit} · ${aseguradora.actividad}`}
            />
          ))}
        </fieldset>
      )}
    </div>
  )
}
