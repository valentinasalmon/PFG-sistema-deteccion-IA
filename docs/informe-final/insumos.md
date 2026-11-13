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

- **Entorno de entrenamiento de la red neuronal (2026-10-28):**
  - se pasó de Kaggle a Google Colab gratuito (GPU T4), a elección de la autora;
  - como Colab no conserva el disco entre sesiones, el cuaderno respalda en Google Drive el resultado de cada etapa y retoma desde la última completa;
  - gracias a que el *pipeline* separa las etapas con entradas y salidas en disco, el cambio solo tocó el cuaderno, no el código;
  - Colab Pro (unos US$ 10 por mes) queda como opción si la versión gratuita no alcanza.

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
- **Pulido de UX/UI (034, 2026-10-29):** relevamiento de las 15 rutas en computadora y celular, y mockups de 49 pantallas en tres versiones validadas por la autora antes de programar (diseño iterativo con la dueña del producto). Para el informe:
  - principio rector: ninguna pantalla sin acción ni salida (se documentó un «mapa de salidas»);
  - el caso pasó de pestañas a un flujo vertical continuo (imágenes → análisis → informe), que refleja el proceso real de trabajo;
  - acceso a pantalla completa y sin el panel de marca repetido; avisos arriba y diálogos centrados con X, Esc y foco atrapado (accesibilidad, WCAG 2.1 AA);
  - ilustraciones propias de la marca en lugar de imágenes genéricas;
  - Microsoft Clarity quedará para que la autora revise el uso antes del lanzamiento (mapas de calor), con enmascarado estricto.
- **Pulido de UX/UI, segunda tanda (034, 2026-10-30):** para el informe:
  - reducción de fricción medible en pasos: la búsqueda de casos se aplica sola, sin botón; crear un caso lleva directo a cargar las fotos; «Seguí donde lo dejaste» retoma el caso activo con un clic;
  - patrón de «paleta de comandos» (Ctrl K), habitual en herramientas profesionales, adaptado al rol;
  - comparador deslizable de la foto con su mapa de niveles de error, para leer el indicio sin alternar imágenes (apoyo a la persona en el circuito, ADR-0017);
  - ningún vacío ni error sin salida: componente único con ilustración, explicación y acción;
  - Clarity solo con identificador, enmascarando toda la página; antes de activarlo, la política de privacidad debe nombrarlo (CP-37). Es un ejemplo de privacidad desde el diseño.


## Integraciones sugeridas, sin definir (2026-10-29)

- Llegaron tres sugerencias externas para la autora. Estado al 2026-10-30:
  - **Microsoft Clarity** (CP-33, funcionalidad 031): la autora lo usa para revisar la experiencia de uso antes del lanzamiento; se deja configurable en la 034 (T10), con enmascaramiento estricto y la CSP abierta solo a sus dominios.
  - **Cobro con Cresium** (CP-34): implementado como pago simulado en el registro (funcionalidad 032, ADR-0020), detrás de un proveedor intercambiable; Mercado Pago quedó descartado por ahora.
  - **Identik** (CP-35, funcionalidad 035): verificación de identidad de quien registra una aseguradora, como refuerzo de la aprobación manual. Implica datos biométricos (sensibles); sigue pendiente.
- Borrador de los capítulos del informe (AE2 y siguientes) redactado en el chat el 2026-10-29 a partir del documento de la autora, este archivo y la bitácora.

## Búsqueda de marca en el INPI (2026-10-29)

- La autora busca «evidentIA» en la base de marcas del INPI. Resultado: «EVIDENTIA» está concedida a un tercero en las clases 9 y 42 (denominativa, vence en 2036), y «EVIDENTIA ESTUDIO PERICIAL», del mismo sector, en la clase 42 (mixta). La denominación no puede registrarse en las clases del servicio (CP-36).
- Para el Capítulo VIII: la búsqueda de antecedentes cumple su función, porque detecta el conflicto antes de invertir en la marca. Es también una lección aprendida: verificar la disponibilidad del nombre antes de construir la identidad visual.


