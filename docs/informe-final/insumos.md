# Insumos para el informe final del proyecto

Lista viva de temas, decisiones y hallazgos que tienen que quedar en el **informe final del proyecto** (el documento para la facultad). La actualiza el agente cada vez que aparece algo relevante. Cada punto indica dónde está el detalle.

## Sello de tiempo: de BFA a Hedera

- **Plan original:** Blockchain Federal Argentina, por su valor probatorio local (especificación 016).
- **Problemas encontrados (2026-10-21 y 22):**
  - la dirección supuesta no existía;
  - el servicio 2.0 estaba caído (404);
  - el 1.0 funciona pero bloquea conexiones desde fuera de Argentina;
  - el diagnóstico se hizo con curl, comparando la PC de la autora con el servidor de AWS.
  
  Ver las bitácoras del 2026-10-22.
- **Alternativa intermedia descartada:** sello pedido desde el navegador del usuario.
- **Decisión:** Hedera Consensus Service, ADR-0018. Incluir:
  - comparación de alternativas;
  - costos (unos US$ 0,0008 por registro);
  - verificación pública con HashScan y el *mirror node*;
  - riesgos (custodia de la clave, reinicios de *testnet*).
  
  Ver `docs/investigacion/2026-10-25-hedera.md`.
- **Usos de Hedera en el sistema:**
  1. huella de cada imagen al cargarla (lo que antes hacía BFA);
  2. huella de cada informe PDF, con página de verificación;
  3. huella de cada versión desplegada del sistema ("host tokenizado", CP-29).
- **Implementación (funcionalidad 023):**
  - mensaje mínimo `{"v":1,"tipo":"imagen","sha256":...}`;
  - recibo `<red>:<tema>/<secuencia>`;
  - verificación en el *mirror node* comparando la huella;
  - enlace público a HashScan;
  - clave privada solo en SSM (nunca en el repositorio ni en el estado de Terraform), pedida sin mostrarla al crear el tema;
  - SDK oficial `hiero-sdk-python`, importado solo cuando el modo es Hedera.
- **Lección para el informe:** depender de un servicio externo sin documentación pública. El patrón Strategy permitió cambiar de proveedor sin tocar el resto del sistema.

## Carga desde el celular

- Hallazgos sobre la web móvil, HEIC, pérdida de ubicación en iOS, fotos sin EXIF y compresión de WhatsApp.
- Diez ideas con pros y contras, y la propuesta elegida.
- **Evolución de la propuesta:**
  - primero, web en el celular más QR;
  - la autora descartó la plataforma móvil;
  - propuesta final: código de carga (QR y 6 dígitos) más "compartir desde la galería", con Web Share Target (PWA) en Android y Atajo de Apple en iPhone.
  
  Las alternativas evaluadas y descartadas (cable, AirDrop, Quick Share, iCloud, LocalSend, correo, WhatsApp, app nativa) están en la investigación.
- **Etapa 1 implementada** (funcionalidad 024): soporte de HEIC sin convertir el original, detectado por la caja `ftyp`, y ELA con validez limitada en HEIC.
- **El tutor aprobó el QR hacia la galería (2026-10-26). Etapa 2 implementada:**
  - enlace de un solo uso (15 minutos, sin tope de fotos más allá del límite del plan, solo carga en ese caso);
  - token de 192 bits, del que solo se guarda la huella;
  - QR en SVG generado en el servidor;
  - página del celular sin sesión, con galería y cámara;
  - auditoría con origen `celular`;
  - actualización automática en la computadora.
  
  Queda como trabajo futuro el "compartir desde la galería" (Web Share Target y Atajo de Apple).
- **Importar desde Drive o Dropbox: descartado** por doble trabajo, por sumar un custodio intermedio sin trazabilidad (que puede comprimir o convertir la foto) y por la privacidad. Como ampliación futura, importar desde un enlace enviado por un tercero requeriría:
  - descargar sin acceder a cuentas;
  - no guardar el enlace;
  - marcar el origen como "sin garantía";
  - una declaración de autorización (Ley 25.326).
- Ver `docs/investigacion/2026-10-25-carga-desde-el-celular.md`.

## Informe PDF breve, por rubro y verificable (funcionalidades 025 y 026)

