# 2026-10-28 — Integración continua en verde e inicio con Google (027)

## Qué se hizo

- **Integración continua**: los últimos Pull Requests hacia `desarrollo` y `main` estaban en rojo por dos motivos.
  - **Una línea de 107 caracteres en `rutas/verificacion.py`** (flake8, E501). Se corrigió en la rama `correccion/integracion-continua`.
  - **La validación de mensajes de commit** fallaba en los Pull Requests de integración (`desarrollo` → `main` y al revés). Volvía a revisar commits ya integrados, entre ellos fusiones escritas en GitHub con títulos como "Versión: …". Ahora no se ejecuta en esos Pull Requests: sus commits ya se validaron en su propio Pull Request.
- **Funcionalidad 027**: "Continuar con Google" en el inicio de sesión y en el registro, también con invitación.
  - La primera vez, la persona completa:
    - el perfil;
    - nombre y apellido (vienen de Google);
    - la institución;
    - los Términos.
  - Con un correo existente, se vincula a esa cuenta.
- **Calidad**:
  - backend: 515 pruebas, cobertura del 97,5 %, pylint 10/10, import-linter con 3 contratos;
  - frontend: 212 pruebas.

## Decisiones

- **El paso del rubro es obligatorio la primera vez** (decisión de la autora). Google no informa si la persona es abogada o trabaja en una aseguradora, y de eso dependen el lenguaje, los permisos y el informe.
- **Flujo del lado del servidor con PKCE y sin biblioteca de JWT** (ADR-0019). No se carga JavaScript de Google y la CSP no cambia.
- **La cookie de sesión pasa a `SameSite=Lax`**: con `Strict`, la vuelta desde Google perdía la sesión. La protección CSRF sigue igual.
- **Se evita el secuestro previo de cuentas**: si alguien registró el correo y no lo verificó, al entrar el dueño con Google se anula esa contraseña y se cierran sus sesiones.
- **El acceso con Google no cuenta para el bloqueo por intentos fallidos**: el bloqueo protege la contraseña, y con Google no se escribe ninguna.

## Pendiente

- La autora crea el cliente OAuth en Google Cloud y lo carga en local y en SSM (guía en `despliegue-aws.md`).
- Probar si Google acepta la dirección `sslip.io`. Si no, se prueba en local hasta comprar el dominio (CP-30).
- Desvincular Google desde el perfil: trabajo futuro.

## Prueba en local (2026-10-26)

- La autora creó el proyecto y el cliente OAuth en Google Cloud (modo de prueba) y probó el ingreso en local: funciona.
- Problema encontrado: el botón no aparecía aunque las claves estaban en `.env`. Seguía respondiendo un backend que había arrancado antes de cargarlas: el modo de depuración de Flask se reinicia cuando cambia el código, no cuando cambia el `.env`. Se agregó a la guía cómo comprobarlo sin mostrar el secreto.
- Falta probarlo en producción (T11).