## Tercera tanda de la 034: portada, registro y privacidad (2026-10-31)

- **Iteración de diseño con la autora:** tres rondas de mockups (v1, v2 y v3 con dos direcciones), rechazos explícitos («muy feo», «el registro sigue muy mal») y una composición final armada con partes de cada dirección. Para el capítulo de metodología: el diseño se validó con prototipos antes de programarlo, y las capturas reales del sistema reemplazaron las ilustraciones porque transmitían más confianza.
- **Registro:** pasar de 4-6 pasos a 2-3 juntando los datos personales y la institución, y no volver a preguntar lo que la persona ya eligió en la portada. Es un ejemplo de reducción de fricción medible (cantidad de pasos).
- **Privacidad técnica:** la política muestra el valor concreto de cada medida (por ejemplo, bcrypt costo 12 o enlaces de 5 minutos) en lugar de frases genéricas, y separa la portada comercial (beneficios, sin proveedores) de la página técnica.
- **Observabilidad del sello:** la página pública de estado informa si el sello en Hedera funciona, sin exponer datos sensibles. Permite comprobar en producción una integración externa sin acceso al servidor.
- **Coherencia legal:** al activar Clarity, la política dejó de ser exacta (decía que no había cookies de seguimiento). Se corrigió con un texto provisorio y quedó como cuestión abierta (CP-37). Lección: cada integración nueva revisa la política de privacidad.

## Cuarta tanda de la 034 (2026-10-31)

- **Componente reutilizable de pestañas**: la organización y Mi perfil comparten `Pestanias` (patrón de pestañas de WAI-ARIA, flechas del teclado, pestaña en la dirección). Ejemplo de refactorización que reduce duplicación al aparecer el segundo uso.
- **Priorizar lo accionable**: en administración, lo que requiere una acción (aprobar aseguradoras) va antes que los indicadores; si no hay nada que hacer, ocupa una línea.
- **Tablas en el celular**: en lugar de desplazamiento horizontal, cada fila se apila como tarjeta con el nombre de cada dato. Se detectó al revisar todas las pantallas a 390 px (CA2).

## Portada: quinta tanda (2026-11-02)

- La autora simplificó la portada: menos elementos decorativos (globos, sellos, letras de fondo, ojo) y menos secciones (sin «para quién»), con las cuatro capas del análisis presentadas como una lista vertical junto a su título. Para el informe: iteración de diseño guiada por la revisión de la autora, de una portada «cargada» a una más directa.
## Prueba de concepto de la red neuronal (2026-10-30)

- El pipeline del clasificador corrió de punta a punta en Colab (GPU T4) con 10 000 imágenes, en unos 11 minutos. Resultados: AUC de prueba 0,985, exactitud 0,933, calibración por temperatura (ECE de 0,047 a 0,021), modelo ONNX idéntico al de PyTorch (diferencia 2,6 × 10⁻⁶) y 24 ms por imagen en CPU.
- Para el informe:
  - es la validación del diseño MLOps (ADR-0014): etapas separadas, respaldo en Drive, ficha generada automáticamente y registro en MLflow;
  - **las métricas de la prueba de concepto no deben presentarse como desempeño real:** una sola fuente, sin generadores no vistos ni imágenes recomprimidas. El resultado válido es el del entrenamiento completo con el conjunto propio;
  - lección aprendida: con muchos generadores y pocas imágenes por cada uno, las métricas por generador son ruido; la receta v1 usa menos generadores con más imágenes;
  - el 82 % del tiempo se va en obtener y preparar los datos, no en entrenar.
- La autora cuenta con Colab Pro por un año (suscripción a Gemini), lo que elimina el costo de GPU del presupuesto.

## Exploración de datos, receta v1 y conjunto propio (2026-10-30)

