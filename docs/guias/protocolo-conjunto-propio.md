# Protocolo del conjunto propio

Guía para que la autora genere y reúna las imágenes del **conjunto propio**: fotos creadas con las herramientas que usaría alguien para falsificar una prueba, fotos reales equivalentes y fotos reales editadas con IA, cada una en tres versiones. Sirve para medir la red neuronal **en las condiciones reales del sistema** (funcionalidad 010, CA12 y CA13; tareas T26 y E04).

> **Estas imágenes nunca se usan para entrenar ni se suben al repositorio.** Se guardan en una carpeta privada de Google Drive y solo se usan para evaluar.

## Cuántas imágenes

| Grupo | Mínimo | Ideal | Variantes |
|---|---|---|---|
| ChatGPT | 50 | 80 | original, WhatsApp, captura |
| Gemini | 50 | 80 | original, WhatsApp, captura |
| Copilot | 50 | 80 | original, WhatsApp, captura |
| Midjourney (si hay acceso) | 50 | 80 | original, WhatsApp, captura |
| **Fotos reales propias** | 200 | 300 | original, WhatsApp, captura |
| **Fotos reales editadas con IA** (ChatGPT y Gemini) | 50 | 80 | original, WhatsApp, captura |

Cada imagen se guarda **tres veces** (una por variante): el mínimo son unas 450 × 3 ≈ 1 350 archivos. No hace falta hacerlo todo de una vez. Se puede ir sumando y evaluar con lo que haya.

## Antes de empezar

1. Crear en Google Drive la carpeta **privada** `evidentia/conjunto-propio/`. No compartirla con nadie.
2. Copiar la planilla de control (abajo) en Google Sheets dentro de esa carpeta.
3. Anotar en la planilla, para cada herramienta, **la fecha y el modelo que usa ese día** (por ejemplo, «ChatGPT, GPT-image, 2026-11-02»). Las herramientas cambian de modelo sin avisar.

## Las escenas

Todas las imágenes, generadas y reales, son de las **mismas escenas**: las que aparecen en los casos de abogados y aseguradoras. Así el modelo se mide con lo que va a ver de verdad, y la temática no delata cuál es generada.

| # | Escena | Ejemplo de foto real equivalente |
|---|---|---|
| 1 | Choque de auto: paragolpes, puerta o capó abollado | Un auto con un golpe en la calle o en un estacionamiento |
| 2 | Rayón o daño leve en un auto | Un rayón en la pintura |
| 3 | Vidrio roto: parabrisas, ventanilla o ventana de una casa | Un vidrio astillado |
| 4 | Lesión leve: moretón, raspón, venda, yeso | Un moretón propio o de alguien que lo consienta, sin mostrar la cara |
| 5 | Humedad, mancha o rotura en una pared o un techo | Una pared con humedad |
| 6 | Daño por agua: piso inundado, mueble mojado | Un piso mojado |
| 7 | Objeto dañado: celular con la pantalla rota, electrodoméstico | Un celular con la pantalla rota |
| 8 | Documento sobre una mesa: recibo, factura, ticket | Un ticket real con los datos tapados |
| 9 | Captura de una conversación de chat | Una captura propia con nombres tapados |
| 10 | Calle o esquina donde ocurrió un hecho | Una esquina del barrio |

## Prompts para generar

Usar **prompts en español**, como los escribiría una persona común, y **pedir realismo**. Variar la escena, el encuadre, la luz y el lugar. No repetir el mismo prompt más de 2 veces.

**Plantilla:** «Foto realista tomada con un celular de [escena], [detalle], [lugar], [luz]. Que parezca una foto común, sin filtros.»

| Escena | Prompts de ejemplo |
|---|---|
| 1 | «Foto realista tomada con un celular del paragolpes delantero abollado de un Fiat Cronos gris después de un choque, en una calle de Buenos Aires, de día nublado.» · «Foto de celular de la puerta trasera hundida de un Volkswagen Gol blanco estacionado en la vereda, de noche, con la luz de un farol.» |
| 2 | «Primer plano de un rayón largo en la puerta de un auto rojo, foto de celular con flash.» |
| 3 | «Foto de celular del parabrisas astillado de una camioneta, vista desde adentro, de día.» · «Ventana de una casa con el vidrio roto y vidrios en el piso, foto tomada con el celular.» |
| 4 | «Foto de celular de un moretón violeta en el antebrazo, luz de interior, sin mostrar la cara.» · «Rodilla con un raspón y una curita, foto casera con el celular.» |
| 5 | «Foto realista de una mancha de humedad en la esquina del techo de un dormitorio, pintura descascarada.» |
| 6 | «Piso de cerámica de una cocina inundado con dos centímetros de agua, foto de celular.» |
| 7 | «Celular Samsung con la pantalla rota en forma de telaraña sobre una mesa de madera, foto de celular.» |
| 8 | «Foto de un ticket de compra arrugado sobre una mesa, tomado con el celular, con letra legible.» |
| 9 | «Captura de pantalla de una conversación de WhatsApp en español sobre un choque de autos.» |
| 10 | «Esquina de un barrio de Córdoba con semáforo y un auto detenido, foto tomada con el celular de día.» |

