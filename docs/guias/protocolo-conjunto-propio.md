# Protocolo del conjunto propio

Guía para que la autora genere y reúna las imágenes del **conjunto propio**. Son fotos creadas con las herramientas que usaría alguien para falsificar una prueba, fotos reales **de las mismas escenas** y fotos reales editadas con IA, cada una en tres versiones. Sirve para medir la red neuronal **en las condiciones reales del sistema** (funcionalidad 010, CA12 y CA13; tareas T26 y E04).

> **Cómo hacerlo, paso a paso:** la [guía paso a paso del conjunto propio](guia-paso-a-paso-conjunto-propio.md) tiene la **lista maestra de 90 prompts ya armados y numerados**, las versiones de cada prompt, las carpetas, la rutina con cada imagen, las fotos reales a sacar y cómo buscar conjuntos de datos. Este protocolo tiene las reglas.

> **Estas imágenes nunca se usan para entrenar ni se suben al repositorio.** Se guardan en una carpeta privada de Google Drive y solo se usan para evaluar.

## Regla de oro: misma escena, misma diversidad

**Las fotos reales tienen que ser de las mismas escenas que las generadas** (criterio de la autora, 2026-10-30). Si las generadas fueran choques y lesiones y las reales fueran paisajes o mascotas, el modelo podría aprender a distinguir **el tema** en lugar de la generación. Las métricas saldrían altas y no medirían nada útil: es el mismo tipo de atajo que la normalización evita con el formato.

Por eso:
- cada escena tiene su par: generadas **y** reales del mismo tipo (un choque generado se compara con choques reales);
- la **diversidad de las personas** (tono de piel, edad, sexo) se cuida igual en las generadas y en las reales;
- los conjuntos de fotos reales «generales» (por ejemplo, VISION) **no** se usan para evaluar. Como mucho sirven para entrenar la resistencia a WhatsApp, siempre que no desbalanceen los temas.

## Herramientas (versiones gratuitas)

| Herramienta | Acceso de la autora | Carpeta | Observaciones |
|---|---|---|---|
| ChatGPT | Gratis | `chatgpt` | Pocas imágenes por día: repartirlas en varios días |
| Gemini | Suscripción | `gemini` | La más cómoda para generar volumen; también edita fotos |
| Copilot (Microsoft Designer) | Gratis | `copilot` | Imágenes cuadradas o apaisadas |
| Meta AI (dentro de WhatsApp, Instagram o meta.ai) | Gratis | `meta-ai` | Muy realista y **muy probable en casos reales**, porque está dentro de WhatsApp |
| Grok (X) | Gratis, con límite | `grok` | Opcional |
| Otras gratuitas (Ideogram, Leonardo, Adobe Firefly) | Créditos gratis | `ideogram`, `leonardo`, `firefly` | Opcionales, para sumar variedad |

Anotar en la planilla, para cada imagen, **la herramienta, el modelo que dice usar y la fecha**: las herramientas cambian de modelo sin avisar.

## Cuántas imágenes

| Grupo | Mínimo | Ideal |
|---|---|---|
| ChatGPT | 30 | 50 |
| Gemini | 50 | 80 |
| Copilot | 50 | 80 |
| Meta AI | 50 | 80 |
| Grok y otras (en total) | — | 30 |
| **Fotos reales de las mismas escenas** | 200 | 300 |
| **Fotos reales editadas con IA** (Gemini, ChatGPT, Meta AI) | 50 | 80 |

Cada imagen se guarda en **tres versiones** (original, WhatsApp y captura). No hace falta hacerlo todo de una vez: se va sumando y se evalúa con lo que haya.

## Las escenas

El sistema tiene **dos tipos de caso: automovilístico y laboral** (accidentes de trabajo). Las escenas son solo de esos dos ámbitos (criterio de la autora, 2026-10-30).

| # | Tipo | Escena | Prefijo del nombre |
|---|---|---|---|
| 1 | Automovilístico | Choque de auto o moto (abolladura, golpe) | `01-choque` |
| 2 | Automovilístico | Rayón o daño leve | `02-rayon` |
| 3 | Automovilístico | Vidrio roto (parabrisas, ventanilla, óptica) | `03-vidrio` |
| 4 | Automovilístico | Lugar del siniestro (esquina, calle, ruta) | `04-calle` |
| 5 | Automovilístico y laboral | Lesión en una persona (moretón, raspón, corte, quemadura, fractura con yeso, vendaje) | `05-lesion` |
| 6 | Laboral | Lugar del accidente de trabajo (obra, andamio, escalera, fábrica, depósito, taller) | `06-lugar-trabajo` |
| 7 | Laboral | Máquina, herramienta o elemento de protección dañado (casco, guante, amoladora, escalera rota) | `07-herramienta` |
| 8 | Ambos (opcional) | Documento: certificado médico, constancia de la ART, presupuesto de taller | `08-documento` |

