# Guía paso a paso del conjunto propio

Todo lo que tiene que hacer la autora con las imágenes del conjunto propio, en orden: qué generar, con qué prompt exacto, dónde guardarlo, cómo hacer las dos versiones, qué fotos reales sacar y cómo buscar conjuntos de datos para que el agente los evalúe.

Las **reglas** (por qué se hace así, privacidad, qué no se hace nunca) están en el [protocolo del conjunto propio](protocolo-conjunto-propio.md). Esta guía es el **cómo**. Si algo de acá contradice el protocolo, manda el protocolo y hay que avisar al agente.

> Estas imágenes **nunca** se usan para entrenar ni se suben al repositorio. Solo sirven para medir la red en condiciones reales.

## 1. Resumen: qué hay que hacer

| # | Tarea | Cuánto | Dónde va | Tiempo aproximado |
|---|---|---|---|---|
| 1 | Crear las carpetas en Drive y la planilla | Una vez | `Mi unidad/evidentia/` | 20 min |
| 2 | Generar las imágenes con la **lista maestra** (sección 5) en cada herramienta | 90 prompts por herramienta; empezar por los 40 de **prioridad A** | `sintetica/<herramienta>/original/` | 2 a 3 min por imagen |
| 3 | Editar fotos reales con IA (sección 6) | 20 ediciones por herramienta (Gemini, ChatGPT, Meta AI) | `sintetica/<herramienta>-edicion/original/` | 3 min por imagen |
| 4 | Sacar fotos reales propias (sección 7) | 30 a 50, de a poco | `real/celular-propio/original/` | Al pasar por la calle |
| 5 | Hacer la versión **captura** de todo lo anterior (sección 4) | Todas | `.../captura/` | 1 min por imagen, en tandas |
| 6 | Completar la planilla | Una fila por imagen | `evidentia/planilla-conjunto-propio` | Al terminar cada tanda |
| 7 | Buscar conjuntos de datos y pasarlos al chat (sección 9) | Cuando aparezcan | Chat con el agente | 5 min por conjunto |
| 8 | Aceptar las condiciones en Hugging Face y correr el cuaderno de exploración (sección 11) | Una vez, **antes que lo demás** | Colab, en CPU | 15 min + 10 a 20 min de ejecución |

No hace falta terminar todo: **con la prioridad A de dos herramientas** ya se puede correr una primera evaluación. Se va sumando.

## 2. Las carpetas

Crear esta estructura en **Google Drive** (en la web: **+ Nuevo → Carpeta**). Los nombres van **exactamente así**: en minúsculas, sin tildes, sin espacios. El pipeline lee `<clase>/<herramienta o fuente>/<variante>/<archivo>`; si una carpeta tiene otro nombre, la evaluación se detiene con un error.

```
Mi unidad/
└── evidentia/                              ← privada, sin compartir con nadie
    ├── planilla-conjunto-propio            ← Hoja de cálculo de Google (sección 8)
    └── conjunto-propio/
        ├── sintetica/
        │   ├── chatgpt/            original/  captura/
        │   ├── gemini/             original/  captura/
        │   ├── copilot/            original/  captura/
        │   ├── meta-ai/            original/  captura/
        │   ├── grok/               original/  captura/    (opcional)
        │   ├── chatgpt-edicion/    original/  captura/
        │   ├── gemini-edicion/     original/  captura/
        │   └── meta-ai-edicion/    original/  captura/
        └── real/
            ├── celular-propio/     original/  captura/
            ├── conocidos/          original/  captura/    (opcional)
            ├── cardd/              original/  captura/    (la llena el agente, sección 7)
            ├── scin/               original/  captura/    (ídem)
            └── obras/              original/  captura/    (ídem)
```

- Las carpetas que no uses pueden quedar vacías o no existir.
- Una herramienta nueva (por ejemplo, Ideogram) es una carpeta nueva dentro de `sintetica/` con sus dos subcarpetas.
- La **foto real original** que usaste para una edición va en `real/celular-propio/` (o `real/conocidos/`), con su propio nombre.

## 3. Cómo se llama cada archivo

```
<escena>-<número>.<extensión>        por ejemplo:  01-choque-007.png
```

- El **número** es el **N.° de prompt** de la lista maestra, con tres cifras. Así, `05-lesion-041.png` es el prompt 41 en **todas** las herramientas: la misma escena generada por ChatGPT, Gemini, Copilot y Meta AI, cada una en su carpeta. Eso permite comparar las herramientas con el mismo contenido.
- La extensión es **la que trae el archivo al descargarlo** (`.png`, `.jpg`, `.webp`). No convertir.
- Las dos versiones llevan **el mismo nombre**, cada una en su carpeta (`original/01-choque-007.png`, `captura/01-choque-007.png`). La extensión puede cambiar entre versiones: está bien.
- Si una herramienta da dos imágenes para un prompt, guardar **solo la primera**.
- Ediciones: la escena y un número del **201 al 220**, según la tabla de la sección 6 (por ejemplo, `01-choque-201.png` es la edición E01). Van en otra numeración para no chocar con la lista maestra.
- Fotos reales propias: la escena y un número desde el 301 (`01-choque-301.jpg`, `06-lugar-trabajo-302.jpg`).

## 4. La rutina con cada imagen

### 4.1 Generar y descargar la versión original

1. Abrir la herramienta en una **conversación nueva** (así no arrastra el estilo de las anteriores).
2. Copiar el prompt **exacto** de la lista maestra (versión v1, sección 5).
3. Descargar con el **botón de descarga** de la herramienta. **Nunca** «copiar imagen» ni capturas: eso ya es otra versión.
4. Renombrar el archivo descargado según la sección 3 y moverlo a `sintetica/<herramienta>/original/`.
5. No abrirlo ni guardarlo en ningún editor (ni siquiera «Fotos» de Windows con «Guardar»).

