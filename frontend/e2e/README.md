# Recorridos de punta a punta por la interfaz

Scripts de Playwright que usan el sistema como una persona: hacen clic, completan formularios, leen los correos del servidor SMTP de prueba y descargan el PDF. Se corren contra el entorno local levantado (backend, cola, SMTP de prueba y Vite) con la cuenta de prueba (`flask administracion cuenta-de-prueba`).

| Script | Qué recorre |
|---|---|
| `recorrido-aseguradora.cjs <capturas> <buzón SMTP>` (con `ASEG=<parte del nombre>` de una aseguradora sin registrar) | Registro de una aseguradora → pago simulado → verificación del correo → ingreso pendiente → verificación de identidad → aprobación del Administrador → menú con «Siniestros» → alta de un siniestro |
| `recorrido-abogado.cjs <capturas> <imágenes> [pc\|cel]` | Ingreso → caso nuevo → dos fotos → análisis → informe PDF descargado → verificación pública por código; `cel` emula un iPhone 13 |

## En la integración continua (039)

La verificación «Interfaz (sensor de diseño y recorrido de punta a punta)» levanta en GitHub Actions el backend (PostgreSQL y Redis como servicios), una abogada de demostración y el frontend, y corre el sensor de diseño y el recorrido del abogado en computadora y celular con dos imágenes sintéticas. El recorrido termina con error si falla un paso o si el sensor encuentra problemas; en ese caso se guardan las capturas y los registros como artefacto `recorrido-interfaz`. La cuenta del recorrido se elige con `RECORRIDO_CORREO` y `RECORRIDO_CLAVE` (por defecto, la cuenta de prueba local). El recorrido de la aseguradora queda manual: necesita leer los correos del servidor SMTP de prueba.

## Sensor de diseño

`sensor-diseno.cjs [base] [pantallas.json]` recorre las pantallas en computadora (1440 px) y celular (390 px) y falla si encuentra desplazamiento horizontal, contenido cortado, contenido escondido en un contenedor con desplazamiento propio (como un pago dentro de una tarjeta de alto fijo) o controles fuera de la pantalla; avisa además los objetivos táctiles de menos de 40 px. Con `SENSOR_CORREO` y `SENSOR_CLAVE` revisa también las pantallas con sesión. Los dos recorridos lo aplican en cada captura y terminan con «Sin problemas de diseño» o con la lista de problemas.

Resultado de la última corrida y capturas: `docs/funcionalidades/037-acceso-y-pantallas/evidencia.md`.

## Sensor de accesibilidad (041)

`accesibilidad.cjs [base] [pantallas.json]` revisa con [axe-core](https://github.com/dequelabs/axe-core) las mismas pantallas en computadora y celular contra las reglas de WCAG 2.1 nivel A y AA (contraste, nombres accesibles de botones y campos, títulos, idioma, regiones y ARIA). Falla con infracciones de impacto serio o crítico y avisa las moderadas. Corre sin animaciones (`prefers-reduced-motion`), porque las que aparecen al desplazarse dan falsos problemas de contraste. Necesita `npm install --no-save axe-core@4.10.3` (en la integración continua se instala junto con Playwright). Con un archivo de pantallas se revisan también un caso con su análisis o Administración.

Primera corrida (2026-11-16): dos problemas de contraste, corregidos (ver `docs/funcionalidades/041-accesibilidad/especificacion.md`).

## Sensor de uso con teclado (043)

`teclado.cjs [base]` recorre en computadora cada pantalla apretando Tab y falla si un elemento recibe el foco sin un indicador visible, si el foco cae en algo invisible o si queda atrapado; además inicia sesión usando solo el teclado (WCAG 2.1: 2.1.1, 2.1.2 y 2.4.7). Un campo de fecha nativo usa Tab para pasar entre día, mes y año, por eso se toleran hasta cinco Tab seguidos en el mismo control. Se comprobó que detecta el problema real quitando el contorno de foco a propósito. Primera corrida (2026-11-16): sin problemas en 9 pantallas.