- **Exploración antes de entrenar:** cada conjunto se verifica en su revisión exacta (licencia, columnas, generadores, formatos) sin bajarlo entero, leyendo solo las columnas livianas de los Parquet. Un conjunto sin licencia verificable se excluye (CA2). Es un buen ejemplo de gobernanza de datos para el informe.
- **Atajos por tema, no solo por formato:** si se agregan fotos reales de autos dañados o de lesiones al entrenamiento sin sintéticas de las mismas escenas, el modelo aprende el tema. Por eso esas fotos solo se usan para evaluar, y la evaluación se desglosa por escena (reales y sintéticas del mismo tema).
- **No hay conjuntos públicos de lesiones con origen verificable** fotografiadas con celular: los que circulan están armados con fotos de internet. Se usa SCIN (piel fotografiada por las propias personas, con tono de piel etiquetado), fotos de conocidos con consentimiento y Fitzpatrick17k para el tono de piel.
- **Diseño del conjunto propio:** 90 prompts numerados y equilibrados (escenas, autos, luces, seis tonos de piel), el mismo prompt en todas las herramientas, versiones del prompt registradas (v1, v2 si la herramienta se niega, v3 si sale con aspecto de render) y tres variantes de cada imagen. Si una herramienta se niega más con algún tono de piel, también se registra como hallazgo.
- **Corrección metodológica:** la partición «no visto» solo tiene sintéticas; se evalúa contra las reales de prueba para que el AUC tenga sentido.
- **Robustez operativa:** el entrenamiento completo saltea las etapas ya terminadas con el mismo manifiesto y guarda los datos preparados en Drive, para tolerar los cortes de Colab sin rehacer horas de trabajo.

## Decisiones de alcance del conjunto propio y relevamiento completo de fuentes (2026-10-30)

### Decisiones de la autora

- **Sin escenas de viviendas** (CP-39): el sistema solo tiene casos automovilísticos y laborales (`TIPOS_CASO` del backend). Se quitaron de la especificación (010, CA12).
- **Sin la versión de WhatsApp** en el conjunto propio: las fotos de un caso las sube la persona afectada desde el enlace de carga, así que llegan como **original, captura o imagen generada con IA**. Se evalúa en dos versiones (original y captura). La aumentación de entrenamiento sigue incluyendo recompresión JPEG, que cubre capturas, cámaras de celular y fotos que pasaron antes por alguna aplicación. Para el informe: es un ejemplo de cómo el diseño del sistema (el enlace de carga de la funcionalidad 028) cambia las condiciones que hay que medir en el modelo.

### Relevamiento de fuentes: qué se encontró y qué se hizo con cada una

Investigación completa en `docs/investigacion/2026-10-30-conjuntos-de-datos-imagenes-sinteticas.md`.

