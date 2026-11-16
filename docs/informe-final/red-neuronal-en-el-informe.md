# La red neuronal en el informe

Textos listos para pegar sobre el clasificador de la capa 4, con todo lo que el informe tiene que contar: el problema, los datos, el conjunto propio, el entrenamiento, la evaluación, los resultados, la mejora continua, la integración en la plataforma, las limitaciones y la ética. Siguen la [guía de redacción](guia-de-redaccion.md): presente, prosa sin viñetas, APA 7 y nada previsto presentado como hecho.

**Fuente de cada dato:** `docs/red-neuronal/` y ADR-0014, ADR-0015 y ADR-0022 de la rama `funcionalidad/010-red-neuronal`. Cifras de la versión 1.0.0 (entrenada el 2026-11-05, publicada el 2026-11-10). **Fecha de corte para el informe: 16/11/2026.** Si la red publica otra versión antes de la entrega, se actualizan las cifras marcadas con ⟳.

**Estado del conjunto propio al corte:** solo tiene imágenes **generadas** (49 de choques, de ChatGPT, Copilot y Gemini, en original y captura); todavía **no tiene fotografías reales** de las mismas escenas. Por eso no se puede calcular el área bajo la curva ni la tasa de falsos positivos en ese conjunto, y los textos lo dicen así. Cuando la autora sume fotos reales, se reemplazan los párrafos marcados con ◆.

## Dónde va cada texto

| Texto | Capítulo y sección | Reemplaza |
|---|---|---|
| R-01 a R-10 | Cap. IX, nueva sección «Clasificador de imágenes sintéticas», después de «Diseño de solución» y antes de «Modelo de datos» | El texto N-03 de la revisión del 16/11 (este es la versión completa) |
| R-11 | Cap. III, Límites del sistema | Agregar al final |
| R-12 | Cap. X, Recursos tecnológicos y Tabla 16 | Agregar |
| R-13 | Anexo Q (nuevo): ficha técnica del modelo | — |
| R-14 | Bibliografía | Agregar en orden alfabético |

Figura y tablas de esta sección, en orden: Tabla 15 (datos de entrenamiento), Figura 16 (pipeline), Tabla 16 (resultados). Con esto, el **Presupuesto pasa a ser la Tabla 17 y el CANVAS la Tabla 18** (corrige la numeración de la revisión del 16/11).

---

## Cap. IX · Clasificador de imágenes sintéticas

### R-01. Problema y enfoque

> La cuarta capa de análisis estima la probabilidad de que una imagen haya sido generada por inteligencia artificial a partir de las huellas que deja el proceso de generación en la textura de la imagen, aun cuando la imagen no conserva metadatos ni credenciales de procedencia. Los detectores de este tipo alcanzan resultados altos con los generadores que conocen, pero pierden desempeño frente a generadores nuevos (Wang et al., 2020), y su eficacia depende más de la diversidad de los generadores de entrenamiento que de su cantidad de imágenes (Park y Owens, 2025). Por eso el clasificador se diseña desde el inicio como un componente que se mide con generadores que no ve durante el entrenamiento y con imágenes propias de las escenas del sistema, y que se reentrena por versiones. Su resultado se presenta siempre como un indicio que se combina con las otras tres capas y nunca como un veredicto.

### R-02. Datos de entrenamiento

> El entrenamiento utiliza dos conjuntos públicos elegidos tras explorar ocho candidatos en cuanto a licencia, formato y contenido. Community Forensics reúne imágenes de miles de generadores, en su mayoría variantes de Stable Diffusion, y aporta diversidad de modelos (Park y Owens, 2025); OpenFake incorpora generadores comerciales recientes, como GPT Image 1, DALL·E 3, Midjourney 6, Ideogram 3 y FLUX 1.1 Pro (Livernoche et al., 2025). De cada conjunto se fija una revisión exacta, porque sus licencias, ambas no comerciales, cambian entre versiones; los demás candidatos se excluyen por licencia no verificable, por formato o por acceso pendiente. La muestra final se compone de 17 500 fotografías reales y 17 500 imágenes sintéticas de 210 generadores, con un máximo de imágenes por generador para que ninguno domine el entrenamiento (Tabla 15). La familia de generadores de Google (Imagen 4, Imagen 3 y Nano Banana 2, que es la que utiliza Gemini) se reserva completa fuera del entrenamiento, para medir cómo responde el modelo ante una herramienta comercial que no conoce.

**Tabla 15.** Datos de entrenamiento del clasificador ⟳

