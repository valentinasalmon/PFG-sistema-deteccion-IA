/**
 * Sección "Informes" de la pantalla de un caso: historial de informes PDF,
 * del más reciente al más antiguo, con quién pidió el análisis, las imágenes
 * incluidas, la huella del PDF y la descarga con un enlace firmado.
 *
 * Cada informe muestra su código de verificación pública y el estado del
 * sello de su huella en Hedera (funcionalidad 026).
 *
 * Desde la funcionalidad 028 es la etapa "Informe" del caso y muestra solo el
 * informe: el más reciente destacado, con las imágenes incluidas arriba, el
 * nivel de cada capa por imagen, el PDF con su código, sello y huella; debajo,
 * los informes anteriores.
 *
 * Realiza: RF45 (CA1, CA2), RF55; CA7 y CA8 de la funcionalidad 008.
 */
import { useCallback, useState } from 'react'
import { Link } from 'react-router'
import { obtenerAnalisis } from '../api/analisis.js'
import { descargarInforme, listarInformes } from '../api/informes.js'
import { useDatos } from '../hooks/useDatos.js'
import { formatearTamanio } from '../utilidades/archivos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import { codigoLegible } from '../utilidades/verificacion.js'
import Aviso from './Aviso.jsx'
import Cargando from './Cargando.jsx'
import Icono from './Icono.jsx'
import { ResumenDeImagen } from './SeccionAnalisis.jsx'

function textoSello(sello) {
  if (sello?.estado === 'sellado') return sello.simulado ? 'Sello simulado (pruebas)' : 'Registrado en Hedera'
  if (sello?.estado === 'fallido') return 'Sin sello de Hedera'
  if (sello?.estado) return 'Sello en Hedera en curso…'
  return 'Sin sello de tiempo'
}

/** Nivel de cada capa por imagen, tomado del análisis que generó el informe. */
function ResumenDelInforme({ idCaso, idAnalisis }) {
  const cargar = useCallback(() => obtenerAnalisis(idCaso, idAnalisis), [idCaso, idAnalisis])
  const { datos: analisis } = useDatos(cargar)
  const imagenes = analisis?.imagenes ?? []
  if (imagenes.length === 0) return null
  return (
    <ul className="resumen-informe" aria-label="Resultado por imagen">
      {imagenes.map((imagen) => (
        <li key={`${imagen.id_imagen}-${imagen.huella}`} className="resumen-informe__imagen">
          <strong>{imagen.nombre}</strong>
          {imagen.integridad === 'alterada' ? (
            <span className="nivel nivel--nd">Integridad alterada: excluida del análisis</span>
          ) : (
            <ResumenDeImagen imagen={imagen} />
          )}
        </li>
      ))}
    </ul>
  )
}

function InformeReciente({ idCaso, informe, alDescargar }) {
  return (
    <article className="informe-reciente" aria-labelledby="titulo-informe-reciente">
      <div className="informe-reciente__cabecera">
        <h3 id="titulo-informe-reciente">Informe del {formatearFecha(informe.generado_en)}</h3>
        <span className="nota">Pedido por {informe.solicitante}</span>
      </div>
      <div>
        <span className="nota">Imágenes incluidas</span>
        <ul className="tira-imagenes">
          {informe.imagenes.map((nombre) => (
            <li key={nombre} className="tira-imagenes__imagen">
              <Icono nombre="imagen" tamanio={16} />
              {nombre}
            </li>
          ))}
        </ul>
      </div>
      {informe.id_analisis && <ResumenDelInforme idCaso={idCaso} idAnalisis={informe.id_analisis} />}
      <div className="informe-pdf">
        <span className="informe-pdf__icono" aria-hidden="true">
          PDF
        </span>
        <dl className="informe-pdf__datos">
          <dt>Informe pericial preliminar</dt>
          <dd>{formatearTamanio(informe.tamanio)}</dd>
          {informe.codigo_verificacion && (
            <>
              <dt>Código de verificación</dt>
              <dd>
                <Link to={`/verificar/${informe.codigo_verificacion}`}>
                  {codigoLegible(informe.codigo_verificacion)}
                </Link>{' '}
                · {textoSello(informe.sello)}
              </dd>
            </>
          )}
          <dt>Huella SHA-256 del PDF</dt>
          <dd className="huella">{informe.huella}</dd>
        </dl>
        <button
          type="button"
          className="boton"
          onClick={() => alDescargar(informe)}
          aria-label={`Descargar el informe del ${formatearFecha(informe.generado_en)}`}
        >
          <Icono nombre="descargar" tamanio={18} />
          Descargar el PDF
        </button>
      </div>
    </article>
  )
}

