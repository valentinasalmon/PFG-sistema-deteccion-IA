/**
 * Sección "Análisis" de la pantalla de un caso.
 *
 * Muestra el historial de análisis y los resultados del elegido: por cada
 * imagen, su verificación de integridad y, por cada capa, el nivel de
 * indicio, la conclusión, las anomalías y los metadatos extraídos. Mientras
 * un análisis está en curso, consulta su progreso cada pocos segundos sin
 * recargar la página. No hay un puntaje que combine capas (RN27).
 *
 * Realiza: RF43, RF46; CA5 a CA7 y CA12 a CA14 de la funcionalidad 007.
 */
import { useCallback, useEffect, useState } from 'react'
import { listarAnalisis, obtenerAnalisis } from '../api/analisis.js'
import { useDatos } from '../hooks/useDatos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import Aviso from './Aviso.jsx'
import Cargando from './Cargando.jsx'
import Etiqueta from './Etiqueta.jsx'

export const INTERVALO_DE_CONSULTA = 2000

const TITULOS_CAPA = { metadatos: 'Metadatos' }
const NOMBRES_SEVERIDAD = {
  directo: 'Directo',
  fuerte: 'Fuerte',
  moderado: 'Moderado',
  debil: 'Débil',
  neutro: 'Informativo',
}

function tipoDeEtiquetaDeAnalisis(estado) {
  if (estado === 'fallido') return 'alerta'
  if (estado === 'finalizado') return 'neutra'
  return 'destacada'
}

function Progreso({ analisis }) {
  const { imagen_actual: actual, capa_actual: capa } = analisis.progreso
  return (
    <div className="progreso-analisis" role="status">
      <Cargando
        texto={
          analisis.estado === 'en_cola'
            ? 'El análisis está en cola…'
            : `Analizando la imagen ${Math.max(actual, 1)} de ${analisis.cantidad_imagenes}` +
              (capa ? ` · capa ${capa}` : '') +
              '…'
        }
      />
      <p className="nota">Podés salir de esta pantalla: te avisamos por correo cuando termine.</p>
    </div>
  )
}

function ResultadoDeCapa({ resultado }) {
  const titulo = TITULOS_CAPA[resultado.capa] ?? resultado.capa
  if (resultado.estado === 'no_disponible') {
    return (
      <div className="resultado-capa">
        <h4>{titulo}: no disponible</h4>
        <p className="nota">{resultado.motivo}</p>
      </div>
    )
  }
  return (
    <div className="resultado-capa">
      <h4>{titulo}</h4>
      <div className="nivel-indicio">
        <label htmlFor={`nivel-${resultado.capa}-${resultado.version}`}>Nivel de indicio</label>
        <meter
          id={`nivel-${resultado.capa}-${resultado.version}`}
          min="0"
          max="100"
          low="40"
          high="70"
          optimum="0"
          value={resultado.nivel}
        />
        <strong>{resultado.nivel} %</strong>
      </div>
      <p>{resultado.conclusion}</p>
      {resultado.anomalias.length > 0 && (
        <ul className="lista-anomalias" aria-label={`Hallazgos de la capa ${titulo}`}>
          {resultado.anomalias.map((anomalia, indice) => (
            <li key={indice}>
              <Etiqueta tipo={anomalia.severidad === 'neutro' ? 'neutra' : 'alerta'}>
                {NOMBRES_SEVERIDAD[anomalia.severidad]}
              </Etiqueta>{' '}
              {anomalia.descripcion}
            </li>
          ))}
        </ul>
      )}
      {resultado.detalle?.tabla?.length > 0 && (
        <details>
          <summary>Metadatos extraídos</summary>
          <dl className="datos-fijos">
            {resultado.detalle.tabla.map((fila) => (
              <div key={fila.campo} className="datos-fijos__fila">
                <dt>{fila.campo}</dt>
                <dd>{fila.valor}</dd>
              </div>
            ))}
          </dl>
        </details>
      )}
      <p className="nota">Versión: {resultado.version}</p>
    </div>
  )
}

