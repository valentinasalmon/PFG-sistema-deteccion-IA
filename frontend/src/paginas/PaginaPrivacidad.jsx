/**
 * Política de Privacidad de la plataforma (texto provisorio, versión 1.0).
 *
 * Informa el tratamiento de datos personales conforme a la Ley N.° 25.326.
 * El texto definitivo debe validarse con los tutores.
 *
 * Realiza: RF01 (CA2); RNF08.
 */
import AvisoProvisorio from '../componentes/AvisoProvisorio.jsx'

export default function PaginaPrivacidad() {
  return (
    <article className="texto-legal">
      <h1>Política de Privacidad</h1>
      <AvisoProvisorio />

      <h2>1. Qué datos se tratan</h2>
      <p>
        Los datos de tu cuenta (nombre, apellido, correo electrónico, perfil y, si los indicás,
        colegio de abogados o empresa), las imágenes que cargás en tus casos y los resultados de
        los análisis.
      </p>

      <h2>2. Para qué se usan</h2>
      <p>
        Para identificarte, proteger el acceso a tus casos, realizar los análisis que solicitás y
        enviarte los correos necesarios para el funcionamiento de la cuenta.
      </p>

      <h2>3. Cuánto tiempo se conservan</h2>
      <p>
        Las imágenes y los informes de un caso se conservan hasta dos años después de cerrarlo o
        archivarlo, y luego se eliminan. Los casos que eliminás se borran de inmediato.
      </p>

      <h2>4. Seguridad</h2>
      <p>
        Las contraseñas se guardan cifradas de forma irreversible, las comunicaciones viajan
        cifradas y el almacenamiento de las imágenes es privado.
      </p>

      <h2>5. Cookies</h2>
      <p>
        Se usa únicamente una cookie de sesión, imprescindible para mantenerte identificado. No se
        usan cookies de publicidad ni de seguimiento.
      </p>

      <h2>6. Tus derechos</h2>
      <p>
        Podés acceder a tus datos, rectificarlos y solicitar su supresión, conforme a la Ley N.°
        25.326 de Protección de los Datos Personales. La Agencia de Acceso a la Información
        Pública es el órgano de control de esa ley.
      </p>
    </article>
  )
}
