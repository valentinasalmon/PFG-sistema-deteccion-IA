# ADR-0011: Arquitectura y contrato de inferencia del clasificador

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Requisitos relacionados**: RF42, RNF24, RN27, RN29

## Contexto

La capa 4 debe estimar en CPU, con ONNX Runtime, la probabilidad de que una imagen sea íntegramente sintética (RF42). Debe ser rápida en un servidor sin GPU, robusta a la recompresión de las aplicaciones de mensajería y entrenable con la GPU gratuita de Kaggle. Además, el preprocesamiento del entrenamiento y el del backend deben ser idénticos: una diferencia mínima, como un reescalado distinto, degrada el modelo sin que nadie lo note.

## Alternativas evaluadas

### Arquitectura base

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| ResNet-50 | Clásica y muy estudiada en detección de imágenes sintéticas | 25 M de parámetros; más lenta en CPU |
| **EfficientNet-B0** | 5,3 M de parámetros; rápida en CPU; buena exactitud por transferencia; exportación a ONNX sin problemas | Menor capacidad que modelos grandes |
| ConvNeXt-Tiny | Mejor exactitud en general | 28 M de parámetros; más costosa en Kaggle y en CPU |
| Transformadores visuales o CLIP | Mejor generalización según la literatura reciente | No es una red convolucional, como pide RF42; pesados en CPU |

### Tratamiento del tamaño de la imagen

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Reescalar toda la imagen a 224 px | Simple | Borra las huellas de alta frecuencia que delatan la generación |
| **Recortes de 224 px sin reescalar, promediados** | Conserva las huellas; usa varias zonas de la imagen | Cinco inferencias por imagen |

### Ubicación del preprocesamiento

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Reimplementarlo en el backend | Sin dependencia entre componentes | Dos implementaciones que pueden divergir |
| **Subpaquete `clasificador.inferencia` sin PyTorch, usado por la evaluación y por el backend** | Una sola implementación, probada contra el modelo original | El backend depende de un paquete del monorepositorio |

## Decisión

- **EfficientNet-B0** preentrenada en ImageNet (vía timm), ajustada como clasificador binario. La fábrica de modelos permite comparar ConvNeXt-Tiny en un experimento si EfficientNet-B0 no alcanza el umbral.
- **Calibración** por *temperature scaling* sobre la partición de validación. La temperatura y la sigmoide se incluyen en el grafo ONNX, que devuelve directamente la probabilidad calibrada.
- **Contrato de entrada**: cinco recortes RGB de 224 × 224 (esquinas y centro) sin reescalar, salvo que el lado mayor supere 1024 px o el lado menor sea inferior a 224 px. Normalización de ImageNet. La probabilidad final es el promedio de los recortes.
- **Metadatos en el ONNX**: versión, arquitectura, temperatura, tamaño de recorte, normalización, huella del manifiesto y commit.
- **`clasificador.inferencia`** solo depende de numpy, Pillow y onnxruntime. El backend lo instala como dependencia en la funcionalidad 012.

## Consecuencias

- La inferencia en CPU queda en el orden de decenas de milisegundos por imagen. Se medirá en la exportación (CA14).
- La salida es una probabilidad, no una clase: no se fija un umbral de decisión en el producto, lo que es coherente con no emitir veredictos (RN27). El umbral de 0,5 se usa solo para reportar exactitud, precisión, exhaustividad y F1.
- Cambiar el contrato de entrada obliga a una versión `MAJOR` del modelo.
- La funcionalidad 012 debe instalar `red_neuronal` como paquete en el backend.
