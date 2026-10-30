# 10. Entrenar en Colab paso a paso

## Preparación (una sola vez)

### 1. Token de Hugging Face (`HF_TOKEN`)

Sirve para descargar los conjuntos de datos y, más adelante, publicar el modelo.

1. Crear la cuenta en [huggingface.co](https://huggingface.co/join).
2. Aceptar las condiciones de los conjuntos que lo pidan, por ejemplo [CommunityForensics-Small](https://huggingface.co/datasets/OwensLab/CommunityForensics-Small).
3. [Settings → Access Tokens](https://huggingface.co/settings/tokens) → **Create new token** → tipo **Read**. Para publicar el modelo final (T33) hará falta uno de tipo **Write**.

### 2. Token de GitHub (`GITHUB_TOKEN`)

Sirve para que Colab clone el repositorio, que es privado.

1. [Crear un token de grano fino](https://github.com/settings/personal-access-tokens/new).
2. **Repository access:** *Only select repositories* → `PFG-sistema-deteccion-IA`.
3. **Permissions → Contents:** *Read-only*. Es el paso que más se olvida.
4. Vencimiento de 30 a 90 días. Cuando venza, se crea otro y se reemplaza el secreto.

### 3. Secretos en Colab

En el cuaderno, ícono de la **llave**: agregar `HF_TOKEN` y `GITHUB_TOKEN` con **Acceso al cuaderno** activado. Los secretos son de la cuenta, no del cuaderno: se cargan una vez. **Nunca** se pegan en una celda ni en el chat.

### 4. Los cuadernos

| Cuaderno | Para qué | GPU | Tiempo |
|---|---|---|---|
| `01_prueba_de_concepto_colab.ipynb` | La prueba de concepto (hecha) | T4 | ≈ 11 min |
| `02_exploracion_datos_colab.ipynb` | **T25:** revisar cada conjunto candidato (licencia, revisión, columnas, generadores, formatos) y proponer la receta v1 | **No: usar CPU** | 10 a 20 min |
| `03_entrenamiento_completo_colab.ipynb` | **T28 a T33:** entrenamiento completo con la receta v1, saltea lo ya hecho | T4 o L4 | 2 a 3 h |

Descargarlos de la carpeta `red_neuronal/cuadernos/` de la rama `funcionalidad/010-red-neuronal` y subirlos en **Archivo → Subir cuaderno**. Cuando un cuaderno cambie en el repositorio, hay que volver a bajarlo.

**Antes del 02:** con la misma cuenta del `HF_TOKEN`, aceptar las condiciones de los conjuntos que lo piden (OpenFake, Community Forensics, CarDD, ConstructionSite). Si el token es de grano fino, necesita el permiso de lectura de conjuntos con condiciones. Si no, aparecen como no disponibles. Los pasos completos, con los enlaces de cada conjunto y cómo abrir el cuaderno (bajarlo y subirlo, o abrirlo desde GitHub), están en la sección 11 de la [guía paso a paso](../guias/guia-paso-a-paso-conjunto-propio.md#11-aceptar-las-condiciones-en-hugging-face-y-correr-el-cuaderno-de-exploración).

**Antes del 03:** la receta `configuracion/v1.yaml` tiene que estar completada con lo que devolvió el 02. Para publicar en Hugging Face (T33), el `HF_TOKEN` tiene que ser de tipo **Write** y existir el repositorio privado (E03); en el cuaderno, `PUBLICAR_EN_HUGGING_FACE = True`.

## Correrlo

1. **Entorno de ejecución → Cambiar tipo de entorno de ejecución:**
   - **T4** para la prueba de concepto: alcanza y es la que menos unidades de cómputo gasta;
   - **L4** o **A100** para entrenamientos grandes, si los tiempos lo justifican;
   - **RAM amplia:** apagada salvo que falte memoria.
2. **Entorno de ejecución → Ejecutar todo.**
3. Aceptar el permiso de **Google Drive**: ahí se respalda todo, en `MyDrive/evidentia/…`.
4. Seguir la salida: cada etapa muestra su progreso y su tiempo (`--> obtener: 218.9 s`).

## Qué hace cada sección del cuaderno

| Sección | Qué hace |
|---|---|
| 1. Parámetros y Drive | Rama o commit a usar, versión del modelo y montaje de Drive |
| 2. Credenciales | Lee los secretos; se detiene con un mensaje claro si falta alguno |
| 3. Código | Clona el repositorio con el token (sin que aparezca nunca), instala el paquete y muestra la GPU |
| 4. Explorar columnas | Muestra el esquema del conjunto sin bajar imágenes |
| 5. Configuración | Arma la configuración efectiva y **recupera de Drive** lo hecho en una corrida anterior |
| 6. Etapas | Ejecuta las siete etapas, mide tiempos y respalda en Drive después de cada una |
| 7. Resultados | Resumen para la bitácora, curva ROC, matriz de confusión y ficha |
| 8. Qué hacer | Instrucciones para pasar los resultados |

## Si Colab corta la sesión

Colab desconecta por **inactividad** (nadie toca la página) y por **duración máxima** de la sesión. Con Pro el margen es mayor, pero existe.

**Para evitarlo:**
- que la computadora no se suspenda (enchufada, suspensión en «Nunca»);
- la pestaña abierta;
- tocar la página cada 30 a 40 minutos.

**No** usar scripts de clics automáticos: van contra las condiciones de Colab y pueden suspender la cuenta.

**Si igual pasa:** **Reconectar → Ejecutar todo**. El cuaderno recupera de Drive lo terminado. El entrenamiento retoma desde la última época guardada (`ultimo.pt`). En la prueba de concepto las imágenes no se guardaban y se volvían a bajar; el cuaderno 03 guarda los **datos preparados** en `MyDrive/evidentia/datos/<receta>/preparado.tar` y, con `python -m clasificador estado`, **saltea cada etapa ya terminada** (capítulo 8).

**Si cambiás la receta:** cambiale el `nombre` en el YAML (por ejemplo, `v1b`). Cada receta tiene su carpeta en Drive, y el cuaderno se detiene si en la carpeta hay resultados de otra configuración.

## Dejarla entrenando sola

Pedido de la autora (2026-10-30): poder dejar el entrenamiento corriendo sin estar al lado. Estas son las opciones:

| Opción | ¿Corre sin el navegador abierto? | Duración máxima | Costo | Estado |
|---|---|---|---|---|
| **Kaggle: «Save & Run All»** | **Sí**: corre en segundo plano en los servidores de Kaggle; se puede cerrar todo | 12 h por corrida, 30 h de GPU por semana | Gratis (requiere verificar el teléfono) | El cuaderno `00_prueba_de_concepto.ipynb` ya existe; falta actualizarlo con las mejoras del de Colab |
| Colab Pro+ | Sí (ejecución en segundo plano) | 24 h | Unos US$ 50 por mes | No recomendado: hay alternativa gratis |
| **Colab Pro (actual)** | No: necesita la pestaña abierta y actividad | Varias horas | Incluido con Gemini | En uso; retoma lo hecho si se corta |

**Decisión de la autora (2026-10-30): se entrena en Colab Pro**, a mano. Una corrida completa lleva unas 2 a 3 horas con unos 15 minutos de atención. Kaggle automático queda como opción futura si el reentrenamiento se vuelve frecuente.

**Recomendación original:**
- **Colab Pro** para corridas cortas o cuando se quiere ver el avance (prueba de concepto, exploración de datos).
- **Kaggle en segundo plano** para el entrenamiento completo (2 a 3 horas estimadas), que así corre solo.

En los dos casos se usa el mismo paquete y la misma configuración. Lo que cambia es solo el cuaderno que orquesta.

> **Límite:** el agente de IA no puede iniciar el entrenamiento por su cuenta. Necesita GPU y las cuentas de la autora (Colab, Kaggle, Hugging Face). Lo que sí hace: preparar los cuadernos para que corran solos y retomen, revisar los resultados y documentarlos.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `SecretNotFoundError` o «Falta HF_TOKEN o GITHUB_TOKEN» | Falta un secreto o no tiene acceso al cuaderno | Cargarlo en la llave con **Acceso al cuaderno** activado |
| `git clone falló: could not read Username` | GitHub rechazó el token: vencido, mal copiado o sin acceso al repositorio | Crear uno nuevo con el repositorio y *Contents: Read-only* |
| `name 'CONFIGURACION' is not defined` | Falló una celda anterior (la 3 o la 5) | Corregir la primera celda roja y **Ejecutar todo** de nuevo |
| «Faltan los resultados de: entrenamiento…» en la sección 7 | Las etapas no corrieron | Mirar el error de la sección 6 o de la primera celda roja |
| `GatedRepoError` o error 401/403 de Hugging Face | Faltan aceptar las condiciones del conjunto | Aceptarlas en la página del conjunto con la misma cuenta del token |
| «Entorno de ejecución desconectado» | Inactividad | Ver «Si Colab corta la sesión» |
| No hay GPU disponible | Demanda alta en Colab | Probar más tarde u otra GPU |
| Una etapa falla | El motivo está en las líneas justo arriba del `RuntimeError` | Copiar esas líneas al chat |

## Qué pasar al terminar

1. La salida de la **sección 7**: el resumen entre llaves y la ficha.
2. Capturas de la **curva ROC** y la **matriz de confusión**.
3. Qué GPU se usó y si se cortó alguna vez.

Antes de pegar, revisar que no aparezca ningún token (`hf_…`, `github_pat_…`).
