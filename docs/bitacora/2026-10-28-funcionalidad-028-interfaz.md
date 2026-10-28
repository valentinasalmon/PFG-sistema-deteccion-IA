# 2026-10-28 — Mejoras de interfaz (028): auditoría, frames y primera tanda

## Qué se hizo

- **Auditoría** de las 19 pantallas en computadora y celular, con la plataforma levantada en local con datos de ejemplo. Se encontraron unos 30 problemas:
  - duplicados;
  - etiquetas del mismo color;
  - datos repetidos;
  - formularios y listas mal armados;
  - una pantalla del caso de unos 8.800 px.
- **Frames de la propuesta** en un lienzo de diseño, en dos rondas.
  - Ronda 1: la autora aprobó Inicio, Lista de casos, Mi perfil, Organización y Administración.
  - Ronda 2: pidió estados de azul a verde, el menú según el rol, la pantalla del caso por etapas con un enlace para la persona afectada, y mejoras en el inicio de sesión y el registro.
- **Primera tanda implementada:** Inicio, Lista de casos (con buscador único en el backend), Mi perfil en pestañas, Organización y Administración, y los estados de azul a verde.
- **Calidad:**
  - backend: 525 pruebas, cobertura del 97,5 %, pylint 10/10;
  - frontend: 221 pruebas.

## Decisiones

- **La actividad propia se redacta en segunda persona** («Cargaste…»). Se convierte el verbo y no se repite el nombre de quien mira.
- **Un solo buscador** que busca a la vez en el número, el expediente (sin tildes) y el lugar. Se conservan los filtros `numero` y `expediente` de la API por compatibilidad.
- **Las pestañas del perfil siguen el patrón de WAI-ARIA** (flechas del teclado) y quedan en la dirección (`?seccion=`).
- **El rol «Responsable» deja de mostrarse como etiqueta**: es lo habitual. Solo se aclara cuando el caso es compartido.
- **Corrección de la auditoría inicial:** dos cosas que se habían marcado como errores eran efectos de la captura de página completa.
  - El menú lateral es fijo y acompaña al desplazarse.
  - El mapa ELA se carga recién al llegar a él.
  
  Igual se le reservó el lugar al mapa para que la pantalla no salte.

## Segunda tanda (validada por la autora)

- **Menú según el rol.**
  - La administradora ve solo Administración y Mi perfil; las rutas de casos y organizaciones la llevan a su tablero, y el tablero lleva al inicio a cualquier otra persona.
  - «Organizaciones» aparece solo para quien es miembro de alguna: la sesión informa `en_organizacion`.
  - Quien no tiene organización encuentra «Crear un estudio jurídico» y sus invitaciones en Mi perfil.
  - Se mantienen los íconos del menú.
- **Pantalla del caso por etapas.**
  - Cargar imágenes, Análisis e Informe son la navegación del caso, y cada etapa muestra solo lo suyo. La etapa queda en la dirección (`?etapa=`); sin elegir, se abre la que corresponde al estado.
  - Carga: tres caminos (computadora, celular con QR y persona afectada), arrastrar y soltar, el origen de cada foto y una barra fija con «Analizar las N imágenes».
  - Análisis: barra de progreso y cada imagen con sus capas (hecha, en curso, en espera); al terminar, los resultados en filas desplegables.
  - Informe: el más reciente destacado, con las imágenes incluidas, el nivel de cada capa por imagen, el PDF con código, sello y huella; debajo, los anteriores.
  - La gestión del caso (estado, accesos, transferir o eliminar) queda plegada en la columna lateral.
- **Enlace para la persona afectada (CP-32).**
  - Backend: `enlaces_carga` suma `tipo`, `destinatario` y `declaracion_aceptada_en`, e `imagenes` suma `origen` (migración `e8c2d4a6f028`).
  - Rutas: `GET/POST /api/casos/<id>/enlaces-persona-afectada` y `DELETE …/<id_enlace>`; la página pública reutiliza `/api/carga/<token>`.
  - El enlace del QR del celular ya no anula los de la persona afectada.
  - Página pública: quién pide las fotos (sin datos del caso), tres pasos, la declaración obligatoria, sacar o elegir fotos y una pantalla final.
- **Cuenta de demostración.** `flask --app wsgi administracion cuenta-de-demostracion` crea o restablece una abogada sin rol de Administrador, con un estudio jurídico. Sirve también en producción, porque no tiene contraseña fija: se escribe en la terminal y debe cumplir la política.
- **Calidad:**
  - backend: 532 pruebas, cobertura del 97,6 %, pylint 10/10, 3 contratos de capas;
  - frontend: 232 pruebas y lint sin errores.

## Decisiones de la segunda tanda

- **El enlace se muestra una sola vez.** Como el del celular, en la base solo queda su huella: si se pierde, se crea otro.
- **El mensaje para WhatsApp o correo no lleva el número del caso** ni otros datos: solo quién pide las fotos y hasta cuándo.
- **La declaración se registra una vez por enlace**, en la auditoría y sin usuario (la persona no tiene cuenta), con la versión del texto.
- **Las fotos de la persona afectada se cargan a nombre de quien creó el enlace**, con sus permisos vigentes y las mismas validaciones, huella y sello. El origen queda en la imagen.
- **La cuenta de prueba de desarrollo sigue siendo Administradora.** Con el menú por rol, para ver los casos hay que usar la cuenta de demostración.

## Pendiente

- Inicio de sesión y registro (frames 9a a 9c) y los ajustes restantes del celular: la autora pidió dejarlos para la tanda siguiente.
- Validar con los tutores el texto de la declaración y sumarlo a la Política de Privacidad (CP-32).
