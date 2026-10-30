# Conjuntos de datos para detectar imágenes generadas con IA (2026-10-30)

Investigación para la receta de datos v1 de la red neuronal (funcionalidad 010, T25 y T27). La autora pidió seguir buscando conjuntos de datos y generando imágenes para mejorar la red (2026-10-30).

## Qué buscamos

1. **Generadores actuales y comerciales:** ChatGPT (GPT-4o / GPT-image), Gemini (Nano Banana), Midjourney, FLUX. Es lo que usaría alguien para falsificar una prueba hoy.
2. **Condiciones reales:** fotos recomprimidas por redes sociales y aplicaciones de mensajería.
3. **Ediciones parciales:** fotos reales con una parte modificada con IA (solo para medir; capa 4 no es responsable de detectarlas).
4. **Licencia verificable:** si no se puede verificar la licencia, el conjunto no se usa (CA2).

## Candidatos

| Conjunto | Qué aporta | Generadores | Licencia (a verificar en la revisión exacta) | Uso propuesto |
|---|---|---|---|---|
| **Community Forensics *Small*** (OwensLab) | Gran variedad de generadores de código abierto; ya probado en la prueba de concepto | Cientos, sobre todo Stable Diffusion y sus ajustes finos, más GAN, DeepFloyd, GLIDE | La versión *Small* figura como CC BY-NC-SA 4.0, solo investigación no comercial; las imágenes heredan la licencia de su generador (mayormente CreativeML OpenRAIL-M) | **Entrenamiento**, base de la receta |
| **OpenFake** (ComplexDataLab) | Generadores comerciales y recientes; incluye un subconjunto «reddit» con imágenes compartidas en la vida real | Muchos modelos, incluidos propietarios | Cambia según la revisión: CC BY-SA 4.0, CC BY-NC 4.0 o CC BY-NC-SA 4.0. Los subconjuntos de generadores propietarios son no comerciales. Prohíbe usarlo para entrenar generadores | **Entrenamiento** y generadores **no vistos**. Fijar una revisión concreta |
| **Treasure** (ThreeLiu) | Lo más nuevo: pensado para «mundo abierto» con generadores que cambian | GPT-image-1.5, Midjourney v6.1 y v7, FLUX.2, GPT-4o, FLUX.1 | No se encontró: verificar en la ficha | Candidato a **no vistos** si la licencia lo permite |
| **AIGenImages2026** (artículo de la ACM) | 19 generadores recientes, construido para detección continua | Midjourney v7, Gemini 2.5 Flash Image, Gemini 3 Pro Image, FLUX.2, subconjunto de GPT-4o | Verificar disponibilidad y licencia | Candidato a **no vistos** (Gemini) |
| **MLLM-Generated-Image-Detection-Dataset** (zr-zhang) | Generadores multimodales más nuevos | GPT Image 2, Nano Banana 2 | Solo investigación | Candidato a **prueba** de generadores comerciales |
| **ShareGPT-4o-Image** (FreedomIntelligence) | Imágenes de GPT-4o | GPT-4o | No se encontró la licencia del conjunto | Solo si se verifica la licencia |
| **TrueFake** (Univ. de Trento, IJCNN 2025) | 600 000 imágenes, 180 000 **compartidas en Facebook, X y Telegram** | 5 de difusión y 3 GAN | Público en GitHub; verificar licencia | **Evaluación en condiciones reales** (recompresión de redes sociales) |
| **Semi-Truths** (NeurIPS 2024) | 850 000 imágenes con **ediciones localizadas** (inpainting) sobre 27 600 reales | Varios modelos de difusión | Figura solo como «cc», sin variante; las fotos de origen tienen licencias propias | Medir **ediciones parciales** (CA13), sin entrenar |
| **VISION** (Univ. de Florencia, 2017) | **Fotos reales de 35 celulares**, en versión nativa y **compartidas por WhatsApp y Facebook** (34 427 imágenes) | — (todas reales) | CC BY-SA 4.0 | Solo para entrenar la resistencia a WhatsApp, sin desbalancear los temas. **No** para evaluar: sus escenas no son las del sistema |
| **FODB · Forchheim Image Database** (2021) | 143 escenas tomadas con 27 celulares, cada una en 6 versiones: original y copias de Facebook, Instagram, Telegram, Twitter y **WhatsApp** | — (todas reales) | No se encontró: verificar | Fotos reales con WhatsApp, si la licencia lo permite |
| **CarDD** (USTC, 2022) | 4 000 fotos reales de **autos dañados**, con caras y patentes tapadas | — (todas reales) | Solo investigación no comercial; requiere aceptar las condiciones de Flickr y Shutterstock | Fotos reales de **choques** para el conjunto propio |
| GenImage | Un millón de pares, 8 generadores | 7 de difusión y 1 GAN (2023) | No se encontró | Descartado: generadores viejos y **sesgo de JPEG** documentado (ver abajo) |
| WildFake (AAAI 2025) | 3,7 millones de imágenes de comunidades | Muchos | No se encontró | Descartado por ahora: sin licencia verificable |
| Chameleon (ICLR 2024) | Imágenes que personas creyeron reales | Varios | Solo investigación académica, a pedido por correo | Opcional, como prueba difícil |

