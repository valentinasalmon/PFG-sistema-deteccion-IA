/**
 * Página pública "Verificar un informe" (funcionalidad 026).
 *
 * Quien recibe un informe de evidentIA (un juzgado, un perito, un liquidador)
 * comprueba que el PDF no fue modificado: elige el archivo, el navegador
 * calcula su huella SHA-256 y la compara con la registrada al generarlo, que
 * además está sellada en Hedera. El PDF nunca se sube al servidor. Se puede
 * entrar con el código del PDF (o su QR) o solo con el archivo.
 *
 * Realiza: RF55 (CA3).
 */
import { useEffect, useId, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { verificarInforme } from '../api/informes.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
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

      {!codigoDeLaRuta && (
        <form className="formulario-en-linea" onSubmit={buscarCodigo}>
          <label htmlFor="codigo-verificacion">Código del informe (opcional)</label>
          <input
            id="codigo-verificacion"
            value={codigo}
            onChange={(evento) => setCodigo(evento.target.value)}
            placeholder="ABCD-EFGH-JKMN"
            autoComplete="off"
          />
          <button type="submit" className="boton boton--secundario">
            Buscar
          </button>
        </form>
      )}

      {codigoDeLaRuta && <p className="nota">Código: {codigoLegible(codigoDeLaRuta.toUpperCase())}</p>}
      {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}
      {informe && <DatosDelInforme informe={informe} />}

      {!estado.error && (
        <div className="verificar-informe__archivo">
          <input
            id={idArchivo}
            type="file"
            accept="application/pdf,.pdf"
            className="solo-lectores"
            onChange={comprobar}
          />
          <label htmlFor={idArchivo} className="boton">
            Elegir el PDF para comprobarlo
          </label>
        </div>
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
