# ADR-0022: Mejora continua de la red por versiones, con evaluación fija y parte de ajuste

- **Estado**: Aceptada (decisión de la autora, 2026-11-11)
- **Fecha**: 2026-11-11
- **Requisitos relacionados**: RF42, RNF08, RNF24, RN29; CA12, CA13 y CA18 de la funcionalidad 010. Complementa ADR-0014 y ADR-0015.

## Contexto

La versión `1.0.0` del clasificador (AUC 0,961 con generadores conocidos, 0,938 con la familia de Google no vista) detectó solo el 10 % de las imágenes de choques generadas por la autora con ChatGPT, Copilot y Gemini, y en producción dio cerca de 0 % en una de ellas. Las herramientas comerciales actuales no están en los conjuntos públicos con los que se entrenó.

Hasta ahora el conjunto propio se usaba **solo para evaluar**. Así la medición era limpia, pero el modelo nunca podía aprender de esas herramientas. La autora decidió que la red mejore de forma continua con datos nuevos, por versiones, sin perder una medición honesta.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| A. El conjunto propio solo evalúa (lo anterior) | Medición limpia | El modelo nunca aprende de las herramientas que importan |
| B. Entrenar con todo el conjunto propio | Más datos de las herramientas comerciales | Ya no queda con qué medir la mejora: cualquier subida sería trampa |
| C. Separarlo en evaluación fija y ajuste, por grupos y con una regla reproducible | Aprende de las herramientas y mide sin trampa | Cada lado tiene la mitad de las imágenes |

## Decisión

Se adopta **C**, con estas reglas de la autora:

1. **Dos lados que nunca se mezclan.** *Evaluación fija*: estratificada por herramienta, escena y variante (original o captura), con fotos reales de las mismas escenas; nunca se entrena con ella. *Ajuste*: puede sumarse al entrenamiento. Cada imagen se asigna a un lado al cargarla y nunca cambia.
2. **Cada reentrenamiento es una versión MINOR** (`1.1.0`, `1.2.0`…), registrada en MLflow y en el capítulo 11, con la receta y el manifiesto versionados.
3. **Compuerta de publicación.** AUC ≥ 0,90 en la prueba de generadores conocidos, **mejora** frente a la versión anterior en la evaluación fija del conjunto propio, y **sin empeorar** en los generadores no vistos. Si no la pasa, se registra y se descarta.
4. **Orden.** Primero, la `1.0.0` tal como está (publicada el 2026-11-10) y la repetición del entrenamiento (T31). Después, la `1.1.0` con la familia de Google más la parte de ajuste, comparada contra la `1.0.0` en la evaluación fija.
5. **Datos prohibidos.** Nunca imágenes de usuarios del sistema (RNF08) ni conjuntos sin licencia verificada. Las licencias solo para investigación quedan en la ficha.
6. **Corte para el informe: 16/11.** La versión publicada a esa fecha y sus cifras van al informe: prueba, no vistos y evaluación fija por herramienta, escena y variante. Las posteriores se documentan para la defensa como evolución del modelo.

### Precisiones técnicas del agente

- **La unidad que se asigna es el prompt, no el archivo.** Las tres herramientas y las dos variantes de un mismo prompt van juntas. Si se asignara archivo por archivo (por ejemplo, con la huella de cada imagen), la versión de ChatGPT de una escena podría quedar en ajuste y la de Gemini en evaluación: el modelo vería esa escena al entrenar y la evaluación saldría inflada.
- **Regla reproducible** (`clasificador/datos/particion_propia.py`):
  - los 89 prompts de la lista maestra tienen su lado en una tabla fija versionada (`red_neuronal/configuracion/particion_conjunto_propio.csv`), mitad y mitad dentro de cada escena y de cada tono de piel (45 de evaluación y 44 de ajuste);
  - las ediciones van del lado de su foto de origen;
  - las fotos reales y los prompts nuevos usan una huella SHA-256 de `escena-número` con semilla fija;
  - los archivos sin ese formato (por ejemplo, de CarDD) usan la huella de su contenido.

  Ninguna regla depende de las demás imágenes, así que sumar fotos no mueve a nadie de lado.
- **Cómo se mide la mejora en la evaluación fija.** Con fotos reales en la evaluación fija: AUC más alto y tasa de falsos positivos en esas reales no mayor. Mientras no haya reales: detección (sensibilidad con umbral 0,5) más alta, sin que suba la tasa de falsos positivos en la prueba. En los dos casos, por herramienta, escena y variante, y la `1.0.0` se vuelve a evaluar sobre la misma evaluación fija para comparar lo mismo.
- **Generadores no vistos en la `1.1.0`.** Si la `1.1.0` entrena con la familia de Google, ya no sirve como «no vista» para comparar con la `1.0.0`. Propuesta provisoria (CP-44): entrenar con Imagen 4 e Imagen 3 y seguir reservando Nano Banana 2. Las dos versiones se comparan sobre ese mismo generador, declarando que las imágenes de Gemini de la parte de ajuste pueden venir de la misma familia.
- **Peso de la parte de ajuste.** Unas decenas de imágenes casi no mueven un modelo entrenado con 35 000. La receta de la `1.1.0` define cuántas veces se repite la parte de ajuste en cada época, y se documenta en el capítulo 5.

## Consecuencias

- **Se gana** un modelo que puede aprender de las herramientas que usaría quien falsifica una prueba, con una mejora medida contra un conjunto que el modelo nunca vio.
- **Se pierde** la mitad del conjunto propio para evaluar. La evaluación fija tiene menos imágenes, y las cifras por subgrupo tienen más incertidumbre.
- **Queda condicionado:**
  - la evaluación fija necesita fotos reales de las mismas escenas para medir falsos positivos;
  - los términos de uso de las herramientas generativas para entrenar un detector se registran en la ficha (CP-45);
  - la decisión anterior («el conjunto propio nunca se usa para entrenar») queda reemplazada en el capítulo 4, el protocolo, la guía y el glosario.
