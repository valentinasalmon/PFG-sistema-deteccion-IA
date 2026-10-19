/**
 * Términos de Uso de la plataforma (texto provisorio, versión 1.0).
 *
 * El texto definitivo debe validarse con los tutores (pregunta abierta de la
 * funcionalidad 002). La versión se registra junto con la aceptación.
 *
 * Realiza: RF01 (CA2) y RN27.
 */
import AvisoProvisorio from '../componentes/AvisoProvisorio.jsx'

export default function PaginaTerminos() {
  return (
    <article className="texto-legal">
      <h1>Términos de Uso</h1>
      <AvisoProvisorio />

      <h2>1. Qué ofrece la plataforma</h2>
      <p>
        La plataforma realiza una evaluación preliminar de imágenes aportadas como prueba en
        siniestros automovilísticos y laborales. Cada imagen se analiza con cuatro técnicas
        independientes y el resultado se entrega en un informe explicativo.
      </p>

      <h2>2. Los resultados son indicios, no veredictos</h2>
      <p>
        Los análisis muestran indicios de posible manipulación o generación artificial. No
        constituyen una pericia ni una conclusión definitiva sobre la autenticidad de una imagen.
        Ante cualquier decisión relevante, consultá con un perito especializado.
      </p>

      <h2>3. Cuenta y seguridad</h2>
      <p>
        La cuenta es personal. Sos responsable de mantener la confidencialidad de tu contraseña y
        de cerrar la sesión en equipos compartidos. El perfil elegido al registrarte (Abogado o
        Aseguradora) no puede modificarse.
      </p>

      <h2>4. Uso de las imágenes</h2>
      <p>
        Solo podés cargar imágenes que tengas derecho a utilizar para el caso en el que trabajás.
        Las imágenes y los informes se usan exclusivamente para prestar el servicio.
      </p>

      <h2>5. Cambios en estos términos</h2>
      <p>
        Si estos términos cambian, se publicará una versión nueva y se te pedirá aceptarla para
        seguir usando la plataforma.
      </p>
    </article>
  )
}
