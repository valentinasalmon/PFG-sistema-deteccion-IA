/**
 * Pantalla "Administración": tablero de la plataforma, aseguradoras pendientes
 * y listados de cuentas y organizaciones.
 *
 * Solo para el Administrador de la plataforma. El tablero (014) muestra
 * indicadores agregados con un rango de fechas; ningún dato permite abrir un
 * caso, una imagen o un informe. Las aseguradoras pendientes se aprueban o se
 * rechazan con un motivo que se informa por correo (021).
 *
 * Desde la funcionalidad 028, el período se elige con botones (este mes,
 * 3 meses, el año o desde el inicio) o con fechas a pedido; los indicadores
 * tienen todos su detalle y los listados usan las pestañas comunes.
 *
 * Realiza: RF21, RF22; RN38; CA7 a CA9 de la funcionalidad 021.
 */
import { useCallback, useState } from 'react'
import {
  aprobarAseguradora,
  listarAseguradorasPendientes,
  listarParaAdministracion,
  obtenerTablero,
  rechazarAseguradora,
} from '../api/administracion.js'
import Aviso from '../componentes/Aviso.jsx'
import BotonConfirmar from '../componentes/BotonConfirmar.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import { NOMBRES_DE_PLAN } from '../utilidades/planes.js'
import { rangoDelPeriodo } from '../utilidades/periodos.js'

function FormularioRechazo({ aseguradora, alTerminar }) {
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    if (!motivo.trim()) {
      setError('Indicá el motivo: se lo enviamos por correo a quien la registró.')
      return
    }
    setEnviando(true)
    try {
      const respuesta = await rechazarAseguradora(aseguradora.id, motivo)
      await alTerminar({ tipo: 'exito', texto: respuesta.mensaje })
    } catch (errorApi) {
      setError(errorApi.message)
      setEnviando(false)
    }
  }

  return (
    <form onSubmit={manejarEnvio} className="formulario formulario--compacto" noValidate>
      <CampoTexto
        etiqueta={`Motivo del rechazo de ${aseguradora.nombre}`}
        nombre="motivo"
        value={motivo}
        onChange={(evento) => setMotivo(evento.target.value)}
        error={error}
        required
      />
      <div className="acciones-en-linea">
        <button type="submit" className="boton boton--peligro boton--chico" disabled={enviando}>
          Rechazar la aseguradora
        </button>
        <button
          type="button"
          className="boton boton--secundario boton--chico"
          onClick={() => alTerminar(null)}
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}

