/**
 * Formulario breve para pedir otra vez el correo de verificación.
 *
 * Se muestra cuando el enlace venció o cuando se intenta iniciar sesión con
 * una cuenta sin verificar. La respuesta no revela si el correo existe.
 *
 * Realiza: RF02 y CA6, CA9 de la funcionalidad 002.
 */
import { useState } from 'react'
import { reenviarVerificacion } from '../api/cuentas.js'
import { useFormulario } from '../hooks/useFormulario.js'
import Aviso from './Aviso.jsx'
import CampoTexto from './CampoTexto.jsx'

export default function FormularioReenvio({ correoInicial = '' }) {
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({
    correo: correoInicial,
  })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar(({ correo }) => reenviarVerificacion(correo))
    if (resultado.ok) setMensaje(resultado.datos.mensaje)
  }

  if (mensaje) return <Aviso tipo="exito">{mensaje}</Aviso>

  return (
    <form onSubmit={manejarEnvio} className="formulario formulario--compacto" noValidate>
      {error && !errores.correo && <Aviso tipo="error">{error.message}</Aviso>}
      <CampoTexto
        etiqueta="Correo electrónico"
        nombre="correo"
        tipo="email"
        autoComplete="email"
        value={valores.correo}
        onChange={cambiar}
        error={errores.correo}
        required
      />
      <button type="submit" className="boton boton--secundario" disabled={enviando}>
        {enviando ? 'Enviando…' : 'Reenviar el correo de verificación'}
      </button>
    </form>
  )
}
