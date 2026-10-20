# Video teaser de evidentIA

Teaser de 38 segundos que genera intriga sin mostrar el software. Se arma completo a partir de estos archivos, sin programas de edición:

| Archivo | Qué hace |
|---|---|
| `teaser.html` | Animación cuadro por cuadro (textos, foto, ojo, capas y logo). Se adapta sola a formato horizontal o vertical. |
| `sonido.py` | Sintetiza la banda sonora sincronizada con la animación (sin música de terceros). |
| `renderizar.mjs` | Abre la animación en Chromium, captura cada fotograma y lo codifica con ffmpeg. |
| `fuentes/montserrat.woff2` | Tipografía Montserrat (licencia SIL Open Font License). |

Los videos generados no se guardan en el repositorio por su tamaño.

## Cómo generarlo

Requisitos: Node.js con Playwright, Python 3 con NumPy y ffmpeg.

```bash
cd docs/marca/video
python3 sonido.py banda.wav
node renderizar.mjs 1920 1080 imagen-horizontal.mp4   # o 1080 1920 para vertical
ffmpeg -i imagen-horizontal.mp4 -i banda.wav -c:v libx264 -crf 25 -preset slow \
  -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart evidentia-teaser.mp4
```

`renderizar.mjs` busca Playwright en `/opt/node-tools/node_modules`; en otra máquina hay que cambiar esa ruta o instalarlo con `npm install playwright`.

## Línea de tiempo

| Tiempo | Escena |
|---|---|
| 0–7,6 s | "Llega una foto. Un choque. Un accidente laboral. Parece real." |
| 7,6–9,8 s | La foto se rompe en interferencias: "¿Lo es?" |
| 10–17,5 s | "Hoy una imagen se edita en segundos. O se crea de la nada. A simple vista, no se nota." |
| 18,3–22,8 s | Se cierra el marco verde y se abre el ojo: "Pero toda imagen deja rastros." |
| 22,8–27,6 s | Las cuatro capas: metadatos, credenciales, compresión, red neuronal. |
| 27,7–32 s | "Cuatro capas de análisis. Un informe claro." "Indicios, no veredictos." |
| 32,3–38 s | Logo, lema, "Próximamente" y la aclaración de consultar a un profesional (RN27). |

Los textos se cambian en el arreglo `TEXTOS` de `teaser.html`; si se mueven los tiempos, hay que mover también los de `sonido.py`.
