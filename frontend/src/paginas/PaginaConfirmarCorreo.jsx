/**
 * Pantalla a la que lleva el enlace enviado a la dirección nueva al cambiar
 * el correo (/confirmar-correo?token=...).
 *
 * No exige sesión: el enlace demuestra el acceso al correo nuevo. Si hay una
 * sesión abierta, actualiza los datos que se muestran.
 *
 * Realiza: RF07 y CA18 de la funcionalidad 002.
 */
import { useCallback } from 'react'
import { Link, useSearchParams } from 'react-router'
import { confirmarCambioCorreo } from '../api/perfil.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import { useAccionAlCargar } from '../hooks/useAccionAlCargar.js'
import { useSesion } from '../hooks/useSesion.js'

export default function PaginaConfirmarCorreo() {
  const [parametros] = useSearchParams()
  const token = parametros.get('token') ?? ''
  const { usuario, cargando, recargarUsuario } = useSesion()
  const haySesion = Boolean(usuario)

  const accion = useCallback(async () => {
    await confirmarCambioCorreo(token)
    if (haySesion) await recargarUsuario()
  }, [token, haySesion, recargarUsuario])
  const { estado, error } = useAccionAlCargar(accion, !cargando)

  const destino = haySesion ? '/perfil' : '/iniciar-sesion'
  const textoDestino = haySesion ? 'Ir a mi perfil' : 'Iniciar sesión'

  return (
    <>
      <h1>Confirmación del correo nuevo</h1>
      {estado === 'cargando' && <Cargando texto="Confirmando tu correo…" />}
      {estado === 'exito' && (
        <Aviso tipo="exito">Tu correo fue actualizado. Desde ahora usalo para ingresar.</Aviso>
      )}
      {estado === 'error' && (
        <Aviso tipo="error">
          {error.message} Si todavía querés cambiarlo, volvé a pedirlo desde tu perfil.
        </Aviso>
      )}
      {estado !== 'cargando' && (
        <Link to={destino} className="boton">
          {textoDestino}
        </Link>
      )}
    </>
  )
}
