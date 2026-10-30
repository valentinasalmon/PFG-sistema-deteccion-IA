# Protocolo del conjunto propio

Guía para que la autora genere y reúna las imágenes del **conjunto propio**. Son fotos creadas con las herramientas que usaría alguien para falsificar una prueba, fotos reales **de las mismas escenas** y fotos reales editadas con IA, cada una en tres versiones. Sirve para medir la red neuronal **en las condiciones reales del sistema** (funcionalidad 010, CA12 y CA13; tareas T26 y E04).

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

| # | Escena | Prefijo del nombre |
|---|---|---|
| 1 | Choque de auto (abolladura, golpe) | `01-choque` |
| 2 | Rayón o daño leve en un auto | `02-rayon` |
| 3 | Vidrio roto (parabrisas, ventanilla, ventana) | `03-vidrio` |
| 4 | Lesión en una persona (moretón, raspón, corte, quemadura, yeso) | `04-lesion` |
| 5 | Humedad o rotura en una pared o un techo | `05-humedad` |
| 6 | Daño por agua (piso inundado, mueble mojado) | `06-agua` |
| 7 | Objeto dañado (celular, electrodoméstico) | `07-objeto` |
| 8 | Documento: ticket, factura, recibo | `08-documento` |
| 9 | Captura de una conversación de chat | `09-chat` |
| 10 | Calle o esquina donde ocurrió un hecho | `10-calle` |

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
| **[ambiente]** | dormitorio, cocina, baño, living, local comercial, oficina |

**Diversidad de tonos de piel:** repartir las lesiones en partes iguales entre los seis tonos de la lista, que siguen de forma aproximada la escala de Fitzpatrick usada en dermatología. Un moretón se ve muy distinto en piel clara y en piel oscura, y un sistema que solo funciona bien con piel clara sería injusto. Hacer lo mismo con las fotos reales, en la medida de lo posible.

### Prompts por escena

1. **Choque:** «Foto realista tomada con un celular del [parte del auto] [daño] de un [auto] [color] después de un choque, en [lugar], [luz], tomada [ángulo]. Que parezca una foto común, sin filtros.»
2. **Rayón:** «Foto de celular de la [parte del auto] [rayada / con la pintura saltada] de un [auto] [color] estacionado en [lugar], [luz], [ángulo].»
3. **Vidrio:** «Foto de celular del [parabrisas astillado / la ventanilla trasera rota / el vidrio de la ventana partido] de un [auto o una casa], [luz], [ángulo], con vidrios en el piso.»
4. **Lesión:** «Foto tomada con un celular de un [lesión] en el/la [parte del cuerpo] de [persona] de piel [tono de piel], luz de [ambiente], sin mostrar la cara. Que parezca una foto casera para mostrarle a un médico.»
5. **Humedad:** «Foto realista de una mancha de humedad [en la esquina del techo / en la pared, con pintura descascarada / con moho negro] de un/a [ambiente], [luz], tomada con el celular.»
6. **Agua:** «Foto de celular del piso de [ambiente] inundado con [dos centímetros de agua / un charco grande], [con un mueble mojado / con cajas mojadas], [luz].»
7. **Objeto:** «Foto de celular de [un celular Samsung / un iPhone / un televisor / una heladera] con [la pantalla rota en forma de telaraña / una abolladura / la puerta rota] sobre [una mesa de madera / el piso], [luz].»
8. **Documento:** «Foto de [un ticket de supermercado / una factura de taller mecánico / un recibo de pago] [arrugado / doblado] sobre [una mesa / el tablero de un auto], tomada con el celular, con letra legible y montos en pesos argentinos.»
9. **Chat:** «Captura de pantalla de una conversación de WhatsApp en español rioplatense entre dos personas que hablan de [un choque / un daño en la casa / un reclamo al seguro], con hora y doble tilde azul.»
10. **Calle:** «Foto tomada con un celular de [una esquina con semáforo / una calle con autos estacionados / una ruta] en [lugar], [luz], [ángulo], como la que sacaría un testigo.»

### Fotos reales editadas con IA (CA13)

