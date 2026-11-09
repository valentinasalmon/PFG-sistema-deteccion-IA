# Plan técnico: 012 — Capa 4 (red neuronal con ONNX)

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

La capa 4 es una capa de análisis más (`app/analisis/red_neuronal.py`) que se suma a `registro.py` sin tocar las otras tres, como prevé ADR-0006. No reimplementa nada del modelo: usa el subpaquete `clasificador.inferencia` de la funcionalidad 010 (`PredictorOnnx`), que solo depende de numpy, Pillow y onnxruntime. Así el backend aplica exactamente el mismo preprocesamiento que la evaluación (cinco recortes de 224, normalización leída del propio ONNX), como exige ADR-0015, y la probabilidad es idéntica a la de la ficha del modelo.

El modelo se obtiene con el registro de modelos de la 010 (`RegistroHuggingFace` o `RegistroLocal`), que baja una **versión fija** y verifica su huella SHA-256 contra `huellas.json` antes de devolverlo (ADR-0014). La ubicación y la versión son configuración del servidor. Sin configuración, o si la descarga o la huella fallan, la capa lanza `CapaNoDisponible` con el motivo y el análisis sigue con las otras capas (RN26). El predictor se guarda en una caché del proceso, así cada trabajador lo carga una sola vez (RF42 CA3).

El nivel de indicio sale de la probabilidad calibrada: 0 por debajo de 50 %; de ahí en adelante, la probabilidad en porcentaje con un máximo de 90 %. La conclusión sale de textos fijos de la capa, versionados con ella, que siempre incluyen las limitaciones del modelo. El informe PDF y la pantalla del caso ya muestran las capas de forma genérica: solo hay que sumar sus títulos y su texto «¿Qué significa?».

## Capas afectadas

| Capa | Archivos nuevos o modificados | Responsabilidad |
|---|---|---|
| Análisis | `app/analisis/red_neuronal.py` (nuevo), `app/analisis/registro.py` | La capa 4 (`CapaRedNeuronal`): nivel, anomalía, conclusión, tabla de criterios y versiones. Se registra al final de la lista |
| Integraciones | `app/integraciones/modelo_red_neuronal.py` (nuevo) | Obtiene la ruta del modelo verificado desde el registro configurado (Strategy: Hugging Face, carpeta local o no configurado) y guarda el predictor en la caché del proceso |
| Configuración | `app/configuracion/entornos.py` | `MODELO_RED_NEURONAL_REGISTRO`, `MODELO_RED_NEURONAL_VERSION`, `CARPETA_MODELOS_ONNX`; el token `HF_TOKEN` se lee del entorno, nunca del repositorio |
| Informes | `app/informes/informe_analisis.py` | Títulos de la capa 4; el resto (tipo probabilístico, «qué mira», tabla, bandas) ya es genérico |
| Servicios, repositorios, modelos, rutas | — | Sin cambios: el servicio de análisis recorre las capas registradas y guarda cada resultado como hasta ahora |
| Frontend | `frontend/src/componentes/SeccionAnalisis.jsx` | Agregar `red_neuronal` a la lista de capas, su título y su texto «¿Qué significa?» |
| Despliegue | `backend/requirements.txt`, `.github/workflows/integracion-continua.yml`, `infraestructura/scripts/desplegar.sh`, `infraestructura/terraform/principal/parametros.tf` (solo comentario) | Instalar `clasificador` sin dependencias de entrenamiento, sumar `red_neuronal` al artefacto y documentar el parámetro `HF_TOKEN` que la autora carga a mano |

## Patrones aplicados

- **Strategy** (constitución, sección 2): la capa es una implementación más de `CapaAnalisis`; el origen del modelo es un proveedor intercambiable (registro de Hugging Face, carpeta local o «no configurado»), y en las pruebas se usa uno local con un modelo diminuto.
- **Adaptador** en `app/integraciones/`: la capa no conoce Hugging Face; solo recibe un predictor.
- **Caché por proceso**: un diccionario a nivel de módulo, con la ruta y la huella del modelo como clave. Un mismo trabajador reutiliza el predictor en todas las imágenes y análisis (RF42 CA3).

## Contratos

```python
# app/integraciones/modelo_red_neuronal.py
class ModeloNoDisponible(Exception): ...           # motivo legible para el usuario

def obtener_predictor(configuracion) -> PredictorOnnx
    """Devuelve el predictor del modelo configurado, cargado una vez por proceso.
    Raises: ModeloNoDisponible (sin configuración, descarga fallida, huella distinta,
    archivo inválido)."""

def huella_modelo(predictor) -> str                 # SHA-256 del archivo ONNX (RN29)

# app/analisis/red_neuronal.py
class CapaRedNeuronal(CapaAnalisis):
    nombre = "red_neuronal"
    titulo = "Red neuronal"
    def __init__(self, configuracion): ...
    def version(self) -> str                         # versión de la capa, del modelo y de ONNX Runtime
    def analizar(self, contenido: bytes, contexto: ContextoImagen) -> ResultadoCapa
        """Raises: CapaNoDisponible (modelo no disponible o imagen ilegible)."""

def calcular_nivel_red(probabilidad: float) -> int  # 0 si < 0,5; si no, round(100·p) con máximo 90
```