| Fuente | Tipo | Licencia | Decisión | Motivo |
|---|---|---|---|---|
| Community Forensics *Small* | Reales y sintéticas, cientos de generadores abiertos | CC BY-NC-SA 4.0 | Entrenamiento (base) | Ya probada en la prueba de concepto |
| OpenFake | Generadores comerciales recientes | Cambia entre revisiones (CC BY-SA / BY-NC / BY-NC-SA) | Entrenamiento y no vistos | Fijar una revisión: ejemplo de que la licencia es parte de la versión de los datos |
| Treasure, AIGenImages2026, MLLM-Generated | Generadores de 2025 y 2026 (GPT-image, Midjourney v7, Gemini, FLUX.2) | A verificar | Candidatos a no vistos | Medir generalización a herramientas comerciales nuevas |
| ShareGPT-4o-Image | Solo GPT-4o | Sin licencia encontrada | Solo si se verifica | CA2: sin licencia verificable no se usa |
| TrueFake | Imágenes compartidas en redes sociales | A verificar | Ya no es prioritaria | Su aporte era la recompresión de redes, que dejó de medirse |
| Semi-Truths | Ediciones localizadas | «cc» sin variante | Solo para medir ediciones (CA13) | La capa 4 no es responsable de ediciones parciales |
| VISION y FODB | Fotos reales de celulares, originales y reenviadas | CC BY-SA 4.0 / a verificar | Descartadas para evaluar | Escenas ajenas al sistema (regla de oro) y la versión WhatsApp ya no se mide |
| CarDD | Fotos reales de autos dañados | Investigación no comercial | Reales del conjunto propio (escenas 1 a 3) | Misma escena que las generadas; no se usa para entrenar |
| SCIN (Google y Stanford) | Fotos de piel sacadas por las personas, con tono de piel | Licencia de uso de datos SCIN, investigación | Reales de lesiones (escena 5), repartidas por tono | Único conjunto con fotos caseras de origen verificable y tono etiquetado |
| Fitzpatrick17k | Fotos clínicas con tipo de piel 1 a 6 | CC BY-NC-SA 3.0 | Complemento para el tono de piel | Origen documentado, anterior a 2022 |
| MOCS / ConstructionSite | Fotos reales de obras | CC BY-NC 4.0 | Reales de lugares de trabajo (escena 6) | Misma escena que las generadas |
| SODA | Obras con trabajadores y herramientas | Sin verificar | Quizás, escena 7 | Pendiente de licencia |
| Heridas de Kaggle, Roboflow y rupeshsah/wound | Heridas por tipo | Varias | **Descartadas** | Fotos juntadas de internet: origen no verificable (podrían ser generadas) y, en un caso, tamaño fijo de 350 × 350 que es un atajo de formato |
| HOUSE DAMAGE LEVEL y otros de viviendas | Daños en casas | CC BY 4.0 | **Fuera de alcance** | Sin casos de viviendas en el sistema (CP-39) |
| GenImage, WildFake, Chameleon | Detección de sintéticas | Sin licencia o a pedido | Descartados por ahora | Generadores viejos, sesgo de JPEG documentado o licencia no verificable |

### Hallazgos para el informe

- **Licencias:** casi todas son no comerciales y algunas cambian entre revisiones. Alcanza para el proyecto final; una versión comercial requeriría reentrenar con datos de licencia compatible.
- **Atajos:** además del atajo de formato («Fake or JPEG?»), existe el **atajo de tema**. Si se suman fotos reales de una escena sin sintéticas de la misma escena, el modelo aprende el tema. Por eso las fotos reales de las escenas del sistema solo se usan para evaluar, y la evaluación se desglosa por escena.
- **Equidad:** las lesiones se generan y se evalúan en seis tonos de piel (escala de Fitzpatrick aproximada). Si una herramienta se niega a generar con algún tono más que con otros, se registra como hallazgo.
- **Gobernanza de datos:** antes de usar un conjunto se verifica en su revisión exacta, sin bajarlo entero; lo que no tiene licencia verificable queda excluido y anotado.
- **Herramienta de generación más probable en casos reales:** Meta AI, porque está dentro de WhatsApp, Instagram y Facebook. Se genera desde la web para tener el archivo original.

## Exploración de datos sin agotar la memoria (2026-11-03)

- La primera ejecución de la exploración en Colab terminó con el código -9: el proceso se quedó sin memoria al bajar un bloque completo de imágenes solo para mirar 24. Medido con un Parquet de prueba, pyarrow lee el bloque entero de la columna aunque se pidan pocas filas.
- Solución: consultar primero el tamaño del bloque en los metadatos del Parquet (unos KB) y omitir la muestra si es grande, guardar los resultados después de cada conjunto y correr cada conjunto en un proceso aparte. Para el informe: ejemplo de diseño robusto ante límites del entorno de ejecución y de diagnóstico a partir del cuaderno guardado.

## Resultado de la exploración y receta v1 (2026-11-04)

