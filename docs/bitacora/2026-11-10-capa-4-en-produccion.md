# 2026-11-10 — Capa 4 en producción y portada

## Qué se hizo

- **T08 de la 012 (autora)**: publicó el modelo `1.0.0` en Hugging Face, cargó `HF_TOKEN` y `MODELO_RED_NEURONAL_*` en Parameter Store y desplegó. La capa 4 funciona en producción.
- **Portada**: se quitó «Próximamente» de la mirada «Imagen con IA» (lo había decidido la autora en la 037 hasta integrar la 012). Los términos ahora describen las cuatro técnicas.
- **Verificación**: lint y 284 pruebas del frontend; sensor de diseño sin problemas en `/` y `/terminos`, en computadora y celular; capturas de la sección «Cuatro miradas» revisadas.
- **Documentación**: capítulos 7 y 12 de la red neuronal, estado de la 012, insumos.

## Hallazgo

- La primera prueba de la autora dio una probabilidad cercana a 0 % en una imagen del conjunto propio. Coincide con el 10 % de detección medido en esas imágenes en la 010: el modelo no conoce los generadores comerciales actuales. No es una falla de la integración.

## Pendiente

- Saber qué imagen se probó (real o generada, y con qué herramienta) para confirmar la lectura.
- Fotos reales para el conjunto propio, o una muestra de CarDD como alternativa.
- Versión `1.1.0` con generadores comerciales recientes en el entrenamiento.
