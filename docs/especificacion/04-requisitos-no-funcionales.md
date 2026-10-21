# 4. Requisitos no funcionales

Los requisitos no funcionales se agrupan según las características de calidad del producto de la norma ISO/IEC 25010. Cada uno incluye criterios de aceptación verificables.

## Resumen

| Característica (ISO/IEC 25010) | Requisitos |
|---|---|
| Seguridad | RNF01 – RNF07 |
| Cumplimiento legal y privacidad | RNF08 – RNF09 |
| Usabilidad | RNF10 – RNF11 |
| Compatibilidad | RNF12 |
| Eficiencia de desempeño | RNF13 – RNF14 |
| Fiabilidad | RNF15 – RNF16 |
| Mantenibilidad | RNF17 – RNF21 |
| Portabilidad | RNF22 |
| Adecuación funcional del análisis | RNF23 – RNF24 |

---

## Seguridad

### RNF01 — Autenticación y gestión de sesiones
**Prioridad:** Debe

- **CA1:** Las contraseñas se almacenan exclusivamente como hash bcrypt con factor de costo de 12 o superior.
- **CA2:** La política de contraseñas exige al menos 10 caracteres, con al menos una letra y un número, y rechaza las contraseñas presentes en una lista de contraseñas comunes.
- **CA3:** Tras 5 intentos fallidos consecutivos, la cuenta se bloquea durante 15 minutos y se notifica al titular.
- **CA4:** La sesión expira tras 30 minutos de inactividad y, en todos los casos, a las 8 horas de iniciada.
- **CA5:** Los tokens de verificación, recuperación e invitación se firman con itsdangerous, tienen vencimiento y son de un solo uso.
- **CA6:** El identificador de sesión se regenera al iniciar sesión.

### RNF02 — Protección de las comunicaciones
**Prioridad:** Debe

- **CA1:** Todo el tráfico se sirve por HTTPS con TLS 1.2 o superior; las solicitudes HTTP se redirigen a HTTPS y se envía la cabecera HSTS.
- **CA2:** Las cookies de sesión tienen los atributos `Secure`, `HttpOnly` y `SameSite=Strict`.
- **CA3:** Toda solicitud que modifica datos exige un token CSRF válido.
- **CA4:** Las respuestas incluyen las cabeceras `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy` y `X-Frame-Options`.

### RNF03 — Protección de los datos almacenados
**Prioridad:** Debe

- **CA1:** El bucket de S3 es privado, tiene activado el bloqueo de acceso público, el cifrado en reposo y el versionado.
- **CA2:** Las imágenes e informes solo se entregan mediante URL firmadas con vencimiento de 5 minutos o menos, emitidas tras verificar el permiso del usuario.
- **CA3:** Las credenciales y secretos se leen de variables de entorno (archivo `.env` en el servidor) y nunca se incluyen en el repositorio; la integración continua verifica su ausencia.
- **CA4:** Las credenciales de AWS de la aplicación aplican el principio de mínimo privilegio, limitadas al bucket y a los servicios utilizados.

### RNF04 — Validación de entradas
**Prioridad:** Debe

- **CA1:** Todas las entradas de la API se validan en el servidor contra un esquema, con independencia de las validaciones del frontend.
- **CA2:** El acceso a la base de datos se realiza exclusivamente mediante el ORM o consultas parametrizadas.
- **CA3:** Los archivos cargados se validan por su firma binaria, se decodifican con una biblioteca de imágenes para descartar contenido malformado, se almacenan con un nombre generado por el sistema y nunca se ejecutan.
- **CA4:** El sistema supera las verificaciones correspondientes al OWASP Top 10 mediante análisis estático de seguridad en la integración continua.

### RNF05 — Control de acceso
**Prioridad:** Debe · **Reglas:** RN13, RN20, RN35

El acceso se controla en tres niveles: rol del sistema (Usuario o Administrador), rol en la organización (Referente o Miembro) y permiso sobre el caso (Responsable, Colaborador o Lector).

