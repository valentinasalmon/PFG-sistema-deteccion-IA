# 11. Prueba de concepto y resultados

Este capítulo registra **cada corrida** del modelo, de la más nueva a la más vieja. Cada corrida nueva agrega su sección.

## Corrida 2 · Entrenamiento completo con la receta v1 · 2026-11-05 · versión 1.0.0 (sin publicar todavía)

| | |
|---|---|
| Objetivo | Entrenamiento completo (T30) con la receta v1 depurada |
| Entorno | Google Colab Pro, cuaderno `03_entrenamiento_completo_colab.ipynb` |
| Código | Commit `0ee4e9e` de `funcionalidad/010-red-neuronal` |
| Datos | 17 500 reales y 17 500 sintéticas: Community Forensics (7 500 + 7 500) y OpenFake (10 000 + 10 000), 210 generadores. Validación sin errores |
| Huella del manifiesto | `9ad67940…f929c480` |
| Configuración | `v1.yaml`: EfficientNet-B0, 15 épocas, lote 64, tasa 0,0003, paciencia 3 |
| Experimento MLflow | `a2c520ed7fc14b9985a6ebe35abe28dc` |
| Tiempos | validar 194 s; preparar 2 900 s (48 min). El entrenamiento terminó a las 18:06 y la evaluación a las 18:10 |

### Entrenamiento

El AUC de validación subió de 0,875 (época 0) a **0,948 (época 12)**, la mejor; las épocas 13 y 14 no mejoraron. La pérdida de entrenamiento bajó de 0,85 a 0,09. Temperatura **2,36**; ECE de validación **0,069 → 0,020**.

### Resultados

| Conjunto | AUC | Otras métricas (umbral 0,5) |
|---|---|---|
| **Prueba** (generadores conocidos, 1 750 reales y 1 696 sintéticas) | **0,961** | Exactitud 0,909 · precisión 0,940 · exhaustividad 0,870 · **F1 0,904** · ECE 0,085 |
| **No visto: familia de Google** (219 sintéticas contra las 1 750 reales de prueba) | **0,938** | Detecta el 74 % (161 de 219). Imagen 4: AUC 0,949; Imagen 3: 0,929; Nano Banana 2: 0,855 (solo 17 imágenes) |
| **Condiciones reales: conjunto propio** (49 imágenes de choques: ChatGPT 12, Copilot 17, Gemini 20; original y captura) | — (no hay reales todavía) | **Detecta solo 5 de 49 (10 %)**: Gemini 3/20, ChatGPT 1/12, Copilot 1/17. Original 3/24, captura 2/25 |
| Exportación ONNX | — | Diferencia con PyTorch 0,0000015 · 22,9 ms por imagen en CPU |

**Por generador (prueba, grupos con 20 o más sintéticas):** los ajustes de SDXL, SD 1.5 y StyleGAN2 superan 0,99. Los más difíciles: VQDiffusion (0,67), GigaGAN (0,62, solo 17 imágenes), SDXL RealVis (0,87), Midjourney 6 (0,92; detecta el 68 %), FLUX 1.1 Pro (0,93; detecta el 54 %) y GPT Image 1 (0,94; detecta el 74 %).

### Cómo leerlo

- **Cumple los dos criterios** que estaban en discusión (CP-07): AUC de prueba 0,961 ≥ 0,90 y F1 0,904 ≥ 0,85. El modelo está bien calibrado (ECE 0,02 en validación).
- **Generaliza razonablemente a una familia comercial que no vio** (Google: AUC 0,938), aunque detecta menos que en la prueba (74 % contra 87 %).
- **El hallazgo más importante es negativo:** con las imágenes que generó la autora con ChatGPT, Gemini y Copilot en la escena de choques, el modelo detecta apenas una de cada diez con el umbral 0,5. Con tan pocas imágenes y sin fotos reales de choques no se puede calcular el AUC, así que todavía no se sabe si el modelo las ordena bien con otro umbral o si directamente no las distingue. Las razones posibles: las herramientas de 2025 y 2026 son más nuevas que los generadores del entrenamiento, y las escenas de autos dañados no están en los datos de entrenamiento.
- **Qué hacer:** sumar fotos reales de choques al conjunto propio (CarDD y fotos propias) para calcular el AUC por escena; ampliar el conjunto propio a las demás escenas; y, en la versión 1.1.0, sumar al entrenamiento generadores comerciales recientes (la familia de Google y, si se puede leer, MLLM-Generated con GPT Image 2 y Nano Banana 2). **Ninguna imagen del conjunto propio se usa para entrenar** (CA12).
- **Falta publicar:** no se ejecutó la celda de publicación (no hay `compuerta.json`). Con estas métricas la compuerta debería aprobar.

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
- **el desempeño real.** El AUC de 0,985 es optimista: hay una sola fuente, no hay generadores reservados, no hay generadores comerciales (ChatGPT, Gemini) y no hay capturas de pantalla ni fotos de las escenas del sistema. Esas condiciones se miden en el entrenamiento completo con el conjunto propio. **No hay que presentar estas cifras como el desempeño del sistema.**

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
