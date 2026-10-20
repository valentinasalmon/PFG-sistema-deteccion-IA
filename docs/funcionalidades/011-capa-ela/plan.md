# Plan técnico: 011 — Capa 3 (análisis de niveles de error, ELA)

Referencias: [especificacion.md](especificacion.md) · [ADR-0006](../../arquitectura/decisiones/0006-capas-de-analisis-strategy.md) (capas intercambiables)

## Resumen de la solución

- Nueva capa `CapaELA` en `backend/app/analisis/ela.py`, registrada después de la de credenciales de contenido. No cambia el motor ni las otras capas (ADR-0006).
- `ResultadoCapa` (de `analisis/base.py`) suma un campo opcional `imagen`, con los bytes PNG que acompañan al resultado.
- El servicio de análisis guarda esa imagen en el almacenamiento, en `analisis/<uuid>.png`, y su clave queda en la columna nueva `resultados_capa.clave_imagen` (migración `b3e1c0a7d911`).
- **Pantalla**: el detalle del análisis entrega un enlace firmado de 5 minutos por cada mapa (RNF03 CA2). `SeccionAnalisis.jsx` lo muestra con su aclaración.
- **Informe**: el PDF incrusta el mapa, igual que las miniaturas, así no depende de enlaces.
- **Borrado**: `ArchivosDeCasos` también borra los mapas al eliminar casos, organizaciones o cuentas (RN21).

## Método

1. Se recomprime la imagen en JPEG con **calidad 90**.
2. Se calcula la diferencia por píxel, quedándose con el máximo de los tres canales.
3. Se divide la imagen en **bloques de 16 × 16 píxeles**. Para cada bloque se calculan:
   - el error medio;
   - la textura, como el desvío de la luminancia.
4. **Corrección por textura.** Los bordes y los detalles cambian más al recomprimir. Por eso los bloques se agrupan en **10 clases por cuantiles de textura** y a cada uno se le resta la mediana de su clase.
5. El residuo se expresa en **desvíos robustos**: (residuo − mediana) / (1,4826 · MAD + 0,25). El 0,25 evita dividir por casi cero en imágenes muy uniformes.
6. Un bloque queda **marcado** si supera **4 desvíos**.
7. Los bloques marcados a **2 bloques o menos** de distancia forman una misma región. Así los bordes de una misma zona pegada, que ELA marca por separado, se informan juntos.
8. Una región necesita **al menos 6 bloques marcados**; si tiene menos, se considera ruido.
9. **Severidad de cada región:**
   - **moderada** si su desvío medio es de **10 o más**;
   - **débil** en los demás casos;
   - en PNG, siempre **débil**.
10. Se informan **hasta 3 regiones**, ordenadas por desvío × √bloques.
11. **Nivel**: el método común de las capas 1 y 2. Una región moderada da 45 %, y cada región moderada adicional suma 10.
12. **Imágenes chicas**: con menos de 8 bloques por lado (128 píxeles) no se analiza. El nivel es 0 y se informa el motivo.
13. **Calidad JPEG estimada**: se compara la tabla de cuantización de luminancia con la estándar del anexo K de JPEG.
14. **Mapa**: la diferencia se amplía al percentil 99,5. Las regiones informadas se recuadran en rojo, el mapa se reduce a 900 píxeles como máximo y se guarda en PNG con una paleta de 64 colores, para que pese poco dentro del PDF.

## Validación

**Imágenes sintéticas** (una "foto" de 1600 × 1200 con gradientes y ruido):

| Imagen | Resultado |
|---|---|
| Original, JPEG al 80 % | 0 %, sin regiones |
| Con una zona de 320 × 260 pegada de otra imagen y guardada al 90 % | 45 %: **una** región moderada, ubicada al 56 % del borde izquierdo y al 41 % del superior, que es donde se pegó |

**Imágenes de la prueba de canales del TIF:**

| Imagen | Resultado |
|---|---|
| Gemini: original, documento, correo, WhatsApp como foto y captura | 0 % |
| ChatGPT: original, documento y correo (PNG) | 20 %, indicios débiles |
| ChatGPT por WhatsApp como foto | 20 %, indicios débiles |

**Conclusión**: ELA distingue un empalme recomprimido, pero también marca como débiles zonas de imágenes generadas o recomprimidas. Por eso no supera el nivel moderado y se presenta siempre como señal complementaria. Los umbrales quedan para revisar con los tutores.

**Hallazgo durante la implementación.** Al principio el empalme aparecía como tres regiones, una por cada borde de la zona pegada. Se agregó la unión de bloques cercanos (paso 7) y ahora se informa como una sola región.

## Capas afectadas

| Capa | Cambio |
|---|---|
| `analisis` | `ela.py` (nuevo); `base.py` (campo `imagen`); `registro.py` |
| `modelos` y migración | `ResultadoCapa.clave_imagen` |
| `repositorios` | `RepositorioAnalisis.claves_de_imagenes_de_casos` |
| `servicios` | `ServicioAnalisis` (guarda el mapa y arma los enlaces); `ArchivosDeCasos` (borra los mapas); `ServicioInformes` (lee los mapas) |
| `esquemas` y `rutas` | El resultado incluye `imagen`, un enlace firmado o `null` |
| `informes` | Título, "¿Qué significa?" y mapa incrustado con su aclaración |
| Frontend | `SeccionAnalisis.jsx` y estilos del mapa |

## Bibliotecas nuevas

- `numpy==2.4.6`: cálculo por bloques. También la usará la capa 4.

## Estrategia de pruebas

- **Unitarias** (`test_capa_ela.py`):
  - imagen sin editar y empalme sintético, con su ubicación;
  - mapa con su recuadro rojo;
  - PNG, imagen chica e imagen ilegible;
  - ausencia de términos de veredicto y versión;
  - calidad JPEG estimada (50, 75, 90 y 95);
  - búsqueda de regiones, incluida la unión de bordes, y descripción de la ubicación.
- **Integración**:
  - el detalle entrega el enlace del mapa y el archivo se sirve como PNG;
  - el mapa se borra al eliminar el caso;
  - si no se puede guardar el mapa, el resultado sigue sin él.
- **Informe**: el mapa va incrustado con su aclaración.
- **Frontend**: el mapa con su aclaración y la tabla "Datos del análisis".
- **Navegador real**: tres imágenes; el PDF de 11 páginas muestra el mapa del empalme con un único recuadro.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Falsos positivos en bordes, textos o imágenes recomprimidas | Corrección por textura, regiones mínimas, nunca más que "moderado", y aclaración en la pantalla y en el PDF |
| Imágenes de 20 MB tardan más | Cálculo vectorizado con NumPy; el mapa se reduce a 900 píxeles |
| Mapas que pesan dentro del PDF | PNG con paleta de 64 colores (de 10 a 400 KB) |
