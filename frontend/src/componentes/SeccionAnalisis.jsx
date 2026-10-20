/**
 * Sección "Análisis" de la pantalla de un caso.
 *
 * Muestra el historial de análisis y los resultados del elegido: por cada
 * imagen, su verificación de integridad y, por cada capa, el nivel de
 * indicio, la conclusión, las anomalías y los metadatos extraídos. Mientras
 * un análisis está en curso, consulta su progreso cada pocos segundos sin
 * recargar la página. No hay un puntaje que combine capas (RN27).
 *
 * Cada análisis finalizado ofrece descargar su informe PDF o, si no se pudo
 * generar, volver a generarlo (funcionalidad 008). La capa de credenciales de
 * contenido muestra además el estado de su firma (funcionalidad 009) y la de
 * niveles de error, su mapa ELA (funcionalidad 011).
 *
 * Realiza: RF40, RF43, RF44, RF46; CA5 a CA7 y CA12 a CA14 de la funcionalidad
 * 007; CA6 de la 008; CA7 de la 009; CA4 de la 011.
 */
import { useCallback, useEffect, useState } from 'react'
import { listarAnalisis, obtenerAnalisis } from '../api/analisis.js'
import { descargarInforme, regenerarInforme } from '../api/informes.js'
import { useDatos } from '../hooks/useDatos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import Aviso from './Aviso.jsx'
import Cargando from './Cargando.jsx'
import Etiqueta from './Etiqueta.jsx'

export const INTERVALO_DE_CONSULTA = 2000

const TITULOS_CAPA = {
  metadatos: 'Metadatos',
  c2pa: 'Credenciales de contenido (C2PA)',
  ela: 'Niveles de error (ELA)',
}
const TITULOS_TABLA = {
  metadatos: 'Metadatos extraídos',
  c2pa: 'Datos de las credenciales',
  ela: 'Datos del análisis',
}
const ESTADOS_FIRMA = {
  confiable: 'Firma confiable',
  firmante_no_reconocido: 'Firmante no reconocido',
  contenido_modificado: 'Modificada después de firmarse',
  firma_invalida: 'Credenciales no válidas',
}
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

function EstadoDeLaFirma({ detalle }) {
  if (detalle?.sin_credenciales) return <Etiqueta tipo="neutra">Sin credenciales</Etiqueta>
  const estado = detalle?.estado_firma
  if (!ESTADOS_FIRMA[estado]) return null
  return (
    <Etiqueta tipo={estado === 'confiable' ? 'neutra' : 'alerta'}>{ESTADOS_FIRMA[estado]}</Etiqueta>
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
      <h4>
        {titulo} {resultado.capa === 'c2pa' && <EstadoDeLaFirma detalle={resultado.detalle} />}
      </h4>
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
      {resultado.imagen && (
        <figure className="mapa-capa">
          <img src={resultado.imagen} alt={`Mapa de la capa ${titulo}`} loading="lazy" />
          <figcaption className="nota">
            Las zonas claras cambiaron más al recomprimir la imagen; las regiones señaladas están
            recuadradas en rojo. Es una señal complementaria: los bordes y los detalles marcados
            también se ven claros sin que haya edición.
          </figcaption>
        </figure>
      )}
      {resultado.detalle?.tabla?.length > 0 && (
        <details>
          <summary>{TITULOS_TABLA[resultado.capa] ?? 'Datos extraídos'}</summary>
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

function AccionesDelInforme({ idCaso, analisis, puedeGenerar, alGenerar }) {
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function ejecutar(accion) {
    setError(null)
    setEnviando(true)
    try {
      await accion()
    } catch (errorApi) {
      setError(errorApi.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="acciones-informe">
      {error && <Aviso tipo="error">{error}</Aviso>}
      {analisis.informe ? (
        <button
          type="button"
          className="boton"
          disabled={enviando}
          onClick={() => ejecutar(() => descargarInforme(idCaso, analisis.informe.id))}
        >
          Descargar el informe PDF
        </button>
      ) : (
        <>
          <Aviso tipo="info">No se pudo generar el informe PDF de este análisis.</Aviso>
          {puedeGenerar && (
            <button
              type="button"
              className="boton boton--secundario"
              disabled={enviando}
              onClick={() =>
                ejecutar(async () => {
                  await regenerarInforme(idCaso, analisis.id)
                  await alGenerar()
                })
              }
            >
              {enviando ? 'Generando…' : 'Generar el informe'}
            </button>
          )}
        </>
      )}
    </div>
  )
}

function Detalle({ idCaso, idAnalisis, puedeGenerar, alTerminar }) {
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
      {analisis.estado === 'finalizado' && (
        <>
          <AccionesDelInforme
            idCaso={idCaso}
            analisis={analisis}
            puedeGenerar={puedeGenerar}
            alGenerar={async () => {
              await recargar()
              await alTerminar()
            }}
          />
          <Resultados analisis={analisis} />
        </>
      )}
    </>
  )
}

export default function SeccionAnalisis({ idCaso, puedeGenerar = false, alTerminar }) {
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
      <Detalle
        key={idElegido}
        idCaso={idCaso}
        idAnalisis={idElegido}
        puedeGenerar={puedeGenerar}
        alTerminar={alTerminar}
      />
    </section>
  )
}
