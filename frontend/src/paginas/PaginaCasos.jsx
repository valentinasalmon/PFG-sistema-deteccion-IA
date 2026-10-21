/**
 * Pantalla "Casos": listado paginado de los casos accesibles, con búsqueda y
 * filtros guardados en la dirección (se pueden compartir y sobreviven a
 * recargar), y las transferencias de casos personales que esperan respuesta.
 *
 * La búsqueda principal (número, expediente, estado y tipo) queda siempre a la
 * vista; el espacio y las fechas se despliegan en "Más filtros" (022).
 *
 * Realiza: RF26, RF33 (CA2); CA5, CA6 y CA18 de la funcionalidad 005; RNF10.
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
import Icono from '../componentes/Icono.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { OPCIONES_ESTADO, OPCIONES_TIPO, tipoDeEtiquetaDeEstado } from '../utilidades/casos.js'
import { textosDelRubro } from '../utilidades/lenguaje.js'
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

function Filtros({ filtros, espacios, alAplicar, etiquetaReferencia }) {
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

  const avanzados = Boolean(filtros.espacio || filtros.desde || filtros.hasta)

  return (
    <form className="filtros" onSubmit={aplicar} role="search" aria-label="Buscar casos">
      <div className="filtros__principal">
        <CampoTexto etiqueta="Número de caso" nombre="numero" value={valores.numero} onChange={cambiar} />
        <CampoTexto etiqueta={etiquetaReferencia} nombre="expediente" value={valores.expediente} onChange={cambiar} />
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
        <button type="submit" className="boton filtros__buscar">
          <Icono nombre="buscar" tamanio={18} />
          Buscar
        </button>
      </div>
      <details className="filtros__mas" open={avanzados}>
        <summary>Más filtros</summary>
        <div className="formulario__fila">
          <CampoSeleccion
            etiqueta="Espacio"
            nombre="espacio"
            value={valores.espacio}
            onChange={cambiar}
            opciones={[{ valor: '', texto: 'Todos' }, ...espacios]}
          />
          <CampoTexto etiqueta="Hecho desde" nombre="desde" tipo="date" value={valores.desde} onChange={cambiar} />
          <CampoTexto etiqueta="Hecho hasta" nombre="hasta" tipo="date" value={valores.hasta} onChange={cambiar} />
        </div>
      </details>
      {hayFiltros && (
        <button type="button" className="boton boton--fantasma boton--chico" onClick={limpiar}>
          Limpiar los filtros
        </button>
      )}
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
        <div>
          <h1>Casos</h1>
          <p className="encabezado-pagina__bajada">{textosDelRubro(usuario.perfil).bajadaCasos}</p>
        </div>
        <Link to="/casos/nuevo" className="boton">
          <Icono nombre="mas" tamanio={18} />
          Nuevo caso
        </Link>
      </div>
      {state?.mensaje && <Aviso tipo="exito">{state.mensaje}</Aviso>}
      {datos?.transferencias.length > 0 && (
        <Transferencias transferencias={datos.transferencias} alResponder={recargar} />
      )}
      <section className="seccion seccion--filtros" aria-labelledby="titulo-buscar">
        <h2 id="titulo-buscar" className="solo-lectores">Buscar</h2>
        <Filtros
          key={clave}
          filtros={filtros}
          espacios={espacios}
          alAplicar={aplicarFiltros}
          etiquetaReferencia={textosDelRubro(usuario.perfil).etiquetaReferencia}
        />
      </section>

      <section className="seccion seccion--lista" aria-labelledby="titulo-resultados" aria-busy={cargando}>
        <h2 id="titulo-resultados" className="seccion__titulo-chico">
          {datos ? `${datos.total} ${datos.total === 1 ? 'caso' : 'casos'}` : 'Resultados'}
        </h2>
        {cargando && <Cargando texto="Buscando casos…" />}
        {error && <Aviso tipo="error">{error.message}</Aviso>}
        {datos && datos.casos.length === 0 && (
          <div className="estado-vacio">
            <div className="visor estado-vacio__visor">
              <Icono nombre={clave ? 'buscar' : 'casos'} tamanio={28} />
            </div>
            <p>{clave ? 'No hay casos con esos filtros.' : 'Todavía no tenés casos. Creá el primero.'}</p>
            {!clave && (
              <Link to="/casos/nuevo" className="boton">
                <Icono nombre="mas" tamanio={18} />
                Nuevo caso
              </Link>
            )}
          </div>
        )}
        {datos && datos.casos.length > 0 && (
          <ul className="lista-casos">
            {datos.casos.map((caso) => (
              <li key={caso.id} className="fila-caso">
                <div className="fila-caso__principal">
                  <Link to={`/casos/${caso.id}`} className="fila-caso__numero">
                    {caso.numero}
                  </Link>
                  <span className="fila-caso__lugar">{caso.lugar}</span>
                </div>
                <span className="fila-caso__detalle">
                  {caso.tipo_nombre} · {caso.espacio.nombre} · Hecho del {formatearDia(caso.fecha_hecho)}
                  {caso.expediente && ` · ${caso.expediente}`}
                </span>
                <div className="fila-caso__etiquetas">
                  <Etiqueta tipo={tipoDeEtiquetaDeEstado(caso.estado)}>{caso.estado_nombre}</Etiqueta>
                  <Etiqueta>{caso.mi_permiso_nombre}</Etiqueta>
                </div>
                <Icono nombre="derecha" tamanio={18} />
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
