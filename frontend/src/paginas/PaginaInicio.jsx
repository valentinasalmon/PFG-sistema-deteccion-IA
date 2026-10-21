/**
 * Pantalla de inicio con sesión iniciada: el panel principal.
 *
 * Muestra, en una sola consulta, los casos por estado, lo que espera una
 * respuesta (invitaciones y transferencias), los casos próximos a destruirse,
 * los análisis en curso, los casos compartidos recientemente, los últimos casos
 * actualizados y la actividad reciente. Cada elemento lleva a su caso o a la
 * pantalla donde se responde (RF48 CA3).
 *
 * Realiza: RF48 (CA1 a CA3), CU30; RN31; CA7 de la funcionalidad 002.
 */
import { Link } from 'react-router'
import { obtenerPanel } from '../api/panel.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { textosDelRubro } from '../utilidades/lenguaje.js'
import { OPCIONES_ESTADO } from '../utilidades/casos.js'
import { formatearFecha } from '../utilidades/fechas.js'

function EnlaceCaso({ caso }) {
  return <Link to={`/casos/${caso.id}`}>{caso.numero}</Link>
}

function Seccion({ id, titulo, children }) {
  return (
    <section className="seccion panel-seccion" aria-labelledby={id}>
      <h2 id={id}>{titulo}</h2>
      {children}
    </section>
  )
}

function CasosPorEstado({ porEstado }) {
  const total = Object.values(porEstado).reduce((suma, cantidad) => suma + cantidad, 0)
  return (
    <Seccion id="titulo-casos" titulo="Tus casos">
      {total === 0 ? (
        <p>Todavía no tenés casos.</p>
      ) : (
        <ul className="resumen-estados">
          {OPCIONES_ESTADO.map(({ valor, texto }) => (
            <li key={valor}>
              <Link to={`/casos?estado=${valor}`}>
                <span className="resumen-estados__cantidad">{porEstado[valor] ?? 0}</span>
                {texto}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Seccion>
  )
}

function Pendientes({ invitaciones, transferencias, proximos }) {
  if (invitaciones.length + transferencias.length + proximos.length === 0) return null
  return (
    <Seccion id="titulo-pendientes" titulo="Pendientes">
      <ul className="lista-panel">
        {invitaciones.map((invitacion) => (
          <li key={`invitacion-${invitacion.id}`}>
            <Etiqueta tipo="destacada">Invitación</Etiqueta>{' '}
            {invitacion.invitante ?? 'Alguien'} te invitó a {invitacion.organizacion.nombre}.{' '}
            <Link to="/organizaciones">Responder</Link>
          </li>
        ))}
        {transferencias.map((transferencia) => (
          <li key={`transferencia-${transferencia.id}`}>
            <Etiqueta tipo="destacada">Transferencia</Etiqueta>{' '}
            {transferencia.solicitante?.nombre ?? 'Alguien'} quiere transferirte el caso{' '}
            {transferencia.numero}. <Link to="/casos">Responder</Link>
          </li>
        ))}
        {proximos.map(({ caso, vence_en: venceEn }) => (
          <li key={`destruccion-${caso.id}`}>
            <Etiqueta tipo="alerta">Retención</Etiqueta> Los datos de <EnlaceCaso caso={caso} /> se
            destruyen el {formatearFecha(venceEn)}.
          </li>
        ))}
      </ul>
    </Seccion>
  )
}

function AnalisisEnCurso({ analisis }) {
  if (analisis.length === 0) return null
  return (
    <Seccion id="titulo-en-curso" titulo="Análisis en curso">
      <ul className="lista-panel">
        {analisis.map((item) => (
          <li key={item.id}>
            <EnlaceCaso caso={item.caso} />: {item.cantidad_imagenes} imagen(es),{' '}
            {item.estado === 'en_cola' ? 'en cola' : 'en proceso'}.
          </li>
        ))}
      </ul>
    </Seccion>
  )
}

function Compartidos({ compartidos }) {
  if (compartidos.length === 0) return null
  return (
    <Seccion id="titulo-compartidos" titulo="Compartidos con vos recientemente">
      <ul className="lista-panel">
        {compartidos.map((item) => (
          <li key={item.caso.id}>
            <EnlaceCaso caso={item.caso} /> ({item.caso.tipo_nombre}) · {item.responsable} te dio
            permiso de {item.nivel_nombre.toLowerCase()} el {formatearFecha(item.otorgado_en)}.
          </li>
        ))}
      </ul>
    </Seccion>
  )
}

function Recientes({ casos }) {
  if (casos.length === 0) return null
  return (
    <Seccion id="titulo-recientes" titulo="Actualizados recientemente">
      <ul className="lista-panel">
        {casos.map((caso) => (
          <li key={caso.id}>
            <EnlaceCaso caso={caso} /> · {caso.tipo_nombre} ·{' '}
            <Etiqueta tipo="neutra">{caso.estado_nombre}</Etiqueta> · {formatearFecha(caso.actualizado_en)}
          </li>
        ))}
      </ul>
    </Seccion>
  )
}

function Actividad({ eventos }) {
  if (eventos.length === 0) return null
  return (
    <Seccion id="titulo-actividad" titulo="Actividad reciente">
      <ul className="lista-panel" aria-label="Actividad reciente de tus casos">
        {eventos.map((evento, indice) => (
          <li key={`${evento.fecha}-${indice}`}>
            <Link to={`/casos/${evento.id_caso}`}>{evento.texto}</Link>
            <span className="nota"> · {formatearFecha(evento.fecha)}</span>
          </li>
        ))}
      </ul>
    </Seccion>
  )
}

export default function PaginaInicio() {
  const { usuario } = useSesion()
  const { datos: panel, error, cargando } = useDatos(obtenerPanel)

  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Hola, {usuario.nombre}</h1>
          <p className="encabezado-pagina__bajada">{textosDelRubro(usuario.perfil).bajadaPanel}</p>
        </div>
        <div className="acciones-en-linea">
          <Link to="/casos" className="boton boton--secundario">
            Ver mis casos
          </Link>
        </div>
      </div>
      {cargando && <Cargando />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {panel && (
        <>
          <CasosPorEstado porEstado={panel.por_estado} />
          <div className="dos-columnas">
            <div className="dos-columnas__principal">
              <Recientes casos={panel.recientes} />
              <Actividad eventos={panel.actividad} />
            </div>
            <div className="dos-columnas__lateral">
              <Pendientes
                invitaciones={panel.invitaciones}
                transferencias={panel.transferencias}
                proximos={panel.proximos_a_destruir}
              />
              <AnalisisEnCurso analisis={panel.analisis_en_curso} />
              <Compartidos compartidos={panel.compartidos} />
            </div>
          </div>
        </>
      )}
    </>
  )
}
