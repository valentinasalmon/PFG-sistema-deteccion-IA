/**
 * Disposiciones (layouts) de las pantallas.
 *
 * - DisposicionInterna: pantallas con sesión, con encabezado.
 * - DisposicionAcceso: pantallas de acceso (registro, inicio de sesión,
 *   recuperación), con una tarjeta centrada.
 *
 * Ambas incluyen el pie con los enlaces a los Términos de Uso y a la
 * Política de Privacidad.
 */
import { Link, Outlet } from 'react-router'
import Encabezado from './Encabezado.jsx'

function Pie() {
  return (
    <footer className="pie">
      <p>
        La plataforma ofrece indicios para una evaluación preliminar y no emite veredictos.
        Ante cualquier duda, consultá con un perito especializado.
      </p>
      <nav aria-label="Información legal" className="pie__enlaces">
        <Link to="/terminos">Términos de Uso</Link>
        <Link to="/privacidad">Política de Privacidad</Link>
        <Link to="/estado">Estado del sistema</Link>
      </nav>
    </footer>
  )
}

export function DisposicionInterna() {
  return (
    <div className="disposicion">
      <a href="#contenido" className="saltar-al-contenido">
        Saltar al contenido
      </a>
      <Encabezado />
      <main id="contenido" className="disposicion__principal">
        <Outlet />
      </main>
      <Pie />
    </div>
  )
}

export function DisposicionAcceso() {
  return (
    <div className="disposicion disposicion--acceso">
      <main id="contenido" className="tarjeta-acceso">
        <p className="tarjeta-acceso__marca">Análisis de imágenes</p>
        <Outlet />
      </main>
      <Pie />
    </div>
  )
}