1. Tomar una foto **real** de las escenas (propia, con consentimiento si hay personas).
2. Subirla a **Gemini**, **ChatGPT** o **Meta AI** y pedir una edición localizada:
   - «Agregale una abolladura grande en la [parte del auto], que se vea real.»
   - «Agregá un [lesión] en el/la [parte del cuerpo].»
   - «Agregá una mancha de humedad en la pared de la derecha.»
   - «Hacé que el parabrisas aparezca roto.»
3. Guardar la imagen editada que devuelve la herramienta.

## Fotos reales: de dónde salen

**Qué cuenta como «real»:** tomada con una cámara. Pero **tiene que ser de las escenas de la tabla** (regla de oro).

| Fuente | Escenas que cubre | Estado |
|---|---|---|
| **CarDD**: 4 000 fotos reales de autos dañados | 1, 2, 3 | La incorpora el agente; licencia de investigación a aceptar |
| **Fotos propias con el celular** (complemento): autos estacionados con golpes o rayones, paredes con humedad, objetos rotos, tickets, calles | 1, 2, 3, 5, 6, 7, 8, 10 | Opcional, de a poco. Unas **30 a 50** ya suman mucho |
| **Fotos de familiares o conocidos** con consentimiento: moretones, raspones, yesos (sin cara) | 4 | Opcional |
| Capturas de chats propios con nombres tapados | 9 | Opcional |
| Conjuntos con escenas de lesiones o viviendas | 4, 5, 6 | Pendiente de buscar: la autora pasa enlaces y el agente los verifica |

**No** se bajan fotos sueltas de internet: pueden estar generadas o editadas y su origen no se puede verificar.

**Si se sacan fotos propias:**
- sin caras, patentes legibles, documentos de identidad ni datos personales. Si aparecen, elegir otra foto (no taparlos en la original, porque eso ya es una edición);
- no usar fotos de casos reales de clientes;
- anotar el modelo del celular en la planilla.

## Las tres versiones de cada imagen

| Variante | Cómo se hace |
|---|---|
| **original** | El archivo tal cual lo descargaste de la herramienta o lo sacó el celular. Sin abrirlo ni guardarlo en ningún editor |
| **whatsapp** | Enviarlo **como foto** (no como documento) a tu chat «Mensajes para mí» de WhatsApp y descargar la versión recibida |
| **captura** | Abrir la imagen en pantalla completa en el celular y sacar una **captura de pantalla** |

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
    │       └── conocidos/            original/  whatsapp/  captura/
    ├── planilla-conjunto-propio      ← Google Sheets
    └── prueba_de_concepto/           ← lo que ya generó Colab
```

- La estructura es **fija**: el pipeline la lee como `<clase>/<generador>/<variante>/<archivo>`. Una herramienta nueva es una carpeta nueva dentro de `sintetica/`.
- **Nombre de archivo:** `<escena>-<número>.<extensión>`, por ejemplo `01-choque-007.png`. La misma imagen lleva **el mismo nombre en sus tres variantes**.
- Sin espacios, tildes ni eñes en los nombres.
- No guardar nada de esto en el repositorio ni en otra nube.

## Planilla de control

| Archivo | Carpeta | Escena | Herramienta y modelo | Fecha | Prompt o descripción | Tono de piel (si hay persona) | ¿3 variantes? | Observaciones |
|---|---|---|---|---|---|---|---|---|
| 01-choque-007 | gemini | 1 | Gemini 2.5 Flash Image | 2026-11-02 | «Foto realista…» | — | sí | |
| 04-lesion-012 | meta-ai | 4 | Meta AI | 2026-11-02 | «Foto tomada con un celular de un moretón…» | morena | sí | |

## Reglas de privacidad

- Carpeta privada; nunca se comparte ni se sube al repositorio.
- Sin caras, patentes, documentos ni datos personales de nadie.
- Nunca fotos de casos reales de clientes.
- Fotos de terceros, solo con su consentimiento.
- Al terminar el proyecto, la autora decide si se conserva o se borra.

## Cuando esté listo (o con una parte)

Avisar al agente. La evaluación se corre en Colab con `python -m clasificador evaluar --conjunto-propio <carpeta>`. El resultado sale **por herramienta y por variante**. El agente suma el desglose **por escena y por tono de piel**, a partir del prefijo del nombre y de la planilla. Todo queda en la ficha del modelo y en el capítulo 11 de [docs/red-neuronal/](../red-neuronal/README.md).