| Fuente | Fotografías reales | Imágenes sintéticas | Generadores | Licencia |
|---|---|---|---|---|
| Community Forensics (subconjunto *Small*) | 7 500 | 7 500 | Variantes de Stable Diffusion, GAN y otros de código abierto | CC BY-NC-SA 4.0 |
| OpenFake | 10 000 | 10 000 | Comerciales y de código abierto recientes | CC BY-NC 4.0 en la revisión utilizada |
| **Total** | **17 500** | **17 500** | **210** | Uso no comercial |

*Nota. Elaboración propia. Se excluyen el contenido explícito, 66 generadores que no producen fotografías (ilustración, historieta, arte de píxeles) y las imágenes de menos de 256 píxeles de lado menor. La familia de Google queda fuera del entrenamiento.*

### R-03. Control de calidad y normalización de los datos

> La exploración de los conjuntos revela un sesgo que, sin corrección, invalidaría el modelo: en OpenFake las fotografías reales son archivos JPEG de alta calidad con un lado menor mediano de 3 349 píxeles, mientras que las sintéticas rondan los 880 píxeles y llegan en PNG, JPEG o WebP; en Community Forensics, las sintéticas son PNG cuadrados de 512 píxeles. Un modelo entrenado así aprende a distinguir el formato o el tamaño, y no la generación. Para evitarlo, todas las imágenes de las dos clases atraviesan el mismo proceso: se convierten a RGB, se llevan a un lado menor elegido al azar entre 256 y 512 píxeles, sin agrandar nunca una imagen, y se guardan como JPEG con una calidad elegida al azar entre 75 y 95. Antes de entrenar, una etapa de validación detiene el proceso si encuentra imágenes corruptas, duplicadas, filtraciones de una misma imagen entre entrenamiento y prueba, generadores reservados presentes en el entrenamiento o un desbalance entre clases mayor al 5 %. Las imágenes se reparten en entrenamiento (80 %), validación (10 %) y prueba (10 %) de forma estratificada por clase y por generador, con una semilla fija que hace reproducible la partición. Cada versión de los datos queda identificada por la huella SHA-256 de su manifiesto, que se registra en la ficha del modelo.

### R-04. Conjunto propio de evaluación ◆

> Ningún conjunto público contiene imágenes generadas con las herramientas que usaría hoy quien falsifica una prueba, en las escenas de los casos del sistema y en las formas en que llegan a la plataforma. Por eso el proyecto construye un conjunto propio, con un protocolo escrito: imágenes generadas con ChatGPT, Gemini y Copilot a partir de una lista de 90 indicaciones numeradas, iguales para todas las herramientas, sobre siete escenas de los casos automovilísticos y laborales (choques, daños leves, vidrios rotos, lugar del siniestro, lesiones, lugar del accidente de trabajo y herramientas o elementos de protección dañados), cada una en su versión original y como captura de pantalla. Las lesiones se generan en seis tonos de piel, siguiendo de forma aproximada la escala de Fitzpatrick, para comprobar que el modelo responda igual para todas las personas. El protocolo exige además fotografías reales de las mismas escenas, porque si las reales mostraran otros temas, el modelo podría distinguir el tema en lugar de la generación. Al 16 de noviembre de 2026, el conjunto propio contiene 49 imágenes generadas de choques (12 de ChatGPT, 17 de Copilot y 20 de Gemini, en versión original y captura) y todavía no incluye fotografías reales, que se suman a partir de fotografías tomadas por la autora y del conjunto público CarDD (Wang et al., 2023), cuyo acceso requiere un acuerdo de uso para investigación. El conjunto se guarda en una carpeta privada y nunca se sube al repositorio.

◆ Cuando haya fotos reales, reemplazar las dos últimas oraciones por: «Al [fecha de corte], el conjunto propio contiene [N] imágenes generadas y [M] fotografías reales de las mismas escenas, en versión original y captura. El conjunto se guarda en una carpeta privada y nunca se sube al repositorio.»

### R-05. Arquitectura, entrenamiento y calibración

