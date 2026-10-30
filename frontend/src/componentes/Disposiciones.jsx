/**
 * Disposiciones (layouts) de las pantallas.
 *
 * - DisposicionInterna: pantallas con sesión, con el menú lateral (022).
 * - DisposicionAcceso: pantallas de acceso (registro, inicio de sesión,
 *   recuperación, enlaces y páginas públicas). Desde la 034 ocupan toda la
 *   pantalla: el logo con el nombre arriba de una tarjeta centrada, sin el
 *   panel de marca dividido (pedido de la autora).
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
 * Acceso a pantalla completa (034): sin panel dividido, el logo con el nombre
 * arriba de una tarjeta centrada y un fondo suave de la marca.
 */
export function DisposicionAcceso() {
  return (
    <ContextoAcceso.Provider value={null}>
      <div className="acceso acceso--completo">
        <header className="acceso__cabecera">
          <Link to="/" className="acceso__volver">
            <Icono nombre="izquierda" tamanio={16} />
            evidentIA
          </Link>
        </header>
        <div className="acceso__formulario">
          <main id="contenido" className="tarjeta-acceso">
            <Link to="/" className="tarjeta-acceso__logo" aria-label="evidentIA, ir a la portada">
              <img src="/marca/logo-tipografia-negra.png" alt="" />
            </Link>
            <Outlet />
          </main>
        </div>
        <Pie />
      </div>
    </ContextoAcceso.Provider>
  )
}
