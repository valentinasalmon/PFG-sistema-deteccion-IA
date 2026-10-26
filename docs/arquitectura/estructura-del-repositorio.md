# Estructura del repositorio

El repositorio es un **monorepositorio** (ver [ADR-0001](decisiones/0001-monorepositorio.md)): backend, frontend, red neuronal e infraestructura conviven en un mismo repositorio, con un único historial y una única integración continua.

Las carpetas vacías contienen un archivo `.gitkeep`, que solo existe para que Git conserve la carpeta. Se elimina al agregar el primer archivo real.

## Raíz

| Ruta | Contenido |
|---|---|
| `README.md` | Presentación del proyecto |
| `CLAUDE.md` | Reglas del arnés para agentes de IA |
| `.claude/commands/` | Comandos del flujo guiado por especificaciones (`/especificar`, `/planificar`, `/tareas`) |
| `.claude/skills/`, `.agents/` | Skills instalados para el asistente de IA |
| `.github/workflows/` | Integración continua en GitHub Actions |
| `skills-lock.json` | Registro de los skills instalados |

## `backend/` — API REST en Flask

| Ruta | Capa | Contenido |
|---|---|---|
| `app/configuracion/` | Transversal | Clases de configuración por entorno y fábrica que las selecciona (Factory + Strategy). |
| `app/modelos/` | Modelos | Entidades de SQLAlchemy: usuario, organización, membresía, caso, acceso, imagen, análisis, resultado, informe, auditoría, plan. |
| `app/repositorios/` | Repositorios | Consultas a la base de datos, una clase por entidad. |
| `app/servicios/` | Servicios | Lógica de negocio y reglas (RN) por dominio: autenticación, organizaciones, casos, imágenes, análisis, retención. |
| `app/rutas/` | Rutas | Blueprints de la API REST (`/api/...`). |
| `app/esquemas/` | Transversal | Validación de entradas y serialización de salidas de la API. |
| `app/seguridad/` | Transversal | Decoradores `@requiere_rol`, `@requiere_permiso_caso`, CSRF, limitación de intentos. |
| `app/analisis/` | Dominio | Interfaz común de capas y sus cuatro implementaciones (metadatos, C2PA, ELA, red neuronal). |
| `app/integraciones/` | Adaptadores | Almacenamiento (S3 y local), correo (SES y consola), sellado de tiempo (Hedera y simulado). |
| `app/tareas/` | Segundo plano | Trabajos de RQ: procesar análisis, enviar correos, aplicar retención. |
| `app/informes/` | Dominio | Construcción del informe PDF (WeasyPrint). |
| `app/plantillas/correos/` | Presentación | Plantillas Jinja2 de los correos electrónicos. |
| `app/plantillas/informes/` | Presentación | Plantillas Jinja2 (HTML + CSS) del informe PDF. |
| `app/comandos.py` | Entrada | Comandos de terminal (`flask administracion promover`); como las rutas, solo usan la fábrica de servicios. |
| `app/utilidades/` | Transversal | Funciones auxiliares sin dependencias de dominio (fechas, hashes, formatos). |
| `migraciones/` | Datos | Migraciones de esquema con Alembic (Flask-Migrate). |
| `recursos/catalogos/` | Datos | Catálogos versionados: aseguradoras de la SSN (021) y, más adelante, textos de conclusiones y explicaciones (RNF23). Cada archivo documenta su fuente en el README de la carpeta. |
| `recursos/confianza_c2pa/` | Datos | Lista de confianza de C2PA (certificados raíz en PEM). |
| `modelos_onnx/` | Datos | Modelo ONNX de la capa 4. **Ignorado por Git**: se descarga o copia en cada entorno. |
| `pruebas/unitarias/` | Pruebas | Pruebas de servicios, repositorios, capas y utilidades. |
| `pruebas/integracion/` | Pruebas | Pruebas de la API completa (rutas + base de datos de pruebas). |
| `pruebas/arquitectura/` | Pruebas | Verificación automática de la dirección de dependencias entre capas (RNF17). |
| `pruebas/datos/imagenes/` | Pruebas | Imágenes de prueba (propias, sin datos personales). |

