/**
 * Encabezado de las pantallas internas: nombre de la plataforma, nombre del
 * usuario, acceso al perfil y botón para cerrar sesión.
 *
 * Realiza: RF04 y CA7, CA11 de la funcionalidad 002.
 */
import { Link, NavLink } from 'react-router'
import { useSesion } from '../hooks/useSesion.js'

export default function Encabezado() {
  const { usuario, cerrarSesion } = useSesion()

  // Al quedar sin usuario, la ruta protegida lleva al inicio de sesión con el aviso.
  function manejarCierre() {
    cerrarSesion().catch(() => {})
  }

  return (
    <header className="encabezado">
      <div className="encabezado__contenido">
        <Link to="/" className="encabezado__marca">
          Análisis de imágenes
        </Link>
        <nav aria-label="Principal" className="encabezado__navegacion">
          <NavLink to="/" end>
            Inicio
          </NavLink>
          <NavLink to="/perfil">Mi perfil</NavLink>
        </nav>
        <div className="encabezado__usuario">
          <span>
            {usuario.nombre} {usuario.apellido}
          </span>
          <button type="button" className="boton boton--secundario" onClick={manejarCierre}>
            Cerrar sesión
          </button>
        </div>
      </div>
    </header>
  )
}
