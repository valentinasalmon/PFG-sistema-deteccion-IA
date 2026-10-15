/**
 * Guardas de navegación según la sesión.
 *
 * - RutaProtegida: sin sesión, redirige al inicio de sesión y recuerda a qué
 *   pantalla se quería ir (CA22).
 * - RutaSoloVisitantes: con sesión iniciada, las pantallas de acceso llevan
 *   a la pantalla que se quería abrir o, si no había ninguna, al inicio. Así,
 *   al iniciar sesión, es esta guarda la que decide el destino (CA7).
 *
 * Realiza: CA12 y CA22 de la funcionalidad 002.
 */
import { Navigate, Outlet, useLocation } from 'react-router'
import { useSesion } from '../hooks/useSesion.js'
import Cargando from './Cargando.jsx'

const MENSAJES_SALIDA = {
  cierre: 'Cerraste la sesión.',
  vencida: 'Tu sesión venció por seguridad. Volvé a iniciar sesión.',
}

export function RutaProtegida() {
  const { usuario, cargando, motivoSalida } = useSesion()
  const ubicacion = useLocation()

  if (cargando) return <Cargando texto="Verificando la sesión…" />
  if (!usuario) {
    // Tras un cierre voluntario se vuelve al inicio; si no, a la pantalla pedida.
    const estado =
      motivoSalida === 'cierre'
        ? { mensaje: MENSAJES_SALIDA.cierre }
        : { desde: ubicacion.pathname, mensaje: MENSAJES_SALIDA[motivoSalida] }
    return <Navigate to="/iniciar-sesion" replace state={estado} />
  }
  return <Outlet />
}

export function RutaSoloVisitantes() {
  const { usuario, cargando } = useSesion()
  const { state } = useLocation()
  if (cargando) return <Cargando texto="Verificando la sesión…" />
  if (usuario) return <Navigate to={state?.desde ?? '/'} replace />
  return <Outlet />
}