- **CA1:** Toda ruta de la API está protegida por un decorador que declara el rol o permiso requerido; una ruta sin declaración explícita se considera un defecto detectado por las pruebas.
- **CA2:** Ante la falta de permiso sobre un recurso existente, la API responde 404, de modo que no se revele su existencia.
- **CA3:** Las pruebas automatizadas verifican, para cada operación sobre casos, el comportamiento con cada nivel de permiso y sin permiso.
- **CA4:** El Administrador no puede acceder a casos, imágenes ni informes por ninguna ruta.
- **CA5:** El frontend oculta las acciones no permitidas, pero la autorización se decide siempre en el servidor.

### RNF06 — Registro de auditoría
**Prioridad:** Debe · **Reglas:** RN34

Toda acción relevante queda registrada con fines de trazabilidad legal. No se incluye una interfaz de consulta.

- **CA1:** Se registran: inicios y cierres de sesión (exitosos y fallidos), cambios de cuenta, operaciones sobre organizaciones y membresías, operaciones sobre casos, imágenes, accesos e informes, descargas, análisis, prórrogas, destrucciones y consultas del Administrador.
- **CA2:** Cada entrada contiene: fecha y hora en UTC, identificador del usuario, dirección IP, acción, tipo e identificador del recurso, resultado y detalle de los cambios.
- **CA3:** El registro es de solo inserción: la aplicación no dispone de operaciones para modificar ni eliminar entradas.
- **CA4:** El registro no almacena contraseñas, tokens ni el contenido de imágenes o informes.
- **CA5:** Al eliminarse una cuenta, sus entradas se conservan con el usuario anonimizado.
- **CA6:** Las entradas se conservan durante **5 años** y luego se eliminan (decisión CP-05).
- **CA7:** Los intentos de inicio de sesión fallidos registran el correo intentado, aunque no corresponda a ninguna cuenta, para poder detectar ataques.
- **CA8:** Si una entrada no puede guardarse, la acción que la origina se cancela: no hay acciones sin rastro en la auditoría.

### RNF07 — Integridad de la evidencia
**Prioridad:** Debe · **Reglas:** RN23, RN29

- **CA1:** La huella SHA-256 de cada imagen se calcula al recibirla y se verifica nuevamente antes de cada análisis.
- **CA2:** Los archivos originales nunca se modifican; las vistas previas y los mapas ELA se almacenan como archivos derivados independientes.
- **CA3:** El informe incluye la huella de cada imagen analizada y, cuando existe, la referencia del sello de tiempo en Blockchain Federal Argentina.

---

## Cumplimiento legal y privacidad

### RNF08 — Cumplimiento de la Ley N.° 25.326
**Prioridad:** Debe · **Reglas:** RN04, RN30 – RN34

- **CA1 (consentimiento):** El registro exige el consentimiento expreso e informado, y se conserva la evidencia de la versión aceptada.
- **CA2 (minimización):** Solo se solicitan los datos necesarios para la prestación; no se solicitan matrículas, DNI ni domicilio.
- **CA3 (calidad y destrucción):** Los datos se destruyen cuando dejan de ser necesarios, según la política de retención de RN30 – RN33 (art. 4, inc. 7).
- **CA4 (derechos del titular):** Se garantizan el acceso (RF09), la rectificación (RF07) y la supresión (RF08, RF32).
- **CA5 (datos sensibles):** Las imágenes se tratan como información de máxima confidencialidad por la posibilidad de contener datos de salud (art. 2 y art. 7).
- **CA6 (transferencia internacional):** Los datos se alojan en la región de AWS de Irlanda (Unión Europea). La documentación del proyecto debe fundamentar que se trata de una jurisdicción con nivel de protección adecuado, conforme al art. 12 y la normativa de la Dirección Nacional de Protección de Datos Personales.
- **CA7 (documentación):** El sistema publica los Términos de Uso y la Política de Privacidad, versionados y accesibles desde todas las pantallas.

### RNF09 — Aislamiento de la información entre espacios
**Prioridad:** Debe

- **CA1:** Ninguna consulta de la capa de repositorios devuelve casos sin aplicar el filtro de permisos del usuario solicitante.
- **CA2:** Las rutas de los objetos en S3 no son predecibles y no contienen datos personales.

---

## Usabilidad

### RNF10 — Facilidad de uso para usuarios no técnicos
**Prioridad:** Debe

