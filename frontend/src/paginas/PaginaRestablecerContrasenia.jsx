/**
 * Pantalla a la que lleva el enlace de recuperación
 * (/restablecer-contrasenia?token=...): permite definir una contraseña nueva.
 *
 * Al guardarla se cierran todas las sesiones abiertas de la cuenta. Si el
 * enlace venció, fue alterado o ya se usó, ofrece pedir uno nuevo.
 *
 * Realiza: RF05 y CA14, CA15 de la funcionalidad 002.
 */
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { restablecerContrasenia } from '../api/cuentas.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import { useFormulario } from '../hooks/useFormulario.js'

export default function PaginaRestablecerContrasenia() {
  const [parametros] = useSearchParams()
  const token = parametros.get('token') ?? ''
  const { valores, errores, error, enviando, cambiar, enviar, marcarError } = useFormulario({
    contrasenia: '',
    confirmacion: '',
  })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    if (valores.contrasenia !== valores.confirmacion) {
      marcarError('confirmacion', 'Las contraseñas no coinciden.')
      return
    }
    const resultado = await enviar(({ contrasenia }) => restablecerContrasenia(token, contrasenia))
    if (resultado.ok) setMensaje(resultado.datos.mensaje)
  }

  if (mensaje) {
    return (
      <>
        <h1>Contraseña actualizada</h1>
        <Aviso tipo="exito">{mensaje}</Aviso>
        <p>Por seguridad, cerramos las sesiones que tenías abiertas en otros dispositivos.</p>
        <Link to="/iniciar-sesion" className="boton">
          Iniciar sesión
        </Link>
      </>
    )
  }

  const enlaceInvalido = error?.codigo === 'enlace_invalido'

  return (
    <>
      <h1>Crear una contraseña nueva</h1>
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {enlaceInvalido ? (
        <Link to="/recuperar-contrasenia" className="boton">
          Pedir un enlace nuevo
        </Link>
      ) : (
        <form onSubmit={manejarEnvio} className="formulario" noValidate>
          <CampoTexto
            etiqueta="Contraseña nueva"
            nombre="contrasenia"
            tipo="password"
            autoComplete="new-password"
            value={valores.contrasenia}
            onChange={cambiar}
            error={errores.contrasenia}
            idDescripcion="reglas-contrasenia"
            required
          />
          <ReglasContrasenia contrasenia={valores.contrasenia} id="reglas-contrasenia" />
          <CampoTexto
            etiqueta="Repetí la contraseña nueva"
            nombre="confirmacion"
            tipo="password"
            autoComplete="new-password"
            value={valores.confirmacion}
            onChange={cambiar}
            error={errores.confirmacion}
            required
          />
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar la contraseña'}
          </button>
        </form>
      )}
    </>
  )
}
