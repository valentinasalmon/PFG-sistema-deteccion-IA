# Análisis de reutilización del repositorio anterior (TIF)

Repositorio analizado: `valentinasalmon/TIF`, ramas `main` y `claude/aws-terraform-infra` (commit `ccdddd0`), revisado el 08/10/2026.

## Resumen

El repositorio anterior ya aplicaba la arquitectura en capas, los patrones obligatorios y un flujo guiado por especificaciones. La lógica de las capas 1 y 2 tiene un buen nivel de avance. Se reutilizan **las ideas, las reglas de detección y la evidencia experimental**; el código se **reescribe** en el nuevo repositorio para adaptarlo a la especificación (API REST, interfaz común de capas, nivel de indicio, idioma, migraciones).

## Decisión por componente

| Componente de TIF | Decisión | Motivo | Destino en el proyecto nuevo |
|---|---|---|---|
| `memory/constitution.md` | **Reutilizar y ampliar** | Principios correctos y vigentes. | `docs/constitucion.md` |
| `specs/`, plantillas y comandos `/specify`, `/plan`, `/tasks` | **Reutilizar y traducir** | El flujo es el adecuado; se traducen nombres y se adaptan rutas. | `docs/funcionalidades/`, `.claude/commands/` |
| `CONTRIBUTING.md` | **Reutilizar y adaptar** | Cambian los tipos de commit (español) y el modelo de ramas. | `docs/guias/flujo-de-trabajo.md` |
| `app/config.py` (Factory + Strategy) | **Reutilizar y ampliar** | Correcto. Falta validar que `SECRET_KEY` exista en producción y agregar S3, SES, Redis y BFA. | `backend/app/configuracion/` |
| `app/__init__.py` (Application Factory) | **Adaptar** | Usa `db.create_all()`: se reemplaza por migraciones con Alembic. Se agregan CSRF, CORS y registro de blueprints de la API. | `backend/app/__init__.py` |
| `app/services/decoradores.py` (`@requiere_rol`) | **Reutilizar y ampliar** | Correcto. Se agrega `@requiere_permiso_caso` y la respuesta 404 sin permiso (RNF05). | `backend/app/seguridad/` |
| `app/models/usuario.py` | **Adaptar** | Rol `perito` no existe; falta perfil, colegio o empresa, verificación de correo, consentimiento. La generación de tokens pasa a un servicio. | `backend/app/modelos/usuario.py` |
| `app/models/caso.py` | **Adaptar** | El expediente era único y obligatorio; ahora es opcional y no único (RN16). Faltan número de caso, espacio, lugar, fecha del hecho, estados y retención. | `backend/app/modelos/caso.py` |
| `app/models/imagen.py` | **Adaptar** | Falta la huella SHA-256, el tamaño, las dimensiones y el estado del sello. El campo `origen_declarado` es útil y se conserva. | `backend/app/modelos/imagen.py` |
| `app/models/analisis.py` | **Adaptar parcialmente** | `ResultadoAnalisis` y `AnomaliaDetectada` sirven. **`ConclusionFinal` se descarta**: combina las capas en una conclusión única y contradice RN27. El tipo `prnu` se descarta (fuera de alcance). | `backend/app/modelos/analisis.py` |
| Repositorios y servicios de casos y autenticación | **Reescribir** | Correctos en estructura, pero la nueva especificación cambia permisos, estados y organizaciones. Se toman como referencia de estilo. | `backend/app/repositorios/`, `backend/app/servicios/` |
| `app/services/metadatos_service.py` | **Reutilizar las reglas, reescribir la estructura** | Las siete validaciones (software, historial XMP, parámetros de generación en PNG, MakerNotes, cronología, bloque de captura, dimensiones típicas de IA) y la escala de severidad son valiosas. Se adapta a la interfaz común de capas, se quita la ruta fija a `tools/exiftool.exe` y la persistencia directa, y la fecha del sistema se reemplaza por la fecha de carga. | `backend/app/analisis/metadatos.py` |
| `app/services/c2pa_service.py` | **Reutilizar parcialmente** | Lee el manifiesto con ExifTool pero **no verifica la firma**. La interpretación de `DigitalSourceType` (vocabulario IPTC) se conserva. | `backend/app/analisis/credenciales_c2pa.py` |
| `probar_c2pa_firma.py` | **Reutilizar como base de la capa 2** | Ya usa c2pa-python con contexto de confianza. Es el punto de partida de la verificación de firma (RF40). | `backend/app/analisis/credenciales_c2pa.py` |
| `probar_canales.py` e imágenes de `tests/imagenes_prueba/` | **Conservar como evidencia experimental** | Demuestra qué canales conservan el manifiesto C2PA. Respalda RN28 y es material para la tesis. | `backend/pruebas/datos/imagenes/` y `docs/` |
| Pruebas (`tests/`) | **Reescribir tomando como referencia** | Las pruebas de metadatos y C2PA son buenos modelos de casos de prueba. | `backend/pruebas/unitarias/` |
| `.github/workflows/ci.yml` | **Adaptar** | Se suman frontend, cobertura mínima, commitlint en español y análisis de seguridad. | `.github/workflows/` |
| `.pre-commit-config.yaml`, `.flake8`, `.pylintrc`, `commitlint.config.cjs` | **Adaptar** | Los tipos de commit pasan al español; pylint deja de desactivar la exigencia de docstrings (RNF21). | `backend/` y raíz |
| `requirements.txt` | **Actualizar** | Se agregan Flask-Migrate, RQ, boto3, c2pa-python, onnxruntime, WeasyPrint, numpy, etc. | `backend/requirements.txt` |
| Plantillas Jinja2 de pantallas (`app/templates/`) | **Descartar** | La interfaz pasa a React ([ADR-0002](decisiones/0002-react-y-api-rest.md)). | — |
| `crear_usuario_prueba.py` | **Descartar** | Se reemplaza por un comando de Flask para crear datos de prueba. | — |
| `tools/exiftool.exe` y `tools/exiftool_files/` | **Descartar** | Ejecutable de Windows. En desarrollo se instala ExifTool en el sistema; en producción, como paquete de Linux. | — |
| `infra/terraform/` | **Rehacer** | Crea una base de datos administrada (RDS), contraria a la decisión de alojarla en la EC2 ([ADR-0005](decisiones/0005-postgresql-en-ec2.md)). Se rehace en la etapa de infraestructura. | `infraestructura/terraform/` |

