# 2026-11-06 — Funcionalidad 012: capa 4 (red neuronal con ONNX)

## Qué se hizo

- **Especificación, plan y tareas** de la 012 (`docs/funcionalidades/012-capa-4-onnx/`).
- **Dependencias**: `onnxruntime` y `huggingface_hub` en el backend, `onnx` solo para las pruebas, y el paquete `clasificador` instalado sin dependencias (sin PyTorch) en la integración continua y en el despliegue.
- **Configuración**: `MODELO_RED_NEURONAL_REGISTRO`, `MODELO_RED_NEURONAL_VERSION` y `CARPETA_MODELOS_ONNX`, sin valores por defecto; `generar_entorno.sh` las copia del Parameter Store junto con `HF_TOKEN`.
- **Obtención del modelo** (`app/integraciones/modelo_red_neuronal.py`): registro local o de Hugging Face, versión fija, huella verificada, caché por proceso y motivo legible ante cualquier falla.
- **Capa 4** (`app/analisis/red_neuronal.py`): nivel, anomalía, conclusión con las limitaciones, tabla de criterios y versiones (RN29). Registrada después de ELA.
- **Informe PDF y pantalla del caso**: título, «¿Qué significa?», tabla y progreso con cuatro capas.
- **Pruebas**: 30 unitarias de la capa y del modelo con un ONNX diminuto, 2 de integración (con y sin modelo), 2 de configuración, 1 del informe y 1 del frontend. Backend: 602 pruebas, 97 % de cobertura; frontend: 274.
- **Documentación**: capítulo 7 de `docs/red-neuronal/`, guía de activación en `despliegue-aws.md`, guía de usuario, insumos.

## Decisiones

- **Se integró antes de tener el modelo publicado.** Con solo unas 8 imágenes del conjunto propio, la 010 no puede cerrarse todavía; la 012 no depende de eso, porque sin modelo la capa queda «No disponible» (RN26). Así, publicar la `1.0.0` alcanza para activarla.
- **Umbral de consideración en 50 %** y nivel igual a la probabilidad (tope 90), leído con la escala común de las otras capas. Con una probabilidad calibrada, el número se explica solo.
- **El modelo se guarda en `/opt/plataforma/modelos_onnx`**, fuera de cada versión desplegada, para no bajarlo en cada despliegue; si ya está, se vuelve a verificar su huella.
- **La versión de la capa no carga el modelo**: el proceso web la informa al crear el análisis con la versión configurada.
- **Desempeño publicado en la tabla** solo para versiones con ficha (`1.0.0`); una versión sin ficha no muestra métricas.
- Sin ADR nuevo: aplican ADR-0006, ADR-0014, ADR-0015 y ADR-0017.

## Hallazgos

- `generar_entorno.sh` solo copia las variables que nombra: sin el cambio, la capa nunca se habría activado en producción. Se encontró al escribir la guía, no con las pruebas.
- En el PDF se ve la versión del modelo en la tabla de la capa; las huellas y el commit quedan en el resultado guardado, como en las otras capas.

## Pendiente

- **T08 (autora)**: publicar la `1.0.0` en Hugging Face, cargar `HF_TOKEN` y `MODELO_RED_NEURONAL_*` en Parameter Store y analizar un caso en producción, con la guía de `despliegue-aws.md`.
- Seguir con el conjunto propio (fotos reales de autos) y la evaluación en condiciones reales de la 010.