- **Por qué:** quien analiza imágenes todos los días no puede leer un PDF de 8 o 9 páginas. Se redujo a unas 4 páginas, sin numeración ni saltos de página, y con más espacio.
- **Orden aprobado por la autora:** caso; custodia con cronología; escala; resultados deterministas y probabilísticos; resultados por imagen; qué hacer ahora; verificación; y el aviso final.
- **Lenguaje por rubro:**
  - Abogado: expediente, prueba, pericia.
  - Aseguradora: siniestro, liquidación, verificación o inspección.
- **Deterministas y probabilísticos:**
  - deterministas: integridad, metadatos y C2PA (hechos verificables, reproducibles y comprobables por terceros);
  - probabilísticos: ELA y la red neuronal (estimaciones que pueden fallar en los dos sentidos).
  
  Un indicio determinista pesa más.
- **PDF verificable:**
  - la huella del PDF se sella en Hedera;
  - QR y código de 12 caracteres;
  - página pública donde el navegador calcula la huella (el PDF nunca se sube);
  - nunca se muestran datos del caso.

- **Ajustes después de probarlo (2026-10-27):**
  - ningún bloque se corta entre páginas;
  - resultados más descriptivos (qué revisó, qué encontró, hallazgos y datos relevantes);
  - se quitaron la sección de tipos, "qué hacer" y las versiones.
  
  Criterio: la plataforma muestra la versión breve y el PDF, el detalle legible.
- **"Host tokenizado" (029):** cada despliegue sella en Hedera la huella de su artefacto, y cada análisis guarda su commit. La verificación pública muestra con qué versión se analizó: refuerza la cadena de custodia sobre el propio software.

- **Inicio con Google (027, 2026-10-28):**
  - OpenID Connect con código de autorización y PKCE del lado del servidor, sin JavaScript de terceros ni biblioteca de JWT (ADR-0019, con la justificación de OpenID Connect Core 3.1.3.7);
  - el rubro se pide igual la primera vez, porque define el lenguaje y los permisos;
  - se evita el "secuestro previo" de cuentas: un correo registrado por otra persona y sin verificar pierde su contraseña al vincularse;
  - para la sección de seguridad: la cookie de sesión pasó de `SameSite=Strict` a `Lax`, porque con `Strict` se perdía la sesión al volver desde Google, y la protección CSRF compensa el cambio.
- **Integración continua (2026-10-28):** la validación de commits se limitó a los Pull Requests de funcionalidades, porque fallaba en los de integración por commits ya validados. Es un ejemplo de ajuste del arnés a la práctica real.

- **Seguridad (030, 2026-10-28):**
  - revisión completa según OWASP Top 10 (2021), con evidencia y riesgos aceptados en `docs/arquitectura/seguridad.md`; sirve directamente para la sección de seguridad del informe;
  - límites de pedidos por IP en Nginx (respuesta 429 en JSON), cabeceras `Permissions-Policy` y `Cross-Origin-Opener-Policy`;
  - auditoría automática de dependencias en cada Pull Request y cada semana, como condición para desplegar;
  - WeasyPrint limitado a recursos `data:` (defensa en profundidad contra SSRF);
  - búsqueda de secretos en todo el historial de Git: sin hallazgos reales.
  - Hallazgo para contar: npm 10 fallaba al instalar ("edgesOut") por un error con las dependencias opcionales de Vite; con npm 11, el mismo que usa la integración continua, se resolvió.

## Gestión con el tablero de Trello (2026-10-26)

- El tablero se reorganizó para coincidir con lo que declara el Capítulo V: columnas Backlog, En análisis, En desarrollo, En pruebas y Completado. Cada funcionalidad integrada tiene su tarjeta con el Pull Request y la fecha de integración, de modo que el historial muestra la cronología real.
- **Corrección necesaria en el informe**: el Capítulo V afirma un límite de una tarea en curso por columna, pero en la práctica la autora y el agente de IA trabajaron en paralelo (por ejemplo, el entrenamiento de la 010 en Colab mientras se integraban otras funcionalidades). Decisión de la autora: corregir la frase en el informe y no forzar el límite en el tablero.
- **Inconsistencia detectada**: el informe (OE4 y aceptación del MVP) exige F1 ≥ 0,85 y la especificación 010 (CP-07) usa AUC ≥ 0,90. Queda para validar con los tutores.
- Revisión del informe contra las consignas de la AE1 y la AE2: deudas y capítulos vacíos cargados en el tablero y en `docs/guias/pendientes.md`.

