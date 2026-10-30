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
  - enlace de un solo uso (15 minutos, 30 fotos, solo carga en ese caso);
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

- **Sin escenas de viviendas** (CP-33): el sistema solo tiene casos automovilísticos y laborales (`TIPOS_CASO` del backend). Se quitaron de la especificación (010, CA12).
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
| HOUSE DAMAGE LEVEL y otros de viviendas | Daños en casas | CC BY 4.0 | **Fuera de alcance** | Sin casos de viviendas en el sistema (CP-33) |
| GenImage, WildFake, Chameleon | Detección de sintéticas | Sin licencia o a pedido | Descartados por ahora | Generadores viejos, sesgo de JPEG documentado o licencia no verificable |

### Hallazgos para el informe

- **Licencias:** casi todas son no comerciales y algunas cambian entre revisiones. Alcanza para el proyecto final; una versión comercial requeriría reentrenar con datos de licencia compatible.
- **Atajos:** además del atajo de formato («Fake or JPEG?»), existe el **atajo de tema**. Si se suman fotos reales de una escena sin sintéticas de la misma escena, el modelo aprende el tema. Por eso las fotos reales de las escenas del sistema solo se usan para evaluar, y la evaluación se desglosa por escena.
- **Equidad:** las lesiones se generan y se evalúan en seis tonos de piel (escala de Fitzpatrick aproximada). Si una herramienta se niega a generar con algún tono más que con otros, se registra como hallazgo.
- **Gobernanza de datos:** antes de usar un conjunto se verifica en su revisión exacta, sin bajarlo entero; lo que no tiene licencia verificable queda excluido y anotado.
- **Herramienta de generación más probable en casos reales:** Meta AI, porque está dentro de WhatsApp, Instagram y Facebook. Se genera desde la web para tener el archivo original.