function Resultados({ analisis }) {
  return analisis.imagenes.map((imagen) => (
    <article key={`${imagen.id_imagen}-${imagen.huella}`} className="resultado-imagen">
      <h3>{imagen.nombre}</h3>
      {imagen.integridad === 'alterada' ? (
        <Aviso tipo="error">
          La huella SHA-256 de esta imagen ya no coincide con la registrada al cargarla: se
          excluyó del análisis por una anomalía de integridad.
        </Aviso>
      ) : (
        imagen.resultados.map((resultado) => (
          <ResultadoDeCapa key={resultado.capa} resultado={resultado} />
        ))
      )}
    </article>
  ))
}

function Detalle({ idCaso, idAnalisis, alTerminar }) {
  const cargar = useCallback(() => obtenerAnalisis(idCaso, idAnalisis), [idCaso, idAnalisis])
  const { datos: analisis, error, recargar } = useDatos(cargar)
  const enCurso = Boolean(analisis?.en_curso)

  useEffect(() => {
    if (!enCurso) return undefined
    const temporizador = setTimeout(async () => {
      await recargar()
    }, INTERVALO_DE_CONSULTA)
    return () => clearTimeout(temporizador)
  }, [enCurso, analisis, recargar])

  const [estabaEnCurso, setEstabaEnCurso] = useState(false)
  if (enCurso && !estabaEnCurso) setEstabaEnCurso(true)
  useEffect(() => {
    if (estabaEnCurso && analisis && !analisis.en_curso) alTerminar()
  }, [estabaEnCurso, analisis, alTerminar])

  if (error) return <Aviso tipo="error">{error.message}</Aviso>
  if (!analisis) return <Cargando texto="Cargando los resultados…" />
  return (
    <>
      {analisis.en_curso && <Progreso analisis={analisis} />}
      {analisis.estado === 'fallido' && (
        <Aviso tipo="error">El análisis no pudo completarse: {analisis.motivo_falla}</Aviso>
      )}
      {analisis.estado === 'finalizado' && <Resultados analisis={analisis} />}
    </>
  )
}

export default function SeccionAnalisis({ idCaso, alTerminar }) {
  const cargar = useCallback(() => listarAnalisis(idCaso), [idCaso])
  const { datos: historial, error } = useDatos(cargar)
  const [elegido, setElegido] = useState(null)

  if (error) {
    return (
      <section className="seccion" aria-labelledby="titulo-analisis">
        <h2 id="titulo-analisis">Análisis</h2>
        <Aviso tipo="error">{error.message}</Aviso>
      </section>
    )
  }
  if (!historial || historial.length === 0) return null
  const idElegido = elegido ?? historial[0].id

  return (
    <section className="seccion" aria-labelledby="titulo-analisis">
      <h2 id="titulo-analisis">Análisis</h2>
      <p className="nota">
        Cada capa informa indicios por separado; no se combinan en un puntaje único. Ante
        cualquier duda, consultá con un perito especializado.
      </p>
      {historial.length > 1 && (
        <ul className="historial-analisis" aria-label="Historial de análisis">
          {historial.map((analisis) => (
            <li key={analisis.id}>
              <button
                type="button"
                className={`boton boton--chico ${analisis.id === idElegido ? '' : 'boton--secundario'}`}
                aria-pressed={analisis.id === idElegido}
                onClick={() => setElegido(analisis.id)}
              >
                {formatearFecha(analisis.creado_en)} · {analisis.cantidad_imagenes} imagen(es)
              </button>{' '}
              <Etiqueta tipo={tipoDeEtiquetaDeAnalisis(analisis.estado)}>
                {analisis.estado_nombre}
              </Etiqueta>
            </li>
          ))}
        </ul>
      )}
      <Detalle key={idElegido} idCaso={idCaso} idAnalisis={idElegido} alTerminar={alTerminar} />
    </section>
  )
}
