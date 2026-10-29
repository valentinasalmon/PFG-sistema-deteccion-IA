/**
 * Botón "Continuar con Google" de las pantallas de acceso (funcionalidad 027).
 *
 * Solo aparece si la plataforma tiene configurado Google: si la consulta
 * falla o no está configurado, no se muestra nada y el acceso con correo y
 * contraseña sigue igual. Es un enlace y no un formulario, porque el flujo
 * es una navegación del navegador hacia Google y de vuelta.
 *
 * Realiza: RF52; RNF10 (texto visible y foco del enlace).
 */
import { useEffect, useState } from 'react'
import { googleHabilitado, urlInicioGoogle } from '../api/google.js'

/** Logo de Google con sus colores, tal como lo pide su guía de marca. */
function LogoGoogle() {
  return (
    <svg className="boton-google__logo" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.7 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.6 5.4 2.7 13.3l7.9 6.2C12.5 13.6 17.8 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.8c4.3-4 6.9-9.9 6.9-17.2z" />
      <path fill="#FBBC05" d="M10.6 28.5c-.5-1.4-.8-2.9-.8-4.5s.3-3.1.8-4.5l-7.9-6.2C1 16.6 0 20.2 0 24s1 7.4 2.7 10.7l7.9-6.2z" />
      <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.8c-2.1 1.4-4.8 2.2-8.5 2.2-6.2 0-11.5-4.1-13.4-9.8l-7.9 6.2C6.6 42.6 14.6 48 24 48z" />
    </svg>
  )
}

export default function BotonGoogle({ invitacion }) {
  const [habilitado, setHabilitado] = useState(false)

  useEffect(() => {
    let activo = true
    googleHabilitado()
      .then((valor) => activo && setHabilitado(Boolean(valor)))
      .catch(() => activo && setHabilitado(false))
    return () => {
      activo = false
    }
  }, [])

  if (!habilitado) return null
  return (
    <div className="acceso-google">
      <a className="boton boton--secundario boton-google" href={urlInicioGoogle(invitacion)}>
        <LogoGoogle />
        Continuar con Google
      </a>
      <p className="acceso-google__separador" aria-hidden="true">
        <span>o con tu correo</span>
      </p>
    </div>
  )
}
