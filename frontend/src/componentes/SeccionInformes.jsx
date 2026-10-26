/**
 * Sección "Informes" de la pantalla de un caso: historial de informes PDF,
 * del más reciente al más antiguo, con quién pidió el análisis, las imágenes
 * incluidas, la huella del PDF y la descarga con un enlace firmado.
 *
 * Cada informe muestra su código de verificación pública y el estado del
 * sello de su huella en Hedera (funcionalidad 026).
 *
 * Realiza: RF45 (CA1, CA2), RF55; CA7 y CA8 de la funcionalidad 008.
 */
import { useCallback, useState } from 'react'
import { Link } from 'react-router'
import { descargarInforme, listarInformes } from '../api/informes.js'
import { useDatos } from '../hooks/useDatos.js'
import { formatearTamanio } from '../utilidades/archivos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import { codigoLegible } from '../utilidades/verificacion.js'
import Aviso from './Aviso.jsx'

function textoSello(sello) {
  if (sello?.estado === 'sellado') return sello.simulado ? 'Sello simulado (pruebas)' : 'Registrado en Hedera'
  if (sello?.estado === 'fallido') return 'Sin sello de Hedera'
  if (sello?.estado) return 'Sello en Hedera en curso…'
  return 'Sin sello de tiempo'
}

export default function SeccionInformes({ idCaso }) {
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
  if (!informes || informes.length === 0) return null

  return (
    <section className="seccion" aria-labelledby="titulo-informes">
      <h2 id="titulo-informes">Informes</h2>
      <p className="nota">
        Cada análisis genera un informe nuevo; los anteriores se conservan sin cambios. La huella SHA-256
        permite comprobar que el PDF no se modificó.
      </p>
      {errorDescarga && <Aviso tipo="error">{errorDescarga}</Aviso>}
      <ul className="lista-tarjetas">
        {informes.map((informe) => (
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
    </section>
  )
}
