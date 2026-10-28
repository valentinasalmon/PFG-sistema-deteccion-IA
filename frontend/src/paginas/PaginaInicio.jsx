/**
 * Pantalla de inicio con sesión iniciada: el panel principal.
 *
 * Muestra, en una sola consulta, los casos por estado (cada contador abre la
 * lista ya filtrada), lo que espera una respuesta (invitaciones y
 * transferencias), los casos próximos a destruirse, los análisis en curso, los
 * casos compartidos recientemente, los últimos casos actualizados y la
 * actividad reciente. Cada elemento lleva a su caso o a la pantalla donde se
 * responde (RF48 CA3).
 *
 * Desde la funcionalidad 028: contadores compactos, casos recientes con la
 * misma fila que la lista de casos, y la actividad en dos columnas, con la
 * propia en segunda persona y el enlace solo en el número del caso.
 *
 * Realiza: RF48 (CA1 a CA3), CU30; RN31; CA7 de la funcionalidad 002.
 */
import { useState } from 'react'
import { Link } from 'react-router'
import { obtenerPanel } from '../api/panel.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import FilaCaso from '../componentes/FilaCaso.jsx'
import Icono from '../componentes/Icono.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { textosDelRubro } from '../utilidades/lenguaje.js'
import { OPCIONES_ESTADO } from '../utilidades/casos.js'
import { formatearFecha } from '../utilidades/fechas.js'

const ACTIVIDAD_VISIBLE = 5

/** Ícono de cada tipo de evento de la actividad. */
const ICONOS_ACTIVIDAD = {
  'imagen.carga': 'imagen',
  'imagen.eliminacion': 'imagen',
  'analisis.solicitud': 'analisis',
  'analisis.finalizacion': 'verificado',
  'informe.generacion': 'documento',
  'caso.creacion': 'mas',
  'caso.edicion': 'lapiz',
}

function EnlaceCaso({ caso }) {
  return <Link to={`/casos/${caso.id}`}>{caso.numero}</Link>
}

function Seccion({ id, titulo, accion, children }) {
  return (
    <section className="seccion panel-seccion" aria-labelledby={id}>
      <div className="panel-seccion__cabecera">
        <h2 id={id}>{titulo}</h2>
        {accion}
      </div>
      {children}
    </section>
  )
}

function CasosPorEstado({ porEstado }) {
  return (
    <ul className="contadores" aria-label="Tus casos por estado">
      {OPCIONES_ESTADO.map(({ valor, texto }) => (
        <li key={valor}>
          <Link to={`/casos?estado=${valor}`} className="contador">
            <span className="contador__cifra">{porEstado[valor] ?? 0}</span>
            <span className="contador__texto">{texto}</span>
          </Link>
        </li>
      ))}
    </ul>
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
  return (
    <Seccion
      id="titulo-recientes"
      titulo="Casos recientes"
      accion={
        <Link to="/casos" className="boton boton--fantasma boton--chico">
          Ver todos los casos
        </Link>
      }
    >
      {casos.length === 0 ? (
        <div className="estado-vacio">
          <div className="visor estado-vacio__visor">
            <Icono nombre="casos" tamanio={28} />
          </div>
          <p>Todavía no tenés casos. Creá el primero desde «Nuevo caso».</p>
        </div>
      ) : (
        <ul className="lista-casos lista-casos--recuadro">
          {casos.map((caso) => (
            <FilaCaso key={caso.id} caso={caso} compacta />
          ))}
        </ul>
      )}
    </Seccion>
  )
}

/** Texto del evento con el enlace solo en el número del caso. */
function TextoEvento({ evento }) {
  const { texto, numero, id_caso: idCaso } = evento
  const posicion = numero ? texto.lastIndexOf(numero) : -1
  if (posicion < 0) return texto
  return (
    <>
      {texto.slice(0, posicion)}
      <Link to={`/casos/${idCaso}`}>{numero}</Link>
      {texto.slice(posicion + numero.length)}
    </>
  )
}

function Actividad({ eventos }) {
  const [todos, setTodos] = useState(false)
  if (eventos.length === 0) return null
  const visibles = todos ? eventos : eventos.slice(0, ACTIVIDAD_VISIBLE)
  return (
    <Seccion id="titulo-actividad" titulo="Actividad reciente">
      <ul className="actividad" aria-label="Actividad reciente de tus casos">
        {visibles.map((evento, indice) => (
          <li key={`${evento.fecha}-${indice}`} className="actividad__evento">
            <span className="actividad__icono" aria-hidden="true">
              <Icono nombre={ICONOS_ACTIVIDAD[evento.accion] ?? 'reloj'} tamanio={16} />
            </span>
            <div>
              <TextoEvento evento={evento} />
              <span className="actividad__fecha">{formatearFecha(evento.fecha)}</span>
            </div>
          </li>
        ))}
      </ul>
      {eventos.length > ACTIVIDAD_VISIBLE && (
        <button
          type="button"
          className="boton boton--secundario boton--chico"
          onClick={() => setTodos(!todos)}
          aria-expanded={todos}
        >
          {todos ? 'Ver menos' : 'Ver toda la actividad'}
        </button>
      )}
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
      </div>
      {cargando && <Cargando />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {panel && (
        <>
          <CasosPorEstado porEstado={panel.por_estado} />
          <Pendientes
            invitaciones={panel.invitaciones}
            transferencias={panel.transferencias}
            proximos={panel.proximos_a_destruir}
          />
          <div className="panel-columnas">
            <div className="panel-columnas__principal">
              <Recientes casos={panel.recientes} />
              <AnalisisEnCurso analisis={panel.analisis_en_curso} />
            </div>
            <div className="panel-columnas__lateral">
              <Actividad eventos={panel.actividad} />
              <Compartidos compartidos={panel.compartidos} />
            </div>
          </div>
        </>
      )}
    </>
  )
}