## Hallazgos a corregir

1. **La firma C2PA no se verifica contra una lista de confianza.** Los resultados guardados muestran `signingCredential.untrusted` en imágenes auténticas de OpenAI porque la prueba se ejecutó sin el parámetro `--confianza`. Hay que verificar qué lista de confianza reconoce a los firmantes reales (OpenAI, Google) antes de fijar el comportamiento de RF40. **Resuelto en la 009**: la lista oficial de C2PA reconoce a los dos (el certificado de OpenAI lo emite Trufo). Además, c2pa-python necesita la configuración de usos de clave (EKU) para no rechazarlos; ver el [plan de la 009](../funcionalidades/009-capa-c2pa/plan.md).
2. **Ruta fija al ejecutable de Windows.** Se reemplaza por una variable de configuración (`RUTA_EXIFTOOL`).
3. **Fecha del sistema basada en `getctime`.** En el servidor esa fecha es la de carga; se reemplaza explícitamente por la fecha de carga registrada.
4. **Capas que escriben en la base de datos.** Las capas de análisis pasan a ser funciones puras que devuelven un resultado; el servicio de análisis es quien persiste.
5. **`db.create_all()` en lugar de migraciones.** Se reemplaza por Alembic ([ADR-0008](decisiones/0008-migraciones-con-alembic.md)).

## Evidencia experimental reutilizable

Resultado de `probar_canales.py` con imágenes generadas por ChatGPT y Gemini:

| Canal | Manifiesto C2PA |
|---|---|
| Archivo original | Se conserva |
| WhatsApp como documento | Se conserva |
| Correo electrónico | Se conserva |
| WhatsApp como foto | **Se pierde** |
| Captura de pantalla | **Se pierde** |