- De ocho conjuntos candidatos, dos quedaron para entrenar (Community Forensics y OpenFake). Los demás quedaron fuera por formato (carpetas de imágenes o `.tar` en lugar de Parquet), por licencia no verificable (Semi-Truths, CA2) o por acceso pendiente (ConstructionSite). Tabla completa en `docs/red-neuronal/04-datos.md`.
- **Sesgo de tamaño y formato medido:** en OpenFake las fotos reales tienen un lado menor mediano de 3 349 px (JPEG, calidad 95) y las sintéticas de unos 880 px (PNG, JPEG, WebP). En Community Forensics, las sintéticas son PNG de 512 × 512. Es la evidencia concreta de por qué hace falta la normalización anti-atajos.
- **Generadores no vistos:** la familia de Google (Imagen 4, Imagen 3, Nano Banana 2), que usa Gemini. Permite medir la generalización a una herramienta comercial y demostrar el reentrenamiento (1.0.0 → 1.1.0).
- **Lección de ingeniería de datos:** una propuesta automática de receta no garantiza que los datos alcancen; se verificó la disponibilidad real por generador antes de fijar cantidades. Y los límites del entorno (RAM y disco de Colab) obligaron a decisiones concretas: búfer de mezcla por fuente y borrado de las imágenes crudas una vez preparadas.
- Receta v1: 19 000 reales y 19 000 sintéticas, 290 generadores en total.

## Hedera y Cresium: estado real al 2026-11-02

- **Hedera**: la integración está completa (SDK oficial, confirmación en el *mirror node*, reintentos cada 15 minutos, huella de cada versión desplegada), pero se valida recién con la prueba de la autora en *testnet*. Para el informe: distinguir «implementado y probado con dobles de prueba» de «probado contra la red real».
- **Cresium**: tiene API de cobros con CVU por pedido y avisos firmados. El diseño con proveedor intercambiable (ADR-0020) deja el cobro real como un agregado acotado; depende de los precios (CP-38) y de la cuenta. Riesgo principal del cobro por transferencia: avisos falsificados, que se mitigan con la firma HMAC, la comprobación del monto y la conciliación de respaldo.
- **CP-20**: una huella SHA-256 simple de un correo no lo anonimiza (se revierte probando correos conocidos); la minimización correcta sería una huella con clave secreta (HMAC). Buen ejemplo para la sección de privacidad.

## Hedera probado en producción (2026-11-02)

- El sello de tiempo en Hedera *testnet* funciona en producción: la página pública `/estado` lo informa con la fecha del último sello confirmado por el *mirror node*. Sirve como evidencia para el informe (captura de `/estado` y de un mensaje en HashScan).
- Lección de operación: las guías con bloques de código se copian enteras; para tareas de la autora con secretos conviene ofrecer primero la consola web.

## Arnés para el trabajo asistido por IA (036, 2026-11-02)

- **Qué es**: el sistema que rodea al agente de IA para que trabaje de forma confiable. Tiene cinco partes:
  - **guías**: `CLAUDE.md`, constitución, especificación, comandos y skills;
  - **sensores**: ganchos, pre-commit, import-linter, integración continua y `/estado`;
  - **memoria**: bitácora, ADR, cuestiones abiertas, Trello e insumos;
  - **persona en el circuito**: la autora revisa, integra, decide y carga los secretos;
  - **mejora continua**: el registro de cambios.
  - Detalle en `docs/arnes/README.md`.
- **Hallazgo**: varias reglas importantes eran solo texto (no tocar secretos) y los comandos del flujo quedaron desactualizados dos semanas después de cambiar el reparto del trabajo. **Un arnés sin sensores depende de la memoria del modelo**; la funcionalidad 036 convirtió la regla de secretos en un gancho que bloquea, y en la primera prueba bloqueó un comando del propio agente.
- **Evolución**: el registro de cambios muestra 19 cambios del arnés entre el 2026-10-08 y el 2026-11-02, cada uno motivado por un problema real. Por ejemplo:
  - el reparto del trabajo se reescribió;
  - Trello pasó a actualizarse sin pedirlo;
  - la red neuronal se documenta aparte;
  - las integraciones externas se prueban contra el servicio real.
- **Números del proceso**: 282 commits, 238 con co-autoría de IA (84 %), 67 Pull Requests integrados, 30 especificaciones, 48 entradas de bitácora, 18 ADR y 724 pruebas automáticas.
- **Episodio para el informe y la exposición**: al commitear la 036, el gancho de secretos bloqueó un commit del propio agente (falso positivo: el mensaje nombraba un archivo secreto). El agente intentó corregir el gancho y Claude Code se lo impidió por ser auto-modificación de un control. La corrección quedó como propuesta para la autora. Muestra que el arnés protege sus propios controles y que la última palabra es humana.

