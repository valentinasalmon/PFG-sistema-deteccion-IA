/**
 * Disposiciones (layouts) de las pantallas.
 *
 * - DisposicionInterna: pantallas con sesión, con el menú lateral (022).
 * - DisposicionAcceso: pantallas de acceso (registro, inicio de sesión,
 *   recuperación, enlaces y páginas públicas). Desde la 034 ocupan toda la
 *   pantalla; desde su tercera tanda siguen la estética de la portada: una
 *   franja verde bosque con la grilla y el logo, y la tarjeta blanca encima,
 *   con píldoras lima y campos más grandes (estilos en acceso.css).
 *
 * Ambas incluyen el pie con los enlaces a los Términos de Uso y a la
 * Política de Privacidad.
 *
 * Realiza: RF01 a RF07 (interfaz); RNF10 (funcionalidad 022).
 */
import { Link, Outlet } from 'react-router'
import { ContextoAcceso } from '../contextos/contextoAcceso.js'
import Encabezado from './Encabezado.jsx'
import Icono from './Icono.jsx'
import '../estilos/acceso.css'

function Pie() {
  return (
    <footer className="pie">
      <p>
        La plataforma ofrece indicios para una evaluación preliminar y no emite veredictos. Ante cualquier
        duda, consultá con un perito especializado.
      </p>
      <nav aria-label="Información legal" className="pie__enlaces">
        <Link to="/terminos">Términos de Uso</Link>
        <Link to="/privacidad">Política de Privacidad</Link>
        <Link to="/verificar">Verificar un informe</Link>
        <Link to="/estado">Estado del sistema</Link>
      </nav>
    </footer>
  )
}

export function DisposicionInterna() {
  return (
    <div className="disposicion disposicion--interna">
      <a href="#contenido" className="saltar-al-contenido">
        Saltar al contenido
      </a>
      <Encabezado />
      <div className="disposicion__area">
        <main id="contenido" className="disposicion__principal">
          <Outlet />
        </main>
        <Pie />
      </div>
    </div>
  )
}

/**
 * Acceso a pantalla completa (034): la franja oscura de la marca con el logo
 * arriba y la tarjeta del formulario centrada, montada sobre la franja.
 */
export function DisposicionAcceso() {
  return (
    <ContextoAcceso.Provider value={null}>
      <div className="acceso acceso--completo">
        <header className="acceso__cabecera">
          <Link to="/" className="acceso__logo" aria-label="evidentIA, ir a la portada">
            <img src="/marca/logo-tipografia-blanca.png" alt="" />
          </Link>
          <Link to="/" className="acceso__volver">
            <Icono nombre="izquierda" tamanio={16} />
            Volver a la portada
          </Link>
        </header>
        <div className="acceso__formulario">
          <main id="contenido" className="tarjeta-acceso">
            <Outlet />
          </main>
        </div>
        <Pie />
      </div>
    </ContextoAcceso.Provider>
  )
}
