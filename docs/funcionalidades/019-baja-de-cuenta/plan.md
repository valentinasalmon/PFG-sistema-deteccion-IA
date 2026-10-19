# Plan técnico: 019 — Eliminación de cuenta y copia de datos personales

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Un `ServicioDatosPersonales` reúne los dos derechos.

**Copia (RF09).**
- La copia se arma al momento a partir de los repositorios y no se guarda.
- `app/informes/copia_de_datos.py` la convierte en JSON y en PDF (WeasyPrint, con una plantilla Jinja2), sin depender de Flask.
- El enlace de descarga lleva un token de itsdangerous que vence a los 15 minutos. La ruta además exige la sesión, y el token tiene que ser de esa misma persona: si se filtra el enlace, no alcanza.
- El correo avisa que se generó la copia, sin enlace.

**Eliminación (RF08).**
- `situacion_para_baja` calcula qué falta resolver:
  - Casos a cargo.
  - Organizaciones donde es Referente con otros miembros.
  - Organizaciones donde es el único miembro, que se eliminan con la cuenta.
- La pantalla lleva a cada caso u organización, donde ya existen las acciones de transferir, eliminar y designar Referente. No se duplican esas reglas.
- `eliminar_cuenta` verifica la contraseña y vuelve a comprobar la situación. Después, en una sola transacción:
  - Elimina las organizaciones de un solo miembro (`ServicioOrganizaciones.eliminar_por_baja`, que reusa la eliminación de la 004 sin confirmar).
  - Quita membresías, accesos e invitaciones a su correo, y cancela las transferencias pendientes.
  - Registra la auditoría y elimina el usuario.
- La base pone en vacío el usuario de sus entradas de auditoría (`ON DELETE SET NULL`), así que no hace falta modificar el registro, que es de solo inserción.
- La ruta cierra la sesión actual. Las demás dejan de valer porque la cuenta ya no existe.

**SQLite en las pruebas.** Las claves foráneas quedan activas (`PRAGMA foreign_keys=ON`), así las pruebas verifican las mismas cascadas y la anonimización que aplica PostgreSQL.

## Capas afectadas

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Repositorios | `repositorio_usuarios.py` (`eliminar`), `repositorio_auditoria.py` (`de_usuario`, solo lectura), `repositorio_casos.py` (`casos_a_cargo`, `accesos_de_usuario`), `repositorio_organizaciones.py` (`invitaciones_de_correo`) | Consultas y baja |
| Servicios | `servicio_datos_personales.py`; `servicio_organizaciones.py` (`eliminar_por_baja`); `auditoria.py`, `tokens.py`, `servicio_correos.py`, `fabrica.py` | Reglas |
| Documentos | `app/informes/copia_de_datos.py`, `app/plantillas/informes/copia_de_datos.html` | JSON y PDF |
| Esquemas y rutas | `app/esquemas/datos_personales.py`, `app/rutas/perfil.py`, `app/seguridad/autenticacion.py` | API |
| Configuración | `VIGENCIA_COPIA_DATOS`; `extensiones.py` (claves foráneas en SQLite) | — |
| Frontend | `src/api/perfil.js`, `PaginaPerfil.jsx`, `Rutas.jsx` (aviso de cuenta eliminada), `PaginaPrivacidad.jsx`, estilos | Pantallas |
| Construcción | `requirements.txt` (`weasyprint==70.0`), integración continua (Pango) | Dependencias |

## Contratos

| Método y ruta | Respuesta |
|---|---|
| `POST /api/perfil/copia` | `{enlaces: {json, pdf}, vence_en, mensaje}` |
| `GET /api/perfil/copia/<json\|pdf>?token=…` | Archivo adjunto `mis-datos-AAAA-MM-DD.<formato>`, `Cache-Control: no-store` |
| `GET /api/perfil/baja` | `{casos, referente_de, a_eliminar, puede_eliminar}` |
| `DELETE /api/perfil` | Cuerpo `{"contrasenia"}`; 400 si es incorrecta, 409 `baja_pendiente` si falta resolver algo |

Acciones de auditoría nuevas: `cuenta.copia_solicitud`, `cuenta.copia_descarga` y `cuenta.eliminacion`.

## Cambios en datos

Ninguna tabla nueva ni migración.

## Bibliotecas nuevas

- **WeasyPrint 70.0**: HTML y CSS a PDF. Ya estaba prevista para el informe de la 008 (estructura del repositorio y ADR-0009). Necesita Pango, que ya instala el script de entorno de WSL y que se agrega a la integración continua.

## Estrategia de pruebas

- **Integración por la API**: copia completa y sin datos de terceros, PDF válido, enlaces ajenos, alterados y vencidos, y la exigencia de sesión.
- **Baja**: pendientes, contraseña incorrecta, eliminación con cascadas y anonimización, cierre de todas las sesiones, y volver a registrar el mismo correo.
- **Frontend**: secciones nuevas de "Mi perfil" con la API simulada.
- **Manual**: recorrido en navegador con PostgreSQL, y consulta de la auditoría anonimizada.

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Los correos en el detalle de la auditoría sobreviven a la baja | CP-20, con propuesta provisoria y alternativa (huella SHA-256), para validar con los tutores |
| Cuando existan imágenes (006) e informes (008), eliminar casos tiene que borrar los archivos | Anotado como pendiente: la baja usa la misma eliminación de casos |
| WeasyPrint tarda en cargar | Se importa solo al generar un PDF |
