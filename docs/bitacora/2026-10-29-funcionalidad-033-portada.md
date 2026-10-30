# 2026-10-29 — Funcionalidad 033: portada pública con los planes

## Qué se hizo

- **Dos propuestas de diseño** completas (A «Visor nocturno», oscura; B «Expediente claro», clara), en computadora y celular.
- **La autora eligió por sección**: encabezado, solución, «Para quién» y preguntas frecuentes de la B; problema y planes de la A. Pidió más diseño, aceptando esta versión para arrancar.
- **Portada implementada** (`PaginaPortada`, `estilos/portada.css`):
  - en `/` para quien no inició sesión (con sesión, `/` sigue siendo el Inicio) y en `/presentacion` para todos;
  - vista de la aplicación con escaneo animado y los indicios por capa apareciendo uno a uno;
  - cinta de capas en movimiento, secciones que aparecen al desplazarse, tarjetas con relieve al pasar el mouse y preguntas desplegables;
  - planes con los límites reales del sistema, precio «A confirmar» y un selector «Estudio jurídico / Aseguradora» que decide a qué registro lleva cada botón (`/registro?tipo=...&plan=...`).
- Capturas en `docs/funcionalidades/033-portada/capturas/`.

## Decisiones del agente

- **Número 033** (y no el 031, libre): la portada depende de la 032 y así queda en orden.
- **La portada vive en la misma aplicación**, no en un sitio aparte: comparte la identidad, las fuentes propias (la política de seguridad no permite fuentes externas) y los planes del sistema. Si más adelante hay un dominio propio, se decide ahí.
- **Al cerrar sesión desde `/`** se sigue yendo al inicio de sesión con el aviso «Cerraste la sesión», en vez de a la portada.
- **Todas las animaciones se apagan con «reducir movimiento»** y, sin `IntersectionObserver`, las secciones se ven de entrada.
- **Formato:** el repositorio no tiene configuración de Prettier y al formatear con sus valores por defecto se agregaron punto y coma en pantallas de la 032. Se devolvió el estilo del proyecto (sin punto y coma, comillas simples) con un commit propio en la rama 032.

## Calidad

- Frontend: 243 pruebas, eslint sin observaciones y compilación correcta.
- Recorrido en el navegador en computadora y en celular (390 px), con el selector de planes y las preguntas.

## Pendiente

- Más diseño, como pidió la autora (por ejemplo, ilustraciones propias, un video corto del análisis o testimonios cuando haya usuarios reales).
- Precios de los planes.
