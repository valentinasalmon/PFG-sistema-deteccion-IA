/**
 * Pantalla para pedir el enlace de recuperación de la contraseña.
 *
 * Muestra el mismo mensaje exista o no la cuenta, para no revelar qué
 * correos están registrados (CA13).
 *
 * Realiza: RF05 y CA13 de la funcionalidad 002.
 */
import { useState } from 'react'
import { Link } from 'react-router'
import { solicitarRecuperacion } from '../api/cuentas.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import { useFormulario } from '../hooks/useFormulario.js'

export default function PaginaRecuperarContrasenia() {
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({ correo: '' })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar(({ correo }) => solicitarRecuperacion(correo))
    if (resultado.ok) setMensaje(resultado.datos.mensaje)
  }

  return (
    <>
      <h1>Recuperar la contraseña</h1>
      {mensaje ? (
        <>
          <Aviso tipo="exito">{mensaje}</Aviso>
          <p>El enlace vence en 1 hora y sirve una sola vez.</p>
        </>
      ) : (
        <>
          <p>Ingresá el correo de tu cuenta y te enviaremos un enlace para crear una contraseña nueva.</p>
          {error && !errores.correo && <Aviso tipo="error">{error.message}</Aviso>}
          <form onSubmit={manejarEnvio} className="formulario" noValidate>
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
            <button type="submit" className="boton" disabled={enviando}>
              {enviando ? 'Enviando…' : 'Enviar el enlace'}
            </button>
          </form>
        </>
      )}
      <p className="enlaces-secundarios">
        <Link to="/iniciar-sesion">Volver a iniciar sesión</Link>
      </p>
    </>
  )
}