## Prompts con partes intercambiables

Cada prompt tiene **[partes entre corchetes]** que se cambian en cada imagen, eligiendo de las listas de abajo. **No repetir la misma combinación.** Siempre pedir que parezca una foto común de celular, sin filtros.

### Listas para combinar

| Parte | Opciones |
|---|---|
| **[auto]** | Fiat Cronos, Toyota Etios, Volkswagen Gol Trend, Chevrolet Onix, Peugeot 208, Renault Sandero, Ford Ka, Toyota Hilux, Ford Ranger, Fiat Uno, Renault Kangoo, una moto Honda Wave |
| **[color]** | blanco, gris plata, negro, rojo, azul, bordó |
| **[parte del auto]** | paragolpes delantero, paragolpes trasero, puerta del conductor, puerta trasera, guardabarros, capó, baúl, espejo lateral, óptica delantera, llanta |
| **[daño]** | abollado, hundido, rayado, con la pintura saltada, partido, desprendido |
| **[lugar]** | una calle de Buenos Aires, una avenida de Rosario, un barrio de Córdoba, un estacionamiento de supermercado, una ruta con banquina de tierra, un garaje, la puerta de una casa |
| **[luz]** | de día soleado, de día nublado, al atardecer, de noche con luz de farol, con flash, bajo la lluvia |
| **[ángulo]** | de frente, de costado, en diagonal, de cerca (primer plano), desde lejos, desde arriba |
| **[tono de piel]** | muy clara, clara, trigueña, morena, marrón oscura, negra |
| **[persona]** | una mujer joven, un hombre joven, una mujer adulta, un hombre adulto, una persona mayor, un adolescente |
| **[parte del cuerpo]** | antebrazo, mano, rodilla, pierna, hombro, espalda, tobillo, frente (sin mostrar la cara completa) |
| **[lesión]** | moretón violeta, moretón amarillento de varios días, raspón, corte con puntos, quemadura leve, inflamación, yeso, vendaje |
| **[ambiente]** | consultorio, guardia de un hospital, casa, vestuario de una fábrica |
| **[trabajo]** | albañil en una obra, operario de fábrica, repartidor en moto, mecánico de taller, electricista, empleada de depósito, cocinero, enfermera |
| **[lugar de trabajo]** | una obra en construcción, un andamio, una fábrica, un depósito con estanterías, un taller mecánico, la cocina de un restaurante, un campo |
| **[accidente laboral]** | caída de una escalera, caída de un andamio, corte con una amoladora, golpe con una máquina, quemadura con aceite, resbalón en un piso mojado, aplastamiento de un pie |

**Diversidad de tonos de piel:** repartir las lesiones en partes iguales entre los seis tonos de la lista, que siguen de forma aproximada la escala de Fitzpatrick usada en dermatología. Un moretón se ve muy distinto en piel clara y en piel oscura, y un sistema que solo funciona bien con piel clara sería injusto. Hacer lo mismo con las fotos reales, en la medida de lo posible.

### Prompts por escena

