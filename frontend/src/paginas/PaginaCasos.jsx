/**
 * Pantalla "Casos": listado paginado de los casos accesibles, con búsqueda y
 * filtros guardados en la dirección (se pueden compartir y sobreviven a
 * recargar), y las transferencias de casos personales que esperan respuesta.
 *
 * Realiza: RF26, RF33 (CA2); CA5, CA6 y CA18 de la funcionalidad 005.
 */
import { useCallback, useState } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router'
import { listarCasos, responderTransferencia, transferenciasPendientes } from '../api/casos.js'
import { listarOrganizaciones } from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoSeleccion from '../componentes/CampoSeleccion.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { OPCIONES_ESTADO, OPCIONES_TIPO, tipoDeEtiquetaDeEstado } from '../utilidades/casos.js'
import { formatearDia, formatearFecha } from '../utilidades/fechas.js'

const CAMPOS_FILTRO = ['numero', 'expediente', 'estado', 'tipo', 'espacio', 'desde', 'hasta']

function Transferencias({ transferencias, alResponder }) {
  const navegar = useNavigate()
  const [error, setError] = useState(null)

  async function responder(transferencia, aceptar) {
    setError(null)
    try {
      const respuesta = await responderTransferencia(transferencia.id, aceptar)
      if (aceptar) {
        navegar(`/casos/${transferencia.id}`, { state: { mensaje: respuesta.mensaje } })
        return
      }
      await alResponder()
    } catch (errorApi) {
      setError(errorApi.message)
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-transferencias">
      <h2 id="titulo-transferencias">Casos que te quieren transferir</h2>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <ul className="lista-tarjetas">
        {transferencias.map((transferencia) => (
          <li key={transferencia.id} className="tarjeta-item">
            <div className="tarjeta-item__principal">
              <span className="tarjeta-item__titulo">{transferencia.numero}</span>
              <span className="tarjeta-item__detalle">
                {transferencia.tipo_nombre} · De {transferencia.solicitante.nombre} · Pedido el{' '}
                {formatearFecha(transferencia.solicitada_en)}
              </span>
            </div>
            <div className="acciones-en-linea">
              <button
                type="button"
                className="boton boton--chico"
                onClick={() => responder(transferencia, true)}
                aria-label={`Aceptar el caso ${transferencia.numero}`}
              >
                Aceptar
              </button>
              <button
                type="button"
                className="boton boton--secundario boton--chico"
                onClick={() => responder(transferencia, false)}
                aria-label={`Rechazar el caso ${transferencia.numero}`}
              >
                Rechazar
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

function Filtros({ filtros, espacios, alAplicar }) {
  const [valores, setValores] = useState(filtros)
  const hayFiltros = CAMPOS_FILTRO.some((campo) => filtros[campo])

  function cambiar(evento) {
    const { name, value } = evento.target
    setValores((anteriores) => ({ ...anteriores, [name]: value }))
  }

  function aplicar(evento) {
    evento.preventDefault()
    alAplicar(valores)
  }

  function limpiar() {
    const vacios = Object.fromEntries(CAMPOS_FILTRO.map((campo) => [campo, '']))
    setValores(vacios)
    alAplicar(vacios)
  }

  return (
    <form className="formulario filtros" onSubmit={aplicar} role="search" aria-label="Buscar casos">
      <div className="formulario__fila">
        <CampoTexto etiqueta="Número de caso" nombre="numero" value={valores.numero} onChange={cambiar} />
        <CampoTexto etiqueta="Expediente" nombre="expediente" value={valores.expediente} onChange={cambiar} />
      </div>
      <div className="formulario__fila">
        <CampoSeleccion
          etiqueta="Estado"
          nombre="estado"
          value={valores.estado}
          onChange={cambiar}
          opciones={[{ valor: '', texto: 'Todos menos archivados' }, ...OPCIONES_ESTADO]}
        />
        <CampoSeleccion
          etiqueta="Tipo"
          nombre="tipo"
          value={valores.tipo}
          onChange={cambiar}
          opciones={[{ valor: '', texto: 'Todos' }, ...OPCIONES_TIPO]}
        />
        <CampoSeleccion
          etiqueta="Espacio"
          nombre="espacio"
          value={valores.espacio}
          onChange={cambiar}
          opciones={[{ valor: '', texto: 'Todos' }, ...espacios]}
        />
      </div>
      <div className="formulario__fila">
        <CampoTexto etiqueta="Hecho desde" nombre="desde" tipo="date" value={valores.desde} onChange={cambiar} />
        <CampoTexto etiqueta="Hecho hasta" nombre="hasta" tipo="date" value={valores.hasta} onChange={cambiar} />
      </div>
      <div className="acciones-en-linea">
        <button type="submit" className="boton">
          Buscar
        </button>
        {hayFiltros && (
          <button type="button" className="boton boton--secundario" onClick={limpiar}>
            Limpiar los filtros
          </button>
        )}
      </div>
    </form>
  )
}

async function cargarPantalla(consulta) {
  const [resultado, transferencias, organizaciones] = await Promise.all([
    listarCasos(consulta),
    transferenciasPendientes(),
    listarOrganizaciones(),
  ])
  return { ...resultado, transferencias, organizaciones }
}

export default function PaginaCasos() {
  const [parametros, setParametros] = useSearchParams()
  const { state } = useLocation()
  const { usuario } = useSesion()
  const filtros = Object.fromEntries(CAMPOS_FILTRO.map((campo) => [campo, parametros.get(campo) ?? '']))
  const pagina = Number(parametros.get('pagina') ?? 1)
  const clave = parametros.toString()
  const cargar = useCallback(
    () => cargarPantalla(Object.fromEntries(new URLSearchParams(clave))),
    [clave],
  )
  const { datos, error, cargando, recargar } = useDatos(cargar)

  function aplicarFiltros(valores) {
    const nuevos = Object.fromEntries(Object.entries(valores).filter(([, valor]) => valor))
    setParametros(nuevos)
  }

  function irAPagina(numero) {
    setParametros({ ...Object.fromEntries(parametros), pagina: String(numero) })
  }

  const espacios = [
    ...(usuario.perfil === 'abogado' ? [{ valor: 'personal', texto: 'Personal' }] : []),
    ...(datos?.organizaciones ?? []).map((o) => ({ valor: String(o.id), texto: o.nombre })),
  ]

  return (
    <>
      <div className="encabezado-pagina">
        <h1>Casos</h1>
        <Link to="/casos/nuevo" className="boton">
          Nuevo caso
        </Link>
      </div>
      {state?.mensaje && <Aviso tipo="exito">{state.mensaje}</Aviso>}
      {datos?.transferencias.length > 0 && (
        <Transferencias transferencias={datos.transferencias} alResponder={recargar} />
      )}
      <section className="seccion" aria-labelledby="titulo-buscar">
        <h2 id="titulo-buscar">Buscar</h2>
        <Filtros key={clave} filtros={filtros} espacios={espacios} alAplicar={aplicarFiltros} />
      </section>

      <section className="seccion" aria-labelledby="titulo-resultados" aria-busy={cargando}>
        <h2 id="titulo-resultados">
          {datos ? `${datos.total} ${datos.total === 1 ? 'caso' : 'casos'}` : 'Resultados'}
        </h2>
        {cargando && <Cargando texto="Buscando casos…" />}
        {error && <Aviso tipo="error">{error.message}</Aviso>}
        {datos && datos.casos.length === 0 && (
          <p className="nota">
            {clave ? 'No hay casos con esos filtros.' : 'Todavía no tenés casos. Creá el primero.'}
          </p>
        )}
        {datos && datos.casos.length > 0 && (
          <ul className="lista-tarjetas">
            {datos.casos.map((caso) => (
              <li key={caso.id} className="tarjeta-item">
                <div className="tarjeta-item__principal">
                  <Link to={`/casos/${caso.id}`} className="tarjeta-item__titulo">
                    {caso.numero}
                  </Link>
                  <span className="tarjeta-item__detalle">
                    {caso.tipo_nombre} · {caso.espacio.nombre} · Hecho del {formatearDia(caso.fecha_hecho)}
                    {caso.expediente && ` · ${caso.expediente}`}
                  </span>
                  <span className="tarjeta-item__detalle">{caso.lugar}</span>
                </div>
                <div className="acciones-en-linea">
                  <Etiqueta tipo={tipoDeEtiquetaDeEstado(caso.estado)}>{caso.estado_nombre}</Etiqueta>
                  <Etiqueta>{caso.mi_permiso_nombre}</Etiqueta>
                </div>
              </li>
            ))}
          </ul>
        )}
        {datos && datos.paginas > 1 && (
          <nav className="paginacion" aria-label="Páginas de resultados">
            <button
              type="button"
              className="boton boton--secundario boton--chico"
              onClick={() => irAPagina(pagina - 1)}
              disabled={pagina <= 1}
            >
              Anterior
            </button>
            <span>
              Página {datos.pagina} de {datos.paginas}
            </span>
            <button
              type="button"
              className="boton boton--secundario boton--chico"
              onClick={() => irAPagina(pagina + 1)}
              disabled={pagina >= datos.paginas}
            >
              Siguiente
            </button>
          </nav>
        )}
      </section>
    </>
  )
}