## Fotos reales de lesiones, lugares de trabajo y viviendas (búsqueda del 2026-10-30)

Pedido de la autora: buscar conjuntos **reales** de lesiones y de daños en viviendas, para cumplir la regla de oro (fotos reales de las mismas escenas que las generadas). Se suman los lugares de trabajo, que el protocolo también necesita.

| Conjunto | Escena | Qué tiene | Licencia | ¿Sirve? | Cómo se usaría |
|---|---|---|---|---|---|
| **SCIN** (Google y Stanford, 2024) | 5 · lesión (piel) | Más de 10 000 fotos de piel **sacadas por las propias personas** y donadas con consentimiento, con **tipo de Fitzpatrick** (dermatólogos) y **tono Monk** (10 tonos) | *SCIN Data Use License*: investigación; prohíbe intentar reidentificar | **Sí, el mejor hallazgo.** Fotos caseras de piel, como las que se mandan a la ART, y con el tono de piel etiquetado | Reales de la escena 5 en el conjunto propio, **repartidas por tono de piel** con sus etiquetas. Son sobre todo afecciones de la piel (alergias, infecciones), no golpes: complementan, no reemplazan, las lesiones |
| **Fitzpatrick17k** (2021) | 5 · lesión (piel) | 16 577 fotos clínicas con tipo de Fitzpatrick (1 a 6) | CC BY-NC-SA 3.0; las imágenes se bajan de su sitio de origen (DermaAmin, Atlas Dermatológico) | Parcial | Para medir el tono de piel con fotos reales anteriores a 2022. Son fotos de atlas médicos, no de celular, y solo 2 168 de pieles 5 y 6 |
| rupeshsah/wound (Hugging Face) | 5 · lesión | 1 564 imágenes de 10 tipos (raspón, moretón, quemadura, corte, laceración…) | Sin verificar | **No** | Imágenes reducidas a 350 × 350 y juntadas de internet: el origen no se puede verificar (podrían ser generadas) y el tamaño fijo es un atajo de formato. Se descarta |
| Kaggle «Wound Images» y conjuntos de Roboflow (wounds_type, basic-wound-classify) | 5 · lesión | Pocas centenas a miles, por tipo de herida | Dominio público o CC BY 4.0 según el conjunto | **No** para evaluar | Mismo problema: fotos juntadas de la web, sin origen documentado y la mitad duplicadas en espejo en el de Kaggle |
| **MOCS** (2021) y su copia LouisChen15/ConstructionSite (Hugging Face) | 6 · lugar de trabajo | 41 668 fotos reales de **obras** de varios sitios | CC BY-NC 4.0, a pedido; la copia en Hugging Face pide aceptar condiciones | **Sí** | Reales de la escena 6 en el conjunto propio (una muestra de 100 a 150). Agregado a `candidatos_v1.yaml` |
| SODA (2022) | 6 y 7 | Más de 20 000 fotos de obras con trabajadores, cascos y herramientas | No figura: verificar en el paquete de descarga | Quizás | Si la licencia se verifica, para la escena 7 (casco, herramienta) |
| HOUSE DAMAGE LEVEL y House-Wall-Damage (Roboflow) | Viviendas | 2 891 imágenes de daño en casas; paredes con humedad o descascaradas | CC BY 4.0 | **Fuera del alcance** por ahora | Ver la nota de abajo |
| Relevamiento del valle del Ahr (Figshare, 2021) | Viviendas | Fotos de campo de fachadas después de la inundación | Verificar | Fuera del alcance | Ídem |

