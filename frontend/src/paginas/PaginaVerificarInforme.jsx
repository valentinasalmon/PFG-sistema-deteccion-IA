/**
 * Página pública "Verificar un informe" (funcionalidad 026).
 *
 * Quien recibe un informe de evidentIA (un juzgado, un perito, un liquidador)
 * comprueba que el PDF no fue modificado: elige el archivo, el navegador
 * calcula su huella SHA-256 y la compara con la registrada al generarlo, que
 * además está sellada en Hedera. El PDF nunca se sube al servidor. Se puede
 * entrar con el código del PDF (o su QR) o solo con el archivo. También
 * muestra con qué versión de la plataforma se hizo el análisis (029).
 *
 *
 * Desde la cuarta tanda de la 034 la acción principal es elegir o soltar el
 * PDF en una zona de carga; el código queda como opción secundaria abajo.
 *
 * Realiza: RF55 (CA3), RF56 (CA2).
 */
import { useEffect, useId, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { verificarInforme } from '../api/informes.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Icono from '../componentes/Icono.jsx'
import { formatearFecha } from '../utilidades/fechas.js'
import { codigoLegible, huellaDeArchivo } from '../utilidades/verificacion.js'

function DatosDelInforme({ informe }) {
  const { sello } = informe
  return (
    <dl className="datos-verificacion">
      <dt>Generado el</dt>
      <dd>{formatearFecha(informe.generado_en)}</dd>
      <dt>Huella SHA-256 registrada</dt>
      <dd className="huella">{informe.huella}</dd>
      <dt>Sello de tiempo</dt>
      <dd>
        {sello.estado === 'sellado' && !sello.simulado && (
          <>
            Registrado en Hedera el {formatearFecha(sello.fecha)} · {sello.referencia}
            {sello.enlace && (
              <>
                {' · '}
                <a href={sello.enlace} target="_blank" rel="noopener noreferrer">
                  Verificar en HashScan
                </a>
              </>
            )}
          </>
        )}
        {sello.estado === 'sellado' && sello.simulado && 'Sello simulado del entorno de pruebas'}
        {sello.estado !== 'sellado' && 'Todavía sin sello en Hedera'}
      </dd>
      {informe.version && (
        <>
          <dt>Versión de la plataforma</dt>
          <dd>
            Analizado con evidentIA {informe.version.numero} (código {informe.version.commit})
            {informe.version.sello.estado === 'sellado' && !informe.version.sello.simulado && (
              <>
                {' · '}registrada en Hedera
                {informe.version.sello.enlace && (
                  <>
                    {' · '}
                    <a href={informe.version.sello.enlace} target="_blank" rel="noopener noreferrer">
                      Ver la versión en HashScan
                    </a>
                  </>
                )}
              </>
            )}
          </dd>
        </>
      )}
    </dl>
  )
}

export default function PaginaVerificarInforme() {
  const { codigo: codigoDeLaRuta } = useParams()
  const navegar = useNavigate()
  const idArchivo = useId()
  const [codigo, setCodigo] = useState(codigoDeLaRuta ?? '')
  const [informe, setInforme] = useState(null)
  const [estado, setEstado] = useState({ cargando: Boolean(codigoDeLaRuta), error: null, resultado: null })
  const [arrastrando, setArrastrando] = useState(false)

  useEffect(() => {
    if (!codigoDeLaRuta) return
    let vigente = true
    verificarInforme({ codigo: codigoDeLaRuta })
      .then(
        (datos) =>
          vigente && (setInforme(datos), setEstado({ cargando: false, error: null, resultado: null })),
      )
      .catch((error) => vigente && setEstado({ cargando: false, error: error.message, resultado: null }))
    return () => {
      vigente = false
    }
  }, [codigoDeLaRuta])

  function buscarCodigo(evento) {
    evento.preventDefault()
    const limpio = codigo.replace(/[^0-9a-z]/gi, '').toUpperCase()
    if (limpio) navegar(`/verificar/${limpio}`)
  }

  async function comprobar(evento) {
    const archivo = evento.target.files?.[0]
    evento.target.value = ''
    await comprobarArchivo(archivo)
  }

  /** También se puede soltar el PDF sobre la zona de carga (034, cuarta tanda). */
  async function soltar(evento) {
    evento.preventDefault()
    setArrastrando(false)
    await comprobarArchivo(evento.dataTransfer.files?.[0])
  }

  async function comprobarArchivo(archivo) {
    if (!archivo) return
    setEstado({ cargando: true, error: null, resultado: null })
    try {
      const huella = await huellaDeArchivo(archivo)
      if (informe) {
        setEstado({
          cargando: false,
          error: null,
          resultado: huella === informe.huella ? 'coincide' : 'no-coincide',
        })
        return
      }
      setInforme(await verificarInforme({ huella }))
      setEstado({ cargando: false, error: null, resultado: 'coincide' })
    } catch (error) {
      setEstado({
        cargando: false,
        error: null,
        resultado: error.estado === 404 ? 'desconocido' : null,
        mensaje: error.estado === 404 ? null : error.message,
      })
    }
  }

  return (
    <div className="verificar-informe">
      <h1>Verificar un informe</h1>
      <p>
        Comprobá que un informe PDF de evidentIA no fue modificado. El archivo no se sube: la comparación se
        hace en tu navegador.
      </p>

      {codigoDeLaRuta && <p className="nota">Código: {codigoLegible(codigoDeLaRuta.toUpperCase())}</p>}
      {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}
      {informe && <DatosDelInforme informe={informe} />}

      {!estado.error && (
        <div
          className={`zona-pdf${arrastrando ? ' zona-pdf--arrastrando' : ''}`}
          onDragOver={(evento) => {
            evento.preventDefault()
            setArrastrando(true)
          }}
          onDragLeave={() => setArrastrando(false)}
          onDrop={soltar}
        >
          <input
            id={idArchivo}
            type="file"
            accept="application/pdf,.pdf"
            className="solo-lectores"
            onChange={comprobar}
            aria-describedby="ayuda-pdf"
          />
          <span className="zona-pdf__icono" aria-hidden="true">
            <Icono nombre="documento" tamanio={26} />
          </span>
          <label htmlFor={idArchivo} className="boton">
            Elegir el PDF para comprobarlo
          </label>
          <p id="ayuda-pdf" className="nota">
            O soltalo acá. Se calcula su huella en tu navegador y se compara con la registrada.
          </p>
        </div>
      )}

      {!codigoDeLaRuta && (
        <form className="buscar-codigo" onSubmit={buscarCodigo}>
          <label htmlFor="codigo-verificacion">Código del informe (opcional)</label>
          <div className="buscar-codigo__fila">
            <input
              id="codigo-verificacion"
              className="campo__control"
              value={codigo}
              onChange={(evento) => setCodigo(evento.target.value)}
              placeholder="ABCD-EFGH-JKMN"
              autoComplete="off"
            />
            <button type="submit" className="boton boton--secundario">
              Buscar
            </button>
          </div>
          <p className="nota">Está en la sección «Verificación de este informe», junto al código QR.</p>
        </form>
      )}

      <div aria-live="polite">
        {estado.cargando && <Cargando texto="Comprobando…" />}
        {estado.resultado === 'coincide' && (
          <Aviso tipo="info">
            <strong>El PDF coincide con el registrado.</strong> Es idéntico al informe que generó la
            plataforma.
          </Aviso>
        )}
        {estado.resultado === 'no-coincide' && (
          <Aviso tipo="error">
            <strong>El PDF no coincide.</strong> Fue modificado después de generarse o no es el informe de
            este código.
          </Aviso>
        )}
        {estado.resultado === 'desconocido' && (
          <Aviso tipo="error">
            <strong>No encontramos este PDF.</strong> No es un informe de evidentIA o fue modificado después
            de generarse.
          </Aviso>
        )}
        {estado.mensaje && <Aviso tipo="error">{estado.mensaje}</Aviso>}
      </div>
    </div>
  )
}
