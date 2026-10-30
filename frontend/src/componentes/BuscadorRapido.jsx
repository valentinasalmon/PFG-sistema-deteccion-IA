/**
 * Buscador «Buscar o ir a…» de las pantallas internas (funcionalidad 034).
 *
 * Se abre con Ctrl K (⌘ K en Mac) desde cualquier pantalla interna o con el
 * botón del menú, y se cierra con Esc, la X o tocando afuera. Sin escribir
 * muestra los atajos del menú que corresponden a la persona; al escribir dos
 * letras o más busca también entre sus casos (número, expediente o lugar).
 * Las flechas mueven la selección y Enter la abre.
 *
 * Realiza: CA7 y CA9 de la funcionalidad 034; RNF10.
 */
import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { listarCasos } from '../api/casos.js'
import { useSesion } from '../hooks/useSesion.js'
import Dialogo from './Dialogo.jsx'
import Icono from './Icono.jsx'

/** Milisegundos sin escribir antes de buscar casos. */
const ESPERA_BUSQUEDA = 250

/** Casos que se muestran como máximo. */
const MAXIMO_CASOS = 6

/** Atajos del menú según quién entra (mismo criterio que el menú lateral, 028). */
function atajosPara(usuario) {
  if (usuario.rol === 'administrador') {
    return [
      { ruta: '/administracion', texto: 'Administración', icono: 'administracion' },
      { ruta: '/perfil', texto: 'Mi perfil', icono: 'perfil' },
    ]
  }
  return [
    { ruta: '/casos/nuevo', texto: 'Nuevo caso', icono: 'mas' },
    { ruta: '/', texto: 'Inicio', icono: 'inicio' },
    { ruta: '/casos', texto: 'Casos', icono: 'casos' },
    ...(usuario.en_organizacion
      ? [{ ruta: '/organizaciones', texto: 'Organizaciones', icono: 'organizaciones' }]
      : []),
    { ruta: '/perfil', texto: 'Mi perfil', icono: 'perfil' },
  ]
}

/** Normaliza para comparar sin mayúsculas ni tildes. */
function normalizar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
}