**Nota sobre viviendas.** El 2026-10-30 la autora decidió que las escenas sean **solo** de casos automovilísticos y laborales, que son los dos tipos de caso del sistema (`TIPOS_CASO` en el backend). La especificación (CA12) todavía menciona «daños en viviendas»: queda registrado como cuestión abierta para que la autora confirme si se suman o se quitan de la especificación. Si se suman, la base es HOUSE DAMAGE LEVEL (CC BY 4.0), verificando que sean fotos y no renders.

**Conclusiones sobre las lesiones:**
- No hay ningún conjunto público con **golpes, moretones o raspones fotografiados con celular y origen verificable**. Los que existen se armaron juntando fotos de internet.
- Por eso las lesiones reales salen de tres lados: **SCIN** (piel fotografiada por las personas, con tono de piel), **fotos de conocidos con consentimiento** (moretones, raspones, yesos, sin cara) y, para medir el tono de piel, **Fitzpatrick17k**.
- Ninguno de estos se usa para **entrenar**: en el entrenamiento no hay sintéticas de lesiones, y el modelo aprendería «piel = real» (el mismo atajo que la regla de oro evita en la evaluación).

## Hallazgos importantes

- **Sesgo de formato en los conjuntos públicos.** El trabajo «Fake or JPEG?» muestra que en conjuntos como GenImage las reales son JPEG y las generadas PNG, y los detectores aprenden a distinguir el formato en lugar de la generación. Nuestra **normalización anti-atajos** (todo a JPEG con calidad y tamaño al azar, igual para las dos clases) responde justamente a esto. Es un buen argumento para el informe.
- **La recompresión de redes sociales baja el desempeño.** TrueFake muestra que los detectores entrenados con imágenes limpias empeoran con imágenes compartidas en redes. No encontramos ningún conjunto público con WhatsApp: por eso **el conjunto propio, con su variante de WhatsApp, es un aporte original del proyecto**.
- **Fotos reales con WhatsApp sí existen:** VISION y FODB tienen fotos de celulares en versión original y reenviadas por WhatsApp. **Pero sus escenas no son las del sistema**, así que no sirven para evaluar. Criterio de la autora: las fotos reales tienen que ser de las mismas escenas que las generadas, para que el modelo no aprenda a distinguir el tema (ver el protocolo). CarDD sí aporta fotos reales de autos dañados, la escena más importante del sistema. Los conjuntos reales de **lesiones** y de **lugares de trabajo** se buscaron el mismo día: ver la sección anterior.
- **Diversidad de tonos de piel:** las lesiones se generan y se evalúan en seis tonos de piel (escala de Fitzpatrick aproximada), para medir si el modelo funciona igual para todas las personas.
- **Bajar fotos sueltas de internet no garantiza que sean reales:** pueden estar generadas o editadas. Las fotos reales se toman de conjuntos académicos con origen documentado (cámara y fecha), preferentemente anteriores a 2022, o las saca la autora con su celular.
- **Las licencias son casi todas no comerciales.** Alcanzan para el proyecto final; una versión comercial requeriría reentrenar (ya registrado como pregunta abierta de la especificación).
- **Las licencias cambian entre revisiones** (OpenFake es el ejemplo más claro). La receta tiene que fijar una **revisión concreta** de cada conjunto, y la ficha la registra.

## Cómo se decide

El cuaderno de exploración (T25, `red_neuronal/cuadernos/02_exploracion_datos_colab.ipynb`), que corre en Colab porque desde el entorno del agente no se puede acceder a Hugging Face. Los candidatos están en `red_neuronal/configuracion/candidatos_v1.yaml`:

1. lee de cada candidato la **licencia de su ficha en la revisión exacta**, sus columnas y sus generadores;
2. baja una muestra chica y mide formatos, tamaños y compresión;
3. descarta los que no estén disponibles o no tengan licencia verificable.

Con eso se arma la receta v1 (T27).

## Propuesta de receta v1 (a confirmar con la exploración)

- **Entrenamiento:** Community Forensics *Small* + OpenFake (revisión fija), con **menos generadores y más imágenes por cada uno** (lección de la prueba de concepto).
- **No vistos:** Gemini y Midjourney v7 (de AIGenImages2026 o Treasure, si la licencia lo permite), para medir generadores comerciales que el modelo no conoce. Es también la base de la demostración de reentrenamiento: después se suman y sale la versión 1.1.0.
- **Condiciones reales:** el conjunto propio (protocolo en [docs/guias/protocolo-conjunto-propio.md](../guias/protocolo-conjunto-propio.md)) y, si se verifica la licencia, TrueFake.
- **Ediciones:** las del conjunto propio y una muestra de Semi-Truths, solo para medir.

