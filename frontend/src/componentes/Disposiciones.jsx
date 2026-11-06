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
import { Link, Outlet, useLocation } from 'react-router'
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
/**
 * Pantallas de cuenta que llevan el panel de marca a la izquierda (037): todas
 * comparten la misma tarjeta, así pasar de una a otra no cambia la identidad.
 */
const CON_PANEL = ['/iniciar-sesion', '/registro', '/recuperar-contrasenia', '/restablecer-contrasenia', '/verificar-correo', '/confirmar-correo', '/invitaciones/responder']

function PanelDeMarca() {
  return (
    <aside className="inicio-dividido__panel" aria-label="Qué hace evidentIA">
      <p className="inicio-dividido__eti">Para abogados y aseguradoras</p>
      <p className="inicio-dividido__tesis">Revisá cada foto antes de presentarla o de liquidar.</p>
      <ul>
        <li>Indicios de edición o de imagen con IA, técnica por técnica.</li>
        <li>Informe breve con un enlace al análisis completo.</li>
        <li>Verificable por cualquiera con su código.</li>
      </ul>
    </aside>
  )
}

export function DisposicionAcceso() {
  const { pathname } = useLocation()
  const conPanel = CON_PANEL.some((ruta) => pathname.startsWith(ruta))
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
            {conPanel ? (
              <div className="inicio-dividido">
                <PanelDeMarca />
                <div className="inicio-dividido__formulario">
                  <Outlet />
                </div>
              </div>
            ) : (
              <Outlet />
            )}
          </main>
        </div>
        <Pie />
      </div>
    </ContextoAcceso.Provider>
  )
}
