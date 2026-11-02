/**
 * Guardas de navegación según la sesión.
 *
 * - RutaProtegida: sin sesión, redirige al inicio de sesión y recuerda a qué
 *   pantalla se quería ir (CA22).
 * - RutaSoloVisitantes: con sesión iniciada, las pantallas de acceso llevan
 *   a la pantalla que se quería abrir o, si no había ninguna, al inicio. Así,
 *   al iniciar sesión, es esta guarda la que decide el destino (CA7).
 *
 * - RutaPortada: en ``/``, sin sesión muestra la portada pública (033) y,
 *   con sesión, deja pasar al Inicio.
 *
 * Realiza: CA12 y CA22 de la funcionalidad 002; CA1 de la 033.
 */
import { Navigate, Outlet, useLocation } from 'react-router'
import { useSesion } from '../hooks/useSesion.js'
import Cargando from '../componentes/Cargando.jsx'
import PaginaPortada from '../paginas/PaginaPortada.jsx'

const MENSAJES_SALIDA = {
  cierre: 'Cerraste la sesión.',
  vencida: 'Tu sesión venció por seguridad. Volvé a iniciar sesión.',
  desactivada:
    'Tu cuenta quedó desactivada porque ya no pertenecés a ninguna aseguradora. Si otra aseguradora te invita, vas a poder ingresar para aceptar la invitación.',
  eliminada: 'Tu cuenta fue eliminada. Te enviamos una confirmación por correo.',
}

const SALIDAS_AL_INICIO = new Set(['cierre', 'desactivada', 'eliminada'])

export function RutaProtegida() {
  const { usuario, cargando, motivoSalida } = useSesion()
  const ubicacion = useLocation()

  if (cargando) return <Cargando texto="Verificando la sesión…" />
  if (!usuario) {
    // Tras un cierre voluntario, una desactivación o una eliminación de la
    // cuenta se vuelve al inicio; si no, a la pantalla pedida.
    const estado = SALIDAS_AL_INICIO.has(motivoSalida)
      ? { mensaje: MENSAJES_SALIDA[motivoSalida] }
      : { desde: ubicacion.pathname, mensaje: MENSAJES_SALIDA[motivoSalida] }
    return <Navigate to="/iniciar-sesion" replace state={estado} />
  }
  return <Outlet />
}

export function RutaPortada() {
  const { usuario, cargando, motivoSalida } = useSesion()
  if (cargando) return <Cargando texto="Verificando la sesión…" />
  // Recién cerrada la sesión, el aviso de salida se muestra en el inicio de sesión.
  if (!usuario && motivoSalida) {
    return <Navigate to="/iniciar-sesion" replace state={{ mensaje: MENSAJES_SALIDA[motivoSalida] }} />
  }
  if (!usuario) return <PaginaPortada />
  return <Outlet />
}

export function RutaSoloVisitantes() {
  const { usuario, cargando } = useSesion()
  const { state } = useLocation()
  if (cargando) return <Cargando texto="Verificando la sesión…" />
  if (usuario) return <Navigate to={state?.desde ?? '/'} replace />
  return <Outlet />
}

/**
 * Pantallas de trabajo con casos y organizaciones: la administradora de la
 * plataforma no las usa y va directo a su tablero (funcionalidad 028).
 */
export function RutaSoloUsuarios() {
  const { usuario } = useSesion()
  if (usuario?.rol === 'administrador') return <Navigate to="/administracion" replace />
  return <Outlet />
}

/** El tablero de administración solo es para la administradora (funcionalidad 028). */
export function RutaSoloAdministracion() {
  const { usuario } = useSesion()
  if (usuario?.rol !== 'administrador') return <Navigate to="/" replace />
  return <Outlet />
}
