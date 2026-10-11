# Tareas: 002 — Cuentas y sesión

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Cada tarea termina con una verificación y un commit. **Responsable** indica quién escribe y sube cada parte: la autora (código central) o el asistente (pruebas, estilos, textos, configuración y documentación), según el reparto de [CLAUDE.md](../../../CLAUDE.md). Después de cada commit del asistente, la autora ejecuta `git pull`. Los comandos del backend se ejecutan en `backend/` con el entorno virtual activado (`source .venv/bin/activate`); los del frontend, en `frontend/`. La integración continua solo corre en el Pull Request, así que las tareas intermedias pueden subirse aunque la cobertura total todavía no llegue al mínimo.

## Backend

- [x] **T01** — Dependencias, variables de entorno y archivos ignorados.
  - Responsable: Autora
  - Archivos: `backend/requirements.txt`, `backend/.env.ejemplo`, `backend/README.md`, `.gitignore`
  - Verificación: `pip install -r requirements-dev.txt` termina sin errores y `pip list` muestra Flask-Login 0.6.3; copiar al `.env` las variables nuevas de `.env.ejemplo`.
  - Commit: `construccion(backend): agregar dependencias de cuentas y sesion`
- [x] **T02** — Configuración de sesiones, seguridad y correo.
  - Responsable: Autora
  - Archivos: `backend/app/configuracion/entornos.py`, `app/extensiones.py`, `app/utilidades/__init__.py`, `app/utilidades/tiempo.py`, `pruebas/unitarias/test_configuracion.py`
  - Verificación: `python -m pytest pruebas/unitarias/test_configuracion.py --no-cov` pasa.
  - Commit: `funcionalidad(configuracion): agregar configuracion de sesiones, seguridad y correo`
- [x] **T03** — Modelo `Usuario` y su repositorio.
  - Responsable: Autora
  - Archivos: `backend/app/modelos/__init__.py`, `app/modelos/usuario.py`, `app/repositorios/repositorio_usuarios.py`, `app/__init__.py` (importa los modelos)
  - Verificación: `flake8 app` sin errores.
  - Commit: `funcionalidad(usuarios): agregar modelo y repositorio de usuarios`
- [x] **T04** — Migración de la tabla `usuarios`.
  - Responsable: Autora
  - Archivos: `backend/migraciones/versions/a58c14fe9514_crear_tabla_de_usuarios.py`
  - Verificación: con `docker compose up -d`, `flask --app wsgi db upgrade` crea la tabla y `flask --app wsgi db check` responde que no hay cambios pendientes.
  - Commit: `funcionalidad(usuarios): agregar migracion de la tabla de usuarios`
- [x] **T05** — Errores de dominio, política de contraseñas y tokens de enlaces.
  - Responsable: Autora
  - Archivos: `backend/app/servicios/errores.py`, `app/servicios/contrasenias.py`, `app/servicios/tokens.py`, `backend/recursos/contrasenias_comunes.txt`, `pruebas/unitarias/test_contrasenias.py`, `pruebas/unitarias/test_tokens.py`
  - Verificación (CA4, CA20): las pruebas de contraseñas y tokens pasan.
  - Commit: `funcionalidad(cuentas): agregar politica de contrasenias y tokens de enlaces`
- [x] **T06** — Envío de correos con plantillas.
  - Responsable: Autora
  - Archivos: `backend/app/integraciones/correo.py`, `app/servicios/servicio_correos.py`, `app/plantillas/correos/` (16 archivos), `pruebas/unitarias/test_correo.py`
  - Verificación: `ls app/plantillas/correos | wc -l` muestra 16 y las pruebas de correo pasan, incluida la que comprueba que cada plantilla tenga su propio texto.
  - Commit: `funcionalidad(correos): agregar envio de correos con plantillas`
