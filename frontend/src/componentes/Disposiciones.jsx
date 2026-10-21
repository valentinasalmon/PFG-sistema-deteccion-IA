/**
 * Disposiciones (layouts) de las pantallas.
 *
 * - DisposicionInterna: pantallas con sesión, con encabezado.
 * - DisposicionAcceso: pantallas de acceso (registro, inicio de sesión,
 *   recuperación), divididas en un panel de marca con el eslogan y el
 *   formulario. En un celular el panel de marca se reduce al logo.
 *
 * Ambas incluyen el pie con los enlaces a los Términos de Uso y a la
 * Política de Privacidad.
 *
 * Realiza: RF01 a RF07 (interfaz); RNF10 (funcionalidad 022).
 */
import { Link, Outlet } from 'react-router'
import Encabezado from './Encabezado.jsx'
import Icono from './Icono.jsx'

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
    <div className="acceso">
      <section className="acceso__marca" aria-label="evidentIA">
        <img className="acceso__logo" src="/marca/logo-tipografia-negra.png" alt="evidentIA" />
        <div className="acceso__mensaje">
          <div className="visor acceso__visor">
            <img src="/marca/isotipo.png" alt="" />
          </div>
          <p className="acceso__eslogan">Tu primera línea de defensa contra el fraude visual</p>
          <p className="acceso__bajada">
            Analizá las imágenes de cada siniestro o reclamo, guardá la evidencia con su huella
            digital y obtené un informe listo para presentar.
          </p>
        </div>
        <ul className="acceso__garantias">
          <li>
            <Icono nombre="administracion" tamanio={18} />
            Evidencia con huella digital
          </li>
          <li>
            <Icono nombre="reloj" tamanio={18} />
            Conservación por 5 años
          </li>
          <li>
            <Icono nombre="documento" tamanio={18} />
            Informe en PDF
          </li>
        </ul>
      </section>
      <div className="acceso__formulario">
        <main id="contenido" className="tarjeta-acceso">
          <Outlet />
        </main>
        <Pie />
      </div>
    </div>
  )
}
