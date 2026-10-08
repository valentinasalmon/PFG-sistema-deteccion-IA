# 1. Visión y alcance

## 1.1 Propósito

El sistema es una plataforma web de **apoyo a la decisión** destinada a abogados y aseguradoras. Provee información estructurada para la **evaluación preliminar de imágenes** aportadas como prueba en siniestros automovilísticos y laborales, con el fin de detectar indicios de manipulación o de generación mediante inteligencia artificial.

El sistema **no emite veredictos**. Cada resultado se presenta como un indicio, acompañado de sus limitaciones y de la recomendación expresa de consultar a un perito o profesional especializado.

## 1.2 Problema que aborda

La difusión de herramientas de edición y de generación de imágenes por IA facilita la presentación de pruebas fotográficas alteradas o íntegramente sintéticas en reclamos por siniestros. Los profesionales que evalúan esas pruebas carecen, en la etapa preliminar, de una herramienta accesible que reúna señales técnicas heterogéneas y las explique en un lenguaje comprensible para usuarios no técnicos.

## 1.3 Alcance

### Incluido

- Registro y autenticación de usuarios con perfil Abogado o Aseguradora.
- Organizaciones (estudios jurídicos y aseguradoras) con invitación de miembros por correo electrónico.
- Gestión de casos con ciclo de vida, búsqueda y colaboración dentro de una organización.
- Carga de imágenes JPEG y PNG con validación de formato real y cálculo de huella digital SHA-256.
- Análisis en cuatro capas independientes: metadatos EXIF/XMP, credenciales de contenido C2PA, análisis de niveles de error (ELA) y clasificador de redes neuronales convolucionales.
- Generación de un informe PDF explicativo por cada análisis, con historial descargable.
- Notificaciones por correo electrónico.
- Panel principal del usuario y tablero estadístico del Administrador.
- Planes de uso diferenciados para usuarios individuales y organizaciones.
- Política de retención y destrucción de datos conforme a la Ley N.° 25.326.
- Registro de auditoría para trazabilidad legal.

### Excluido

- Emisión de dictámenes periciales o veredictos de autenticidad.
- Análisis de video, audio o documentos.
- Detección de manipulación localizada mediante la red neuronal (la capa 4 estima únicamente si la imagen es íntegramente sintética).
- Interfaz de consulta del registro de auditoría.
- Validación de matrículas profesionales o de la pertenencia a una empresa.
- Aplicaciones móviles nativas.
- Cobro en línea mediante pasarela de pagos **[A DEFINIR]** (ver CP-01).

## 1.4 Actores

| Actor | Descripción |
|---|---|
| **Visitante** | Persona no autenticada. Puede registrarse, iniciar sesión, recuperar la contraseña y aceptar invitaciones. |
| **Usuario** | Persona registrada y autenticada. Tiene un **perfil** Abogado o Aseguradora; ambos perfiles tienen las mismas capacidades. |
| **Referente** | Usuario que administra una organización. El creador de la organización es su primer Referente. |
| **Miembro** | Usuario que pertenece a una organización sin ser su Referente. |
| **Responsable del caso** | Usuario titular de un caso (equivale al rol "dueño"). Tiene control total sobre él. |
| **Colaborador** | Usuario con permiso de colaboración sobre un caso: edita datos, carga imágenes y solicita análisis. |
| **Lector** | Usuario con permiso de lectura sobre un caso: consulta datos y descarga informes. |
| **Administrador** | Responsable de la plataforma. Consulta estadísticas agregadas y listados de usuarios y organizaciones. **No accede a los casos ni a su contenido.** |
| **Sistema** | Procesos automáticos: cola de análisis, tareas programadas de retención y envío de notificaciones. |
| **Servicios externos** | Amazon S3 (almacenamiento), Amazon SES (correo) y Blockchain Federal Argentina (sello de tiempo). |

Un mismo usuario puede desempeñar varios roles a la vez: por ejemplo, ser Referente de su organización, Miembro de otra y Lector de un caso compartido.

## 1.5 Modelo de negocio

El modelo diferencia dos tipos de espacio de trabajo:

| Espacio | Quién lo usa | Costo | Capacidades |
|---|---|---|---|
| **Personal** | Todo usuario registrado | Gratuito | Gestión de casos propios y análisis, con límites de uso. **No permite compartir casos.** |
| **Organización** | Estudios jurídicos y aseguradoras | Plan pago | Todo lo del espacio personal, más invitación de miembros, casos compartidos y colaboración, con límites según el plan. |

La colaboración es el principal diferencial de los planes pagos. Los planes concretos, sus límites y su forma de cobro están **[A DEFINIR]** (ver CP-01 y CP-02).

## 1.6 Glosario

| Término | Definición |
|---|---|
| **Análisis** | Ejecución de las cuatro capas sobre un conjunto de imágenes de un caso. Cada análisis produce un informe. |
| **C2PA** | *Coalition for Content Provenance and Authenticity*. Estándar de credenciales de contenido que permite declarar y firmar el origen de un archivo multimedia. |
| **Capa de análisis** | Técnica independiente de detección que devuelve un nivel de indicio, una lista de anomalías y una conclusión. |
| **Caso** | Unidad de trabajo que agrupa los datos de un siniestro, sus imágenes y sus informes. |
| **ELA** | *Error Level Analysis*. Técnica que resalta regiones de una imagen JPEG con una historia de compresión distinta al resto. |
| **EXIF / XMP** | Estándares de metadatos embebidos en archivos de imagen (cámara, fechas, software, historial de edición). |
| **Espacio de trabajo** | Ámbito al que pertenece un caso: el espacio personal de un usuario o el de una organización. |
| **Expediente** | Número de referencia externo del caso (judicial o de siniestro), cargado por el usuario. |
| **Huella digital** | Resumen criptográfico SHA-256 del contenido de un archivo, que permite verificar su integridad. |
| **Informe** | Documento PDF que expone el resultado de un análisis, capa por capa. |
| **Nivel de indicio** | Valor de 0 % a 100 % que expresa la intensidad de las señales halladas por una capa. No es una probabilidad de culpabilidad ni un veredicto. |
| **Número de caso** | Identificador interno, único y no editable, que el sistema asigna a cada caso. |
| **ONNX** | Formato abierto para modelos de aprendizaje automático, ejecutado en producción con ONNX Runtime. |
| **Plan** | Conjunto de capacidades y límites de uso asociados a un espacio de trabajo. |
| **Sello de tiempo** | Registro en Blockchain Federal Argentina que acredita que una huella digital existía en una fecha determinada. |
