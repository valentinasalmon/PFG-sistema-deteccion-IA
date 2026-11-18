# 2026-11-18 · Cambio a GitHub Flow (ADR-0023)

## Contexto

El 2026-11-16 la autora pidió dejar de abrir una rama y un Pull Request por cada arreglo chico, agrupar el trabajo en ramas que representen algo para la defensa y aplicar el mismo criterio a los commits. Pidió una propuesta de ingeniería «sin importar nada más que un código limpio, mantenible y que refleje la ingeniería», y la aprobó como **decisión de mejora del proceso**.

## Hecho

- **ADR-0023**: GitHub Flow con despliegue continuo. `main` única rama permanente; ramas cortas por objetivo con el área adelante; un Pull Request directo a `main`; protección de `main` (nada se integra sin todas las verificaciones en verde); fusión con *squash*; versiones con GitHub Releases.
- **Integración continua**: corre en los Pull Requests y en `main`; se quitó `desarrollo`. Dependabot (`.github/dependabot.yml`) y notas de versión (`.github/release.yml`).
- **Guía para la autora** (`docs/guias/configurar-github.md`): transición, *squash*, protección de `main`, Dependabot, archivo de ramas y versiones.
- **`herramientas/archivar_ramas.sh`**: archiva como etiqueta `archivo/<área>/<nombre>` cada rama del modelo anterior ya integrada en `main` y la borra; muestra primero qué haría. La corre la autora: desde el entorno del agente no se pueden subir etiquetas ni borrar ramas en bloque.
- `CLAUDE.md`, `/especificar`, flujo de trabajo, hoja de ruta, despliegue, tablero, mapa de ramas, versiones y README al día.
- Ya del 2026-11-16: gancho `revisar_commit.py` (formato, 72 caracteres, `Co-Authored-By`). Commitlint en la integración continua queda en 100: con 72 rechazaba commits ya subidos (uno de la 044 tiene 79) y habría bloqueado el Pull Request de transición.

## Unificación con la 045

Otra sesión del agente («Harness engineering») había preparado en paralelo la funcionalidad 045 (rama `claude/charming-turing-j7esco`, sin integrar): un verificador que compara lo que declara la documentación del arnés con lo real, un control de numeración de funcionalidades, el comando `/revisar-arnes`, una política de ramas para `desarrollo` y los scripts `compactar_rama.sh` y `limpiar_ramas.sh`. Integradas por separado, las dos propuestas se pisaban. Se incorporó la 045 a esta rama y se adaptó a GitHub Flow:

- se quedan el verificador, el control de numeración, `/revisar-arnes` y el índice de la bitácora, ahora contra `main` (el verificador encontró enseguida que esta bitácora faltaba en el índice);
- se quitan el paso «Forma del Pull Request» de la integración continua y `compactar_rama.sh`, que solo tenían sentido hacia `desarrollo` (con *squash* cada Pull Request ya entra como un commit);
- `limpiar_ramas.sh` se reemplaza por `herramientas/archivar_ramas.sh`, que guarda cada rama como etiqueta antes de borrarla, como pidió la autora;
- su propuesta de configuración de GitHub queda resuelta por el ADR-0023.

## Decisiones

- **Se descartaron las ramas permanentes por área**: una rama que vive meses se aleja de la principal y arrastra conflictos.
- **Se retira `desarrollo`**: el segundo Pull Request repetía las mismas verificaciones sin sumar control; la protección automática de `main` lo reemplaza con más fuerza.
- **Las ramas viejas no se borran sin dejar rastro**: quedan como etiquetas y el mapa las agrupa por área, como pidió la autora.
- **Lo ya subido no se reescribe**: el *squash* ordena la historia de ahora en adelante.

## Pendiente

- Autora: el Pull Request de transición (`infraestructura/flujo-github` → `main`, que ya trae todo `desarrollo`), la configuración de GitHub y el archivo de ramas (guía `configurar-github.md`).
- Agente: `interfaz/calidad-visual` (sensor de composición, galería, comparación visual y auditoría completa) desde `main` cuando termine la transición.

## Más tarde: 047, análisis confiable para fotos de celular (rama `plataforma/analisis-confiable`)

- La autora informó que con fotos subidas desde el celular «no se toman» los metadatos y que el ELA «transforma todo». Pidió que funcione bien para todos, sobre todo con iPhone.
- **Metadatos**: la extracción funciona (ExifTool lee JPEG y HEIC). Las fuentes sobre qué entrega el iPhone al subir desde el navegador se contradicen (un reporte de WebKit dice que desde iOS 13 se quita el EXIF; otras pruebas dicen que no). **Decisión: medir antes de cambiar.** Se hizo la página pública «Probar mi celular», que muestra qué llega por cada camino (galería, cámara, Archivos) sin guardar la foto.
- **ELA**: experimento con fotos de una biblioteca científica guardadas al 97 % (como un celular), sin y con un parche pegado. Cambiar la calidad de recompresión según la de la foto no mejoró de forma consistente, así que no se cambió. Lo que «transformaba todo» era el **mapa**: se estiraba para que el punto más brillante quedara blanco, y en una foto sin cambios el ruido se amplificaba unas 40 veces. Se le puso un piso de escala: la proporción de píxeles encendidos en una foto limpia bajó de alrededor del 7 % a menos del 1 %, y una zona con error alto se sigue destacando. Los umbrales de detección no se tocaron.
- **Decisiones de la autora** (2026-11-18): el filtro de fotos «hace lo que consideres» → avisa y no bloquea (ADR-0017); reCAPTCHA de Google; no hay entrega el 19/11, se sigue mejorando hasta enero; «realtime» a criterio del agente → se mantienen las consultas periódicas (2 a 4 segundos), que ya actualizan solas el análisis, el celular y el pago; se revisará que ninguna pantalla obligue a recargar.
