# Recorridos de punta a punta por la interfaz

Scripts de Playwright que usan el sistema como una persona: hacen clic, completan formularios, leen los correos del servidor SMTP de prueba y descargan el PDF. Se corren contra el entorno local levantado (backend, cola, SMTP de prueba y Vite) con la cuenta de prueba (`flask administracion cuenta-de-prueba`).

| Script | Qué recorre |
|---|---|
| `recorrido-aseguradora.cjs <capturas> <buzón SMTP>` (con `ASEG=<parte del nombre>` de una aseguradora sin registrar) | Registro de una aseguradora → pago simulado → verificación del correo → ingreso pendiente → verificación de identidad → aprobación del Administrador → menú con «Siniestros» → alta de un siniestro |
| `recorrido-abogado.cjs <capturas> <imágenes> [pc\|cel]` | Ingreso → caso nuevo → dos fotos → análisis → informe PDF descargado → verificación pública por código; `cel` emula un iPhone 13 |

## Sensor de diseño

`sensor-diseno.cjs [base] [pantallas.json]` recorre las pantallas en computadora (1440 px) y celular (390 px) y falla si encuentra desplazamiento horizontal, contenido cortado, contenido escondido en un contenedor con desplazamiento propio (como un pago dentro de una tarjeta de alto fijo) o controles fuera de la pantalla; avisa además los objetivos táctiles de menos de 40 px. Con `SENSOR_CORREO` y `SENSOR_CLAVE` revisa también las pantallas con sesión. Los dos recorridos lo aplican en cada captura y terminan con «Sin problemas de diseño» o con la lista de problemas.

Resultado de la última corrida y capturas: `docs/funcionalidades/037-acceso-y-pantallas/evidencia.md`.