export default function SeccionInformes({ idCaso, alVerAnalisis }) {
  const cargar = useCallback(() => listarInformes(idCaso), [idCaso])
  const { datos: informes, error } = useDatos(cargar)
  const [errorDescarga, setErrorDescarga] = useState(null)

  async function descargar(informe) {
    setErrorDescarga(null)
    try {
      await descargarInforme(idCaso, informe.id)
    } catch (errorApi) {
      setErrorDescarga(errorApi.message)
    }
  }

  if (error) {
    return (
      <section className="seccion" aria-labelledby="titulo-informes">
        <h2 id="titulo-informes">Informes</h2>
        <Aviso tipo="error">{error.message}</Aviso>
      </section>
    )
  }
  if (!informes) return <Cargando texto="Cargando los informes…" />
  if (informes.length === 0) {
    return (
      <section className="seccion estado-vacio-etapa" aria-labelledby="titulo-informes">
        <h2 id="titulo-informes">Informes</h2>
        <p className="nota">
          Todavía no hay informes. Se generan solos al terminar cada análisis.
        </p>
        {alVerAnalisis && (
          <button type="button" className="boton boton--secundario" onClick={alVerAnalisis}>
            Ir al análisis
          </button>
        )}
      </section>
    )
  }

  const [reciente, ...anteriores] = informes
  return (
    <section className="seccion" aria-labelledby="titulo-informes">
      <h2 id="titulo-informes">Informes</h2>
      <p className="nota">
        Cada análisis genera un informe nuevo; los anteriores se conservan sin cambios. La huella SHA-256
        permite comprobar que el PDF no se modificó.
      </p>
      {errorDescarga && <Aviso tipo="error">{errorDescarga}</Aviso>}
      <InformeReciente idCaso={idCaso} informe={reciente} alDescargar={descargar} />
      {anteriores.length > 0 && (
        <>
          <h3 className="informes-anteriores__titulo">Informes anteriores</h3>
          <ul className="lista-tarjetas">
            {anteriores.map((informe) => (
              <li key={informe.id} className="tarjeta-item">
                <div className="tarjeta-item__principal">
                  <span className="tarjeta-item__titulo">Informe del {formatearFecha(informe.generado_en)}</span>
                  <span className="tarjeta-item__detalle">
                    Pedido por {informe.solicitante} · {informe.imagenes.length} imagen(es):{' '}
                    {informe.imagenes.join(', ')}
                  </span>
                  <span className="huella">
                    SHA-256 del PDF: {informe.huella} · {formatearTamanio(informe.tamanio)}
                  </span>
                  {informe.codigo_verificacion && (
                    <span className="tarjeta-item__detalle">
                      Código de verificación:{' '}
                      <Link to={`/verificar/${informe.codigo_verificacion}`}>
                        {codigoLegible(informe.codigo_verificacion)}
                      </Link>{' '}
                      · {textoSello(informe.sello)}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  className="boton boton--secundario boton--chico"
                  onClick={() => descargar(informe)}
                  aria-label={`Descargar el informe del ${formatearFecha(informe.generado_en)}`}
                >
                  Descargar PDF
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