function Ventana({ alCerrar }) {
  const { usuario } = useSesion()
  const navegar = useNavigate()
  const idLista = useId()
  const [consulta, setConsulta] = useState('')
  const [casos, setCasos] = useState([])
  const [buscando, setBuscando] = useState(false)
  const [activa, setActiva] = useState(0)
  const refConsulta = useRef('')
  const buscaCasos = usuario.rol !== 'administrador'
  const texto = consulta.trim()

  useEffect(() => {
    refConsulta.current = texto
    if (!buscaCasos || texto.length < 2) return undefined
    const temporizador = setTimeout(() => {
      setBuscando(true)
      listarCasos({ busqueda: texto })
        .then((respuesta) => {
          if (refConsulta.current === texto) setCasos(respuesta.casos.slice(0, MAXIMO_CASOS))
        })
        .catch(() => {
          if (refConsulta.current === texto) setCasos([])
        })
        .finally(() => setBuscando(false))
    }, ESPERA_BUSQUEDA)
    return () => clearTimeout(temporizador)
  }, [texto, buscaCasos])

  const opciones = useMemo(() => {
    const buscado = normalizar(texto)
    const atajos = atajosPara(usuario)
      .filter((atajo) => !buscado || normalizar(atajo.texto).includes(buscado))
      .map((atajo) => ({ ...atajo, grupo: 'Ir a' }))
    const encontrados =
      texto.length < 2
        ? []
        : casos.map((caso) => ({
            ruta: `/casos/${caso.id}`,
            texto: caso.numero,
            detalle: [caso.lugar, caso.estado_nombre].filter(Boolean).join(' · '),
            icono: 'documento',
            grupo: 'Casos',
          }))
    return [...encontrados, ...atajos]
  }, [texto, casos, usuario])

  const seleccion = Math.min(activa, Math.max(opciones.length - 1, 0))

  function abrir(opcion) {
    alCerrar()
    navegar(opcion.ruta)
  }

  function alTeclear(evento) {
    if (evento.key === 'ArrowDown' || evento.key === 'ArrowUp') {
      evento.preventDefault()
      if (opciones.length === 0) return
      const paso = evento.key === 'ArrowDown' ? 1 : -1
      setActiva((seleccion + paso + opciones.length) % opciones.length)
    } else if (evento.key === 'Enter' && opciones[seleccion]) {
      evento.preventDefault()
      abrir(opciones[seleccion])
    }
  }

  function cambiar(evento) {
    setConsulta(evento.target.value)
    setActiva(0)
    if (evento.target.value.trim().length < 2) setCasos([])
  }

  const idOpcion = (indice) => `${idLista}-${indice}`
  const sinResultados = opciones.length === 0 && !buscando

  return (
    <Dialogo titulo="Buscar o ir a…" alCerrar={alCerrar}>
      <div className="buscador-rapido">
        <label className="buscador-rapido__campo">
          <Icono nombre="buscar" tamanio={18} />
          <span className="solo-lectores">Buscar un caso o una pantalla</span>
          <input
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-controls={idLista}
            aria-autocomplete="list"
            aria-activedescendant={opciones.length ? idOpcion(seleccion) : undefined}
            placeholder={buscaCasos ? 'Número de caso, expediente, lugar o pantalla' : 'Pantalla'}
            value={consulta}
            onChange={cambiar}
            onKeyDown={alTeclear}
            autoComplete="off"
            data-foco-inicial
          />
        </label>
        <ul id={idLista} role="listbox" aria-label="Resultados" className="buscador-rapido__lista">
          {opciones.map((opcion, indice) => (
            <li
              key={`${opcion.grupo}-${opcion.ruta}`}
              id={idOpcion(indice)}
              role="option"
              aria-selected={indice === seleccion}
              className="buscador-rapido__opcion"
              onMouseDown={(evento) => evento.preventDefault()}
              onMouseEnter={() => setActiva(indice)}
              onClick={() => abrir(opcion)}
            >
              <span className="buscador-rapido__icono" aria-hidden="true">
                <Icono nombre={opcion.icono} tamanio={16} />
              </span>
              <span className="buscador-rapido__texto">
                <strong>{opcion.texto}</strong>
                {opcion.detalle && <small>{opcion.detalle}</small>}
              </span>
              <span className="buscador-rapido__grupo">{opcion.grupo}</span>
            </li>
          ))}
        </ul>
        <p className="buscador-rapido__estado" role="status">
          {buscando && 'Buscando casos…'}
          {sinResultados && `Nada coincide con «${texto}».`}
        </p>
        <p className="buscador-rapido__ayuda" aria-hidden="true">
          <kbd>↑</kbd> <kbd>↓</kbd> para moverte · <kbd>Enter</kbd> para abrir · <kbd>Esc</kbd> para cerrar
        </p>
      </div>
    </Dialogo>
  )
}

/** Verdadero si la tecla es el atajo Ctrl K (⌘ K en Mac). */
function esAtajoBuscar(evento) {
  return (evento.ctrlKey || evento.metaKey) && !evento.altKey && evento.key.toLowerCase() === 'k'
}

/**
 * Botón del menú que abre el buscador y escucha el atajo de teclado en toda
 * la pantalla interna.
 */
export default function BuscadorRapido({ alAbrir }) {
  const [abierto, setAbierto] = useState(false)

  useEffect(() => {
    function alTeclear(evento) {
      if (!esAtajoBuscar(evento)) return
      evento.preventDefault()
      setAbierto((actual) => !actual)
    }
    document.addEventListener('keydown', alTeclear)
    return () => document.removeEventListener('keydown', alTeclear)
  }, [])

  return (
    <>
      <button
        type="button"
        className="buscador-rapido__abrir"
        onClick={() => {
          alAbrir?.()
          setAbierto(true)
        }}
        aria-keyshortcuts="Control+K Meta+K"
      >
        <Icono nombre="buscar" tamanio={18} />
        <span>Buscar o ir a…</span>
        <kbd aria-hidden="true">Ctrl K</kbd>
      </button>
      {abierto && <Ventana alCerrar={() => setAbierto(false)} />}
    </>
  )
}
