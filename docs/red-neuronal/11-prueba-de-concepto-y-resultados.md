# 11. Prueba de concepto y resultados

Este capítulo registra **cada corrida** del modelo, de la más nueva a la más vieja. Cada corrida nueva agrega su sección.

## Corrida 1 · Prueba de concepto · 2026-10-30 · versión 0.1.0

| | |
|---|---|
| Objetivo | Validar el pipeline de punta a punta y medir tiempos (CA1). Sin umbral de desempeño |
| Entorno | Google Colab Pro, GPU Tesla T4, Python 3.13.16, PyTorch 2.11.0 |
| Código | Commit `e6efee9` de `funcionalidad/010-red-neuronal` |
| Datos | Community Forensics *Small*: 5 000 reales + 5 000 sintéticas, semilla 42, sin generadores reservados |
| Particiones | 7 999 entrenamiento · 999 validación · 1 002 prueba |
| Configuración | `prueba_de_concepto.yaml`: EfficientNet-B0, 3 épocas, lote 64, tasa 0,0003, paciencia 2 |
| Experimento MLflow | `cf3ddf07889b4827b7945e34d4f256dc` |
| Huella del ONNX | `67ef3e3f…bbd924` |
| Registro | Local, en Drive. **No** publicado en Hugging Face |

### Tiempos

| Etapa | Segundos | % |
|---|---|---|
| obtener | 218,9 | 32 % |
| validar | 32,6 | 5 % |
| preparar | 337,4 | 50 % |
| entrenar (3 épocas) | 19,7 | 3 % |
| exportar | 17,5 | 3 % |
| evaluar | 41,3 | 6 % |
| publicar | 6,3 | 1 % |
| **Total** | **673,7 (≈ 11 min)** | |

### Métricas

| Métrica | Valor |
|---|---|
| AUC de validación (mejor época: la tercera) | 0,981 |
| **AUC de prueba** | **0,985** |
| Exactitud (umbral 0,5) | 0,933 |
| Precisión · Exhaustividad · F1 | 0,941 · 0,924 · 0,933 |
| Temperatura | 2,35 |
| ECE en validación, antes → después de calibrar | 0,047 → 0,021 |
| ECE en prueba | 0,052 |
| Diferencia ONNX frente a PyTorch | 0,0000026 |
| Latencia en CPU | 24,3 ms por imagen (26,6 ms con los cinco recortes en la ficha) |

### Cómo leerlo

**Lo que sí demuestra:**
- **el diseño funciona:** las siete etapas se conectan, la validación y la compuerta corren, se genera la ficha y queda el experimento en MLflow;
- **el modelo que llega a producción es fiel:** el ONNX coincide con PyTorch casi exactamente;
- **alcanza la CPU del servidor:** unos 25 ms por foto;
- **la calibración funciona:** bajó el error de calibración a menos de la mitad.

**Lo que no demuestra:**
- **el desempeño real.** El AUC de 0,985 es optimista: hay una sola fuente, no hay generadores reservados, no hay generadores comerciales (ChatGPT, Gemini) y no hay fotos pasadas por WhatsApp. Esas condiciones se miden en el entrenamiento completo con el conjunto propio. **No hay que presentar estas cifras como el desempeño del sistema.**

**La tabla por generador no es concluyente.** Con unas 3 imágenes por generador en la prueba, las métricas por generador son ruido estadístico. Igual aparecen pistas:
- **BigGAN**, el único GAN clásico, fue el más difícil (exhaustividad 0,62);
- algunos ajustes finos de Stable Diffusion bajaron a AUC 0,79 a 0,89;
- **DeepFloyd** y **GLIDE** se detectaron bien (exhaustividad 0,95 y 1,0).

**Dónde se va el tiempo:** el 82 % en bajar y preparar imágenes. El entrenamiento en sí tardó unos 7 segundos por época.

### Incidentes

- Faltaba `HF_TOKEN`, y el primer `GITHUB_TOKEN` no tenía acceso al repositorio. Se corrigió y el cuaderno ahora lo explica en español.
- La salida de las etapas no se veía en Colab. Se corrigió en el commit `e6efee9`.
- Hubo una desconexión por inactividad durante «validar», y se retomó con el respaldo de Drive.

### Qué se aprendió para la receta v1

1. **Menos generadores, más imágenes por cada uno**, para que las métricas por generador signifiquen algo. En la ficha conviene publicar por generador solo los grupos con un mínimo de imágenes.
2. **Reservar generadores como «no vistos»**, para medir la generalización (CA6).
3. **Sumar fuentes con generadores comerciales recientes** (OpenFake, ShareGPT-4o-Image).
4. **Más épocas:** con 3 la mejor fue la última, así que el modelo todavía podía mejorar.

### Estimación del entrenamiento completo

Con unas 100 000 imágenes, escalando de forma lineal:
- obtener, validar y preparar: unos 100 minutos;
- entrenar 15 épocas: unos 30 a 40 minutos en una T4;
- exportar, evaluar y publicar: unos 10 minutos.

En total, **2 a 3 horas en una T4**. Cabe en una corrida de Kaggle en segundo plano o en una sesión de Colab Pro.