- [ ] **T07** — Servicios de cuentas, sesión y perfil.
  - Responsable: Autora
  - Archivos: `backend/app/servicios/servicio_cuentas.py`, `servicio_sesion.py`, `servicio_perfil.py`, `fabrica.py`
  - Verificación: `python -m pytest --no-cov` (35 pruebas), `flake8 app pruebas wsgi.py` y `lint-imports` sin errores (los servicios no importan Flask). De la T07 a la T09 la cobertura total queda por debajo del 80 % hasta que llegan las pruebas de la API en la T10; por eso se usa `--no-cov`.
  - Commit: `funcionalidad(cuentas): agregar servicios de cuentas, sesion y perfil`
- [ ] **T08** — Validación de entradas.
  - Responsable: Autora (`app/esquemas/`); asistente (`test_esquemas.py`)
  - Archivos: `backend/app/esquemas/__init__.py`, `app/esquemas/cuentas.py`, `pruebas/unitarias/test_esquemas.py`
  - Verificación: las pruebas de esquemas pasan (mensajes en español).
  - Commit: `funcionalidad(cuentas): agregar esquemas de validacion de entradas`
- [ ] **T09** — Autenticación y rutas de la API.
  - Responsable: Autora
  - Archivos: `backend/app/seguridad/__init__.py`, `app/seguridad/autenticacion.py`, `app/rutas/errores.py`, `app/rutas/cuentas.py`, `app/rutas/sesion.py`, `app/rutas/perfil.py`, `app/rutas/__init__.py`, `app/__init__.py`
  - Verificación: `flask --app wsgi routes` lista las 15 rutas de `/api`.
  - Commit: `funcionalidad(cuentas): agregar rutas de cuentas, sesion y perfil`
- [ ] **T10** — Pruebas de integración de la API.
  - Responsable: Asistente
  - Archivos: `backend/pruebas/conftest.py`, `pruebas/integracion/test_rutas_cuentas.py`, `test_rutas_sesion.py`, `test_rutas_perfil.py`, `test_seguridad.py`
  - Verificación (CA1–CA22 del lado del servidor): `python -m pytest`, `flake8 app pruebas wsgi.py`, `pylint app pruebas wsgi.py` y `lint-imports` en verde; 94 pruebas y cobertura cercana al 99 %.
  - Commit: `pruebas(cuentas): agregar pruebas de integracion de la api`

## Frontend

- [ ] **T11** — Dependencias y umbral de cobertura.
  - Responsable: Asistente
  - Archivos: `frontend/package.json`, `frontend/package-lock.json` (generado por `npm install`), `frontend/vite.config.js`
  - Verificación: `npm install` termina sin errores.
  - Commit: `construccion(frontend): agregar enrutador y umbral de cobertura`
- [ ] **T12** — Cliente de la API con CSRF.
  - Responsable: Autora (`src/api/`); asistente (`cliente.test.js` y `src/pruebas/`)
  - Archivos: `frontend/src/api/cliente.js`, `cuentas.js`, `sesion.js`, `perfil.js`, `src/api/cliente.test.js`, `src/pruebas/configuracion.js`, `src/pruebas/api.js`
  - Verificación (CA21, CA22): `npx vitest run src/api` pasa.
  - Commit: `funcionalidad(frontend): agregar cliente de la api con proteccion csrf`
- [ ] **T13** — Sesión compartida, formularios y reglas de contraseña.
  - Responsable: Autora (contexto y hooks); asistente (`src/utilidades/` y las pruebas)
  - Archivos: `frontend/src/contextos/contextoSesion.js`, `ProveedorSesion.jsx`, `src/hooks/useSesion.js`, `useFormulario.js`, `useAccionAlCargar.js`, `src/hooks/useSesion.test.jsx`, `src/utilidades/contrasenia.js`, `contrasenia.test.js`, `legales.js`
  - Verificación: `npx vitest run src/hooks src/utilidades` pasa.
  - Commit: `funcionalidad(frontend): agregar contexto de sesion y utilidades de formularios`
