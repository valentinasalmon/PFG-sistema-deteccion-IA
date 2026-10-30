# 2. Conceptos básicos

Este capítulo explica, sin matemática, las ideas necesarias para entender el resto. Si ya las conocés, podés saltarlo.

## Red neuronal

Una red neuronal es una función con **millones de números ajustables** (los **pesos**). Recibe una entrada (los píxeles de una foto) y devuelve una salida (un número). Al principio los pesos son casi aleatorios y la salida no sirve; **entrenar** es ajustar esos pesos, de a poco, para que la salida se parezca a la respuesta correcta en miles de ejemplos.

## Red convolucional

Las redes para imágenes usan **convoluciones**: pequeños filtros (de 3 × 3 píxeles, por ejemplo) que recorren la foto buscando patrones. Las primeras capas detectan cosas simples (bordes, texturas, ruido); las siguientes combinan esas detecciones en patrones cada vez más complejos.

Para detectar imágenes generadas importan sobre todo los **patrones finos**: el ruido, la textura y las regularidades de alta frecuencia que deja el proceso de generación y que el ojo no ve. Por eso el sistema **no achica las fotos** antes de analizarlas (capítulo 7): achicarlas borraría justamente esas huellas.

## EfficientNet-B0

Es la red que usa evidentIA. Es una red convolucional **chica y eficiente** (unos 5 millones de pesos) diseñada por Google para lograr buena precisión con poco cómputo. Se eligió porque:

- entrena rápido en una GPU de Colab;
- corre en el servidor **sin GPU** en unos 25 ms por foto;
- es un estándar conocido, fácil de justificar en el informe.

Si no alcanza el umbral, la misma fábrica de modelos permite probar ConvNeXt-Tiny o ResNet-50 cambiando un nombre en la configuración.

## Transferencia de aprendizaje

Entrenar una red desde cero necesita millones de imágenes. En cambio, se parte de una EfficientNet-B0 **ya entrenada con ImageNet** (1,2 millones de fotos de 1000 categorías). Esa red ya sabe «ver»: bordes, texturas, formas. Se le cambia la última capa por una que da **una sola salida** (real o sintética) y se la reentrena con las fotos del proyecto. Así alcanza con decenas de miles de imágenes y pocas horas de GPU.

## Clasificación binaria, logit y probabilidad

El problema tiene dos clases: **0 = real** y **1 = sintética**. La red devuelve un número sin límites llamado **logit** (puede ser −7 o +4). Para convertirlo en una probabilidad entre 0 y 1 se aplica la **función sigmoide**: un logit muy negativo da casi 0, un logit 0 da 0,5 y uno muy positivo da casi 1.

## Entrenamiento: lotes, pasos, épocas

- **Lote (batch):** grupo de imágenes que la red procesa de una vez. En evidentIA, 64.
- **Paso:** procesar un lote, medir el error y corregir los pesos un poquito.
- **Época:** pasar **una vez por todas** las imágenes de entrenamiento. Con 8 000 imágenes y lotes de 64, una época son 125 pasos.
- Se entrenan varias épocas: en la prueba de concepto fueron 3, y en el entrenamiento completo se planean unas 10 a 15.

## Pérdida

Es el número que mide **cuánto se equivoca** la red en un lote. Se usa la **entropía cruzada binaria**: es baja cuando la red da probabilidades altas a las sintéticas y bajas a las reales, y alta cuando se equivoca con confianza. Entrenar es bajar la pérdida.

## Optimizador y tasa de aprendizaje

El **optimizador** decide cómo corregir los pesos en cada paso. Se usa **AdamW**, el estándar actual para reentrenar redes preentrenadas. La **tasa de aprendizaje** (0,0003) dice qué tan grandes son las correcciones: si es muy grande, la red se desordena; si es muy chica, no aprende. Se va reduciendo con una curva de **coseno** a lo largo de las épocas, para hacer ajustes finos al final.

## Particiones: entrenamiento, validación y prueba

Las imágenes se dividen en tres grupos que **nunca se mezclan**:

| Partición | Proporción | Para qué |
|---|---|---|
| Entrenamiento | 80 % | Con estas la red ajusta sus pesos |
| Validación | 10 % | Al final de cada época se mide con estas para elegir la mejor época y calibrar |
| Prueba | 10 % | Se usan **una sola vez**, al final, para medir el desempeño de verdad |

Si una misma imagen estuviera en entrenamiento y en prueba, la red la «recordaría» y las métricas mentirían. La validación de datos lo impide (capítulo 4).

Hay una cuarta partición, **no visto**: imágenes de generadores que se reservan enteros y nunca se usan para entrenar. Miden cómo se comporta el modelo frente a un generador desconocido, que es la situación real cuando sale una herramienta nueva.

## Sobreajuste y parada temprana

Si se entrena demasiado, la red empieza a **memorizar** las imágenes de entrenamiento en lugar de aprender patrones generales: mejora en entrenamiento y empeora en validación. Es el **sobreajuste**. Para evitarlo se usa **parada temprana**: si el desempeño en validación no mejora durante `paciencia` épocas seguidas (2 o 3), se detiene y se queda con la mejor época.

## Aumentación de datos

Durante el entrenamiento, cada imagen se modifica un poco al azar cada vez que se usa: se achica, se recomprime en JPEG, se recorta en otra zona o se espeja. Así la red aprende patrones que **sobreviven a WhatsApp** y no depende de detalles irrelevantes.

## Métricas

| Métrica | Pregunta que responde |
|---|---|
| **AUC ROC** | Si tomo una foto real y una sintética al azar, ¿con qué frecuencia la red le da más puntaje a la sintética? 1 = siempre, 0,5 = al azar. **Es la métrica principal**, porque no depende de ningún umbral |
| Exactitud | ¿Qué proporción de fotos clasifica bien con un umbral de 0,5? |
| Precisión | De las que marca como sintéticas, ¿cuántas lo son? |
| Exhaustividad (recall) | De las sintéticas, ¿cuántas detecta? |
| F1 | Promedio equilibrado de precisión y exhaustividad |
| ECE | ¿Cuánto se aleja la confianza de la red de su tasa real de aciertos? Más bajo es mejor |

El umbral de 0,5 se usa **solo para reportar** estas métricas. El sistema no clasifica las fotos en «real» o «falsa»: muestra la probabilidad (RN27).

## Calibración

Las redes profundas suelen ser **sobreconfiadas**: dicen 0,99 cuando aciertan el 90 % de las veces. La **calibración por temperatura** divide el logit por un número `T` (la temperatura) antes de la sigmoide. Con `T > 1` las probabilidades se vuelven más moderadas y honestas. No cambia qué foto tiene más puntaje que otra (el AUC queda igual), solo cuán extremas son. En la prueba de concepto, `T = 2,35` bajó el ECE de 0,047 a 0,021.

## ONNX

Es un formato estándar para guardar redes neuronales. El modelo se entrena con PyTorch (que necesita mucha memoria y conviene usar con GPU) y se **exporta a ONNX**, que se ejecuta con **ONNX Runtime**: una biblioteca liviana que corre rápido en CPU. Así el servidor de AWS no necesita GPU ni PyTorch.

## MLOps

Es aplicar ingeniería de software a los modelos: versionar datos, código y modelos; automatizar el entrenamiento por etapas; probar el código; registrar cada experimento; y no publicar un modelo sin verificar su calidad. Está desarrollado en el capítulo 9.