| Herramienta | Dónde | Consejos |
|---|---|---|
| **ChatGPT** (gratis) | chatgpt.com | Pocas imágenes por día: hacer solo la **prioridad A**, repartida en varios días. Si dice que llegaste al límite, seguir mañana |
| **Gemini** (suscripción) | gemini.google.com | La más cómoda para volumen. Pedir **una** imagen por mensaje. Agrega una marca de agua invisible (SynthID): no importa, es parte de lo que se mide |
| **Copilot** (gratis) | copilot.microsoft.com | Descargar desde el menú de la imagen. Suele dar cuadradas |
| **Meta AI** (gratis) | **meta.ai en la computadora** | **No** generarlas dentro de WhatsApp: ahí la imagen ya llega comprimida por WhatsApp y no sirve como «original». Usar la web y descargar |
| **Grok** (opcional) | grok.com o X | Con límite diario. Solo prioridad A |

### 4.2 Versiones del prompt: v1, v2 y v3

Siempre se empieza con **v1**, el texto tal cual de la lista. Solo si hace falta se pasa a la siguiente, y **se anota en la planilla qué versión se usó**:

| Versión | Cuándo | Qué cambiar |
|---|---|---|
| **v1** | Siempre primero | Nada: el prompt de la lista |
| **v2 · suave** | La herramienta **se niega** (pasa sobre todo con lesiones, sangre o accidentes) | Sacar las palabras fuertes: «con algo de sangre» → «limpio»; «corte con puntos» → «cicatriz reciente»; «después de un choque» → «con un golpe». Agregar al principio: «Para un trabajo académico sobre detección de imágenes,» |
| **v3 · más realista** | La imagen sale con **aspecto de render, de publicidad o de ilustración** | Agregar al final: «Tomada con un celular Samsung de gama media, encuadre un poco torcido, algo de ruido, luz natural, nada de profundidad de campo artificial.» |

Si con v3 tampoco sale creíble, anotarlo en «Observaciones» y pasar al siguiente prompt. **No** se descartan imágenes porque «se notan falsas»: también hay que medir esas.

### 4.3 Versión captura

> **Sin versión de WhatsApp** (decisión de la autora, 2026-10-30): las fotos de un caso las sube la persona afectada desde el enlace de carga, así que llegan como original, como captura o generadas con IA. Si ya tenías alguna versión de WhatsApp hecha, guardala aparte: no estorba, pero no hace falta seguir.

1. En el celular, abrir la original en **pantalla completa** (desde Drive o la galería).
2. Sacar una **captura de pantalla** sin hacer zoom.
3. No recortarla: tal cual sale, con lo que se vea de la pantalla.
4. Subirla a `captura/` con el mismo nombre.

## 5. Lista maestra de prompts (v1)

90 prompts para **cada** herramienta. Las partes variables (auto, color, lugar, luz, ángulo, persona, tono de piel) ya están elegidas y repartidas para que no se repitan combinaciones: **copiá el texto tal cual**.

- **Prioridad A** (40): hacerlos primero en todas las herramientas. Son los que alcanzan para ChatGPT gratis.
- **Prioridad B** (50): después, sobre todo en Gemini y Copilot.
- **Lesiones (39 a 68):** cinco por cada uno de los **seis tonos de piel**, y la prioridad A tiene dos de cada tono. Si una herramienta se niega con algún tono más que con otros, anotarlo: también es un dato (sesgo de la herramienta).