> El modelo parte de una red EfficientNet-B0 (Tan y Le, 2019) preentrenada con ImageNet, a la que se reemplaza la última capa por una salida única que estima la probabilidad de que la imagen sea sintética. Se elige por su equilibrio entre precisión y velocidad en un procesador común, lo que permite ejecutarla en el servidor sin una placa gráfica. El entrenamiento ajusta toda la red mediante transferencia de aprendizaje, con el optimizador AdamW (Loshchilov y Hutter, 2019), una tasa de aprendizaje inicial de 0,0003 que decrece con una curva de coseno, lotes de 64 imágenes y un máximo de 15 épocas con parada temprana tras tres épocas sin mejora, conservando siempre la mejor época según el área bajo la curva ROC en validación. Durante el entrenamiento, cada imagen recibe transformaciones al azar que simulan lo que le ocurre a una fotografía antes de llegar al sistema: reducción de tamaño, recompresión JPEG con calidad entre 50 y 95, recorte de 224 × 224 píxeles en cualquier zona y espejado horizontal. Al terminar, las probabilidades se calibran mediante escalado por temperatura (Guo et al., 2017), de modo que un 70 % signifique efectivamente que siete de cada diez imágenes con ese valor son sintéticas; el error de calibración en validación baja de 0,069 a 0,020. El modelo calibrado se exporta al formato ONNX, se comprueba que su salida coincida con la del modelo original con una diferencia máxima de 0,001, y en la plataforma analiza cada imagen mediante cinco recortes (las cuatro esquinas y el centro), cuyo resultado se promedia, en unos 23 milisegundos por imagen. El entrenamiento se ejecuta en Google Colab Pro, y cada etapa del proceso puede retomarse sin rehacer las anteriores si la sesión se interrumpe.

### R-06. Evaluación y compuerta de publicación

> El modelo se evalúa sobre tres conjuntos que miden cosas distintas: el conjunto de prueba, con generadores que el modelo conoce; los generadores reservados, que miden la capacidad de generalizar a una herramienta comercial nueva; y el conjunto propio, que mide el desempeño en las condiciones reales del sistema, con las imágenes tal como llegan, sin normalizar. Una compuerta automática solo publica una versión si cumple cinco condiciones: un área bajo la curva ROC de al menos 0,90 en el conjunto de prueba, la coincidencia entre el modelo exportado y el original, una ficha técnica completa, la correspondencia entre la huella de los datos declarados y la de los datos utilizados, y un código sin cambios pendientes de registrar. La ficha técnica de cada versión se genera de forma automática, siguiendo la propuesta de fichas de modelo de Mitchell et al. (2019), con el uso previsto, las limitaciones, los datos y sus licencias, el entrenamiento, el entorno, las métricas por generador y los datos para reproducirlo (Anexo Q). El proceso completo, desde la obtención de los datos hasta el uso del modelo en la plataforma, se presenta en la Figura 16.

**Figura 16.** Pipeline del clasificador de imágenes — `docs/arquitectura/diagramas/12-pipeline-red-neuronal.png`
*Nota. Elaboración propia, diagrama de actividad en notación UML 2.5.*

### R-07. Resultados ⟳ ◆

> La versión 1.0.0 cumple el valor de referencia del proyecto con margen: alcanza un área bajo la curva ROC de 0,961 y un F1-score de 0,904 en el conjunto de prueba, y conserva un área de 0,938 frente a la familia de Google, que no participa del entrenamiento (Tabla 16). El análisis por generador muestra que el modelo supera el 0,99 con las variantes de Stable Diffusion y con StyleGAN2, y que los generadores comerciales más difíciles son Midjourney 6, del que detecta el 68 %, y FLUX 1.1 Pro, del que detecta el 54 %. El resultado sobre el conjunto propio es, en cambio, el hallazgo más importante de esta capa: de las 49 imágenes de choques generadas con ChatGPT, Gemini y Copilot, el modelo identifica como sintéticas solo 5 con el umbral de 0,5, y la primera prueba en producción con una imagen de ese conjunto arroja una probabilidad cercana a cero. Como el conjunto propio todavía no incluye fotografías reales de las mismas escenas, no es posible calcular su área bajo la curva y, por lo tanto, no se puede distinguir si el modelo ordena correctamente esas imágenes con otro umbral o si directamente no las reconoce. Las causas posibles son dos: las herramientas comerciales de 2025 y 2026 son más recientes que los generadores de los conjuntos públicos, y las escenas de autos dañados no forman parte de los datos de entrenamiento. Este resultado confirma la decisión de diseño de no basar la conclusión en una sola capa y de presentar la probabilidad como un indicio.

**Tabla 16.** Resultados del clasificador, versión 1.0.0 ⟳