## Depuración de los datos de entrenamiento (2026-11-04)

- No se usan los conjuntos completos: se toma una muestra de archivos con revisión fija y se depura en cada etapa (tabla en `docs/red-neuronal/04-datos.md`).
- Se agregaron dos filtros contra atajos: **excluir los generadores que no hacen fotos** (anime, historieta, pixel art, logos, maquetas, fractales: 66 en total), porque las reales son fotos y el modelo aprendería «ilustración = IA»; y **descartar las imágenes de menos de 256 px sin agrandar nunca** al normalizar, porque la interpolación deja marcas propias.
- Limitaciones declaradas: no se detectan casi duplicados, no se filtran las reales de OpenFake que no son fotos y los temas de reales y sintéticas difieren entre conjuntos.
- Incidente de los cuadernos (2026-11-04): al cuaderno de entrenamiento completo le faltaba la celda de instalación; las pruebas automáticas cubren el paquete, pero no los cuadernos de Colab, que solo se validaban por sintaxis. Se agregó una verificación de dependencias al inicio del cuaderno. Para el informe: límite de la integración continua y por qué el paso a paso en Colab tiene su propia comprobación.

## Verificación de identidad de aseguradoras (035, 2026-11-04)

- **Qué resuelve**: antes, el Administrador solo podía comprobar a mano que quien registraba una aseguradora trabajara en ella. Con la 035, el Referente verifica su identidad (DNI + rostro con prueba de vida) y la aprobación queda bloqueada hasta que esté aprobada (RN41).
- **Privacidad por diseño**: la plataforma guarda solo el resultado, el motivo y una referencia del proveedor; no tiene dónde guardar biometría. Los datos biométricos son sensibles (Ley 25.326) y quedan del lado del proveedor.
- **Proveedor intercambiable**: igual que el cobro (ADR-0020), con una versión simulada que permite mostrar el flujo completo antes de tener el contrato.
- **Identik** (proveedor argentino): ofrece redirección o iFrame y resultado por *webhook*. Precios publicados al 2026-11-04: firma electrónica desde USD 0,27 por documento (pack de 1.000) y verificación biométrica USD 0,80 por firma; firma digital $ 21.990 por documento. La verificación aparte se cotiza a medida. RENAPER requiere credencial propia del registro.
- **Decisiones abiertas** para el informe: CP-41 (verificación aparte o dentro de la firma electrónica) y CP-42 (firmar el informe PDF o dejarlo como trabajo futuro).

## Índice de calidad y usabilidad (018, 2026-11-04)

- **Fórmula del QI** (propuesta para CP-04): QI = 0,20·Cb + 0,15·Cf + 0,15·E + 0,10·K + 0,10·D + 0,30·U. Los componentes son la cobertura del backend y del frontend, pylint, la complejidad ciclomática acotada, el código sin duplicar y el SUS. Se mide con `backend/herramientas/indice_calidad.py`.
- **Medición provisoria**: 0,977 sin SUS. Valores: backend 97,5 %, frontend 92,4 %, pylint 10, ninguna función con complejidad mayor a 10, 0,1 % de duplicación.
- **Hallazgo metodológico**: un índice dominado por métricas de código que ya están al máximo puede ocultar una mala usabilidad (con estos valores, alcanzaría un SUS de 23). Conviene informar el SUS y la tasa de éxito aparte, con sus propios objetivos.
- **Prueba de usabilidad**: protocolo con 8 tareas del flujo principal, SUS en español (Brooke, 1996) y al menos 5 participantes del dominio (Nielsen y Landauer, 1993). Resultados pendientes.

## Revisión integral de la interfaz (037, 2026-11-05)

