/**
 * Verificación de identidad del Referente de una aseguradora pendiente
 * (funcionalidad 035).
 *
 * Se muestra en la pantalla de la organización mientras la aseguradora espera
 * aprobación y la verificación está activa en la plataforma. El Referente la
 * inicia y va a la página del proveedor (hoy simulada); el resto de los
 * miembros solo ve el estado. La plataforma guarda solo el resultado.
 *
 * Realiza: RN41; CA1, CA2, CA4 y CA7 de la 035.
 */
import { useCallback, useState } from 'react'
import { iniciarIdentidad, obtenerIdentidad } from '../api/organizaciones.js'
import { useDatos } from '../hooks/useDatos.js'
import { etiquetaDeIdentidad, navegador } from '../utilidades/identidad.js'
import Aviso from './Aviso.jsx'
import Etiqueta from './Etiqueta.jsx'

const EXPLICACIONES = {
  sin_verificar:
    'Antes de aprobar la aseguradora, el Administrador necesita que verifiques tu identidad con tu DNI y una foto de tu rostro.',
  pendiente: 'Iniciaste la verificación y todavía no tenemos el resultado. Si no la terminaste, podés empezarla de nuevo.',
  aprobada: 'Tu identidad está verificada. Ahora el Administrador puede aprobar la aseguradora.',
  rechazada: 'La verificación no se pudo completar. Revisá que el DNI y la foto se vean bien e intentá otra vez.',
}

export default function SeccionIdentidad({ organizacion, esReferente }) {
  const cargar = useCallback(() => obtenerIdentidad(organizacion.id), [organizacion.id])
  const { datos: identidad, error } = useDatos(cargar)
  const [iniciando, setIniciando] = useState(false)
  const [errorInicio, setErrorInicio] = useState(null)

  if (error || !identidad || !identidad.activa || !identidad.corresponde) return null

  const { texto, tipo } = etiquetaDeIdentidad(identidad.estado)
  const puedeIniciar = esReferente && identidad.estado !== 'aprobada'

  async function iniciar() {
    setErrorInicio(null)
    setIniciando(true)
    try {
      const { url } = await iniciarIdentidad(organizacion.id)
      navegador.ir(url)
    } catch (errorApi) {
      setErrorInicio(errorApi.message)
      setIniciando(false)
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-identidad">
      <h2 id="titulo-identidad">
        Verificación de identidad <Etiqueta tipo={tipo}>{texto}</Etiqueta>
      </h2>
      <p className="nota">
        {esReferente
          ? EXPLICACIONES[identidad.estado] ?? EXPLICACIONES.sin_verificar
          : 'La verificación la hace el Referente de la aseguradora.'}
      </p>
      {identidad.motivo && identidad.estado === 'rechazada' && (
        <p className="nota">Motivo: {identidad.motivo}</p>
      )}
      {errorInicio && <Aviso tipo="error">{errorInicio}</Aviso>}
      {puedeIniciar && (
        <div className="acciones-en-linea">
          <button type="button" className="boton" onClick={iniciar} disabled={iniciando}>
            {iniciando ? 'Abriendo la verificación…' : 'Verificar mi identidad'}
          </button>
        </div>
      )}
      <p className="nota">Guardamos solo el resultado: nunca tu DNI, tu foto ni tus datos biométricos.</p>
    </section>
  )
}