## Fuentes

- [VISION: README de la Universidad de Florencia](https://lesc.dinfo.unifi.it/VISION/README.txt) y [artículo](https://link.springer.com/doi/10.1186/s13635-017-0067-2)
- [The Forchheim Image Database for Camera Identification in the Wild](https://arxiv.org/pdf/2011.02241)
- [CarDD: A New Dataset for Vision-based Car Damage Detection](https://arxiv.org/pdf/2211.00945) y [copia en Hugging Face](https://huggingface.co/datasets/harpreetsahota/CarDD/commit/c8abb22ec09d2ef65594caa87545ed0a7fa99318)

- [Treasure (Hugging Face)](https://huggingface.co/datasets/ThreeLiu/Treasure/blob/main/README.md) y [Fleet: Few Shots Lead Effective AI-generated Image Detection](https://arxiv.org/pdf/2606.31082)
- [Automated In-the-Wild Data Collection for Continual AI Generated Image Detection (ACM)](https://dl.acm.org/doi/10.1145/3810988.3812662)
- [MLLM-Generated-Image-Detection-Dataset (Hugging Face)](https://huggingface.co/datasets/zr-zhang/MLLM-Generated-Image-Detection-Dataset)
- [OpenFake: ficha en Hugging Face](https://huggingface.co/datasets/ComplexDataLab/OpenFake/blob/main/README.md) y [artículo](https://arxiv.org/abs/2509.09495v1)
- [Community Forensics *Small*: historial de la ficha](https://huggingface.co/datasets/OwensLab/CommunityForensics-Small/commit/307a7bb22aa0b62e5a51e4a8168a804ddf87596d)
- [ShareGPT-4o-Image (Hugging Face)](https://huggingface.co/datasets/FreedomIntelligence/ShareGPT-4o-Image/tree/refs%2Fconvert%2Fparquet/2_text_and_image_to_image/train)
- [TrueFake: A Real World Case Dataset of Last Generation Fake Images also Shared on Social Networks](https://arxiv.org/abs/2504.20658v1)
- [Semi-Truths (Hugging Face)](https://huggingface.co/datasets/semi-truths/Semi-Truths/blob/main/README.md?code=true)
- [SCIN: blog de Google Research](https://www.research.google/blog/scin-a-new-resource-for-representative-dermatology-images/), [repositorio](https://github.com/google-research-datasets/scin) y [artículo](https://www.arxiv.org/abs/2402.18545)
- [Fitzpatrick17k (arXiv 2104.09957)](https://arxiv.org/abs/2104.09957) y [CleanPatrick, que confirma la licencia](https://arxiv.org/pdf/2505.11034)
- [rupeshsah/wound (Hugging Face)](https://huggingface.co/datasets/rupeshsah/wound), [wounds_type (Roboflow)](https://universe.roboflow.com/wounddetectionai/wounds_type-jtzt1) y [basic-wound-classify (Roboflow)](https://universe.roboflow.com/clinicvision/basic-wound-classify-mpoys)
- [OpenConstruction: relevamiento de conjuntos de obras, con la licencia de MOCS](https://arxiv.org/pdf/2508.11482), [SODA](https://arxiv.org/pdf/2202.09554) y [ConstructionSite (Hugging Face)](https://huggingface.co/datasets/LouisChen15/ConstructionSite)
- [HOUSE DAMAGE LEVEL (Roboflow)](https://universe.roboflow.com/anne-pearl-inting/house-damage-level), [House-Wall-Damage (Roboflow)](https://universe.roboflow.com/salehs/house-wall-damage) y [relevamiento del valle del Ahr (Figshare)](https://figshare.com/articles/dataset/Post-flood_field_survey_of_the_Ahr_Valley_Germany_/19222656)
- [GenImage](https://github.com/weili-thu/genimage) y [Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets](https://arxiv.org/pdf/2403.17608)
- [WildFake (arXiv)](https://arxiv.org/pdf/2402.11843)
- [A Sanity Check for AI-generated Image Detection (Chameleon)](https://arxiv.org/pdf/2406.19435v2)