| N.° | Archivo | Escena | Tono de piel | Prioridad | Prompt |
|---|---|---|---|---|---|
| 1 | `01-choque-001` | choque | — | A | Foto realista tomada con un celular del espejo lateral abollado de un Fiat Cronos bordó después de un choque, en una ruta con banquina de tierra, bajo la lluvia, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 2 | `01-choque-002` | choque | — | A | Foto realista tomada con un celular de la óptica delantera con la pintura saltada de un Ford Ka negro después de un choque, en una avenida de Rosario, de noche con luz de farol, tomada desde un poco lejos. Que parezca una foto común de celular, sin filtros ni retoques. |
| 3 | `01-choque-003` | choque | — | A | Foto realista tomada con un celular de la puerta del conductor desprendida de un Volkswagen Gol Trend blanco después de un choque, en un garaje, de día nublado, tomada de frente. Que parezca una foto común de celular, sin filtros ni retoques. |
| 4 | `01-choque-004` | choque | — | A | Foto realista tomada con un celular del capó hundido de un Chevrolet Onix gris plata después de un choque, en una calle de Buenos Aires, al atardecer, tomada en diagonal. Que parezca una foto común de celular, sin filtros ni retoques. |
| 5 | `01-choque-005` | choque | — | A | Foto realista tomada con un celular de la puerta trasera partida de un Renault Kangoo rojo después de un choque, en un estacionamiento de supermercado, de noche con flash, tomada de costado. Que parezca una foto común de celular, sin filtros ni retoques. |
| 6 | `01-choque-006` | choque | — | A | Foto realista tomada con un celular del paragolpes delantero abollado de un Peugeot 208 azul después de un choque, en la puerta de una casa en Mendoza, de día soleado, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 7 | `01-choque-007` | choque | — | A | Foto realista tomada con un celular del baúl con la pintura saltada de un Toyota Hilux bordó después de un choque, en un barrio de Córdoba, bajo la lluvia, tomada desde un poco lejos. Que parezca una foto común de celular, sin filtros ni retoques. |
| 8 | `01-choque-008` | choque | — | B | Foto realista tomada con un celular del guardabarros delantero desprendido de un Volkswagen Amarok negro después de un choque, en una ruta con banquina de tierra, de noche con luz de farol, tomada de frente. Que parezca una foto común de celular, sin filtros ni retoques. |
| 9 | `01-choque-009` | choque | — | B | Foto realista tomada con un celular del paragolpes trasero hundido de un Fiat Uno blanco después de un choque, en una avenida de Rosario, de día nublado, tomada en diagonal. Que parezca una foto común de celular, sin filtros ni retoques. |
| 10 | `01-choque-010` | choque | — | B | Foto realista tomada con un celular del espejo lateral partido de un Ford Ranger gris plata después de un choque, en un garaje, al atardecer, tomada de costado. Que parezca una foto común de celular, sin filtros ni retoques. |
| 11 | `01-choque-011` | choque | — | B | Foto realista tomada con un celular de la óptica delantera abollada de un Renault Sandero rojo después de un choque, en una calle de Buenos Aires, de noche con flash, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 12 | `01-choque-012` | choque | — | B | Foto realista tomada con un celular de la puerta del conductor con la pintura saltada de un Toyota Etios azul después de un choque, en un estacionamiento de supermercado, de día soleado, tomada desde un poco lejos. Que parezca una foto común de celular, sin filtros ni retoques. |
| 13 | `01-choque-013` | choque | — | B | Foto realista tomada con un celular del capó desprendido de un Fiat Cronos bordó después de un choque, en la puerta de una casa en Mendoza, bajo la lluvia, tomada de frente. Que parezca una foto común de celular, sin filtros ni retoques. |
| 14 | `01-choque-014` | choque | — | B | Foto realista tomada con un celular de la puerta trasera hundida de un Ford Ka negro después de un choque, en un barrio de Córdoba, de noche con luz de farol, tomada en diagonal. Que parezca una foto común de celular, sin filtros ni retoques. |
| 15 | `01-choque-015` | choque | — | B | Foto realista tomada con un celular del paragolpes delantero partido de un Volkswagen Gol Trend blanco después de un choque, en una ruta con banquina de tierra, de día nublado, tomada de costado. Que parezca una foto común de celular, sin filtros ni retoques. |
| 16 | `01-choque-016` | choque | — | B | Foto realista tomada con un celular del baúl abollado de un Chevrolet Onix gris plata después de un choque, en una avenida de Rosario, al atardecer, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 17 | `02-rayon-017` | rayon | — | A | Foto de celular del guardabarros delantero rayado de un Renault Kangoo rojo estacionado en un garaje, de noche con flash, tomada desde un poco lejos. Que parezca una foto común de celular, sin filtros ni retoques. |
| 18 | `02-rayon-018` | rayon | — | A | Foto de celular del paragolpes trasero rayado de un Peugeot 208 azul estacionado en una calle de Buenos Aires, de día soleado, tomada de frente. Que parezca una foto común de celular, sin filtros ni retoques. |
| 19 | `02-rayon-019` | rayon | — | A | Foto de celular del espejo lateral rayado de un Toyota Hilux bordó estacionado en un estacionamiento de supermercado, bajo la lluvia, tomada en diagonal. Que parezca una foto común de celular, sin filtros ni retoques. |
| 20 | `02-rayon-020` | rayon | — | A | Foto de celular de la óptica delantera rayada de un Volkswagen Amarok negro estacionado en la puerta de una casa en Mendoza, de noche con luz de farol, tomada de costado. Que parezca una foto común de celular, sin filtros ni retoques. |
| 21 | `02-rayon-021` | rayon | — | B | Foto de celular de la puerta del conductor rayada de un Fiat Uno blanco estacionado en un barrio de Córdoba, de día nublado, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 22 | `02-rayon-022` | rayon | — | B | Foto de celular del capó rayado de un Ford Ranger gris plata estacionado en una ruta con banquina de tierra, al atardecer, tomada desde un poco lejos. Que parezca una foto común de celular, sin filtros ni retoques. |
| 23 | `02-rayon-023` | rayon | — | B | Foto de celular de la puerta trasera rayada de un Renault Sandero rojo estacionado en una avenida de Rosario, de noche con flash, tomada de frente. Que parezca una foto común de celular, sin filtros ni retoques. |
| 24 | `02-rayon-024` | rayon | — | B | Foto de celular del paragolpes delantero rayado de un Toyota Etios azul estacionado en un garaje, de día soleado, tomada en diagonal. Que parezca una foto común de celular, sin filtros ni retoques. |
| 25 | `03-vidrio-025` | vidrio | — | A | Foto de celular de la luneta trasera estallada de un Fiat Cronos bordó, bajo la lluvia, tomada de costado, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 26 | `03-vidrio-026` | vidrio | — | A | Foto de celular de el parabrisas astillado de un Ford Ka negro, de noche con luz de farol, tomada de cerca, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 27 | `03-vidrio-027` | vidrio | — | A | Foto de celular de la ventanilla del conductor rota de un Volkswagen Gol Trend blanco, de día nublado, tomada desde un poco lejos, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 28 | `03-vidrio-028` | vidrio | — | A | Foto de celular de la óptica delantera partida de un Chevrolet Onix gris plata, al atardecer, tomada de frente, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 29 | `03-vidrio-029` | vidrio | — | B | Foto de celular de la ventanilla trasera rota de un Renault Kangoo rojo, de noche con flash, tomada en diagonal, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 30 | `03-vidrio-030` | vidrio | — | B | Foto de celular de la luneta trasera estallada de un Peugeot 208 azul, de día soleado, tomada de costado, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 31 | `03-vidrio-031` | vidrio | — | B | Foto de celular de el parabrisas astillado de un Toyota Hilux bordó, bajo la lluvia, tomada de cerca, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 32 | `03-vidrio-032` | vidrio | — | B | Foto de celular de la ventanilla del conductor rota de un Volkswagen Amarok negro, de noche con luz de farol, tomada desde un poco lejos, con pedazos de vidrio en el piso. Que parezca una foto común de celular, sin filtros ni retoques. |
| 33 | `04-calle-033` | calle | — | A | Foto tomada con un celular de un cruce de avenida en una calle de Buenos Aires, de día nublado, como la que sacaría un testigo justo después de un choque, sin patentes legibles. Que parezca una foto común de celular, sin filtros ni retoques. |
| 34 | `04-calle-034` | calle | — | A | Foto tomada con un celular de una rotonda en un estacionamiento de supermercado, al atardecer, como la que sacaría un testigo justo después de un choque, sin patentes legibles. Que parezca una foto común de celular, sin filtros ni retoques. |
| 35 | `04-calle-035` | calle | — | A | Foto tomada con un celular de una ruta con banquina en la puerta de una casa en Mendoza, de noche con flash, como la que sacaría un testigo justo después de un choque, sin patentes legibles. Que parezca una foto común de celular, sin filtros ni retoques. |
| 36 | `04-calle-036` | calle | — | B | Foto tomada con un celular de una calle con autos estacionados en un barrio de Córdoba, de día soleado, como la que sacaría un testigo justo después de un choque, sin patentes legibles. Que parezca una foto común de celular, sin filtros ni retoques. |
| 37 | `04-calle-037` | calle | — | B | Foto tomada con un celular de una esquina con semáforo en una ruta con banquina de tierra, bajo la lluvia, como la que sacaría un testigo justo después de un choque, sin patentes legibles. Que parezca una foto común de celular, sin filtros ni retoques. |
| 38 | `04-calle-038` | calle | — | B | Foto tomada con un celular de un cruce de avenida en una avenida de Rosario, de noche con luz de farol, como la que sacaría un testigo justo después de un choque, sin patentes legibles. Que parezca una foto común de celular, sin filtros ni retoques. |
| 39 | `05-lesion-039` | lesion | muy clara | A | Foto tomada con un celular de un moretón amarillento de varios días en el tobillo de una persona mayor de piel muy clara, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 40 | `05-lesion-040` | lesion | clara | A | Foto tomada con un celular de un moretón violeta en la rodilla de una mujer joven de piel clara, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 41 | `05-lesion-041` | lesion | trigueña | A | Foto tomada con un celular de una inflamación en la mano de un hombre joven de piel trigueña, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 42 | `05-lesion-042` | lesion | morena | A | Foto tomada con un celular de un vendaje con algo de sangre en el antebrazo de un hombre adulto de piel morena, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 43 | `05-lesion-043` | lesion | marrón oscura | A | Foto tomada con un celular de un corte con puntos en la pierna de una mujer adulta de piel marrón oscura, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 44 | `05-lesion-044` | lesion | negra | A | Foto tomada con un celular de un raspón en la espalda de una persona mayor de piel negra, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 45 | `05-lesion-045` | lesion | muy clara | A | Foto tomada con un celular de una quemadura leve en el hombro de una mujer joven de piel muy clara, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 46 | `05-lesion-046` | lesion | clara | A | Foto tomada con un celular de un yeso en el codo de un hombre joven de piel clara, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 47 | `05-lesion-047` | lesion | trigueña | A | Foto tomada con un celular de un moretón amarillento de varios días en el tobillo de un hombre adulto de piel trigueña, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 48 | `05-lesion-048` | lesion | morena | A | Foto tomada con un celular de un moretón violeta en la rodilla de una mujer adulta de piel morena, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 49 | `05-lesion-049` | lesion | marrón oscura | A | Foto tomada con un celular de una inflamación en la mano de una persona mayor de piel marrón oscura, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 50 | `05-lesion-050` | lesion | negra | A | Foto tomada con un celular de un vendaje con algo de sangre en el antebrazo de una mujer joven de piel negra, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 51 | `05-lesion-051` | lesion | muy clara | B | Foto tomada con un celular de un corte con puntos en la pierna de un hombre joven de piel muy clara, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 52 | `05-lesion-052` | lesion | clara | B | Foto tomada con un celular de un raspón en la espalda de un hombre adulto de piel clara, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 53 | `05-lesion-053` | lesion | trigueña | B | Foto tomada con un celular de una quemadura leve en el hombro de una mujer adulta de piel trigueña, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 54 | `05-lesion-054` | lesion | morena | B | Foto tomada con un celular de un yeso en el codo de una persona mayor de piel morena, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 55 | `05-lesion-055` | lesion | marrón oscura | B | Foto tomada con un celular de un moretón amarillento de varios días en el tobillo de una mujer joven de piel marrón oscura, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 56 | `05-lesion-056` | lesion | negra | B | Foto tomada con un celular de un moretón violeta en la rodilla de un hombre joven de piel negra, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 57 | `05-lesion-057` | lesion | muy clara | B | Foto tomada con un celular de una inflamación en la mano de un hombre adulto de piel muy clara, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 58 | `05-lesion-058` | lesion | clara | B | Foto tomada con un celular de un vendaje con algo de sangre en el antebrazo de una mujer adulta de piel clara, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 59 | `05-lesion-059` | lesion | trigueña | B | Foto tomada con un celular de un corte con puntos en la pierna de una persona mayor de piel trigueña, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 60 | `05-lesion-060` | lesion | morena | B | Foto tomada con un celular de un raspón en la espalda de una mujer joven de piel morena, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 61 | `05-lesion-061` | lesion | marrón oscura | B | Foto tomada con un celular de una quemadura leve en el hombro de un hombre joven de piel marrón oscura, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 62 | `05-lesion-062` | lesion | negra | B | Foto tomada con un celular de un yeso en el codo de un hombre adulto de piel negra, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 63 | `05-lesion-063` | lesion | muy clara | B | Foto tomada con un celular de un moretón amarillento de varios días en el tobillo de una mujer adulta de piel muy clara, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 64 | `05-lesion-064` | lesion | clara | B | Foto tomada con un celular de un moretón violeta en la rodilla de una persona mayor de piel clara, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 65 | `05-lesion-065` | lesion | trigueña | B | Foto tomada con un celular de una inflamación en la mano de una mujer joven de piel trigueña, con ropa común, en un consultorio, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 66 | `05-lesion-066` | lesion | morena | B | Foto tomada con un celular de un vendaje con algo de sangre en el antebrazo de un hombre joven de piel morena, con ropa de trabajo, en la guardia de un hospital, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 67 | `05-lesion-067` | lesion | marrón oscura | B | Foto tomada con un celular de un corte con puntos en la pierna de un hombre adulto de piel marrón oscura, con ropa común, en el vestuario de una fábrica, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 68 | `05-lesion-068` | lesion | negra | B | Foto tomada con un celular de un raspón en la espalda de una mujer adulta de piel negra, con ropa de trabajo, en una casa, sin mostrar la cara. Que parezca una foto casera de celular, sin filtros, para mostrarle a un médico o a la ART. |
| 69 | `06-lugar-trabajo-069` | lugar-trabajo | — | A | Foto realista tomada con un celular de una fábrica justo después de un resbalón en un piso mojado, de día nublado, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 70 | `06-lugar-trabajo-070` | lugar-trabajo | — | A | Foto realista tomada con un celular de un andamio de una obra justo después de la caída de una caja desde una estantería, al atardecer, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 71 | `06-lugar-trabajo-071` | lugar-trabajo | — | A | Foto realista tomada con un celular de una obra en construcción justo después de un corte con una amoladora, de noche con flash, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 72 | `06-lugar-trabajo-072` | lugar-trabajo | — | A | Foto realista tomada con un celular de un galpón de campo justo después de una quemadura con aceite, de día soleado, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 73 | `06-lugar-trabajo-073` | lugar-trabajo | — | B | Foto realista tomada con un celular de un depósito con estanterías justo después de un golpe con una máquina, bajo la lluvia, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 74 | `06-lugar-trabajo-074` | lugar-trabajo | — | B | Foto realista tomada con un celular de un taller mecánico justo después de la caída de una escalera, de noche con luz de farol, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 75 | `06-lugar-trabajo-075` | lugar-trabajo | — | B | Foto realista tomada con un celular de la cocina de un restaurante justo después de la caída de un andamio, de día nublado, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 76 | `06-lugar-trabajo-076` | lugar-trabajo | — | B | Foto realista tomada con un celular de una fábrica justo después de un resbalón en un piso mojado, al atardecer, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 77 | `06-lugar-trabajo-077` | lugar-trabajo | — | B | Foto realista tomada con un celular de un andamio de una obra justo después de la caída de una caja desde una estantería, de noche con flash, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 78 | `06-lugar-trabajo-078` | lugar-trabajo | — | B | Foto realista tomada con un celular de una obra en construcción justo después de un corte con una amoladora, de día soleado, sin personas o con personas de espaldas, como la que saca un compañero de trabajo. Que parezca una foto común de celular, sin filtros ni retoques. |
| 79 | `07-herramienta-079` | herramienta | — | A | Foto de celular de un casco de obra partido en el piso de un galpón de campo, bajo la lluvia, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 80 | `07-herramienta-080` | herramienta | — | A | Foto de celular de un andamio con una tabla quebrada en el piso de un depósito con estanterías, de noche con luz de farol, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 81 | `07-herramienta-081` | herramienta | — | A | Foto de celular de un guante de trabajo roto y manchado en el piso de un taller mecánico, de día nublado, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 82 | `07-herramienta-082` | herramienta | — | A | Foto de celular de una escalera de aluminio doblada en el piso de la cocina de un restaurante, al atardecer, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 83 | `07-herramienta-083` | herramienta | — | B | Foto de celular de un arnés de seguridad cortado en el piso de una fábrica, de noche con flash, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 84 | `07-herramienta-084` | herramienta | — | B | Foto de celular de una amoladora con el disco roto en el piso de un andamio de una obra, de día soleado, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 85 | `07-herramienta-085` | herramienta | — | B | Foto de celular de un taladro con el cable pelado en el piso de una obra en construcción, bajo la lluvia, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 86 | `07-herramienta-086` | herramienta | — | B | Foto de celular de unas botas de seguridad con la punta aplastada en el piso de un galpón de campo, de noche con luz de farol, tomada de cerca. Que parezca una foto común de celular, sin filtros ni retoques. |
| 87 | `08-documento-087` | documento | — | A | Foto de un presupuesto de un taller mecánico sobre una mesa, un poco doblado, tomada con el celular, con letra legible, en español de Argentina, sin nombres reales. Que parezca una foto común de celular, sin filtros ni retoques. |
| 88 | `08-documento-088` | documento | — | A | Foto de un certificado médico sobre una mesa, un poco doblado, tomada con el celular, con letra legible, en español de Argentina, sin nombres reales. Que parezca una foto común de celular, sin filtros ni retoques. |
| 89 | `08-documento-089` | documento | — | B | Foto de una constancia de una ART sobre una mesa, un poco doblado, tomada con el celular, con letra legible, en español de Argentina, sin nombres reales. Que parezca una foto común de celular, sin filtros ni retoques. |
| 90 | `08-documento-090` | documento | — | B | Foto de un parte de enfermería sobre una mesa, un poco doblado, tomada con el celular, con letra legible, en español de Argentina, sin nombres reales. Que parezca una foto común de celular, sin filtros ni retoques. |


