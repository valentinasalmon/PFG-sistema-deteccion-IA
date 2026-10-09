# Especificación: 001 — Esqueleto caminante

- **Rama**: `funcionalidad/001-esqueleto-caminante`
- **Estado**: Borrador
- **Requisitos que realiza**: RNF17, RNF19, RNF20, RNF21, RNF22
- **Reglas de negocio aplicadas**: ninguna (funcionalidad técnica de base)
- **Casos de uso**: ninguno (no tiene interacción de usuario final)

## Problema

Antes de construir cualquier funcionalidad del negocio, todas las piezas del sistema tienen que existir y estar conectadas entre sí: interfaz en React, API en Flask, base de datos PostgreSQL, Redis, almacenamiento compatible con S3, servidor de correo de prueba y la integración continua con sus controles de calidad.

Un **esqueleto caminante** es la versión mínima del sistema que recorre todas esas piezas de punta a punta, aunque todavía no haga nada útil para el usuario. Sirve para:

- detectar desde el primer día los problemas de integración entre tecnologías;
- dejar establecidas la arquitectura en capas, la configuración por entorno y las reglas de calidad que van a respetar todas las funcionalidades siguientes;
- tener desde el inicio una integración continua que impida integrar código que no cumple los estándares.

## Alcance

### Incluido

**Servicios de desarrollo**
- Definición en un único archivo de Docker Compose de los servicios: PostgreSQL, Redis y servidor de correo de prueba.

**Backend**
- Aplicación Flask construida con *Application Factory*.
- Configuración por entorno (desarrollo, pruebas y producción) con *Factory + Strategy*, leída de variables de entorno.
- Validación de la configuración al arrancar: en producción, la falta de una variable obligatoria impide iniciar la aplicación con un mensaje claro.
- Conexión a PostgreSQL con Flask-SQLAlchemy y migraciones con Flask-Migrate, sin tablas de negocio todavía.
- Endpoint de salud `GET /api/salud` que informa el estado de la API, de la base de datos y de Redis.
- Estructura de capas (rutas, servicios, repositorios, modelos) con el primer ejemplo real: la ruta de salud usa un servicio de salud.
- Prueba automática de arquitectura que verifica la dirección de dependencias entre capas.

**Frontend**
- Proyecto React creado con Vite.
- Página inicial que consulta `/api/salud` y muestra el estado de cada servicio en español.
- Mensaje claro cuando la API no responde.

**Calidad y proceso**
- Pruebas del backend con pytest y medición de cobertura con coverage.py (mínimo 80 %).
- Análisis estático con flake8 y pylint, exigiendo docstrings.
- Análisis estático del frontend con ESLint y pruebas con Vitest.
- Validación local de los mensajes de commit (tipos en español) antes de crear cada commit.
- Integración continua en GitHub Actions con tres trabajos: backend, frontend y mensajes de commit.
- Archivos de configuración del repositorio: `.gitignore`, `.gitattributes`, `.editorconfig` y un archivo de ejemplo de variables de entorno.

**Documentación**
- Instrucciones para levantar el sistema completo en `backend/README.md` y `frontend/README.md`.
- Entrada en la bitácora.

### Excluido

- Modelos y tablas del negocio (desde la funcionalidad 002).
- Autenticación y sesión (funcionalidad 002).
- Almacenamiento compatible con S3: se elige, se levanta y se usa en la funcionalidad 006.
- Uso del correo: en esta funcionalidad solo se levanta el servicio (funcionalidad 013).
- Cola de tareas en segundo plano con RQ: solo se verifica la conexión a Redis (funcionalidad 007).
- Despliegue en AWS (funcionalidad 017).

## Criterios de aceptación

- [ ] **CA1 — Servicios**: Dado el repositorio clonado, cuando se ejecuta `docker compose up -d`, entonces PostgreSQL, Redis y el servidor de correo quedan en ejecución y en estado saludable.
- [ ] **CA2 — Salud de la API**: Dados los servicios en ejecución, cuando se consulta `GET /api/salud`, entonces la respuesta es 200 con un JSON que informa `ok` para la API, la base de datos y Redis, junto con el entorno y la versión.
- [ ] **CA3 — Servicio caído**: Dada la base de datos detenida, cuando se consulta `GET /api/salud`, entonces la respuesta es 503 e indica cuál servicio no responde.
- [ ] **CA4 — Interfaz conectada**: Dados el backend y el frontend en ejecución, cuando se abre la página inicial en el navegador, entonces se muestra en español que la API está conectada y el estado de cada servicio.
- [ ] **CA5 — Interfaz sin API**: Dado el backend detenido, cuando se abre la página inicial, entonces se muestra el mensaje "No se pudo conectar con la API" sin errores en pantalla.
- [ ] **CA6 — Configuración segura**: Dado el entorno de producción sin la variable de la clave secreta, cuando se intenta iniciar la aplicación, entonces no arranca e informa qué variable falta.
- [ ] **CA7 — Pruebas y cobertura**: Cuando se ejecutan las pruebas del backend, entonces todas pasan y la cobertura es de al menos 80 %.
- [ ] **CA8 — Análisis estático**: Cuando se ejecutan flake8, pylint y ESLint, entonces flake8 y ESLint no reportan errores y pylint obtiene al menos 8,5.
- [ ] **CA9 — Arquitectura**: Dada una ruta que importa directamente un repositorio, cuando se ejecuta la prueba de arquitectura, entonces la prueba falla indicando la violación.
- [ ] **CA10 — Commits**: Dado un commit con el mensaje `feat: algo`, entonces se rechaza localmente; dado `funcionalidad(esqueleto): algo`, entonces se acepta.
- [ ] **CA11 — Integración continua**: Dado un Pull Request hacia `desarrollo`, cuando GitHub Actions lo procesa, entonces los trabajos de backend, frontend y commits finalizan en verde.

## Preguntas abiertas

- Ninguna.

## Registro de cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-10-10 | Se quita el almacenamiento compatible con S3 (MinIO) del alcance de esta funcionalidad y se traslada a la 006. | La imagen `minio/minio` dejó de publicarse en Docker Hub. El almacenamiento S3 recién se utiliza en la funcionalidad 006, donde se elegirá un reemplazo verificado y se registrará en un ADR. |
