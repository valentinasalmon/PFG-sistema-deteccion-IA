# 2026-11-11 — Red neuronal: mejora continua por versiones

## Decisión de la autora

La red se mejora de forma continua con datos nuevos, por versiones MINOR. El conjunto propio se separa en **evaluación fija** (nunca entrena) y **ajuste** (puede entrenar). Una versión se publica solo si pasa la compuerta: AUC de prueba ≥ 0,90, mejora frente a la anterior en la evaluación fija y sin empeorar en los generadores no vistos. Orden: `1.0.0` (publicada el 2026-11-10), repetición T31 y después `1.1.0` con la familia de Google y la parte de ajuste. Corte para el informe: 16/11. Queda en el [ADR-0022](../arquitectura/decisiones/0022-mejora-continua-de-la-red-por-versiones.md).

## Qué se hizo

- **Regla de separación** (`red_neuronal/clasificador/datos/particion_propia.py`, 7 pruebas) y **tabla fija** de los 89 prompts (`red_neuronal/configuracion/particion_conjunto_propio.csv`). Queda mitad y mitad en cada escena y en cada tono de piel: 45 de evaluación y 44 de ajuste. Paquete: 216 pruebas, 96,6 % de cobertura, flake8 y pylint en verde.
- **Revisión del conjunto propio en Drive**: 106 imágenes sintéticas, que son 53 imágenes en dos variantes. ChatGPT tiene los prompts 1 a 15 y 17 a 19; Gemini, 1 a 15 y 17 a 20; Copilot, 1 a 15 y 17. Todas tienen original y captura. Todavía no hay fotos reales.
- **Documentación**: ADR-0022, capítulos 4 y 12, glosario, protocolo, guía (columna «Lado» de la planilla), tareas T36 a T40 de la 010, cuestiones CP-44 y CP-45.

## Decisiones del agente

- **Se asigna por prompt y no por archivo.** Con la huella de cada archivo, la versión de ChatGPT de una escena podría quedar en ajuste y la de Gemini en evaluación: sería una fuga.
- **Tabla fija para la lista maestra** en lugar de una huella pura: con 15 prompts por escena, una huella sola deja escenas desparejas. La tabla se generó una vez y una prueba verifica que coincide con la regla.
- **Mejora sin fotos reales:** se mide con la detección y sin que suban los falsos positivos de la prueba, y se declara la limitación.

## Hallazgos de la revisión

- **Nombres de los rayones:** los archivos se llaman `01-rayon-0NN`, y la planilla dice `02-rayon-0NN`. El lado no cambia, porque depende del número, pero la escena se lee del prefijo: hay que renombrarlos a `02-…`.
- **Falta el prompt 16** en la planilla (pasa del 15 al 17).
- La carpeta `REAL/CELULAR PROPIO` tiene espacio en el nombre y una subcarpeta `WHATSAPP`, que ya no se usa.
- Con la parte de ajuste actual (unas 50 imágenes) frente a 35 000 de entrenamiento, el efecto sería mínimo sin repetirlas en cada época: la receta de la `1.1.0` lo define.

## Pendiente

- T31 (repetición), T37 a T40.
- CP-44 (no visto de la `1.1.0`) y CP-45 (términos de uso de las herramientas), para la autora.
- Fotos reales de las mismas escenas.