## 6. Fotos reales editadas con IA (CA13)

Se parte de una **foto real tuya** (sección 7) y se le pide a la herramienta un cambio **localizado**. Guardar la foto real en `real/celular-propio/original/` y la editada en `sintetica/<herramienta>-edicion/original/`, con el número de edición.

1. Abrir Gemini, ChatGPT o Meta AI (web), **subir la foto real** y escribir el pedido de la tabla.
2. Descargar la editada con el botón de descarga.
3. Anotar en la planilla el nombre de la foto real de origen.

| Edición | Foto real de partida | Pedido | Archivo editado |
|---|---|---|---|
| E01 | Auto estacionado sano, de costado | «Agregale una abolladura grande en la puerta delantera, que se vea real y con la misma luz.» | `01-choque-201` |
| E02 | Auto sano, de atrás | «Hacé que el paragolpes trasero aparezca hundido y rayado por un choque.» | `01-choque-202` |
| E03 | Auto sano, de frente | «Rompé la óptica delantera izquierda, con pedazos en el piso.» | `03-vidrio-203` |
| E04 | Auto sano, de frente | «Hacé que el parabrisas aparezca astillado desde una esquina.» | `03-vidrio-204` |
| E05 | Auto sano, de costado | «Agregá rayones largos en la puerta trasera, como hechos con una llave.» | `02-rayon-205` |
| E06 | Auto con un golpe chico | «Hacé el golpe mucho más grande y profundo.» | `01-choque-206` |
| E07 | Calle o esquina | «Agregá vidrios rotos y restos de plástico de un choque en el asfalto.» | `04-calle-207` |
| E08 | Calle con autos | «Agregá una moto caída en el medio de la calle, sin personas.» | `04-calle-208` |
| E09 | Antebrazo sano (propio o de un conocido, sin cara) | «Agregá un moretón violeta grande, que se vea real.» | `05-lesion-209` |
| E10 | Rodilla sana | «Agregá un raspón reciente, como de una caída.» | `05-lesion-210` |
| E11 | Mano sana | «Agregá un corte cerrado con tres puntos.» | `05-lesion-211` |
| E12 | Brazo sano | «Poné el brazo enyesado, como recién salido de la guardia.» | `05-lesion-212` |
| E13 | Tobillo sano | «Hacé que el tobillo se vea hinchado y morado, como de un esguince.» | `05-lesion-213` |
| E14 | Escalera de aluminio sana | «Hacé que la escalera aparezca doblada y caída en el piso.» | `07-herramienta-214` |
| E15 | Casco o guante | «Hacé que el casco aparezca partido / el guante roto y manchado.» | `07-herramienta-215` |
| E16 | Herramienta eléctrica | «Hacé que el disco de la amoladora aparezca roto.» | `07-herramienta-216` |
| E17 | Piso de un taller o cocina | «Agregá una mancha grande de aceite derramado y un balde caído.» | `06-lugar-trabajo-217` |
| E18 | Estantería o depósito | «Hacé que haya cajas caídas y rotas en el piso.» | `06-lugar-trabajo-218` |
| E19 | Obra vista desde la vereda | «Agregá un andamio con una tabla quebrada.» | `06-lugar-trabajo-219` |
| E20 | Certificado o papel cualquiera | «Cambiá la fecha y el nombre del documento por otros.» | `08-documento-220` |