| Conjunto de evaluación | Imágenes | Área bajo la curva ROC | Otras métricas (umbral 0,5) |
|---|---|---|---|
| Prueba: generadores conocidos | 1 750 reales y 1 696 sintéticas | 0,961 | Exactitud 0,909; precisión 0,940; exhaustividad 0,870; F1 0,904 |
| Generadores no vistos: familia de Google | 1 750 reales y 219 sintéticas | 0,938 | Detecta 161 de 219 (74 %) |
| Conjunto propio: choques generados con ChatGPT, Gemini y Copilot | 49 sintéticas, sin reales | No calculable | Detecta 5 de 49 (10 %): Gemini 3 de 20, ChatGPT 1 de 12, Copilot 1 de 17 |

*Nota. Elaboración propia a partir del entrenamiento del 5 de noviembre de 2026. El área bajo la curva requiere imágenes de las dos clases; el conjunto propio todavía no tiene fotografías reales.*

◆ Cuando haya reales: completar la tercera fila con el AUC y la tasa de falsos positivos en las reales, y cambiar en el texto «no es posible calcular su área bajo la curva…» por el valor obtenido y su lectura.

### R-08. Mejora continua por versiones

> El bajo desempeño con las herramientas comerciales lleva a una decisión de diseño: el clasificador se mejora de forma continua y por versiones, sin perder la posibilidad de medir esa mejora con honestidad. El conjunto propio se divide de antemano en dos partes que nunca se mezclan: una evaluación fija, que nunca se utiliza para entrenar y contra la que se compara cada versión, y una parte de ajuste, que se suma al entrenamiento de la versión siguiente. La unidad que se asigna a cada parte es la indicación de generación y no el archivo, de modo que las imágenes de una misma escena producidas con distintas herramientas o en distintas variantes quedan siempre del mismo lado; de lo contrario, el modelo vería durante el entrenamiento la misma escena con la que luego se lo evalúa. La asignación sigue una regla reproducible que no depende de las demás imágenes: las 89 indicaciones de la lista se reparten mitad y mitad dentro de cada escena y de cada tono de piel, y las imágenes nuevas se asignan mediante una huella con semilla fija, por lo que sumar imágenes no cambia de lado a ninguna. Cada reentrenamiento produce una versión nueva, que solo se publica si, además de superar la compuerta, mejora a la anterior sobre la evaluación fija y no empeora con los generadores reservados; si no lo logra, se registra y se descarta. Este criterio sigue el nivel de madurez de MLOps con un pipeline automatizado y reentrenamiento a pedido (Google Cloud, s. f.). Las imágenes de los usuarios del sistema nunca se utilizan para entrenar, porque son confidenciales.

### R-09. Integración en la plataforma

> El modelo publicado se guarda en un repositorio privado de modelos de Hugging Face, identificado por su número de versión, y la plataforma lo descarga, verifica su huella antes de usarlo y lo conserva fuera de cada despliegue. La versión 1.0.0 se publica el 10 de noviembre de 2026 y se activa en producción como cuarta capa. Cada resultado guarda la probabilidad, la versión y la huella del modelo, la huella de los datos con que se entrena, el commit que lo produce y la versión del motor de ejecución, de modo que cualquier análisis puede reproducirse y auditarse. Por debajo de una probabilidad del 50 %, la capa no aporta indicios; por encima, su nivel equivale a la probabilidad calibrada, con un tope de 90, porque el máximo queda reservado a la evidencia criptográfica de la capa de credenciales de procedencia. La conclusión de la capa enuncia siempre sus tres limitaciones: no detecta ediciones parciales sobre una fotografía real, puede fallar con generadores que no conoce y una probabilidad baja no indica que la imagen sea real. Si el modelo no está disponible o su archivo no coincide con la huella registrada, la capa se informa como no disponible, con el motivo, y las otras tres se presentan igual.

### R-10. Limitaciones y consideraciones éticas ◆

> El clasificador presenta limitaciones que el informe de cada caso declara. Su desempeño con las herramientas comerciales actuales en las escenas del sistema es bajo, y su medición en condiciones reales todavía no incluye fotografías reales de esas escenas. No detecta ediciones localizadas sobre una fotografía auténtica, que quedan a cargo del análisis del nivel de error. Los datos de entrenamiento no se depuran de casi duplicados ni de fotografías reales de OpenFake que no son fotografías de cámara, y los temas de las imágenes reales y sintéticas difieren entre conjuntos, lo que se mitiga en parte con la evaluación por generador y en condiciones reales. Las licencias de los conjuntos utilizados permiten el uso con fines de investigación, como el de este proyecto, pero una explotación comercial requiere reentrenar con datos de licencia compatible y verificar los términos de uso de las herramientas generativas para el entrenamiento de un detector. En el plano ético, el diseño mide el desempeño por tono de piel en las imágenes de lesiones, nunca utiliza imágenes de usuarios ni de causas reales, y presenta el resultado como una probabilidad calibrada y explicada, acompañada del descargo de que no constituye un dictamen pericial, conforme al principio de supervisión humana que orienta al sistema (Parlamento Europeo y Consejo de la Unión Europea, 2024).

