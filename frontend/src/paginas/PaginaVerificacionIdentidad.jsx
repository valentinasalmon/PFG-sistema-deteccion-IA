/**
 * Página del enlace de verificación de identidad (funcionalidad 035).
 *
 * Mientras no esté conectado Identik, la verificación es simulada: la página
 * lo dice claramente y permite elegir el resultado. Con el proveedor real, el
 * Referente hace la verificación en la página de Identik y el resultado llega
 * por aviso al backend, no por el navegador. No requiere sesión: el enlace es
 * la credencial.
 *
 * Realiza: RN41; CA6 y CA7 de la 035; CP-35.
 */
import { useCallback, useState } from 'react'
import { Link, useParams } from 'react-router'
import { consultarVerificacion, simularVerificacion } from '../api/identidad.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { etiquetaDeIdentidad } from '../utilidades/identidad.js'

const RESULTADOS = {
  aprobada: 'Tu identidad quedó verificada. El Administrador ya puede aprobar la aseguradora.',
  rechazada: 'La verificación fue rechazada. Podés intentarlo de nuevo desde la pantalla de la organización.',
}

export default function PaginaVerificacionIdentidad() {
  const { token } = useParams()
  const { usuario } = useSesion()
  const cargar = useCallback(() => consultarVerificacion(token), [token])
  const { datos, error, cargando } = useDatos(cargar)
  const [resuelta, setResuelta] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [errorSimulacion, setErrorSimulacion] = useState(null)

  async function simular(resultado) {
    setErrorSimulacion(null)
    setEnviando(true)
    try {
      setResuelta(await simularVerificacion(token, resultado))
    } catch (errorApi) {
      setErrorSimulacion(errorApi.message)
    } finally {
      setEnviando(false)
    }
  }

  if (cargando) return <Cargando texto="Cargando la verificación…" />
  if (error) {
    return (
      <div className="registro-ancho">
        <h1>Verificación de identidad</h1>
        <Aviso tipo="error" flotante={false}>
          {error.message}
        </Aviso>
      </div>
    )
  }

  const verificacion = resuelta ?? datos
  const { texto, tipo } = etiquetaDeIdentidad(verificacion.estado)
  const pendiente = verificacion.estado === 'pendiente'

  return (
    <div className="registro-ancho">
      <h1>Verificación de identidad</h1>
      <p>
        Referente de <strong>{datos.aseguradora}</strong> <Etiqueta tipo={tipo}>{texto}</Etiqueta>
      </p>

      {pendiente && datos.simulada && (
        <>
          <Aviso tipo="info" flotante={false}>
            Esta verificación es una simulación: la plataforma todavía no está conectada con el
            proveedor de identidad. En la versión final vas a fotografiar tu DNI de ambos lados y
            grabar un video corto de tu rostro. No se pide ni se guarda ningún dato acá.
          </Aviso>
          {errorSimulacion && <Aviso tipo="error">{errorSimulacion}</Aviso>}
          <div className="acciones-en-linea">
            <button type="button" className="boton" onClick={() => simular('aprobada')} disabled={enviando}>
              Simular verificación aprobada
            </button>
            <button
              type="button"
              className="boton boton--secundario"
              onClick={() => simular('rechazada')}
              disabled={enviando}
            >
              Simular rechazo
            </button>
          </div>
        </>
      )}

      {pendiente && !datos.simulada && (
        <p className="nota">Completá la verificación en la página del proveedor. El resultado llega solo.</p>
      )}

      {!pendiente && <p>{RESULTADOS[verificacion.estado]}</p>}

      <div className="acciones-en-linea">
        <Link to={usuario ? '/organizaciones' : '/iniciar-sesion'} className="boton-enlace">
          {usuario ? 'Volver a mis organizaciones' : 'Iniciar sesión'}
        </Link>
      </div>
    </div>
  )
}
