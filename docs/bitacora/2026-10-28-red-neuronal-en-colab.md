# 2026-10-28 — La red neuronal (010) pasa de Kaggle a Google Colab

## Qué se hizo

- Se retomó la rama de la funcionalidad 010 (`funcionalidad/010-red-neuronal`) y se le integró `desarrollo`.
- Nuevo cuaderno `red_neuronal/cuadernos/01_prueba_de_concepto_colab.ipynb`, versión para Colab del cuaderno de Kaggle:
  - lee `HF_TOKEN` y `GITHUB_TOKEN` desde los *Secrets* de Colab; nunca se imprimen;
  - clona el repositorio en la rama de la funcionalidad e instala el paquete `clasificador`;
  - monta Google Drive y, después de cada etapa, respalda el trabajo y el registro en `MyDrive/evidentia/prueba_de_concepto` (sin las imágenes);
  - si Colab corta la sesión, restaura desde Drive y retoma en la última etapa completa.
- La especificación, el plan, las tareas, la guía del ciclo de vida y las cuestiones CP-21 pasan a nombrar Colab. Las versiones de datos se guardan en carpetas privadas de Drive en lugar de en Kaggle Datasets.

## Decisiones

- **Colab gratuito primero.** La GPU T4 alcanza para EfficientNet-B0 con recortes de 224 px. Si las sesiones se cortan antes de terminar una época, o no hay GPU disponible, se evalúa Colab Pro: unos US$ 10 por mes, o 100 unidades de cómputo por unos US$ 10 sin suscripción.
- **Respaldo en Drive después de cada etapa.** Reemplaza a la salida persistente de Kaggle. Las etapas ya escriben en disco, así que el *pipeline* no cambia: solo el cuaderno.
- Se mantiene el cuaderno de Kaggle `00_…` como alternativa, sin cambios.

## Pendiente

- E05: *token* de GitHub de solo lectura en los *Secrets* de Colab (lo hace la autora).
- T24: ejecutar la prueba de concepto en Colab y registrar tiempos y métricas.
- T25 a T33: datos reales, entrenamiento completo, evaluación y publicación.