## `frontend/` — Interfaz en React

| Ruta | Contenido |
|---|---|
| `public/` | Archivos estáticos servidos tal cual (ícono, etc.). |
| `src/api/` | Cliente HTTP y funciones por recurso (casos, imágenes, organizaciones). Único lugar que conoce las URL de la API. |
| `src/componentes/` | Componentes reutilizables de interfaz (botones, tablas, formularios, diálogos). |
| `src/paginas/` | Un archivo por pantalla (inicio, casos, detalle de caso, organización, perfil, administración) y sus pruebas. |
| `src/rutas/` | Guardas de navegación: rutas protegidas por sesión (y por rol desde la 014). La tabla de rutas está en `src/App.jsx`. |
| `src/contextos/` | Estado global de React (sesión del usuario). |
| `src/hooks/` | Hooks propios (sesión, formularios, acciones de enlaces y, más adelante, progreso de análisis). |
| `src/estilos/` | Estilos globales y variables de diseño. |
| `src/utilidades/` | Formateo de fechas, textos y validaciones del lado del cliente. |

## `red_neuronal/` — Capa 4

| Ruta | Contenido |
|---|---|
| `pyproject.toml` | Paquete instalable: dependencias base (inferencia) y extra `[entrenamiento]`; configuración de calidad. |
| `clasificador/` | Paquete de Python con un módulo por etapa del pipeline (datos, modelo, entrenamiento, evaluación, exportación, inferencia, seguimiento, registro) y línea de comandos `python -m clasificador <etapa>`. Ver [ADR-0014](decisiones/0014-ciclo-de-vida-y-mlops-del-clasificador.md). |
| `clasificador/inferencia/` | Contrato de entrada del modelo y predictor ONNX, sin PyTorch. Lo reutiliza el backend. Ver [ADR-0015](decisiones/0015-arquitectura-y-contrato-de-inferencia-del-clasificador.md). |
| `configuracion/` | Recetas de datos y configuraciones de entrenamiento en YAML, versionadas. |
| `cuadernos/` | Cuadernos de Jupyter que orquestan el pipeline en Kaggle. No contienen lógica. |
| `pruebas/` | Pruebas del paquete con imágenes generadas en memoria, sin GPU. |
| `datos/` | Conjuntos de datos. **Ignorado por Git**. |
| `modelos/` | Pesos entrenados y modelos exportados. **Ignorado por Git**. |
| `informes/` | Ficha de cada versión del modelo (`<version>/ficha.md`) con métricas, matrices de confusión y curvas ROC. |

## `infraestructura/`

| Ruta | Contenido |
|---|---|
| `terraform/` | Infraestructura como código de AWS (EC2, S3, SES, IAM, grupos de seguridad). |
| `nginx/` | Configuración del proxy inverso y TLS. |
| `systemd/` | Servicios de Gunicorn y del trabajador de RQ. |
| `scripts/` | Respaldos de la base de datos, restauración y tareas de operación. |

## `docs/`

| Ruta | Contenido |
|---|---|
| `constitucion.md` | Principios no negociables. |
| `especificacion/` | Especificación general: visión, reglas, requisitos y casos de uso. |
| `funcionalidades/` | Una carpeta por funcionalidad con `especificacion.md`, `plan.md` y `tareas.md`. |
| `funcionalidades/plantillas/` | Plantillas de esos tres documentos. |
| `arquitectura/` | Estructura del repositorio, modelo de datos, análisis del repositorio anterior. |
| `arquitectura/decisiones/` | Registros de decisiones de arquitectura (ADR). |
| `arquitectura/diagramas/` | Diagramas (Excalidraw y exportaciones). |
| `guias/` | Guías de instalación, flujo de trabajo y despliegue. |
| `bitacora/` | Registro cronológico de cada etapa del desarrollo. |
| `legal/` | Términos de Uso y Política de Privacidad versionados. |