- **CA1:** Un usuario sin capacitación previa completa el flujo "crear caso, cargar imágenes, analizar y descargar el informe" sin asistencia; se valida con pruebas de usabilidad con al menos 5 participantes del dominio y una tasa de éxito de 80 % o superior.
- **CA2:** Los mensajes de error indican qué ocurrió y cómo resolverlo, en lenguaje no técnico.
- **CA3:** Toda acción destructiva o irreversible exige confirmación explícita.
- **CA4:** La interfaz y los informes están íntegramente en español rioplatense formal.

### RNF11 — Accesibilidad
**Prioridad:** Debería

- **CA1:** La interfaz cumple el nivel AA de las pautas WCAG 2.1, verificado con herramientas automáticas sin errores críticos.
- **CA2:** Toda la funcionalidad es operable con teclado y los indicadores de estado no dependen solo del color.

---

## Compatibilidad

### RNF12 — Navegadores y dispositivos
**Prioridad:** Debe

- **CA1:** El sistema funciona sin instalación local en Chrome 90+, Firefox 88+, Edge 90+ y Safari 14+.
- **CA2:** La interfaz es utilizable en pantallas desde 360 px de ancho, sin desplazamiento horizontal.

---

## Eficiencia de desempeño

### RNF13 — Tiempos de respuesta
**Prioridad:** Debería **[PROPUESTA]**

- **CA1:** Las operaciones de consulta y gestión responden en menos de 500 ms en el percentil 95, sin contar la transferencia de archivos.
- **CA2:** El análisis de una imagen de hasta 20 MB a través de las cuatro capas finaliza en menos de 60 segundos en la instancia de producción.
- **CA3:** La carga de solicitudes no queda bloqueada durante un análisis, ya que este se ejecuta en un proceso de trabajo independiente.

### RNF14 — Capacidad
**Prioridad:** Debería **[PROPUESTA]**

- **CA1:** El sistema soporta 50 usuarios concurrentes y 5 análisis simultáneos en cola en una única instancia EC2 sin degradar CA1 de RNF13.

---

## Fiabilidad

### RNF15 — Disponibilidad y respaldo
**Prioridad:** Debe

- **CA1:** La disponibilidad objetivo es de 99 % mensual, excluidas las ventanas de mantenimiento anunciadas.
- **CA2:** La base de datos se respalda diariamente en S3 cifrado; los respaldos se conservan 30 días y luego se eliminan automáticamente.
- **CA3:** El punto de recuperación objetivo (RPO) es de 24 horas y el tiempo de recuperación objetivo (RTO) es de 8 horas; el procedimiento de restauración está documentado y se prueba al menos una vez antes de la entrega.

### RNF16 — Tolerancia a fallos del procesamiento
**Prioridad:** Debe

- **CA1:** La falla de una capa de análisis, del sellado en Blockchain Federal Argentina o del envío de correo no interrumpe el resto del procesamiento.
- **CA2:** Las tareas en segundo plano se reintentan hasta 3 veces con espera creciente antes de marcarse como fallidas.

---

## Mantenibilidad

### RNF17 — Arquitectura en capas
**Prioridad:** Debe

- **CA1:** El backend se organiza en las capas Rutas, Servicios, Repositorios y Modelos; cada capa solo depende de la inmediatamente inferior.
- **CA2:** Las rutas no contienen lógica de negocio ni acceso directo a la base de datos; los servicios no dependen de objetos de Flask como `request`.
- **CA3:** Se aplican los patrones: Factory y Strategy para la configuración por entorno; Repository para el acceso a datos; Service Layer para la lógica de negocio; Decorator para el control de acceso; Strategy para las capas de análisis y el sellado de tiempo.
- **CA4:** Una prueba automatizada de arquitectura verifica que no existan importaciones que violen la dirección de dependencias.

### RNF18 — Extensibilidad
**Prioridad:** Debe

- **CA1:** Incorporar una nueva capa de análisis requiere únicamente implementar la interfaz común de capas y registrarla, sin modificar las capas existentes ni el servicio de análisis.
- **CA2:** Reemplazar el proveedor de correo, de almacenamiento o de sellado de tiempo requiere únicamente una nueva implementación de su interfaz.

### RNF19 — Calidad del código
**Prioridad:** Debe

