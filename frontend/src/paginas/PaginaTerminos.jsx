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
        de cerrar la sesión en equipos compartidos. El perfil elegido al registrarte no puede
        modificarse:
      </p>
      <ul>
        <li>
          <strong>Abogado o abogada:</strong> trabaja con <em>casos</em>, solo o en un estudio
          jurídico, para evaluar si conviene ofrecer una foto como prueba o pedir una pericia. La
          cuenta personal es gratuita; el estudio paga un plan.
        </li>
        <li>
          <strong>Aseguradora:</strong> trabaja con <em>siniestros</em>, siempre dentro de la
          organización de su compañía, para decidir si un siniestro se liquida o se deriva a
          verificación. La organización paga un plan, la aprueba el Administrador de la
          plataforma y su equipo entra por invitación.
        </li>
      </ul>

      <h2>4. Uso de las imágenes</h2>
      <p>
        Solo podés cargar imágenes que tengas derecho a utilizar para el caso en el que trabajás.
        Las imágenes y los informes se usan exclusivamente para prestar el servicio.
      </p>

      <h2>5. Organizaciones y planes</h2>
      <p>
        Quien crea una organización es su Referente: invita a su equipo, define los permisos y
        responde por el uso que hacen sus miembros. Los planes se pagan por adelantado; los
        límites de cada uno (miembros, análisis por mes e imágenes por caso) se muestran antes de
        pagar. Si el Administrador rechaza una aseguradora, el pago se devuelve.
      </p>

      <h2>6. Cambios en estos términos</h2>
      <p>
        Si estos términos cambian, se publicará una versión nueva y se te pedirá aceptarla para
        seguir usando la plataforma.
      </p>
    </article>
  )
}