- Fotos de **conocidos**, solo con su consentimiento y **sin cara**, tatuajes ni rasgos que los identifiquen.
- Repartir las lesiones (E09 a E13) entre personas de **distintos tonos de piel** cuando se pueda, y anotar el tono.

## 7. Fotos reales

**Regla de oro:** las reales tienen que ser **de las mismas escenas** que las generadas.

### 7.1 Las que sacás vos (30 a 50, de a poco)

Con tu celular, **sin modo retrato, sin filtros, sin HDR forzado** (dejá la cámara en automático, como saca fotos cualquiera). Ninguna con caras, patentes legibles ni documentos con datos.

| # | Qué fotografiar | Escena | Cuántas |
|---|---|---|---|
| 1 | Autos estacionados **con golpes o rayones de verdad** (en la calle hay muchos), de cerca y de lejos, sin la patente | 01, 02 | 10 a 15 |
| 2 | Ópticas o vidrios rotos o astillados que veas | 03 | 3 a 5 |
| 3 | Esquinas, calles, rotondas y estacionamientos, de día y de noche | 04 | 5 a 8 |
| 4 | Obras vistas **desde la vereda**, andamios, depósitos, talleres (con permiso si entrás) | 06 | 5 a 8 |
| 5 | Herramientas, cascos, guantes, escaleras (sanos o gastados) | 07 | 5 |
| 6 | Autos, brazos, rodillas y escaleras **sanos** para las ediciones de la sección 6 | — | 10 |
| 7 | (Opcional) Moretones, raspones o yesos de conocidos, con consentimiento y sin cara | 05 | Los que haya |