- **Usabilidad e interfaz (028, 2026-10-28):**
  - auditoría heurística de las 19 pantallas en computadora y celular (duplicados, consistencia, formularios, listas);
  - propuesta en frames de alta fidelidad validados por la autora en dos rondas antes de programar: diseño iterativo con la usuaria-dueña del producto;
  - capturas de antes y después en `docs/funcionalidades/028-mejoras-interfaz/capturas/`;
  - cambios medibles: la pantalla del caso pasa de unos 8.800 px a etapas cortas; el perfil, de 5 tarjetas apiladas a 4 pestañas; un solo buscador en lugar de dos campos;
  - nueva funcionalidad surgida de la validación: un enlace para que la persona afectada suba las fotos sin cuenta (CP-32, tercero y Ley 25.326).

## Otros temas ya registrados

- Metodología: desarrollo guiado por especificaciones, arnés para agentes de IA (CLAUDE.md, constitución) y trazabilidad con `Co-Authored-By`.
- Arquitectura en capas verificada con import-linter; patrón Strategy en análisis, almacenamiento, cola y sello.
- Marco normativo y supervisión humana (ADR-0017): sin veredictos, persona en el circuito y umbrales publicados.
- Entrevista con Federico Miskinich (2026-10-02) y su impacto en el informe PDF.
- Infraestructura en AWS con Terraform, despliegue continuo con OIDC, y SES en modo de prueba (solo destinatarios verificados).
- Rediseño de la interfaz (022): identidad "Visor" y lenguaje por rubro.
- Calidad: cobertura del 98 %, pylint 10/10, cantidad de pruebas.

## Secciones nuevas pedidas por la autora

- Pendiente: la autora indica qué secciones agregar y qué modificar (CP-31).
  - segunda tanda: menú según el rol, pantalla del caso en tres etapas (carga, análisis con progreso por imagen y capa, informe) y un enlace para que la persona afectada suba sus propias fotos con una declaración expresa (CP-32). Es un aporte para la cadena de custodia: cada imagen registra si vino de la computadora, del celular de quien lleva el caso o de la persona afectada;
  - decisión de diseño: separar el trabajo por etapas redujo una pantalla de unos 8.800 px a una etapa por vez, sin perder información;
  - pendiente: validar con los tutores el texto de la declaración (Ley 25.326).
  - tercera tanda (2026-10-29): inicio de sesión con ventajas reales y contraseña visible, y revisión completa a 390 px de ancho (celular).
- **Pago en el registro (032, 2026-10-29):** la autora decidió cobrar el plan al registrar un estudio jurídico o una aseguradora, simulado con Cresium (fintech argentina: cobro por transferencia a un CVU con conciliación automática, comisión desde el 0,4 %; sin API pública ni entorno de pruebas). Para el informe: es una decisión de modelo de negocio que conecta el plan con los límites del sistema (miembros, análisis, almacenamiento).
  - Implementación (ADR-0020): el proveedor de pagos es intercambiable (patrón Strategy, como el análisis y el almacenamiento); hoy un proveedor simulado genera el CVU, el alias y la referencia, y cuando haya API de Cresium se cambia solo esa pieza.
  - Seguridad: el enlace de pago lleva un token aleatorio y la base guarda solo su huella SHA-256; un registro con un correo existente genera un cobro «señuelo» igual a uno real, para no revelar qué correos están registrados (RF01 CA3).
  - Reglas de negocio nuevas: sin el pago acreditado no se invitan miembros ni se cargan casos de la organización; la aseguradora llega al Administrador recién pagada y, si se rechaza, el pago se devuelve; las invitaciones pendientes ocupan lugar del plan.
  - La landing pública lleva directo al registro con el camino y el plan elegidos (`/registro?tipo=estudio&plan=profesional`).
- **Portada pública (033, 2026-10-29):** se diseñaron dos propuestas completas (A oscura, B clara) y la autora armó la versión final combinando secciones de cada una: diseño iterativo con la dueña del producto. Para el informe: la portada comunica el problema (imágenes alteradas con IA en siniestros y juicios), la propuesta de valor y el modelo de negocio (plan personal gratuito y planes pagos para organizaciones), siempre con el descargo de que la plataforma ofrece indicios y no veredictos.
