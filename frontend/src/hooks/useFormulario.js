/**
 * Estado común de los formularios: valores, errores por campo, error general
 * y envío en curso.
 *
 * Los errores por campo llegan del backend (ErrorApi.errores), que es quien
 * valida de forma definitiva (RNF04 CA1).
 */
import { useState } from 'react'
import { ErrorApi } from '../api/cliente.js'

const MENSAJE_INESPERADO = 'Ocurrió un error inesperado. Intentá de nuevo.'

/**
 * @param {Object} valoresIniciales valores de cada campo, por nombre.
 */
export function useFormulario(valoresIniciales) {
  const [valores, setValores] = useState(valoresIniciales)
  const [errores, setErrores] = useState({})
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  /** Actualiza el valor del campo que disparó el evento (texto, radio o casilla). */
  function cambiar(evento) {
    const { name, type, checked, value } = evento.target
    setValores((anteriores) => ({ ...anteriores, [name]: type === 'checkbox' ? checked : value }))
  }

  /**
   * Ejecuta la acción con los valores actuales y captura sus errores.
   *
   * @param {(valores: Object) => Promise<any>} accion
   * @returns {Promise<{ok: boolean, datos?: any, error?: ErrorApi}>}
   */
  async function enviar(accion) {
    setEnviando(true)
    setErrores({})
    setError(null)
    try {
      return { ok: true, datos: await accion(valores) }
    } catch (excepcion) {
      const errorApi =
        excepcion instanceof ErrorApi ? excepcion : new ErrorApi(0, { mensaje: MENSAJE_INESPERADO })
      setErrores(errorApi.errores)
      setError(errorApi)
      return { ok: false, error: errorApi }
    } finally {
      setEnviando(false)
    }
  }

  /**
   * Muestra los errores detectados en el navegador, antes de enviar, uno por
   * campo. Con un objeto vacío borra los errores anteriores.
   *
   * @param {Object<string, string>} nuevos mensaje de error de cada campo.
   */
  function marcarErrores(nuevos) {
    setErrores(nuevos)
    const hayErrores = Object.keys(nuevos).length > 0
    setError(hayErrores ? new ErrorApi(400, { mensaje: 'Revisá los datos marcados.', errores: nuevos }) : null)
  }

  /** Muestra un error detectado en el navegador en un solo campo. */
  function marcarError(campo, mensaje) {
    marcarErrores({ [campo]: mensaje })
  }

  return { valores, setValores, errores, error, enviando, cambiar, enviar, marcarError, marcarErrores }
}