---

## R-11. Cap. III, Límites del sistema (agregar al final)

> El clasificador de imágenes sintéticas no garantiza la detección de imágenes producidas con herramientas posteriores a su entrenamiento ni de ediciones parciales sobre una fotografía auténtica, y su desempeño en las escenas del sistema depende de su reentrenamiento periódico.

## R-12. Cap. X, Recursos tecnológicos y presupuesto

En Recursos tecnológicos, después de la oración sobre PyTorch y ONNX Runtime, agregar:

> El entrenamiento utiliza además timm para la arquitectura preentrenada, MLflow para registrar cada experimento y Hugging Face como fuente de los conjuntos de datos y como registro privado de las versiones del modelo.

En la tabla de presupuesto, fila Google Colab: «Google Colab Pro · Entrenamiento del clasificador · Incluido en la suscripción a Gemini de la autora, sin costo adicional para el proyecto». Hugging Face: «Registro privado de modelos y conjuntos de datos · Sin costo».

## R-13. Anexo Q: ficha técnica del modelo

Exportar a PDF la ficha `red_neuronal/informes/1.0.0/ficha.md` (rama de la red) y agregarla como «Anexo Q. Ficha técnica del clasificador, versión 1.0.0». En el texto (R-06) ya está la mención.

## R-14. Bibliografía (agregar en orden alfabético)

> Google Cloud. (s. f.). *MLOps: Continuous delivery and automation pipelines in machine learning*. https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
>
> Guo, C., Pleiss, G., Sun, Y., y Weinberger, K. Q. (2017). On calibration of modern neural networks. En *Proceedings of the 34th International Conference on Machine Learning* (pp. 1321-1330). PMLR.
>
> Livernoche, V., Arodi, A., Musulan, A., Yang, Z., Salvail, A., Marceau Caron, G., Godbout, J.-F., y Rabbany, R. (2025). *OpenFake: An open dataset and platform toward large-scale deepfake detection* (arXiv:2509.09495). arXiv. https://arxiv.org/abs/2509.09495
>
> Loshchilov, I., y Hutter, F. (2019). Decoupled weight decay regularization. En *International Conference on Learning Representations*. https://openreview.net/forum?id=Bkg6RiCqY7
>
> Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., y Gebru, T. (2019). Model cards for model reporting. En *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 220-229). https://doi.org/10.1145/3287560.3287596
>
> Park, J., y Owens, A. (2025). Community Forensics: Using thousands of generators to train fake image detectors. En *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 8245-8257).
>
> Tan, M., y Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. En *Proceedings of the 36th International Conference on Machine Learning* (pp. 6105-6114). PMLR.
>
> Wang, S.-Y., Wang, O., Zhang, R., Owens, A., y Efros, A. A. (2020). CNN-generated images are surprisingly easy to spot… for now. En *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 8695-8704).
>
> Wang, X., Li, W., y Wu, Z. (2023). CarDD: A new dataset for vision-based car damage detection. *IEEE Transactions on Intelligent Transportation Systems, 24*(7), 7202-7214. https://doi.org/10.1109/TITS.2023.3258480

## Lo que tiene que hacer la autora para que esta sección quede completa

1. **Fotos reales de las mismas escenas** en el conjunto propio (propias y, si se firma el acuerdo, CarDD), repartidas por la regla de la evaluación fija. Con eso se calculan el AUC y los falsos positivos y se reemplazan los párrafos ◆.
2. **Más generadas** de las demás escenas (rayones, vidrios, lesiones en los seis tonos, accidentes de trabajo), para que el resultado no sea solo de choques.
3. **Reevaluar la 1.0.0** con el conjunto propio al día y pasar las cifras (por herramienta, escena y variante).
4. **Repetición del entrenamiento** (T31) para mostrar que es reproducible: suma una oración a R-05.
5. Si hay tiempo, la **1.1.0** con la parte de ajuste: su comparación contra la 1.0.0 en la evaluación fija sería la mejor evidencia del informe y de la defensa.
6. Exportar la **ficha** a PDF para el Anexo Q.
