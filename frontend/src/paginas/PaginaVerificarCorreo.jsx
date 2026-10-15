/**
 * Pantalla a la que lleva el enlace del correo de verificación
 * (/verificar-correo?token=...).
 *
 * Envía el token al cargar. Si el enlace venció o ya se usó, informa el motivo
 * y ofrece reenviar el correo.
 *
 * Realiza: RF02 y CA6 de la funcionalidad 002.
 */
import { useCallback } from 'react'
import { Link, useSearchParams } from 'react-router'
import { verificarCorreo } from '../api/cuentas.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import { useAccionAlCargar } from '../hooks/useAccionAlCargar.js'

export default function PaginaVerificarCorreo() {
  const [parametros] = useSearchParams()
  const token = parametros.get('token') ?? ''
  const accion = useCallback(() => verificarCorreo(token), [token])
  const { estado, error } = useAccionAlCargar(accion)

  return (
    <>
      <h1>Verificación del correo</h1>
      {estado === 'cargando' && <Cargando texto="Verificando tu correo…" />}
      {estado === 'exito' && (
        <>
          <Aviso tipo="exito">Tu correo fue verificado. Ya podés iniciar sesión.</Aviso>
          <Link to="/iniciar-sesion" className="boton">
            Iniciar sesión
          </Link>
        </>
      )}
      {estado === 'error' && (
        <>
          <Aviso tipo="error">{error.message}</Aviso>
          <p>Ingresá tu correo y te enviamos un enlace nuevo.</p>
          <FormularioReenvio />
          <p className="enlaces-secundarios">
            <Link to="/iniciar-sesion">Ir a iniciar sesión</Link>
          </p>
        </>
      )}
    </>
  )
}