- **Método**: recorrido automatizado con capturas en dos anchos (1440 y 390 px), por perfil (abogado, aseguradora, administrador y visitante), más un script que detecta contenido fuera del ancho. Encontró 21 problemas; 17 se corrigieron y 4 quedaron como decisiones de la autora.
- **Hallazgo de diseño**: el mismo motor sirve a dos rubros, pero el vocabulario era único («caso»). Para una aseguradora el objeto de trabajo es el *siniestro*; se resolvió con un diccionario por perfil, sin tocar los datos ni las direcciones.
- **Hallazgo de coherencia**: la portada y el acceso tenían una identidad (verde bosque y lima) y el sistema otra (azul). Se unificaron con una maqueta previa de dos alternativas sobre las pantallas reales.
- **Informe**: el descargo de que no emite veredictos estaba solo al final; pasó a la primera página, que es la que se lee siempre (ADR-0017).

## Verificación visual automatizada (037, 2026-11-05)

- **Problema**: al unificar el tamaño de las tarjetas de acceso (alto fijo, pedido de la autora), el agente verificó las pantallas que motivaron el cambio y no las demás que usan la misma tarjeta; el pago, la elección del plan y el resultado del pago quedaron cortados. Lo detectó la autora.
- **Lección**: un estilo compartido es una dependencia: cambiarlo exige revisar a todos sus usuarios, igual que una función compartida exige correr las pruebas de quienes la llaman. Las pruebas unitarias de la interfaz (Vitest con jsdom) no ven la maquetación.
- **Solución en el arnés**: un sensor de diseño con Playwright que mide, en 1440 y 390 px, desplazamiento horizontal, contenido cortado, contenido escondido en contenedores con desplazamiento propio y controles fuera de la pantalla, aplicado en cada captura de los recorridos de punta a punta. Se validó reintroduciendo el error: el sensor lo informa («muestra 672 px de 1308 px») y no marca nada con la corrección.
- **Otras decisiones de la tanda**: el pago es una «caja» y usa la tarjeta a todo el ancho; la aseguradora se elige con un cuadro combinado accesible (WAI-ARIA combobox) en lugar de una lista de tarjetas; el Administrador recibe un correo cuando una aseguradora paga; el caso guía el siguiente paso (cargar → analizar → informe) con un cierre al pie del análisis.

## Capa 4 en el análisis: el clasificador ONNX en el backend (012, 2026-11-06)

- **Mismo código en la evaluación y en producción.** El backend instala el paquete `clasificador` sin dependencias y usa su `PredictorOnnx`: no hay una segunda implementación del preprocesamiento que pueda desviarse. Una prueba automática verifica que la probabilidad del backend es igual a la de la evaluación (ADR-0015). El servidor no instala PyTorch ni usa GPU.
- **Lectura publicada de la probabilidad (ADR-0017).** Por debajo de 50 % la capa no aporta indicios; desde ahí el nivel es la probabilidad calibrada, con tope de 90 (el 100 queda para C2PA, RN28). La conclusión aclara siempre tres limitaciones: no detecta ediciones parciales, puede fallar con generadores que no vio y una probabilidad baja no indica que la foto sea real. Es la traducción directa de los resultados de la 010: AUC 0,961 con generadores conocidos, 0,938 con la familia de Google no vista y solo 10 % de detección en el conjunto propio de choques.
- **Integridad y reproducibilidad del modelo.** Versión fija, huella SHA-256 verificada antes de usarlo (ADR-0014) y, en cada resultado, versión, huella del ONNX, huella del manifiesto de entrenamiento, commit y versión de ONNX Runtime (RN29). Cambiar de versión es cambiar un parámetro; los análisis anteriores conservan la suya.
- **Tolerancia a fallas (RN26).** Sin modelo configurado, con el registro caído o con un archivo alterado, la capa queda «No disponible» con el motivo y las otras tres se presentan igual. Por eso la funcionalidad se pudo integrar antes de publicar el modelo.
- **Pruebas sin red ni PyTorch.** Un ONNX diminuto con el mismo contrato que el real (sigmoide del brillo medio) permite probar la carga, la caché, las huellas y la capa en milisegundos.
- **Hallazgo de despliegue.** El script que arma el `.env` del servidor copia solo las variables que nombra; sin agregarlas, los parámetros del Parameter Store nunca habrían llegado a la aplicación. Se detectó al escribir la guía de activación, no con las pruebas: refuerza la regla de probar las integraciones contra el servicio real.

