/**
 * Encabezado de las pantallas internas: logo de evidentIA, navegación con
 * íconos (inicio, casos, organizaciones y perfil), iniciales y nombre del
 * usuario y botón para cerrar sesión.
 *
 * Realiza: RF04 y CA7, CA11 de la funcionalidad 002; RNF10 (funcionalidad 022).
 */
import { Link, NavLink } from 'react-router'
import { useSesion } from '../hooks/useSesion.js'
import Icono from './Icono.jsx'

export default function Encabezado() {
  const { usuario, cerrarSesion } = useSesion()

  // Al quedar sin usuario, la ruta protegida lleva al inicio de sesión con el aviso.
  function manejarCierre() {
    cerrarSesion().catch(() => {})
  }

  const iniciales = `${usuario.nombre?.[0] ?? ''}${usuario.apellido?.[0] ?? ''}`.toUpperCase()

  return (
    <header className="encabezado">
      <div className="encabezado__contenido">
        <Link to="/" className="encabezado__marca">
          <img src="/marca/logo-tipografia-negra.png" alt="evidentIA, ir al inicio" />
        </Link>
        <nav aria-label="Principal" className="encabezado__navegacion">
          <NavLink to="/" end>
            <Icono nombre="inicio" />
            <span>Inicio</span>
          </NavLink>
          <NavLink to="/casos">
            <Icono nombre="casos" />
            <span>Casos</span>
          </NavLink>
          <NavLink to="/organizaciones">
            <Icono nombre="organizaciones" />
            <span>Organizaciones</span>
          </NavLink>
          <NavLink to="/perfil">
            <Icono nombre="perfil" />
            <span>Mi perfil</span>
          </NavLink>
          {usuario.rol === 'administrador' && (
            <NavLink to="/administracion">
              <Icono nombre="administracion" />
              <span>Administración</span>
            </NavLink>
          )}
        </nav>
        <div className="encabezado__usuario">
          <span className="encabezado__avatar" aria-hidden="true">
            {iniciales}
          </span>
          <span className="encabezado__nombre">
            {usuario.nombre} {usuario.apellido}
          </span>
          <button type="button" className="boton boton--fantasma" onClick={manejarCierre}>
            <Icono nombre="salir" />
            Cerrar sesión
          </button>
        </div>
      </div>
    </header>
  )
}