1. **Choque:** «Foto realista tomada con un celular del [parte del auto] [daño] de un [auto] [color] después de un choque, en [lugar], [luz], tomada [ángulo]. Que parezca una foto común, sin filtros.»
2. **Rayón:** «Foto de celular de la [parte del auto] [rayada / con la pintura saltada] de un [auto] [color] estacionado en [lugar], [luz], [ángulo].»
3. **Vidrio:** «Foto de celular del [parabrisas astillado / la ventanilla trasera rota / la óptica delantera partida] de un [auto] [color], [luz], [ángulo], con vidrios en el piso.»
4. **Lugar del siniestro:** «Foto tomada con un celular de [una esquina con semáforo / una calle con autos estacionados / una ruta con banquina] en [lugar], [luz], [ángulo], como la que sacaría un testigo después de un choque.»
5. **Lesión:** «Foto tomada con un celular de un [lesión] en el/la [parte del cuerpo] de [persona] de piel [tono de piel], [con ropa de trabajo / con ropa común], en [ambiente], sin mostrar la cara. Que parezca una foto casera para mostrarle a un médico o a la ART.»
6. **Lugar del accidente de trabajo:** «Foto realista tomada con un celular de [lugar de trabajo] justo después de [accidente laboral], [luz], [ángulo], sin personas o con personas de espaldas. Que parezca la foto que saca un compañero de trabajo.»
7. **Herramienta o protección dañada:** «Foto de celular de [un casco de obra partido / un guante de trabajo roto y manchado / una amoladora con el disco roto / una escalera de aluminio doblada] en el piso de [lugar de trabajo], [luz].»
8. **Documento (opcional):** «Foto de [un certificado médico / una constancia de una ART / un presupuesto de un taller mecánico] [doblado / sobre una mesa], tomada con el celular, con letra legible, en español de Argentina.»

### Fotos reales editadas con IA (CA13)

1. Tomar una foto **real** de las escenas (propia, con consentimiento si hay personas).
2. Subirla a **Gemini**, **ChatGPT** o **Meta AI** y pedir una edición localizada:
   - «Agregale una abolladura grande en la [parte del auto], que se vea real.»
   - «Agregá un [lesión] en el/la [parte del cuerpo].»
   - «Agregale un yeso en el brazo.»
   - «Hacé que la escalera aparezca doblada y caída en el piso.»
   - «Hacé que el parabrisas aparezca roto.»
3. Guardar la imagen editada que devuelve la herramienta.

## Fotos reales: de dónde salen

**Qué cuenta como «real»:** tomada con una cámara. Pero **tiene que ser de las escenas de la tabla** (regla de oro).

| Fuente | Escenas que cubre | Estado |
|---|---|---|
| **CarDD**: 4 000 fotos reales de autos dañados | 1, 2, 3 | La incorpora el agente; licencia de investigación a aceptar |
| **MOCS** (fotos reales de obras; copia en Hugging Face como ConstructionSite) | 6, 7 | Encontrado el 2026-10-30; CC BY-NC 4.0, pide aceptar condiciones |
| **SCIN** (Google y Stanford): fotos de piel sacadas por las propias personas, con el tono de piel etiquetado | 5 | Encontrado el 2026-10-30; licencia de investigación. Los conjuntos de heridas que circulan (Kaggle, Roboflow) se descartaron: son fotos juntadas de internet, sin origen verificable |
| **Fotos propias con el celular** (complemento): autos estacionados con golpes o rayones, calles, obras vistas desde la vereda, herramientas | 1, 2, 3, 4, 6, 7 | Opcional, de a poco. Unas **30 a 50** ya suman mucho |
| **Fotos de familiares o conocidos** con consentimiento: moretones, raspones, yesos (sin cara) | 5 | Opcional |

**No** se bajan fotos sueltas de internet: pueden estar generadas o editadas y su origen no se puede verificar.

**Si se sacan fotos propias:**
- sin caras, patentes legibles, documentos de identidad ni datos personales. Si aparecen, elegir otra foto (no taparlos en la original, porque eso ya es una edición);
- no usar fotos de casos reales de clientes;
- anotar el modelo del celular en la planilla.

## Las tres versiones de cada imagen

| Variante | Cómo se hace |
|---|---|
| **original** | El archivo tal cual lo descargaste de la herramienta o lo sacó el celular. Sin abrirlo ni guardarlo en ningún editor. Meta AI se usa desde **meta.ai en la web**: la imagen generada dentro de WhatsApp ya llega comprimida |
| **whatsapp** | Enviarlo **como foto** (no como documento) a tu chat «Mensajes para mí» de WhatsApp y descargar la versión recibida |
| **captura** | Abrir la imagen en pantalla completa en el celular y sacar una **captura de pantalla** |

## ¿Se comprimen las imágenes al guardarlas?

**Google Drive no comprime nada:** guarda el archivo tal cual, se suba desde la web, desde la aplicación del celular o desde Google Drive para computadoras. Lo que sí comprime, y hay que evitar para la versión **original**:

