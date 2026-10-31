/**
 * Política de Privacidad de la plataforma (texto provisorio, versión 1.0).
 *
 * Informa el tratamiento de datos personales conforme a la Ley N.° 25.326.
 * El texto definitivo debe validarse con los tutores.
 *
 * Desde la tercera tanda de la 034 abre con cuatro pilares (confidencialidad,
 * veracidad, seguridad y apoyo) y un detalle técnico de las medidas, tomado
 * de la revisión OWASP de docs/arquitectura/seguridad.md (pedido de la
 * autora: «ser bien técnico» y mostrar que somos apoyo). No nombra
 * proveedores de infraestructura.
 *
 * Realiza: RF01 (CA2); RNF01, RNF02, RNF06, RNF08; RN27.
 */
import AvisoProvisorio from '../componentes/AvisoProvisorio.jsx'

const PILARES = [
  {
    titulo: 'Confidencialidad',
    texto: 'Solo ven un caso las personas con permiso sobre él. Nadie más: ni otros clientes, ni el público.',
  },
  {
    titulo: 'Veracidad',
    texto:
      'Cada foto guarda su huella digital desde la carga; si cambia un solo píxel, la huella deja de coincidir.',
  },
  {
    titulo: 'Seguridad',
    texto: 'Todo viaja y se guarda cifrado, y cada acceso queda registrado en una auditoría que no se puede editar.',
  },
  {
    titulo: 'Apoyo, no veredicto',
    texto:
      'Mostramos indicios técnicos con su explicación. La decisión es siempre de una persona, con un perito si hace falta.',
  },
]

/** Medidas técnicas, con el dato concreto de cada una. */
const MEDIDAS = [
  ['Cifrado en tránsito', 'TLS 1.2 y 1.3; HTTP redirige a HTTPS y HSTS de un año.'],
  [
    'Cifrado en reposo',
    'Imágenes e informes con AES-256; discos del servidor cifrados; claves y secretos en un almacén cifrado, nunca en el código.',
  ],
  ['Contraseñas', 'Guardadas con bcrypt (costo 12). Tras 5 intentos fallidos, la cuenta se bloquea 15 minutos.'],
  [
    'Sesión',
    'Vence a los 30 minutos sin uso y a las 8 horas. Cookie HttpOnly, Secure y SameSite, y token CSRF en cada cambio.',
  ],
  [
    'Acceso a los archivos',
    'El almacenamiento no tiene acceso público: cada foto o PDF se abre con un enlace firmado que vence a los 5 minutos.',
  ],
  [
    'Integridad de la prueba',
    'Huella SHA-256 de cada imagen, informe y versión del sistema, sellada con fecha en una red pública (Hedera). Cualquiera puede verificar un informe con su código, sin cuenta.',
  ],
  [
    'Auditoría',
    'Cada acción relevante queda registrada con fecha, cuenta, IP y resultado, en la misma operación que el cambio. No se puede modificar y se conserva cinco años.',
  ],
  ['Abuso', 'Límites de pedidos por dirección IP y respuestas que no revelan qué cuentas existen.'],
  [
    'Revisión',
    'Controles revisados contra el OWASP Top 10 (2021). Solo se publica código que pasa las pruebas automáticas.',
  ],
  ['Ubicación', 'Los datos se alojan en centros de datos de la Unión Europea.'],
]

export default function PaginaPrivacidad() {
  return (
    <article className="texto-legal pagina-legal">
      <h1>Política de Privacidad</h1>
      <AvisoProvisorio />
      <p className="pagina-legal__bajada">
        Tus casos son prueba. Así los cuidamos, con el detalle técnico de cada medida.
      </p>

      <ul className="pilares" aria-label="Cómo cuidamos tus datos">
        {PILARES.map((pilar) => (
          <li key={pilar.titulo}>
            <strong>{pilar.titulo}</strong>
            <span>{pilar.texto}</span>
          </li>
        ))}
      </ul>

      <h2>Detalle técnico</h2>
      <dl className="medidas">
        {MEDIDAS.map(([nombre, detalle]) => (
          <div key={nombre}>
            <dt>{nombre}</dt>
            <dd>{detalle}</dd>
          </div>
        ))}
      </dl>

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
        Las imágenes y los informes de un caso se conservan hasta cinco años después de cerrarlo o
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
        Las medidas concretas, con sus valores, están en el detalle técnico de esta página.
      </p>

      <h2>6. Cookies y medición de uso</h2>
      <p>
        Se usa una cookie de sesión, imprescindible para mantenerte identificado. No se usan
        cookies de publicidad.
      </p>
      <p>
        Durante el período de prueba usamos Microsoft Clarity para mejorar la facilidad de uso:
        registra clics, desplazamientos y el recorrido por las pantallas mediante cookies de
        medición. La plataforma oculta todos los textos y las imágenes antes de enviarlos, así que
        Clarity no ve tus datos, tus casos ni tus fotos. Podés evitarlo bloqueando las cookies de
        terceros en tu navegador.
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
