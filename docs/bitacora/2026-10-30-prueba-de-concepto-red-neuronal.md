# 2026-10-30 — Red neuronal (010): prueba de concepto completa (T24)

La autora ejecutó `01_prueba_de_concepto_colab.ipynb` en Colab Pro con GPU **Tesla T4**, sobre el commit `e6efee9` de `funcionalidad/010-red-neuronal`. El pipeline corrió **de punta a punta** y publicó la versión `0.1.0` en el registro local (Drive), no en Hugging Face. Ejecución de MLflow: `cf3ddf07889b4827b7945e34d4f256dc`.

## Tiempos por etapa (10 000 imágenes de Community Forensics *Small*, 5 000 reales y 5 000 sintéticas)

| Etapa | Segundos |
|---|---|
| obtener | 218,9 |
| validar | 32,6 |
| preparar | 337,4 |
| entrenar (3 épocas) | 19,7 |
| exportar | 17,5 |
| evaluar | 41,3 |
| publicar | 6,3 |
| **Total** | **673,7 (≈ 11 min)** |

Disco ocupado al final: 54,4 GB. Es todo el disco de Colab, incluido el sistema; no lo usa solo la prueba.

## Métricas (sin umbral exigido: CA1)

| Métrica | Valor |
|---|---|
| AUC de validación (mejor época, la 2) | 0,981 |
| **AUC de prueba** | **0,985** |
| Exactitud de prueba (umbral 0,5) | 0,933 |
| Precisión / exhaustividad / F1 de prueba | 0,941 / 0,924 / 0,933 |
| ECE antes y después de calibrar (validación) | 0,047 → 0,021 (temperatura 2,35) |
| ECE de prueba | 0,052 |
| Diferencia máxima ONNX frente a PyTorch | 2,6 × 10⁻⁶ |
| Latencia en CPU por imagen (ONNX) | 24,3 ms (26,6 ms con 5 recortes) |

## Lectura

- **El diseño queda validado (CA1):** todas las etapas se conectan, el modelo ONNX coincide con el de PyTorch y corre en CPU en unos 25 ms por imagen. Alcanza holgado para el backend (funcionalidad 012).
- **Las métricas son optimistas y no anticipan el desempeño real:** la prueba usa una sola fuente, sin generadores reservados como no vistos y sin el conjunto propio (WhatsApp, capturas, generadores comerciales). Esas condiciones se miden recién en el entrenamiento completo (T30 y T32).
- **La tabla por generador no es concluyente:** con unas 3 imágenes de cada generador en la prueba, la exactitud y la precisión por generador son ruido estadístico. Los más débiles fueron BigGAN (exhaustividad 0,62, el único GAN clásico), `riteshjha01/my-pet-cat` (AUC 0,79) y algunos ajustes finos de Stable Diffusion. Para la receta v1 (T27) se proponen menos generadores con más imágenes cada uno, y en la ficha, publicar por generador solo los grupos con un mínimo de imágenes.
- **El entrenamiento es la parte más rápida** (≈ 7 s por época con precisión mixta). Lo que pesa es descargar y preparar las imágenes (≈ 82 % del tiempo).

## Estimación del entrenamiento completo

Escalando de forma lineal, con una receta v1 de unas 100 000 imágenes:

- obtener + validar + preparar: unos 100 minutos;
- entrenar 15 épocas: unos 30 a 40 minutos en T4;
- exportar, evaluar y publicar: unos 10 minutos.

En total, **2 a 3 horas en una T4**, dentro de una sesión de Colab Pro. No hace falta una GPU más cara. Se recomienda que el cuaderno retome sin repetir etapas terminadas y que el entrenamiento guarde un punto de control por época, para no depender de la inactividad.

## Incidentes de la corrida

- Faltaba `HF_TOKEN` y el primer `GITHUB_TOKEN` no tenía acceso al repositorio: se corrigió y el cuaderno ahora lo explica en español.
- La salida de las etapas no se veía en Colab: corregido (commit `e6efee9`).
- Una desconexión por inactividad durante «validar»: se retomó con el respaldo de Drive.

## Pendiente

- T25 a T27: exploración de datos, protocolo del conjunto propio y receta v1, con generadores no vistos y mínimo por generador.
- Cuaderno de entrenamiento que retome sin repetir etapas (antes de T30).
- E03 y E04 (autora): repositorio privado de modelos en Hugging Face y conjunto propio.
