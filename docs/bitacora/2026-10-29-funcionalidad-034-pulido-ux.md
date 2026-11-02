# 2026-10-29 — Funcionalidad 034: pulido de UX/UI, primera tanda

## Qué se hizo

- **Relevamiento** de las 15 rutas en computadora y celular (capturas) y **mockups de 49 pantallas** en tres versiones, con código por pantalla, cambios y «mapa de salidas». La autora validó la versión 3 con estos cambios:
  - acceso a pantalla completa, solo con el logo y el nombre;
  - campos más cortos y todo centrado;
  - el caso como flujo (no cajas);
  - avisos arriba y diálogos con X;
  - colores e íconos representativos;
  - no quitar información importante.
- **Base común:** botones de 40 px con estados, campos de 40 px con anillo de foco, formularios de ancho acotado, avisos flotantes arriba (arriba al centro en el celular) y `Dialogo` reutilizable con X, Esc, clic afuera y foco atrapado. `BotonConfirmar` ahora pregunta en ese diálogo.
- **Acceso y registro a pantalla completa:** tarjeta centrada con el logo; sin el panel de marca dividido; las tres opciones del registro en una fila y con textos de una línea.
- **El caso como flujo vertical:** Imágenes → Análisis → Informe unidos por una línea.
  - Solo se abre un paso por vez.
  - Los terminados quedan en verde con su resumen y «Ver».
  - Los pendientes dicen cuándo se habilitan.
- **Portada:**
  - ilustraciones propias (`Ilustraciones.jsx`) en el problema, la solución y «Para quién»;
  - sección nueva «Cómo funciona» en tres pasos, con la foto que se escanea.

## Decisiones

- **Clarity:** lo usa la autora para revisar el uso antes del lanzamiento; no se muestra nada a los usuarios. Se cargará solo con su identificador configurado y con enmascarado estricto (pendiente, tanda siguiente).
- **Se reutilizaron las secciones existentes** (imágenes, análisis, informes) dentro del flujo, para no perder funcionalidad ni pruebas.

## Calidad

- Frontend: 243 pruebas, eslint sin observaciones y compilación correcta.
- Revisión en el navegador del acceso, el registro, el caso y la portada, en computadora y celular.

## Pendiente (próximas tandas, pantalla por pantalla con la autora)

- Inicio, Casos y Nuevo caso.
- Organización en pestañas, perfil y administración.
- Páginas públicas y estados vacíos con ilustraciones.
- Ctrl K y comparador de la foto con el mapa de error.
- Clarity configurable.