- [ ] **T14** — Componentes comunes.
  - Responsable: Autora (`Encabezado`, `Disposiciones`, `Rutas`, `FormularioReenvio`); asistente (`Aviso`, `AvisoProvisorio`, `CampoTexto`, `Cargando`, `ReglasContrasenia` y `global.css`)
  - Archivos: `frontend/src/componentes/Aviso.jsx`, `AvisoProvisorio.jsx`, `CampoTexto.jsx`, `Cargando.jsx`, `Disposiciones.jsx`, `Encabezado.jsx`, `FormularioReenvio.jsx`, `ReglasContrasenia.jsx`, `Rutas.jsx`, `src/estilos/global.css`
  - Verificación: `npm run lint` sin errores.
  - Commit: `funcionalidad(frontend): agregar componentes comunes y estilos`
- [ ] **T15** — Pantallas, rutas de la aplicación y sus pruebas.
  - Responsable: Autora (pantallas, `App.jsx`, `main.jsx`); asistente (`PaginaTerminos`, `PaginaPrivacidad`, `PaginaNoEncontrada`, `src/pruebas/renderizar.jsx` y las pruebas de pantallas)
  - Archivos: `frontend/src/paginas/` (`PaginaEstado.jsx` y su prueba, que reemplazan a `PaginaInicio`; `PaginaInicio.jsx`, `PaginaIniciarSesion.jsx`, `PaginaRegistro.jsx`, `PaginaVerificarCorreo.jsx`, `PaginaRecuperarContrasenia.jsx`, `PaginaRestablecerContrasenia.jsx`, `PaginaConfirmarCorreo.jsx`, `PaginaPerfil.jsx`, `PaginaTerminos.jsx`, `PaginaPrivacidad.jsx`, `PaginaNoEncontrada.jsx`, `acceso.test.jsx`, `enlaces.test.jsx`, `PaginaPerfil.test.jsx`), `src/App.jsx`, `src/main.jsx`, `src/pruebas/renderizar.jsx`
  - Verificación (CA1–CA22 del lado de la interfaz): `npm run lint` y `npm run test:cobertura` en verde; 50 pruebas y cobertura cercana al 98 %.
  - Commit: `funcionalidad(frontend): agregar pantallas de cuentas, sesion y perfil`

## Verificación manual

- [ ] **T16** — Recorrido completo en el navegador (sin commit).
  - Responsable: Autora
  - Con `docker compose up -d`, el backend (`flask --app wsgi run --debug`) y el frontend (`npm run dev`):
    1. Abrir `http://localhost:5173/perfil` → lleva a "Iniciar sesión" (CA22).
    2. Registrarse sin aceptar los términos y con una contraseña corta → se ven los dos errores juntos (CA2, CA4).
    3. Registrarse bien → llega el correo a Mailpit (`http://localhost:8025`) (CA1); registrarse otra vez con el mismo correo → mismo mensaje y aviso al titular (CA3).
    4. Abrir el enlace del correo → cuenta verificada; abrirlo otra vez → "ya fue utilizado" (CA6).
    5. Iniciar sesión con una contraseña incorrecta → mensaje genérico (CA8); con la correcta → "Hola, nombre" (CA7).
    6. En "Mi perfil": cambiar el nombre (CA17), comprobar que el perfil no se puede cambiar (CA19), cambiar la contraseña (CA16) y pedir el cambio de correo (CA18).
    7. Cerrar sesión → aviso "Cerraste la sesión" (CA11).
    8. Recuperar la contraseña desde "¿Olvidaste tu contraseña?" y usar el enlace dos veces (CA13–CA15).
    9. Cinco intentos fallidos → correo de bloqueo en Mailpit (CA10).
    10. En las herramientas del navegador (F12 → Aplicación → Cookies), la cookie `sesion` tiene `HttpOnly` y `SameSite=Strict` (CA21).

## Cierre

- [ ] Pruebas, flake8, pylint, import-linter, ESLint y cobertura en verde.
- [ ] Criterios de aceptación de la especificación verificados.
- [ ] Entrada en la bitácora, ADR-0010, casillas y estado de la funcionalidad (asistente).
- [ ] Pull Request de `funcionalidad/002-cuentas-y-sesion` hacia `desarrollo` con la integración continua en verde (autora).
