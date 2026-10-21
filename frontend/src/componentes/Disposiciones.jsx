/**
 * Disposiciones (layouts) de las pantallas.
 *
 * - DisposicionInterna: pantallas con sesión, con el menú lateral (022).
 * - DisposicionAcceso: pantallas de acceso (registro, inicio de sesión,
 *   recuperación), divididas en un panel de marca verde bosque, con el logo
 *   centrado dentro de las esquinas de visor y el eslogan, y el formulario en
 *   una tarjeta. En un celular el panel de marca se reduce al logo.
 *
 * Ambas incluyen el pie con los enlaces a los Términos de Uso y a la
 * Política de Privacidad.
 *
 * Realiza: RF01 a RF07 (interfaz); RNF10 (funcionalidad 022).
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

export function DisposicionAcceso() {
  return (
    <div className="acceso">
      <section className="acceso__marca" aria-label="evidentIA">
        <div className="acceso__mensaje">
          <div className="visor acceso__visor">
            <img src="/marca/logo-tipografia-blanca.png" alt="evidentIA" />
            <span className="acceso__escaneo" aria-hidden="true" />
          </div>
          <p className="acceso__eslogan">Tu primera línea de defensa contra el fraude visual</p>
          <p className="acceso__bajada">
            Detectá fotos editadas o generadas con inteligencia artificial antes de que lleguen a un
            expediente o a la liquidación de un siniestro.
          </p>
        </div>
        <div className="acceso__muestra" aria-hidden="true">
          <div className="acceso__muestra-cabecera">
            <span>frente.jpg</span>
            <span className="acceso__muestra-ok">Integridad verificada</span>
          </div>
          <div className="acceso__muestra-fila">
            <span>Metadatos</span>
            <span className="nivel nivel--ninguno">Sin indicios · 0 %</span>
          </div>
          <div className="acceso__muestra-fila">
            <span>Credenciales de contenido</span>
            <span className="nivel nivel--ninguno">Sin indicios · 0 %</span>
          </div>
          <div className="acceso__muestra-fila">
            <span>Niveles de error</span>
            <span className="nivel nivel--moderado">Indicios moderados · 45 %</span>
          </div>
        </div>
        <ul className="acceso__servicios">
          <li>
            <strong>Legal</strong>
            Prueba documentada para demandas, mediaciones y reclamos.
          </li>
          <li>
            <strong>Seguros</strong>
            Fotos de siniestros verificadas antes de liquidar.
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
