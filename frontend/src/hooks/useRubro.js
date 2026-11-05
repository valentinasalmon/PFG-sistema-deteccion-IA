/**
 * Textos del rubro de quien está usando el sistema (funcionalidad 037).
 *
 * Atajo de ``textosDelRubro(usuario.perfil)`` para no pasar el perfil por
 * cada componente. Sin sesión devuelve los textos del servicio Legal.
 *
 * Realiza: RNF10.
 */
import { textosDelRubro } from '../utilidades/lenguaje.js'
import { useSesion } from './useSesion.js'

export function useRubro() {
  const { usuario } = useSesion()
  return textosDelRubro(usuario?.perfil)
}
