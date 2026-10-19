/**
 * Política de Privacidad de la plataforma (texto provisorio, versión 1.0).
 *
 * Informa el tratamiento de datos personales conforme a la Ley N.° 25.326.
 * El texto definitivo debe validarse con los tutores.
 *
 * Realiza: RF01 (CA2); RNF08; RNF06 (informa el registro de auditoría,
 * funcionalidad 003).
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

      <h2>4. Registro de actividad</h2>
      <p>
        Para poder reconstruir quién hizo cada acción, la plataforma registra las acciones
        relevantes de las cuentas: registro, verificación del correo, inicios y cierres de sesión
        (incluidos los intentos fallidos, con el correo ingresado), bloqueos, cambios de contraseña
        y cambios en los datos del perfil y del correo. Cada registro guarda la fecha y la hora,
        la cuenta, la dirección IP de origen, la acción, su resultado y los datos modificados.
        Nunca guarda contraseñas ni enlaces de acceso.
      </p>
      <p>
        Este registro se usa solo con fines de seguridad y de trazabilidad legal, no puede
        modificarse y se conserva durante cinco años. Si eliminás tu cuenta, los registros se
        conservan sin vincularse a ella; los que guardan un correo electrónico (por ejemplo, un
        intento de inicio de sesión fallido) lo conservan hasta que se cumplen esos cinco años.
      </p>

      <h2>5. Seguridad</h2>
      <p>
        Las contraseñas se guardan cifradas de forma irreversible, las comunicaciones viajan
        cifradas y el almacenamiento de las imágenes es privado.
      </p>

      <h2>6. Cookies</h2>
      <p>
        Se usa únicamente una cookie de sesión, imprescindible para mantenerte identificado. No se
        usan cookies de publicidad ni de seguimiento.
      </p>

      <h2>7. Tus derechos</h2>
      <p>
        Podés acceder a tus datos, rectificarlos y solicitar su supresión, conforme a la Ley N.°
        25.326 de Protección de los Datos Personales. La Agencia de Acceso a la Información
        Pública es el órgano de control de esa ley.
      </p>
      <p>
        Desde "Mi perfil" podés corregir tus datos, descargar una copia de ellos (en PDF y en
        JSON) y eliminar tu cuenta. Al eliminarla se suprimen tus datos personales de inmediato;
        antes tenés que transferir o eliminar los casos a tu cargo y designar otro Referente en
        las organizaciones que administrás.
      </p>
    </article>
  )
}
