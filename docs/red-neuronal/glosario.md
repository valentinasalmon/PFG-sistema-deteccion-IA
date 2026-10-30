# Glosario de la red neuronal

| Término | Significado |
|---|---|
| **AdamW** | Optimizador que decide cómo corregir los pesos en cada paso; estándar para reentrenar redes preentrenadas |
| **AUC ROC** | Área bajo la curva ROC. Probabilidad de que el modelo le dé más puntaje a una sintética que a una real tomadas al azar. 1 = perfecto, 0,5 = azar. Métrica principal |
| **Aumentación** | Transformaciones al azar (recompresión, reducción, recorte, espejo) aplicadas a cada imagen de entrenamiento para que el modelo resista a WhatsApp y no memorice |
| **Calibración** | Ajuste para que la probabilidad informada coincida con la frecuencia real de aciertos |
| **Calidad JPEG** | Nivel de compresión de un JPEG (1 a 100). La exploración la estima a partir de la tabla de cuantización del archivo, para detectar sesgos de formato entre clases |
| **Capa 4** | La red neuronal, una de las cuatro capas independientes del análisis de cada foto |
| **CI · CT · CD** | Integración continua (probar el código en cada cambio), entrenamiento continuo (reentrenar a pedido) y entrega continua (exportar, verificar y publicar) |
| **Clasificación binaria** | Problema con dos clases: 0 = real, 1 = sintética |
| **Compuerta de promoción** | Verificación automática de cinco criterios antes de publicar un modelo |
| **Conjunto propio** | Fotos reunidas por la autora (ChatGPT, Gemini, Copilot, reales, editadas) en tres variantes; solo para evaluar |
| **Convolución** | Filtro chico que recorre la imagen buscando patrones; base de las redes para imágenes |
| **Cuaderno (notebook)** | Archivo `.ipynb` de Colab o Kaggle que ejecuta las etapas; no contiene lógica propia |
| **Cuota por generador** | Máximo de imágenes sintéticas que aporta un mismo generador, para que ninguno domine y las métricas por generador tengan sentido |
| **ECE** | Error de calibración esperado: cuánto se aleja la confianza del modelo de su tasa real de aciertos |
| **EfficientNet-B0** | Red convolucional chica y eficiente (≈ 5 millones de pesos) que usa evidentIA |
| **Entropía cruzada binaria** | La función de pérdida: mide cuánto se equivoca el modelo, castigando más los errores con mucha confianza |
| **Época** | Una pasada completa por todas las imágenes de entrenamiento |
| **Escala de Fitzpatrick** | Clasificación dermatológica de la piel en seis tipos. El conjunto propio reparte las lesiones en seis tonos que la siguen de forma aproximada |
| **Escena** | Tipo de foto del conjunto propio (choque, rayón, vidrio, calle, lesión, lugar de trabajo, herramienta, documento), indicada por el prefijo del nombre del archivo |
| **Etapa** | Cada uno de los siete pasos del pipeline: obtener, validar, preparar, entrenar, exportar, evaluar y publicar |
| **Exhaustividad (recall)** | De las sintéticas, qué proporción detecta el modelo |
| **Exploración** | Revisión previa de cada conjunto candidato: disponibilidad, revisión exacta, licencia, columnas, generadores y formatos (T25) |
| **Ficha del modelo (model card)** | Documento generado con cada versión: datos, entrenamiento, entorno, métricas, limitaciones y cómo reproducirlo |
| **Fuga entre particiones** | La misma imagen en entrenamiento y en prueba; infla las métricas |
| **GAN / difusión** | Familias de generadores de imágenes. Los GAN (como BigGAN) son más viejos; los de difusión (Stable Diffusion, DALL·E, Midjourney) son los actuales |
| **Generador** | Programa o modelo que creó una imagen sintética |
| **Generador no visto** | Generador reservado que nunca se usa para entrenar; mide cómo responde el modelo a uno desconocido |
| **Hiperparámetro** | Valor que se fija antes de entrenar (épocas, lote, tasa de aprendizaje); vive en el YAML |
| **Huella (SHA-256)** | Identificador único calculado a partir del contenido de un archivo; si cambia un bit, cambia la huella |
| **Hugging Face** | Plataforma de conjuntos de datos y modelos; de ahí salen los datos públicos y ahí se publicará el modelo |
| **ImageNet** | Conjunto de 1,2 millones de fotos con el que se preentrenó EfficientNet-B0 |
| **Inferencia** | Usar el modelo ya entrenado para estimar la probabilidad de una foto nueva |
| **Kaggle** | Plataforma con GPU gratis que permite correr cuadernos en segundo plano |
| **Lista maestra** | Los 90 prompts numerados del conjunto propio, que se usan iguales en todas las herramientas |
| **Logit** | Salida cruda de la red, sin límites; la sigmoide la convierte en probabilidad |
| **Lote (batch)** | Grupo de imágenes que se procesa de una vez (64) |
| **Manifiesto** | CSV con una fila por imagen (fuente, clase, generador, variante, partición, huella); identifica una versión del conjunto |
| **Matriz de confusión** | Tabla de aciertos y errores con un umbral: verdaderos y falsos positivos y negativos |
| **MLflow** | Herramienta que registra cada experimento de entrenamiento con sus parámetros y métricas |
| **MLOps** | Ingeniería de software aplicada a modelos: versionar, automatizar, probar y verificar |
| **Muestreo por archivos** | Elegir al azar archivos enteros de un conjunto en lugar de filas sueltas: en Parquet, leer una imagen obliga a bajar la columna de imágenes de todo el archivo |
| **Normalización anti-atajos** | Llevar reales y sintéticas al mismo formato, tamaño y compresión para que el modelo no las distinga por eso |
| **ONNX / ONNX Runtime** | Formato estándar para guardar redes y la biblioteca liviana que las ejecuta en CPU |
| **Parada temprana** | Detener el entrenamiento si la validación no mejora durante `paciencia` épocas |
| **Partición** | Grupo de imágenes con un uso: entrenamiento, validación, prueba o no visto |
| **Pérdida** | Número que mide cuánto se equivoca el modelo; entrenar es bajarla |
| **Pipeline** | Cadena de etapas que leen y escriben en disco |
| **Precisión** | De las que el modelo marca como sintéticas, qué proporción lo son |
| **Precisión mixta** | Calcular en 16 bits donde no afecta el resultado; casi el doble de rápido en GPU |
| **Preentrenada** | Red que ya aprendió a «ver» con otro conjunto (ImageNet) antes de reentrenarse |
| **Prueba de concepto** | Recorrido completo con pocos datos para validar el diseño y medir tiempos |
| **Punto de control (checkpoint)** | Archivo con el estado del entrenamiento (`ultimo.pt`) para retomarlo si se corta |
| **Receta** | Configuración de datos: fuentes, cantidades, generadores reservados y semilla |
| **Registro de modelos** | Lugar donde se guardan las versiones publicadas, inmutables, con su ficha y sus huellas |
| **Revisión** | Versión exacta (commit) de un conjunto de Hugging Face. Se fija en la receta porque la licencia y el contenido cambian entre revisiones |
| **Semilla** | Número que fija todo lo aleatorio para que se pueda repetir igual (42) |
| **Sigmoide** | Función que convierte un logit en una probabilidad entre 0 y 1 |
| **Sobreajuste** | Cuando el modelo memoriza el entrenamiento y empeora con imágenes nuevas |
| **Streaming** | Leer un conjunto de datos de a partes por internet sin bajarlo entero |
| **Tasa de aprendizaje** | Qué tan grandes son las correcciones de los pesos (0,0003, baja en coseno) |
| **Temperatura** | Número que divide al logit antes de la sigmoide para calibrar; `T > 1` modera la confianza |
| **timm** | Biblioteca con cientos de redes preentrenadas con la misma interfaz |
| **Transferencia de aprendizaje** | Partir de una red preentrenada y reentrenarla para otra tarea con menos datos |
| **Variante** | Versión de una foto del conjunto propio: original, WhatsApp, captura o editada |
| **Versión MAJOR.MINOR.PATCH** | Numeración del modelo: MAJOR cambia el contrato, MINOR reentrena con datos nuevos, PATCH corrige sin datos nuevos |
