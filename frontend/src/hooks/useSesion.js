/**
 * Hook para leer la sesión desde cualquier componente.
 *
 * @returns {{
 *   usuario: Object | null,
 *   cargando: boolean,
 *   motivoSalida: 'cierre' | 'vencida' | 'desactivada' | 'eliminada' | null,
 *   iniciarSesion: (correo: string, contrasenia: string) => Promise<Object>,
 *   cerrarSesion: () => Promise<void>,
 *   terminarSesion: (motivo: string) => void,
 *   recargarUsuario: () => Promise<Object | null>,
 *   actualizarUsuario: (usuario: Object) => void,
 * }}
 */
import { useContext } from 'react'
import { ContextoSesion } from '../contextos/contextoSesion.js'

export function useSesion() {
  const contexto = useContext(ContextoSesion)
  if (contexto === null) {
    throw new Error('useSesion debe usarse dentro de <ProveedorSesion>.')
  }
  return contexto
}
