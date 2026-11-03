# Plan técnico: 033 — Portada pública

## Frontend

- **`PaginaPortada`** en `paginas/`, con sus estilos en `estilos/portada.css` (todas las clases con el prefijo `portada`), para no cargar más `global.css`.
- **Ruta**: la guarda nueva `RutaPortada` muestra la portada en `/` sin sesión y deja pasar al Inicio con sesión. `/presentacion` la muestra siempre (útil para presentarla).
- **Planes**: `listarPlanes()` (API pública de la 032). Si no responde, las tarjetas se muestran sin los límites.
- **Selector de organización** con botones de opción nativos: cambia el `tipo` de los enlaces de Básico y Profesional.
- **Animaciones**: `IntersectionObserver` agrega la clase que hace aparecer cada sección (sin él, todo se ve de entrada). El escaneo y la cinta son CSS y quedan apagados con `prefers-reduced-motion`.
- **Preguntas frecuentes** con `<details>` nativos: accesibles sin JavaScript extra.
- Íconos nuevos en `Icono`: `capas` y `escudo`.

## Backend

- Sin cambios: usa `GET /api/catalogos/planes`.

## Pruebas

- Portada sin sesión, Inicio con sesión, enlaces de los planes según el selector, «A confirmar» y descargo de responsabilidad.
