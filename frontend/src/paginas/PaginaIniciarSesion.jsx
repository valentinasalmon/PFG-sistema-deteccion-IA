/**
 * Pantalla de inicio de sesión.
 *
 * Ante credenciales incorrectas muestra el mensaje genérico del backend, que
 * no indica qué dato falló (CA8). Si la cuenta no está verificada, ofrece
 * reenviar el correo (CA9). Al ingresar, la guarda RutaSoloVisitantes lleva
 * a la pantalla que se quería abrir o al inicio (CA7).
 *
 * Realiza: RF03 y CA7, CA8, CA9, CA10 de la funcionalidad 002.
 */
import { Link, useLocation } from 'react-router'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'

export default function PaginaIniciarSesion() {
  const { iniciarSesion } = useSesion()
  const { state } = useLocation()
  const { valores, error, enviando, cambiar, enviar } = useFormulario({
    correo: '',
    contrasenia: '',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    await enviar(({ correo, contrasenia }) => iniciarSesion(correo, contrasenia))
  }

  const noVerificada = error?.codigo === 'cuenta_no_verificada'

  return (
    <>
      <h1>Iniciar sesión</h1>
      {state?.mensaje && !error && <Aviso tipo="info">{state.mensaje}</Aviso>}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {noVerificada && <FormularioReenvio correoInicial={valores.correo} />}

      <form onSubmit={manejarEnvio} className="formulario" noValidate>
        <CampoTexto
          etiqueta="Correo electrónico"
          nombre="correo"
          tipo="email"
          autoComplete="email"
          value={valores.correo}
          onChange={cambiar}
          required
        />
        <CampoTexto
          etiqueta="Contraseña"
          nombre="contrasenia"
          tipo="password"
          autoComplete="current-password"
          value={valores.contrasenia}
          onChange={cambiar}
          required
        />
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>

      <p className="enlaces-secundarios">
        <Link to="/recuperar-contrasenia">¿Olvidaste tu contraseña?</Link>
        <span>
          ¿No tenés cuenta? <Link to="/registro">Registrate</Link>
        </span>
      </p>
    </>
  )
}