Nombre: escena + número desde el 301 (`01-choque-301.jpg`). Pasarlas a Drive con la **aplicación de Drive** o por cable, nunca por Google Fotos ni por una aplicación de mensajería.

### 7.2 Las que salen de conjuntos públicos (las prepara el agente)

| Carpeta | De dónde | Escenas | Qué hacés vos |
|---|---|---|---|
| `real/cardd/` | CarDD: autos dañados reales | 01 a 03 | Aceptar las condiciones del conjunto en Hugging Face. El agente prepara una celda que copia una muestra de 150 a tu Drive; vos hacés las capturas |
| `real/scin/` | SCIN: fotos de piel sacadas por las propias personas, con el tono de piel etiquetado | 05 | Ídem (25 por tono de piel) |
| `real/obras/` | MOCS: obras reales | 06 | Aceptar las condiciones en Hugging Face (ConstructionSite); ídem |

Esto se hace después de correr el cuaderno de exploración, que confirma que estén disponibles y su licencia.

## 8. La planilla

Hoja de cálculo de Google `evidentia/planilla-conjunto-propio`, con estas columnas (una fila por imagen, no por versión):

| Archivo | Carpeta | N.° de prompt | Versión del prompt | Escena | Herramienta y modelo | Fecha | Tono de piel | Foto de origen (ediciones) | ¿Captura? | Observaciones |
|---|---|---|---|---|---|---|---|---|---|---|
| 01-choque-007 | gemini | 7 | v1 | 01 | Gemini 2.5 Flash Image | 2026-11-02 | — | — | sí | |
| 05-lesion-041 | chatgpt | 41 | v2 | 05 | ChatGPT (GPT-image) | 2026-11-03 | trigueña | — | no | Se negó con v1 |
| 01-choque-201 | gemini-edicion | E01 | — | 01 | Gemini | 2026-11-04 | — | 01-choque-301 | sí | |

