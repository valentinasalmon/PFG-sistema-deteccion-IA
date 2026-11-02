/**
 * Menú lateral de las pantallas internas (funcionalidad 022).
 *
 * Reemplaza al encabezado horizontal, que se saturaba con muchas opciones:
 * logo con el servicio del rubro (Legal o Seguros), navegación con íconos,
 * acceso rápido a "Nuevo caso" y, abajo, la cuenta y el cierre de sesión. En
 * pantallas angostas pasa a ser una barra superior que se despliega.
 *
 * El menú depende de quién entra (funcionalidad 028): la administradora de la
 * plataforma ve solo Administración y Mi perfil; «Organizaciones» aparece
 * solo para quien es miembro de alguna.
 *
 * Desde la funcionalidad 034 suma el buscador «Buscar o ir a…» (Ctrl K).
 *
 * Realiza: RF04 y CA7, CA11 de la funcionalidad 002; CA7 de la 034; RNF10.
 */
import { useState } from 'react'
import { Link, NavLink } from 'react-router'
import { useSesion } from '../hooks/useSesion.js'
import { textosDelRubro } from '../utilidades/lenguaje.js'
import BuscadorRapido from './BuscadorRapido.jsx'
import Icono from './Icono.jsx'

export default function Encabezado() {
  const { usuario, cerrarSesion } = useSesion()
  const [abierto, setAbierto] = useState(false)
  const rubro = textosDelRubro(usuario.perfil)
  const esAdministradora = usuario.rol === 'administrador'

  // Al quedar sin usuario, la ruta protegida lleva al inicio de sesión con el aviso.
  function manejarCierre() {
    cerrarSesion().catch(() => {})
  }

  const iniciales = `${usuario.nombre?.[0] ?? ''}${usuario.apellido?.[0] ?? ''}`.toUpperCase()
  const cerrarMenu = () => setAbierto(false)

  return (
    <header className={`lateral ${abierto ? 'lateral--abierto' : ''}`}>
      <div className="lateral__marca">
        <Link to={esAdministradora ? '/administracion' : '/'} className="lateral__logo" onClick={cerrarMenu}>
          <img src="/marca/logo-tipografia-negra.png" alt="evidentIA, ir al inicio" />
        </Link>
        <span className="lateral__servicio">{rubro.servicio}</span>
        <button
          type="button"
          className="lateral__alternar"
          aria-expanded={abierto}
          aria-controls="menu-principal"
          onClick={() => setAbierto(!abierto)}
        >
          {abierto ? 'Cerrar menú' : 'Menú'}
        </button>
      </div>
      <div id="menu-principal" className="lateral__contenido">
        {!esAdministradora && (
          <Link to="/casos/nuevo" className="boton lateral__nuevo" onClick={cerrarMenu}>
            <Icono nombre="mas" tamanio={18} />
            Nuevo caso
          </Link>
        )}
        <BuscadorRapido alAbrir={cerrarMenu} />
        <nav aria-label="Principal" className="encabezado__navegacion">
          {esAdministradora ? (
            <NavLink to="/administracion" onClick={cerrarMenu}>
              <Icono nombre="administracion" />
              <span>Administración</span>
            </NavLink>
          ) : (
            <>
              <NavLink to="/" end onClick={cerrarMenu}>
                <Icono nombre="inicio" />
                <span>Inicio</span>
              </NavLink>
              <NavLink to="/casos" onClick={cerrarMenu}>
                <Icono nombre="casos" />
                <span>Casos</span>
              </NavLink>
              {usuario.en_organizacion && (
                <NavLink to="/organizaciones" onClick={cerrarMenu}>
                  <Icono nombre="organizaciones" />
                  <span>Organizaciones</span>
                </NavLink>
              )}
            </>
          )}
          <NavLink to="/perfil" onClick={cerrarMenu}>
            <Icono nombre="perfil" />
            <span>Mi perfil</span>
          </NavLink>
        </nav>
        <div className="encabezado__usuario">
          <span className="encabezado__avatar" aria-hidden="true">
            {iniciales}
          </span>
          <span className="encabezado__nombre">
            {usuario.nombre} {usuario.apellido}
            <small>{usuario.correo}</small>
          </span>
          <button type="button" className="boton boton--fantasma lateral__salir" onClick={manejarCierre}>
            <Icono nombre="salir" />
            Cerrar sesión
          </button>
        </div>
      </div>
    </header>
  )
}