## Entrenamiento completo de la red (2026-11-05)

- Con 35 000 imágenes de 210 generadores: **AUC de prueba 0,961, F1 0,904, ECE 0,02** (validación, tras calibrar). Cumple tanto el AUC ≥ 0,90 de la especificación como el F1 ≥ 0,85 del informe (CP-07).
- **Generalización:** con la familia de Google que nunca vio (Imagen 4, Imagen 3, Nano Banana 2), AUC 0,938.
- **Límite en condiciones reales:** con imágenes de choques generadas por la autora con ChatGPT, Gemini y Copilot, detecta 5 de 49 con el umbral 0,5. Es el resultado más importante para el informe: los detectores entrenados con conjuntos públicos rinden mucho peor con las herramientas comerciales actuales y con escenas que no vieron. Justifica la capa 4 como un indicio más y no un veredicto (RN27), y el ciclo de reentrenamiento (CA18).
- Generadores más difíciles en la prueba: VQDiffusion y GigaGAN (AUC ~0,62-0,67), Midjourney 6 y FLUX 1.1 Pro (detecta el 54-68 %).

## Flujos del día a día (038, 2026-11-06)

- **Aprobación de estudios**: la autora decidió que ninguna organización se presenta como activa antes de la revisión del Administrador; se extendió RN38 a los estudios jurídicos sin exigirles la verificación de identidad de las aseguradoras.
- **Redirección después de iniciar sesión**: un enlace con consulta (`?etapa=analisis`) perdía la consulta al pasar por el inicio de sesión. Es un error típico de las rutas protegidas en aplicaciones de una sola página; se corrigió conservando la dirección completa y, para Google (que sale del sistema), guardándola en el navegador.
- **QR de un solo uso**: atar el enlace al primer dispositivo al abrir la página falló en la prueba porque el navegador puede repetir la consulta; se ata con la primera foto subida. Lección: los controles de un solo uso tienen que tolerar repeticiones.
- **Diseño**: agrandar un contenedor no alcanza; el contenido tiene que reorganizarse (dos columnas, índice, largo de línea). Se registró como criterio de revisión visual.


## Correcciones de producción (039, 2026-11-10)

- **Probar en producción encuentra lo que el entorno local no**: el flujo de aprobación de estudios funcionaba en local, pero en producción el correo dependía de SES en modo de prueba (solo entrega a direcciones verificadas). Lección: las integraciones externas se validan contra el servicio real, como pide el arnés.
- **Un enlace tiene que cumplir lo que su rótulo promete**: el QR «Análisis detallado» llevaba al análisis plegado; se agregó un parámetro que lo despliega entero.
- **Vocabulario por destinatario**: los correos usan «caso» o «siniestro» según el perfil de quien los recibe.
- **Verificación visual automatizada**: el sensor de diseño y los recorridos de punta a punta pasaron a la integración continua, con un entorno completo (base, Redis, backend y frontend) levantado en GitHub Actions; deja de depender de que alguien los corra a mano.

## Dominio propio (040, 2026-11-13)

- **Dominio**: `evidentiaa.com.ar`. `evidentia.com` estaba tomado y las variantes libres en `.com` eran dominios premium; el `.com.ar` era accesible y en pesos.
- **DNS como código**: la zona de Route 53, los registros de DKIM y DMARC y el registro del servidor se crean con Terraform; la única acción manual es delegar el dominio en NIC Argentina. Evita errores al copiar registros largos y deja el DNS versionado.
- **Correo**: verificar el dominio entero en SES (DKIM) en lugar de direcciones sueltas mejora la entrega y es requisito práctico para pedir la salida del modo de prueba.