Reparto sugerido por herramienta: **5 a 8 imágenes por escena**, que suman entre 50 y 80.

## Fotos reales

**Qué cuenta como «real»:** cualquier foto tomada con una cámara, aunque no muestre un hecho real. Un auto estacionado, una pared con humedad, el propio brazo, un ticket: todas son reales. No hace falta un choque de verdad.

**De dónde salen, en orden de preferencia:**
1. **Conjuntos académicos de fotos reales** (no hace falta sacarlas): VISION (fotos de 35 celulares, ya con su versión de WhatsApp), FODB (si se verifica la licencia) y CarDD (autos dañados). El agente las incorpora con el cuaderno de exploración.
2. **Fotos propias con el celular**, de las escenas de la tabla: suman las condiciones de Argentina (autos, calles, documentos locales).
3. **Fotos de familiares o conocidos**, con su consentimiento por escrito y sin datos personales.

**No** se bajan fotos sueltas de internet: pueden estar generadas o editadas y su origen no se puede verificar.

**Si se sacan fotos propias:**

- Tomarlas de las mismas escenas.
- **No** usar fotos de casos reales de clientes ni de terceros sin su consentimiento.
- **No** mostrar caras, patentes legibles, documentos de identidad ni datos personales. Si aparecen, elegir otra foto (no taparlos en la original, porque eso ya es una edición).
- Anotar el modelo del celular en la planilla.

## Fotos reales editadas con IA (CA13)

1. Tomar una foto real (de las de arriba).
2. Subirla a ChatGPT o a Gemini y pedir una **edición localizada**, por ejemplo:
   - «Agregale una abolladura grande en la puerta del conductor, que se vea real.»
   - «Agregá una mancha de humedad en la pared de la derecha.»
   - «Hacé que el parabrisas aparezca roto.»
   - «Agregá un moretón en el brazo.»
3. Guardar la imagen editada que devuelve la herramienta.

## Las tres versiones de cada imagen

| Variante | Cómo se hace |
|---|---|
| **original** | El archivo tal cual lo descargaste de la herramienta o lo sacó el celular. Sin abrirlo ni guardarlo en ningún editor |
| **whatsapp** | Enviarlo **como foto** (no como documento) a un chat propio de WhatsApp (por ejemplo, «Mensajes para mí») y descargar la versión recibida |
| **captura** | Abrir la imagen en pantalla completa en el celular y sacar una **captura de pantalla** |

## Carpetas y nombres

La estructura es fija: el pipeline la lee así (`<clase>/<generador>/<variante>/`).

```
evidentia/conjunto-propio/
├── sintetica/
│   ├── chatgpt/            original/  whatsapp/  captura/
│   ├── gemini/             original/  whatsapp/  captura/
│   ├── copilot/            original/  whatsapp/  captura/
│   ├── midjourney/         original/  whatsapp/  captura/
│   ├── chatgpt-edicion/    original/  whatsapp/  captura/
│   └── gemini-edicion/     original/  whatsapp/  captura/
└── real/
    └── celular-propio/     original/  whatsapp/  captura/
```

- **Nombre de archivo:** `<escena>-<número>.<extensión>`, por ejemplo `01-choque-007.png`. La misma imagen lleva **el mismo nombre en sus tres variantes**, así se pueden comparar.
- Nada de espacios, tildes ni eñes en los nombres.

## Planilla de control

| Archivo | Grupo | Escena | Herramienta y modelo | Fecha | Prompt o descripción | ¿Tiene las 3 variantes? | Observaciones |
|---|---|---|---|---|---|---|---|
| 01-choque-007 | chatgpt | 1 | ChatGPT, GPT-image | 2026-11-02 | «Foto realista…» | sí | |

## Reglas de privacidad

- Carpeta privada; nunca se comparte ni se sube al repositorio.
- Sin caras, patentes, documentos ni datos personales de nadie.
- Nunca fotos de casos reales de clientes.
- Al terminar el proyecto, la autora decide si se conserva o se borra.

## Cuando esté listo (o con una parte)

Avisar al agente. La evaluación se corre en Colab con `python -m clasificador evaluar --conjunto-propio <carpeta>`. El resultado sale **por herramienta y por variante**, y queda en la ficha del modelo y en el capítulo 11 de [docs/red-neuronal/](../red-neuronal/README.md).