function Pendientes() {
  const { datos, error, cargando, recargar } = useDatos(listarAseguradorasPendientes)
  const [aviso, setAviso] = useState(null)
  const [rechazando, setRechazando] = useState(null)

  async function terminar(resultado) {
    setRechazando(null)
    setAviso(resultado)
    if (resultado) await recargar()
  }

  async function aprobar(aseguradora) {
    try {
      const respuesta = await aprobarAseguradora(aseguradora.id)
      await terminar({ tipo: 'exito', texto: respuesta.mensaje })
    } catch (errorApi) {
      setAviso({ tipo: 'error', texto: errorApi.message })
    }
  }

  if (cargando) return <Cargando texto="Cargando las aseguradoras pendientes…" />
  if (error) return <Aviso tipo="error">{error.message}</Aviso>

  return (
    <section className="seccion" aria-labelledby="titulo-pendientes">
      <h2 id="titulo-pendientes">Aseguradoras pendientes de aprobación</h2>
      <p className="nota">
        Antes de aprobar, comprobá que la persona trabaje en la aseguradora (por ejemplo, con el dominio de su
        correo o comunicándote con la empresa).
      </p>
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      {datos.length === 0 ? (
        <p className="nota">No hay aseguradoras pendientes.</p>
      ) : (
        <ul className="lista-tarjetas">
          {datos.map((aseguradora) => (
            <li key={aseguradora.id} className="tarjeta-item">
              <div className="tarjeta-item__principal">
                <span className="tarjeta-item__titulo">{aseguradora.nombre}</span>
                <span className="tarjeta-item__detalle">
                  CUIT {aseguradora.cuit} · Registrada el {formatearFecha(aseguradora.creada_en)}
                </span>
                <span className="tarjeta-item__detalle">
                  Por {aseguradora.referente.nombre} ({aseguradora.referente.correo})
                  {!aseguradora.referente.verificado && ' · correo sin verificar'}
                </span>
                <span className="tarjeta-item__detalle">
                  <Etiqueta tipo="destacada">Pago acreditado</Etiqueta> Plan{' '}
                  {NOMBRES_DE_PLAN[aseguradora.plan] ?? aseguradora.plan}. Si la rechazás, el pago se
                  devuelve.
                </span>
              </div>
              {rechazando === aseguradora.id ? (
                <FormularioRechazo aseguradora={aseguradora} alTerminar={terminar} />
              ) : (
                <div className="acciones-en-linea">
                  <BotonConfirmar
                    texto="Aprobar"
                    pregunta={`¿Aprobar ${aseguradora.nombre}?`}
                    textoConfirmar="Aprobar"
                    onConfirmar={() => aprobar(aseguradora)}
                  />
                  <button
                    type="button"
                    className="boton boton--secundario-peligro boton--chico"
                    onClick={() => {
                      setAviso(null)
                      setRechazando(aseguradora.id)
                    }}
                    aria-label={`Rechazar ${aseguradora.nombre}`}
                  >
                    Rechazar
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

const NOMBRES = {
  abogado: 'Abogados',
  aseguradora: 'Aseguradoras',
  estudio_juridico: 'Estudios jurídicos',
  basico: 'Básico',
  profesional: 'Profesional',
  borrador: 'Borrador',
  en_analisis: 'En análisis',
  analizado: 'Analizado',
  cerrado: 'Cerrado',
  archivado: 'Archivado',
  automovilistico: 'Automovilístico',
  laboral: 'Laboral',
}
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

const suma = (valores) => Object.values(valores ?? {}).reduce((total, n) => total + n, 0)
const nombreDeMes = (clave) => `${MESES[Number(clave.slice(5, 7)) - 1]} ${clave.slice(2, 4)}`

function Indicador({ titulo, valor, detalle }) {
  return (
    <li className="indicador">
      <span className="indicador__titulo">{titulo}</span>
      <span className="indicador__valor">{valor}</span>
      {detalle && <span className="indicador__detalle">{detalle}</span>}
    </li>
  )
}

/** Barras horizontales de una distribución, con el valor escrito (no depende del color). */
function Distribucion({ titulo, valores }) {
  const total = suma(valores) || 1
  const filas = Object.entries(valores ?? {}).sort((a, b) => b[1] - a[1])
  return (
    <figure className="grafico">
      <figcaption>{titulo}</figcaption>
      {filas.length === 0 ? (
        <p className="nota">Sin datos.</p>
      ) : (
        <ul className="distribucion">
          {filas.map(([clave, cantidad]) => (
            <li key={clave}>
              <span>{NOMBRES[clave] ?? clave}</span>
              <span className="distribucion__barra" aria-hidden="true">
                <span style={{ width: `${(cantidad / total) * 100}%` }} />
              </span>
              <strong>{cantidad}</strong>
            </li>
          ))}
        </ul>
      )}
    </figure>
  )
}

/** Columnas por mes; cada una dice su valor para que se lea sin el gráfico. */
function SeriePorMes({ titulo, valores }) {
  const filas = Object.entries(valores ?? {})
  const maximo = Math.max(1, ...filas.map(([, n]) => n))
  return (
    <figure className="grafico">
      <figcaption>{titulo}</figcaption>
      {filas.length === 0 ? (
        <p className="nota">Sin datos en el período.</p>
      ) : (
        <ol className="serie">
          {filas.map(([mes, cantidad]) => (
            <li key={mes} aria-label={`${nombreDeMes(mes)}: ${cantidad}`}>
              <strong>{cantidad}</strong>
              <span className="serie__barra" style={{ height: `${(cantidad / maximo) * 100}%` }} />
              <span className="serie__mes">{nombreDeMes(mes)}</span>
            </li>
          ))}
        </ol>
      )}
    </figure>
  )
}

const PERIODOS = [
  ['mes', 'Este mes'],
  ['trimestre', '3 meses'],
  ['anio', 'Este año'],
  ['inicio', 'Desde el inicio'],
]

/** Detalle de los casos por estado: los dos estados con más casos. */
function detalleDeCasos(porEstado) {
  return Object.entries(porEstado ?? {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([estado, cantidad]) => `${cantidad} ${NOMBRES[estado].toLowerCase()}`)
    .join(' · ')
}

function Tablero() {
  const [periodo, setPeriodo] = useState('inicio')
  const [rango, setRango] = useState({ desde: '', hasta: '' })
  const [borrador, setBorrador] = useState(rango)
  const [fechasAbiertas, setFechasAbiertas] = useState(false)
  const cargar = useCallback(() => obtenerTablero(rango), [rango])
  const { datos, error, cargando } = useDatos(cargar)

  function elegirPeriodo(clave) {
    setPeriodo(clave)
    setFechasAbiertas(false)
    const nuevo = rangoDelPeriodo(clave)
    setBorrador(nuevo)
    setRango(nuevo)
  }

  function aplicar(evento) {
    evento.preventDefault()
    setPeriodo('fechas')
    setRango(borrador)
  }

  return (
    <section className="seccion" aria-labelledby="titulo-tablero">
      <div className="seccion__cabecera">
        <h2 id="titulo-tablero">Tablero de la plataforma</h2>
        <div className="periodos" role="group" aria-label="Período">
          {PERIODOS.map(([clave, texto]) => (
            <button
              key={clave}
              type="button"
              aria-pressed={periodo === clave}
              className={`segmentos__opcion ${periodo === clave ? 'segmentos__opcion--activa' : ''}`}
              onClick={() => elegirPeriodo(clave)}
            >
              {texto}
            </button>
          ))}
          <button
            type="button"
            className="boton boton--fantasma boton--chico"
            aria-expanded={fechasAbiertas}
            onClick={() => setFechasAbiertas(!fechasAbiertas)}
          >
            Elegir fechas…
          </button>
        </div>
      </div>
      {fechasAbiertas && (
        <form className="rango-fechas" onSubmit={aplicar} aria-label="Rango de fechas">
          <CampoTexto
            etiqueta="Desde"
            nombre="desde"
            tipo="date"
            value={borrador.desde}
            onChange={(e) => setBorrador({ ...borrador, desde: e.target.value })}
          />
          <CampoTexto
            etiqueta="Hasta"
            nombre="hasta"
            tipo="date"
            value={borrador.hasta}
            onChange={(e) => setBorrador({ ...borrador, hasta: e.target.value })}
          />
          <button type="submit" className="boton boton--secundario">
            Aplicar
          </button>
        </form>
      )}
      {cargando && <Cargando texto="Calculando los indicadores…" />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {datos && (
        <>
          <ul className="indicadores">
            <Indicador
              titulo="Cuentas verificadas"
              valor={suma(datos.usuarios_por_perfil)}
              detalle={`${datos.usuarios_por_perfil.abogado ?? 0} abogados · ${datos.usuarios_por_perfil.aseguradora ?? 0} de aseguradoras`}
            />
            <Indicador
              titulo="Organizaciones"
              valor={suma(datos.organizaciones_por_tipo)}
              detalle={`${datos.organizaciones_por_tipo.estudio_juridico ?? 0} estudios · ${datos.organizaciones_por_tipo.aseguradora ?? 0} aseguradoras`}
            />
            <Indicador
              titulo="Casos"
              valor={suma(datos.casos_por_estado)}
              detalle={detalleDeCasos(datos.casos_por_estado) || 'Sin casos'}
            />
            <Indicador
              titulo="Análisis en el período"
              valor={suma(datos.analisis_por_mes)}
              detalle={periodo === 'inicio' ? 'Desde el inicio' : 'En el período elegido'}
            />
          </ul>
          <div className="graficos">
            <SeriePorMes titulo="Análisis por mes" valores={datos.analisis_por_mes} />
            <SeriePorMes titulo="Altas de cuentas por mes" valores={datos.altas_por_mes} />
            <Distribucion titulo="Casos por estado" valores={datos.casos_por_estado} />
            <Distribucion titulo="Casos por tipo" valores={datos.casos_por_tipo} />
            <Distribucion titulo="Organizaciones por plan" valores={datos.organizaciones_por_plan} />
            <Distribucion titulo="Cuentas por perfil" valores={datos.usuarios_por_perfil} />
          </div>
          <p className="nota">
            Los indicadores son agregados: ninguno permite identificar ni abrir un caso, una imagen o un
            informe.
          </p>
        </>
      )}
    </section>
  )
}

function Listados() {
  const [recurso, setRecurso] = useState('usuarios')
  const [busqueda, setBusqueda] = useState('')
  const [consulta, setConsulta] = useState({ busqueda: '', pagina: 1 })
  const cargar = useCallback(
    () =>
      listarParaAdministracion(recurso, {
        busqueda: consulta.busqueda,
        pagina: consulta.pagina,
      }),
    [recurso, consulta],
  )
  const { datos, error, cargando } = useDatos(cargar)
  const filas = datos?.[recurso] ?? []

  function elegir(nuevo) {
    setRecurso(nuevo)
    setConsulta({ busqueda: '', pagina: 1 })
    setBusqueda('')
  }

  return (
    <section className="seccion" aria-labelledby="titulo-listados">
      <div className="seccion__cabecera">
        <h2 id="titulo-listados">Cuentas y organizaciones</h2>
      </div>
      <div className="pestanias" role="tablist" aria-label="Qué listar">
        {[
          ['usuarios', 'Cuentas'],
          ['organizaciones', 'Organizaciones'],
        ].map(([clave, texto]) => (
          <button
            key={clave}
            type="button"
            role="tab"
            aria-selected={recurso === clave}
            className="pestanias__pestania"
            onClick={() => elegir(clave)}
          >
            {texto}
          </button>
        ))}
      </div>
      <form
        className="busqueda-en-linea"
        role="search"
        onSubmit={(e) => {
          e.preventDefault()
          setConsulta({ busqueda, pagina: 1 })
        }}
      >
        <CampoTexto
          etiqueta={recurso === 'usuarios' ? 'Buscar por nombre o correo' : 'Buscar por nombre'}
          nombre="busqueda"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <button type="submit" className="boton boton--secundario">
          Buscar
        </button>
      </form>
      {cargando && <Cargando texto="Cargando el listado…" />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {datos && (
        <div className="tabla-contenedor">
          <table className="tabla">
            <thead>
              {recurso === 'usuarios' ? (
                <tr>
                  <th>Nombre</th>
                  <th>Correo</th>
                  <th>Perfil</th>
                  <th>Estado</th>
                  <th>Alta</th>
                </tr>
              ) : (
                <tr>
                  <th>Nombre</th>
                  <th>Tipo</th>
                  <th>Plan</th>
                  <th>Miembros</th>
                  <th>Estado</th>
                </tr>
              )}
            </thead>
            <tbody>
              {filas.length === 0 && (
                <tr>
                  <td colSpan={5} className="nota">
                    No hay resultados.
                  </td>
                </tr>
              )}
              {recurso === 'usuarios'
                ? filas.map((u) => (
                    <tr key={u.id}>
                      <td>
                        <strong>{u.nombre}</strong>
                        {u.rol === 'administrador' && <span className="nota"> · Administrador</span>}
                      </td>
                      <td>{u.correo}</td>
                      <td>{NOMBRES[u.perfil] ?? u.perfil}</td>
                      <td>{u.estado}</td>
                      <td>{formatearFecha(u.creado_en)}</td>
                    </tr>
                  ))
                : filas.map((o) => (
                    <tr key={o.id}>
                      <td>{o.nombre}</td>
                      <td>{NOMBRES[o.tipo] ?? o.tipo}</td>
                      <td>{o.plan}</td>
                      <td>{o.miembros}</td>
                      <td>{o.estado === 'pendiente' ? 'Pendiente' : 'Activa'}</td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
      )}
      {datos && datos.paginas > 1 && (
        <nav className="paginacion" aria-label="Páginas del listado">
          <button
            type="button"
            className="boton boton--secundario boton--chico"
            disabled={consulta.pagina <= 1}
            onClick={() => setConsulta({ ...consulta, pagina: consulta.pagina - 1 })}
          >
            Anterior
          </button>
          <span>
            Página {datos.pagina} de {datos.paginas}
          </span>
          <button
            type="button"
            className="boton boton--secundario boton--chico"
            disabled={consulta.pagina >= datos.paginas}
            onClick={() => setConsulta({ ...consulta, pagina: consulta.pagina + 1 })}
          >
            Siguiente
          </button>
        </nav>
      )}
    </section>
  )
}

/** Tablero de la administradora; la ruta ya impide que lo abra otra persona (028). */
export default function PaginaAdministracion() {
  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Administración</h1>
          <p className="encabezado-pagina__bajada">
            Cómo crece la plataforma, qué aseguradoras esperan aprobación y quiénes la usan.
          </p>
        </div>
      </div>
      <Tablero />
      <Pendientes />
      <Listados />
    </>
  )
}