- **CA1:** Las pruebas unitarias alcanzan una cobertura de líneas de 80 % o superior, medida con coverage.py en el backend y con Vitest en el frontend.
- **CA2:** El Índice de Calidad del Software (QI) es de 0,75 o superior al cierre del proyecto, calculado según la fórmula **[A DEFINIR]** (ver CP-04).
- **CA3:** flake8 no reporta errores y pylint alcanza una puntuación de 8,5 o superior **[PROPUESTA]**.
- **CA4:** El frontend no presenta errores de ESLint.

### RNF20 — Integración continua y control de versiones
**Prioridad:** Debe

- **CA1:** Cada envío al repositorio ejecuta en GitHub Actions el análisis estático, las pruebas, la medición de cobertura y la verificación de los mensajes de commit.
- **CA2:** Una integración no puede fusionarse si alguna verificación falla o la cobertura baja del umbral.
- **CA3:** Los mensajes de commit siguen la especificación Conventional Commits con tipos y descripciones en español (por ejemplo, `funcionalidad(casos): agregar filtro por estado`), validados automáticamente.
- **CA4:** Cada integración en `main` que pasa las verificaciones se despliega automáticamente en la EC2; si la versión nueva no responde, se restablece la anterior (CP-06, ADR-0016).

### RNF21 — Idioma del código y de la documentación
**Prioridad:** Debe

- **CA1:** Los identificadores del código propio (módulos, clases, funciones, variables, tablas y columnas), los comentarios, las cadenas de documentación, los mensajes de commit, los nombres de ramas y la documentación están en español.
- **CA2:** Se exceptúan los nombres impuestos por bibliotecas y protocolos externos (por ejemplo, `db.Model`, los métodos HTTP y los tipos MIME).
- **CA3:** Los identificadores no utilizan tildes ni la letra ñ, que se reemplaza por `ni` (por ejemplo, `anio`), para evitar problemas de codificación en herramientas.
- **CA4:** Todo módulo, clase y función pública tiene una cadena de documentación que explica su propósito.

---

## Portabilidad

### RNF22 — Configuración por entorno y despliegue
**Prioridad:** Debe

- **CA1:** La aplicación se configura para los entornos de desarrollo, pruebas y producción mediante una fábrica de configuración seleccionada por una variable de entorno.
- **CA2:** El entorno de desarrollo se levanta con un único comando mediante contenedores (PostgreSQL, Redis y almacenamiento compatible con S3).
- **CA3:** La producción se ejecuta en una instancia EC2 de la región de Irlanda detrás de Nginx y Gunicorn.

---

## Adecuación funcional del análisis

### RNF23 — Explicabilidad y prudencia de los resultados
**Prioridad:** Debe · **Reglas:** RN27, RN28

- **CA1:** Todo resultado presentado en la interfaz o en el informe incluye una explicación en lenguaje no técnico y sus limitaciones.
- **CA2:** El informe incluye en todas sus páginas la leyenda: "Este informe no constituye un dictamen pericial. Consulte a un profesional especializado."
- **CA3:** Los textos de las conclusiones provienen de un catálogo revisado y versionado, no de redacción libre.
- **CA4:** El informe, la pantalla de resultados y el correo de fin de análisis incluyen un descargo: el resultado es parcial, lo produce un sistema automatizado con técnicas de inteligencia artificial y no reemplaza el criterio de un perito (ADR-0017).
- **CA5:** Cada capa presenta en el informe una tabla con los criterios, el valor de referencia de una imagen sin edición y el valor obtenido, con sus umbrales numéricos, sin describir el algoritmo interno (ADR-0017).

### RNF24 — Desempeño y trazabilidad del modelo de red neuronal
**Prioridad:** Debe

- **CA1:** El modelo se entrena en PyTorch mediante transferencia de aprendizaje, se exporta a ONNX y se ejecuta en producción con ONNX Runtime en CPU.
- **CA2:** El entrenamiento es reproducible: se documentan el conjunto de datos, la partición, los hiperparámetros, la semilla y la versión del modelo.
- **CA3:** El desempeño se reporta sobre un conjunto de prueba independiente con exactitud, precisión, exhaustividad, F1 y área bajo la curva ROC; el umbral mínimo de aceptación es **[A DEFINIR]** (ver CP-07).
- **CA4:** Cada informe registra la versión del modelo utilizada.