- **Herramienta y modelo:** lo que diga la herramienta (por ejemplo, en Gemini aparece el nombre del modelo). Si no lo dice, solo la herramienta.
- **Tono de piel:** el del prompt en las generadas; en las reales, el que veas, con las mismas seis palabras.

## 9. Cómo buscar conjuntos de datos y pasármelos

### Dónde buscar

| Sitio | Qué hay | Buscar con estas palabras (en inglés) |
|---|---|---|
| **Hugging Face** (huggingface.co/datasets) | La mayoría de los conjuntos de detección | `ai generated image detection`, `synthetic image detection`, `deepfake image dataset`, `gpt-image`, `nano banana`, `midjourney dataset`, `flux images` |
| **Papers with Code / arXiv** | El artículo de cada conjunto (dice cómo se armó y su licencia) | `AI-generated image detection dataset 2026`, `in the wild synthetic images` |
| **GitHub** | Conjuntos académicos con su página | `<nombre del conjunto> dataset` |
| **Kaggle, Zenodo, Mendeley Data, Figshare** | Fotos reales de escenas específicas | `car damage dataset`, `vehicle accident photos`, `wound images smartphone`, `bruise dataset`, `construction site images`, `workplace accident`, `skin tone dataset` |
| **Roboflow Universe** | Muchos conjuntos chicos de escenas | Igual que arriba. **Cuidado:** muchos están armados con fotos bajadas de internet |

### Qué mirar antes de mandarlo (dos minutos)

1. **¿Qué tiene?** ¿Generadas, reales o las dos? ¿De qué generadores? ¿De qué escenas?
2. **¿Las reales son de verdad reales?** Que diga cómo se sacaron (cámara, celular, personas que donaron) y de qué fecha. Si dice *scraped from the web* o no dice nada, igual mandalo, pero avisame.
3. **¿Tiene licencia?** Buscá la palabra *license* en la página (en Hugging Face está arriba a la derecha). No hace falta entenderla: copiala.
4. **¿Pide aceptar condiciones?** En Hugging Face aparece un botón *Agree and access*. Si lo aceptás, avisame.

### Qué pegar en el chat

```
Conjunto: <enlace>
Qué vi: <generadas / reales / las dos>, <generadores o escenas que nombra>
Licencia: <lo que dice, copiado>
¿Pide aceptar condiciones?: <sí / no / ya acepté>
Por qué me pareció útil: <una línea>
```

Con eso el agente responde: **si sirve**, **qué aporta que no tengamos**, **su licencia**, **cómo se usaría** (entrenar, generadores no vistos, condiciones reales o solo fotos reales para el conjunto propio) y, si sirve, lo agrega a `red_neuronal/configuracion/candidatos_v1.yaml` para que el cuaderno de exploración lo verifique en Colab.

## 10. Cuándo avisar al agente

- Al terminar la **prioridad A de dos herramientas** con sus dos versiones: ya se puede correr la primera evaluación en condiciones reales.
- Si una herramienta se niega sistemáticamente con alguna escena o algún tono de piel.
- Si encontrás un conjunto de datos (sección 9).
- Si algo de esta guía no se entiende: se corrige la guía.

## 11. Aceptar las condiciones en Hugging Face y correr el cuaderno de exploración

Es lo primero que hay que hacer: con su resultado el agente completa la receta v1 y prepara las fotos reales de CarDD, SCIN y MOCS.

### 11.1 Aceptar las condiciones de cada conjunto

Varios conjuntos de Hugging Face piden aceptar condiciones antes de dejar bajarlos. Se aceptan **una sola vez**, con **la misma cuenta del `HF_TOKEN`** que está en los secretos de Colab.