`ResultadoCapa.detalle` lleva:

- `tabla`: probabilidad obtenida, umbral de consideración (50 %), escala de lectura (moderados desde 45 %, fuertes desde 70 %), referencia de desempeño del modelo (AUC con generadores conocidos y no vistos, de la ficha publicada) y versión del modelo;
- `probabilidad` (número de 0 a 1);
- `modelo`: versión, huella del ONNX, huella del manifiesto de entrenamiento y commit (RN29).

No hay endpoints nuevos: el resultado viaja por la API del análisis existente.

## Cambios en datos

Ninguno. Los resultados de las capas ya se guardan con su nombre, nivel, anomalías, conclusión, detalle y versión.

## Bibliotecas nuevas

| Biblioteca | Versión | Para qué se usa |
|---|---|---|
| `onnxruntime` | La misma de la integración continua de la 010, fijada en `requirements.txt` | Ejecutar el modelo en CPU (ADR-0015) |
| `huggingface_hub` | Fijada en `requirements.txt` | Bajar la versión fija del modelo del registro privado (ADR-0014) |
| `clasificador` (paquete del monorepositorio) | El commit desplegado | `PredictorOnnx` y el registro de modelos. Se instala con `--no-deps`, para no arrastrar PyTorch |
| `onnx` (solo desarrollo) | Fijada en `requirements-dev.txt` | Armar, en las pruebas, un modelo diminuto con los mismos metadatos que el real, sin PyTorch |

## Estrategia de pruebas

- **Unitarias de la capa** (`backend/pruebas/analisis/test_red_neuronal.py`), con un modelo ONNX diminuto armado en la prueba con `onnx.helper` (sale una probabilidad fija o que depende del brillo de la imagen):
  - nivel 0 por debajo de 50 %, la probabilidad hasta 90 y el tope en 90 (CA4);
  - la conclusión no tiene términos de veredicto e incluye las tres aclaraciones (CA5);
  - la tabla y el detalle traen la versión, la huella del modelo y la del manifiesto (CA6);
  - la probabilidad es igual a la de `PredictorOnnx.predecir` con la misma imagen (CA2);
  - una imagen ilegible da `CapaNoDisponible`.
- **Integración** (`backend/pruebas/integraciones/test_modelo_red_neuronal.py`):
  - registro local con el paquete del modelo y su `huellas.json`: devuelve el predictor y lo reutiliza, sin volver a cargarlo (CA3);
  - huella alterada, versión inexistente o sin configuración dan `ModeloNoDisponible` con el motivo (CA7).
- **Servicio de análisis:** con la capa 4 sin configurar, el análisis termina, la capa 4 queda «No disponible» y las otras tres tienen resultado (CA7, RN26).
- **Informe y frontend:** el PDF incluye la capa 4 con su título y su tabla; la sección de análisis la muestra con su texto «¿Qué significa?» (CA8). No hay puntaje combinado (CA9, ya cubierto por las pruebas de la 007 y la 025).
- **Manual (autora):**
  1. Publicar el modelo 1.0.0 en el repositorio privado de Hugging Face (E03 de la 010).
  2. Cargar `HF_TOKEN` (de lectura) y la versión en Parameter Store.
  3. Analizar un caso en producción y verificar la capa 4 en la pantalla y en el PDF.

## Excepciones a la constitución

Ninguna. La capa accede al modelo a través de una integración (constitución, sección 1), y el servicio de análisis no cambia.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| El repositorio de modelos todavía no existe (E03) | La capa queda «No disponible» con un motivo claro; el resto del análisis no cambia. Para probar antes, se admite un registro local (`local:/ruta`) con el paquete publicado por el cuaderno 03 |
| `onnxruntime` agrega memoria al trabajador de la EC2 | El modelo pesa ~16 MB y la sesión, unos 100 MB; se carga una sola vez por proceso. Se mide en la prueba manual |
| El modelo falla con las herramientas comerciales actuales (detectó 5 de 49 en el conjunto propio) | La conclusión lo dice siempre; nivel 0 por debajo de 50 % sin afirmar autenticidad; ninguna combinación con otras capas (RN27). Se mejora con la 1.1.0 de la 010 |
| Diferencias entre la versión del paquete `clasificador` y la del modelo | El preprocesamiento sale de los metadatos del ONNX; una versión `MAJOR` nueva cambia el contrato (ADR-0015) y obliga a actualizar el backend |
| El token de Hugging Face se filtra | Va solo en Parameter Store como SecureString, igual que la clave de Hedera; nunca en el repositorio ni en los registros |
