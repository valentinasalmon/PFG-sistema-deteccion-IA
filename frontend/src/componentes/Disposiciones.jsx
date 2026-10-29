/**
 * Disposiciones (layouts) de las pantallas.
 *
 * - DisposicionInterna: pantallas con sesión, con el menú lateral (022).
 * - DisposicionAcceso: pantallas de acceso (registro, inicio de sesión,
 *   recuperación), divididas en un panel de marca verde bosque, con el logo
 *   centrado dentro de las esquinas de visor y el eslogan, y el formulario en
 *   una tarjeta (sin tarjeta de muestra ni servicios, por pedido de la
 *   autora). Desde la 028 el panel suma tres ventajas reales y para quién es.
 *   En un celular el panel de marca se reduce a una banda corta con el logo.
 *
 * Ambas incluyen el pie con los enlaces a los Términos de Uso y a la
 * Política de Privacidad.
 *
 * Realiza: RF01 a RF07 (interfaz); RNF10 (funcionalidad 022).
 */
import { useState } from "react";
import { Link, Outlet } from "react-router";
import { ContextoAcceso } from "../contextos/contextoAcceso.js";
import Encabezado from "./Encabezado.jsx";
import Icono from "./Icono.jsx";

function Pie() {
  return (
    <footer className="pie">
      <p>
        La plataforma ofrece indicios para una evaluación preliminar y no emite
        veredictos. Ante cualquier duda, consultá con un perito especializado.
      </p>
      <nav aria-label="Información legal" className="pie__enlaces">
        <Link to="/terminos">Términos de Uso</Link>
        <Link to="/privacidad">Política de Privacidad</Link>
        <Link to="/verificar">Verificar un informe</Link>
        <Link to="/estado">Estado del sistema</Link>
      </nav>
    </footer>
  );
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
  );
}

/** Lo que hace la plataforma, en tres puntos verificables (028, frame 9a). */
const VENTAJAS = [
  {
    icono: "buscar",
    titulo: "Varios análisis por imagen",
    texto: "Metadatos, credenciales de contenido (C2PA) y niveles de error.",
  },
  {
    icono: "candado",
    titulo: "Cadena de custodia sellada",
    texto: "La huella de cada imagen queda registrada en Hedera.",
  },
  {
    icono: "documento",
    titulo: "Informe verificable",
    texto: "Cualquiera puede comprobar con el QR que el PDF no cambió.",
  },
];

export function DisposicionAcceso() {
  const [panelPasos, setPanelPasos] = useState(null);
  return (
    <ContextoAcceso.Provider value={panelPasos}>
      <div className="acceso">
        <section className="acceso__marca" aria-label="evidentIA">
          <div className="acceso__mensaje">
            <div className="visor acceso__visor">
              <img src="/marca/logo-tipografia-blanca.png" alt="evidentIA" />
              <span className="acceso__escaneo" aria-hidden="true" />
            </div>
            <p className="acceso__eslogan">
              Tu primera línea de defensa contra el fraude visual
            </p>
            <p className="acceso__bajada">
              Detectá fotos editadas o generadas con inteligencia artificial
              antes de que lleguen a un expediente o a la liquidación de un
              siniestro.
            </p>
            <ul className="acceso__ventajas">
              {VENTAJAS.map((ventaja) => (
                <li key={ventaja.titulo}>
                  <span className="acceso__ventaja-icono" aria-hidden="true">
                    <Icono nombre={ventaja.icono} tamanio={22} />
                  </span>
                  <span>
                    <strong>{ventaja.titulo}</strong>
                    <span className="acceso__ventaja-texto">
                      {ventaja.texto}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
            <ul className="acceso__rubros" aria-label="Para quién es">
              <li>Estudios jurídicos</li>
              <li>Aseguradoras</li>
              <li>Peritos</li>
            </ul>
          </div>
          {/* El registro dibuja acá sus pasos con nombre (032); si lo hace, se oculta lo anterior. */}
          <div className="acceso__pasos" ref={setPanelPasos} />
        </section>
        <div className="acceso__formulario">
          <main id="contenido" className="tarjeta-acceso">
            <Outlet />
          </main>
          <Pie />
        </div>
      </div>
    </ContextoAcceso.Provider>
  );
}
