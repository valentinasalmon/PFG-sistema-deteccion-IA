# Plan técnico: 034 — Pulido de UX/UI

Referencia visual: mockups v3 (artefacto «Mockups de evidentIA», 49 pantallas con código).

## Orden de implementación

1. **Base**: tokens y componentes en `global.css`; avisos flotantes arriba; diálogo reutilizable (`Dialogo.jsx`) con X, Esc, clic afuera y foco atrapado; íconos nuevos.
2. **Acceso y registro** a pantalla completa (`DisposicionAcceso`), sin el panel de marca; el registro muestra «Paso N de M · nombre» con barra fina.
3. **Caso como flujo vertical** (`PaginaCaso`, `FlujoCaso.jsx`): pasos Imágenes, Análisis e Informe con estado, resumen y cuerpo; datos del caso en una línea bajo el título; Editar, Compartir y «⋯».
4. **Inicio, Casos y Nuevo caso**.
5. **Organización en pestañas, perfil y administración**.
6. **Páginas públicas** y estados vacíos con ilustraciones.
7. **Portada** con ilustraciones propias y animaciones.
8. **Novedades**: Ctrl K y comparador de la foto con su mapa de error.
9. **Clarity**: `utilidades/clarity.js` carga el script solo si `VITE_CLARITY_ID` está definido; Terraform y la guía de despliegue suman la variable.

Cada tanda: pruebas del frontend actualizadas, lint, build y revisión en el navegador en computadora y celular.
