/**
 * Buscador para elegir la aseguradora del catálogo de la SSN.
 *
 * Es un cuadro combinado (patrón «combobox» de WAI-ARIA): al escribir se
 * despliega debajo del campo una lista corta con desplazamiento propio, que
 * se recorre con las flechas, se elige con Enter o con un toque y se cierra
 * con Escape. Así el paso no crece ni empuja el resto del formulario (037,
 * pedido de la autora). Filtra por parte de la denominación (sin distinguir
 * mayúsculas ni tildes) o del CUIT, y anuncia la cantidad de resultados.
 *
 * Realiza: CA2 de la funcionalidad 021; RNF10.
 *
 * @param {{aseguradoras: Array<{id: number, denominacion: string, cuit: string, actividad: string}>,
 *   elegida: number | null, onElegir: (id: number) => void, error?: string}} propiedades
 */
import { useEffect, useId, useRef, useState } from 'react'
import { filtrarAseguradoras } from '../utilidades/aseguradoras.js'
import Icono from './Icono.jsx'

const MAXIMO_RESULTADOS = 8

export default function SelectorAseguradora({ aseguradoras, elegida, onElegir, error }) {
  const id = useId()
  const seleccionada = aseguradoras.find((aseguradora) => aseguradora.id === elegida)
  const [busqueda, setBusqueda] = useState(seleccionada?.denominacion ?? '')
  const [abierta, setAbierta] = useState(false)
  const [activa, setActiva] = useState(0)

  // Con la elegida escrita tal cual, no se filtra: se ve qué se eligió.
  const escribiendo = busqueda.trim() && busqueda !== seleccionada?.denominacion
  const coincidencias = escribiendo ? filtrarAseguradoras(aseguradoras, busqueda) : []
  const visibles = coincidencias.slice(0, MAXIMO_RESULTADOS)
  const desplegada = abierta && visibles.length > 0
  const campo = useRef(null)

  // Al desplegarse, el campo sube al borde de arriba para que la lista entre entera.
  useEffect(() => {
    if (desplegada) campo.current?.scrollIntoView?.({ block: 'start', behavior: 'smooth' })
  }, [desplegada])

  let estado = 'Escribí al menos una parte del nombre o del CUIT.'
  if (seleccionada && !escribiendo) {
    estado = `Elegiste ${seleccionada.denominacion} (CUIT ${seleccionada.cuit}).`
  } else if (escribiendo && coincidencias.length === 0) {
    estado = 'No encontramos ninguna aseguradora con ese nombre o CUIT.'
  } else if (coincidencias.length > MAXIMO_RESULTADOS) {
    estado = `Hay ${coincidencias.length} resultados: mostramos los primeros ${MAXIMO_RESULTADOS}. Escribí más para acotar.`
  } else if (coincidencias.length > 0) {
    estado = `${coincidencias.length} ${coincidencias.length === 1 ? 'resultado' : 'resultados'}.`
  }

  function elegir(aseguradora) {
    onElegir(aseguradora.id)
    setBusqueda(aseguradora.denominacion)
    setAbierta(false)
  }

  function alEscribir(evento) {
    setBusqueda(evento.target.value)
    setActiva(0)
    setAbierta(true)
  }

  function alTeclear(evento) {
    if (evento.key === 'ArrowDown' || evento.key === 'ArrowUp') {
      evento.preventDefault()
      if (!desplegada) {
        setAbierta(true)
        return
      }
      const paso = evento.key === 'ArrowDown' ? 1 : -1
      setActiva((actual) => (actual + paso + visibles.length) % visibles.length)
    } else if (evento.key === 'Enter' && desplegada) {
      evento.preventDefault()
      elegir(visibles[Math.min(activa, visibles.length - 1)])
    } else if (evento.key === 'Escape' && abierta) {
      evento.preventDefault()
      setAbierta(false)
    }
  }

  function limpiar() {
    setBusqueda('')
    setAbierta(false)
  }

  const idLista = `${id}-lista`
  return (
    <div className="selector-aseguradora">
      <div className="campo">
        <label htmlFor={`${id}-busqueda`} className="campo__etiqueta">
          Buscá tu aseguradora
        </label>
        <div className="combo" ref={campo}>
          <span className="combo__lupa">
            <Icono nombre="buscar" tamanio={18} />
          </span>
          <input
            id={`${id}-busqueda`}
            type="text"
            role="combobox"
            className={error ? 'campo__control combo__control campo__control--error' : 'campo__control combo__control'}
            value={busqueda}
            onChange={alEscribir}
            onKeyDown={alTeclear}
            onFocus={() => escribiendo && setAbierta(true)}
            onBlur={() => setAbierta(false)}
            aria-expanded={desplegada}
            aria-controls={idLista}
            aria-autocomplete="list"
            aria-activedescendant={desplegada ? `${id}-opcion-${activa}` : undefined}
            aria-describedby={`${id}-estado${error ? ` ${id}-error` : ''}`}
            aria-invalid={error ? 'true' : undefined}
            placeholder="Nombre o CUIT"
            autoComplete="off"
            spellCheck="false"
          />
          {busqueda && (
            <button type="button" className="combo__limpiar" onClick={limpiar} aria-label="Borrar la búsqueda">
              <Icono nombre="cerrar" tamanio={16} />
            </button>
          )}
          <ul id={idLista} role="listbox" aria-label="Aseguradoras encontradas" className="combo__lista" hidden={!desplegada}>
            {visibles.map((aseguradora, indice) => (
              <li
                key={aseguradora.id}
                id={`${id}-opcion-${indice}`}
                role="option"
                aria-selected={aseguradora.id === elegida}
                className={`combo__opcion${indice === activa ? ' combo__opcion--activa' : ''}`}
                // Evita que el campo pierda el foco antes de elegir.
                onMouseDown={(evento) => evento.preventDefault()}
                onMouseEnter={() => setActiva(indice)}
                onClick={() => elegir(aseguradora)}
              >
                <span className="combo__nombre">{aseguradora.denominacion}</span>
                <span className="combo__detalle">
                  CUIT {aseguradora.cuit} · {aseguradora.actividad}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <p
          id={`${id}-estado`}
          className={`campo__ayuda${seleccionada && !escribiendo ? ' combo__elegida' : ''}`}
          aria-live="polite"
        >
          {seleccionada && !escribiendo && <Icono nombre="marca" tamanio={16} />}
          {estado}
        </p>
        {error && (
          <p id={`${id}-error`} className="campo__error">
            {error}
          </p>
        )}
      </div>
    </div>
  )
}