| Comprime | Cómo evitarlo |
|---|---|
| **Google Fotos** en calidad «Ahorro de almacenamiento» | Para pasar fotos del celular, usar la aplicación de **Drive** (botón **+ → Subir**) o un cable USB, no Google Fotos |
| **WhatsApp, Telegram, Instagram** | Solo se usan a propósito para la variante **whatsapp** |
| Abrir la imagen en un editor y «Guardar» o «Guardar como» | No abrirla en ningún editor: descargarla y moverla |
| Algunos clientes de correo y la opción «enviar en tamaño reducido» | No pasar las imágenes por correo |
| La copia que muestra el chat de ChatGPT, Gemini o Copilot al hacer clic derecho → «Copiar imagen» | Usar siempre el botón **Descargar** de la herramienta |

Descargar a la computadora y después subir a Drive **no cambia el archivo**. Para comprobarlo, el tamaño en KB tiene que ser el mismo en la computadora y en Drive.

## Dónde se guarda

**En Google Drive**, porque Colab lo lee directo. Si querés trabajar desde la computadora, instalá **Google Drive para computadoras**: crea una carpeta que se sincroniza sola, y lo que guardes ahí queda en Drive.

```
Mi unidad/
└── evidentia/                        ← carpeta privada, sin compartir
    ├── conjunto-propio/
    │   ├── sintetica/
    │   │   ├── chatgpt/              original/  whatsapp/  captura/
    │   │   ├── gemini/               original/  whatsapp/  captura/
    │   │   ├── copilot/              original/  whatsapp/  captura/
    │   │   ├── meta-ai/              original/  whatsapp/  captura/
    │   │   ├── grok/                 original/  whatsapp/  captura/
    │   │   ├── gemini-edicion/       original/  whatsapp/  captura/
    │   │   ├── chatgpt-edicion/      original/  whatsapp/  captura/
    │   │   └── meta-ai-edicion/      original/  whatsapp/  captura/
    │   └── real/
    │       ├── celular-propio/       original/  whatsapp/  captura/
    │       ├── conocidos/            original/  whatsapp/  captura/
    │       ├── cardd/                original/  whatsapp/  captura/
    │       ├── scin/                 original/  whatsapp/  captura/
    │       └── obras/                original/  whatsapp/  captura/
    ├── planilla-conjunto-propio      ← Google Sheets
    └── prueba_de_concepto/           ← lo que ya generó Colab
```

- La estructura es **fija**: el pipeline la lee como `<clase>/<generador>/<variante>/<archivo>`. Una herramienta nueva es una carpeta nueva dentro de `sintetica/`.
- **Nombre de archivo:** `<escena>-<número>.<extensión>`, por ejemplo `01-choque-007.png`. La misma imagen lleva **el mismo nombre en sus tres variantes**.
- Sin espacios, tildes ni eñes en los nombres.
- No guardar nada de esto en el repositorio ni en otra nube.

## Planilla de control

La planilla completa, con el número y la versión del prompt, está en la sección 8 de la [guía paso a paso](guia-paso-a-paso-conjunto-propio.md#8-la-planilla). Ejemplo:

| Archivo | Carpeta | N.° de prompt | Versión del prompt | Escena | Herramienta y modelo | Fecha | Tono de piel | Foto de origen | ¿WhatsApp? | ¿Captura? | Observaciones |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01-choque-007 | gemini | 7 | v1 | 01 | Gemini 2.5 Flash Image | 2026-11-02 | — | — | sí | sí | |
| 05-lesion-041 | meta-ai | 41 | v2 | 05 | Meta AI | 2026-11-02 | trigueña | — | sí | sí | Se negó con v1 |

## Reglas de privacidad

- Carpeta privada; nunca se comparte ni se sube al repositorio.
- Sin caras, patentes, documentos ni datos personales de nadie.
- Nunca fotos de casos reales de clientes.
- Fotos de terceros, solo con su consentimiento.
- Al terminar el proyecto, la autora decide si se conserva o se borra.

## Cuando esté listo (o con una parte)

Avisar al agente. La evaluación se corre en Colab con el cuaderno `03_entrenamiento_completo_colab.ipynb`, que usa la carpeta de Drive si existe (`python -m clasificador evaluar --conjunto-propio <carpeta>`). El resultado sale **por herramienta, por variante y por escena** (el prefijo del nombre del archivo). El agente suma el desglose **por tono de piel** a partir de la planilla. Todo queda en la ficha del modelo y en el capítulo 11 de [docs/red-neuronal/](../red-neuronal/README.md).