1. Entrar a [huggingface.co](https://huggingface.co) con tu cuenta.
2. Abrir cada enlace de la tabla. Si arriba aparece un recuadro del estilo *«You need to agree to share your contact information to access this dataset»*, completar lo que pida (nombre, institución: **Universidad / proyecto final de carrera**, uso: **investigación académica, no comercial**) y tocar **Agree and access repository**.
3. Si después dice *«Your request is pending»*, la aprobación es manual: avisame cuál y seguimos con los demás.
4. Si no aparece ningún recuadro, no hay nada que aceptar.

| Conjunto | Enlace | ¿Pide aceptar? |
|---|---|---|
| Community Forensics *Small* | [OwensLab/CommunityForensics-Small](https://huggingface.co/datasets/OwensLab/CommunityForensics-Small) | Sí (ya lo aceptaste para la prueba de concepto) |
| OpenFake | [ComplexDataLab/OpenFake](https://huggingface.co/datasets/ComplexDataLab/OpenFake) | Probablemente |
| Treasure | [ThreeLiu/Treasure](https://huggingface.co/datasets/ThreeLiu/Treasure) | Verificar |
| MLLM-Generated-Image-Detection | [zr-zhang/MLLM-Generated-Image-Detection-Dataset](https://huggingface.co/datasets/zr-zhang/MLLM-Generated-Image-Detection-Dataset) | Verificar |
| ShareGPT-4o-Image | [FreedomIntelligence/ShareGPT-4o-Image](https://huggingface.co/datasets/FreedomIntelligence/ShareGPT-4o-Image) | Verificar |
| Semi-Truths | [semi-truths/Semi-Truths](https://huggingface.co/datasets/semi-truths/Semi-Truths) | Verificar |
| CarDD | [harpreetsahota/CarDD](https://huggingface.co/datasets/harpreetsahota/CarDD) | Verificar |
| ConstructionSite (MOCS) | [LouisChen15/ConstructionSite](https://huggingface.co/datasets/LouisChen15/ConstructionSite) | Sí |

**Si el `HF_TOKEN` es de grano fino** (*fine-grained*), en [Settings → Access Tokens](https://huggingface.co/settings/tokens) → el token → **Edit permissions**, tiene que tener tildado *«Read access to contents of all public gated repos you can access»*. Sin eso, aunque aceptes las condiciones, el cuaderno ve el conjunto como no disponible (error 401 o 403). Un token clásico de tipo **Read** ya lo incluye.

### 11.2 Abrir el cuaderno en Colab

Es un cuaderno **nuevo** en Colab: no se toca el de la prueba de concepto. Hay dos formas; la primera es la más simple.

**Forma A: bajarlo y subirlo (recomendada)**

1. En GitHub, entrar al repositorio, elegir la rama **`funcionalidad/010-red-neuronal`** (botón de ramas arriba a la izquierda) y abrir `red_neuronal/cuadernos/02_exploracion_datos_colab.ipynb`.
2. Tocar el botón **Download raw file** (ícono de la flecha hacia abajo, arriba a la derecha del archivo).
3. Abrir [colab.research.google.com](https://colab.research.google.com) → **Archivo → Subir cuaderno** → elegir el archivo bajado.

**Forma B: abrirlo directo desde GitHub**

1. En Colab: **Archivo → Abrir cuaderno → pestaña GitHub**.
2. Tildar **Incluir repositorios privados** y autorizar a Colab en GitHub la primera vez.
3. Elegir el repositorio, la rama `funcionalidad/010-red-neuronal` y el cuaderno `02_exploracion_datos_colab.ipynb`.

En los dos casos, **Archivo → Guardar una copia en Drive** para tenerlo a mano. Si el cuaderno cambia en el repositorio, hay que volver a bajarlo.

### 11.3 Correrlo

1. **Entorno de ejecución → Cambiar tipo de entorno de ejecución → CPU**. No usa GPU: así no gasta unidades de cómputo.
2. Los secretos `HF_TOKEN` y `GITHUB_TOKEN` son de tu cuenta y ya están cargados. Revisar en el ícono de la **llave** que los dos tengan **Acceso al cuaderno** activado *en este cuaderno* (se activa por cuaderno).
3. **Entorno de ejecución → Ejecutar todas** y aceptar el permiso de **Google Drive**.
4. Esperar: tarda unos **10 a 20 minutos**. En la sección 3 aparece `Explorando <conjunto>...` por cada uno. Si uno falla, no detiene a los demás: queda «excluido» con el motivo.
5. Los resultados quedan en Drive, en `MyDrive/evidentia/exploracion/` (`exploracion.md`, `exploracion.json` y `propuesta_receta_v1.yaml`).

### 11.4 Qué pasarme

1. La **tabla** de la sección 4 del cuaderno.
2. La salida de la sección 5 (columnas y generadores de cada conjunto).
3. La **propuesta** de la sección 7.
4. Si algún conjunto quedó «pendiente de aprobación» en Hugging Face.

Antes de pegar, revisar que no aparezca ningún token (`hf_…`, `github_pat_…`). No hay imágenes ni datos personales en esa salida.

| Si ves… | Qué pasa | Qué hacer |
|---|---|---|
| `GatedRepoError`, 401 o 403 en un conjunto | Faltan aceptar sus condiciones o el token no tiene permiso para conjuntos con condiciones | Sección 11.1 y volver a ejecutar todo |
| `RepositoryNotFoundError` o 404 | El conjunto cambió de nombre o se borró | Pasame el mensaje: lo reemplazo |
| «faltan las columnas …» | El conjunto usa otros nombres de columnas | Pasame la salida de la sección 5: corrijo los candidatos |
| «no tiene archivos Parquet» | El conjunto está en otro formato | Normal en algunos (CarDD, Semi-Truths): lo resuelvo yo |
| `SecretNotFoundError` | Falta activar el acceso del secreto en este cuaderno | Ícono de la llave → Acceso al cuaderno |

