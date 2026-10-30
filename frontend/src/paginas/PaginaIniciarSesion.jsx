/**
 * Pantalla de inicio de sesión.
 *
 * Ante credenciales incorrectas muestra el mensaje genérico del backend, que
 * no indica qué dato falló (CA8). Si la cuenta no está verificada, ofrece
 * reenviar el correo (CA9). Al ingresar, la guarda RutaSoloVisitantes lleva
 * a la pantalla que se quería abrir o al inicio (CA7).
 *
 * Desde la funcionalidad 028 (frame 9a): crear una cuenta debajo del título,
 * Google arriba, «¿La olvidaste?» junto a la contraseña y el botón «Mostrar».
 *
 * Ofrece "Continuar con Google" (027). Si Google no autentica a la persona,
 * el backend vuelve acá con ``?google=<código>`` y se muestra el motivo.
 *
 * Realiza: RF03, RF52 y CA7, CA8, CA9, CA10 de la funcionalidad 002.
 */
import { Link, useLocation, useSearchParams } from 'react-router'
import Aviso from '../componentes/Aviso.jsx'
import BotonGoogle from '../componentes/BotonGoogle.jsx'
import CampoContrasenia from '../componentes/CampoContrasenia.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'

/** Mensaje de cada motivo por el que no se pudo entrar con Google (027). */
const MENSAJES_GOOGLE = {
  google_cancelado: 'Cancelaste el ingreso con Google. Podés intentarlo de nuevo cuando quieras.',
  google_no_verificado:
    'Google no confirmó tu correo electrónico. Verificalo en Google o ingresá con tu correo y contraseña.',
  cuenta_desactivada:
    'Tu cuenta está desactivada porque ya no pertenecés a ninguna aseguradora. Si otra aseguradora te invita, vas a poder ingresar para aceptar la invitación.',
  no_disponible: 'El ingreso con Google no está disponible en este momento.',
}
const MENSAJE_GOOGLE_GENERICO =
  'No pudimos ingresar con Google. Probá de nuevo o usá tu correo y contraseña.'

export default function PaginaIniciarSesion() {
  const [parametros] = useSearchParams()
  const codigoGoogle = parametros.get('google')
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
      <p className="tarjeta-acceso__bajada">
        ¿No tenés cuenta? <Link to="/registro">Creá una</Link>
      </p>
      {state?.mensaje && !error && <Aviso tipo="info">{state.mensaje}</Aviso>}
      {codigoGoogle && !error && (
        <Aviso tipo="error">{MENSAJES_GOOGLE[codigoGoogle] ?? MENSAJE_GOOGLE_GENERICO}</Aviso>
      )}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {noVerificada && <FormularioReenvio correoInicial={valores.correo} />}

      <BotonGoogle />

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
        <CampoContrasenia
          etiqueta="Contraseña"
          nombre="contrasenia"
          autoComplete="current-password"
          value={valores.contrasenia}
          onChange={cambiar}
          required
          enlace={
            <Link to="/recuperar-contrasenia" className="campo__enlace">
              ¿La olvidaste?
            </Link>
          }
        />
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>
    </>
  )
}
