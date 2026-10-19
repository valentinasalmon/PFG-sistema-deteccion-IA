# ADR-0012: Ciclo de vida y herramientas de MLOps del clasificador

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Requisitos relacionados**: RNF24, RNF20, RN29

## Contexto

El clasificador de la capa 4 se entrena fuera del servidor (Kaggle, con GPU gratuita) y se usa en el backend. Su comportamiento depende del código, de los datos y de los pesos, y cada informe debe poder indicar con qué modelo se obtuvo su resultado (RN29). Hace falta decidir cómo se versionan los datos y los modelos, cómo se registran los experimentos y cómo llega un modelo al backend, con herramientas gratuitas y acordes al tamaño del proyecto. Los datos de los casos son confidenciales (RNF08) y no se reutilizan para entrenar.

## Alternativas evaluadas

### Versionado de datos

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| DVC con almacenamiento remoto | Estándar de la industria; versiona archivos grandes junto a Git | Requiere un almacenamiento remoto propio; más complejidad para datos que ya están versionados en su origen |
| **Receta en Git + manifiesto con huellas + Kaggle Dataset privado** | Sin infraestructura nueva; el Kaggle Dataset ya tiene versiones; la receta y la huella permiten reconstruir y verificar | Depende de Kaggle para guardar las imágenes preparadas |

### Seguimiento de experimentos

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Weights & Biases | Tablero en línea; muy simple desde Kaggle | Servicio privativo; cuenta externa |
| **MLflow (almacén de archivos)** | Código abierto y estándar; sin cuenta; se puede autoalojar en el futuro | Sin servidor compartido: los registros se empaquetan con cada versión y se consultan localmente con `mlflow ui` |
| Archivos JSON propios | Mínimo | Reinventa una herramienta existente; sin comparación visual |

### Registro de modelos

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Archivo en el repositorio | Simple | Prohibido por la constitución; Git no es apto para binarios grandes |
| GitHub Releases | Junto al código | Atado a la visibilidad del repositorio; sin metadatos de modelo |
| S3 | Ya previsto para producción | Costo y configuración antes de la etapa de infraestructura (017) |
| **Repositorio privado de Hugging Face Hub** | Gratuito; versiones por etiqueta; se lee y se escribe con el mismo *token* desde Kaggle y desde el backend | Servicio externo; requiere *token* |

## Decisión

- **Nivel 1 de madurez de MLOps**: pipeline automatizado por etapas, reentrenamiento a pedido y compuerta de promoción automática. El nivel 2 (reentrenamiento disparado por datos de producción) queda fuera de alcance.
- **Datos**: la receta de cada conjunto (fuentes, revisiones, cantidades y semilla) se versiona en Git. Las imágenes preparadas y su manifiesto se guardan como Kaggle Dataset privado, y la huella del manifiesto se registra en la ficha del modelo.
- **Experimentos**: MLflow con almacén de archivos, detrás de la interfaz `RegistradorExperimentos`.
- **Modelos**: repositorio privado de Hugging Face Hub con una etiqueta inmutable `vMAJOR.MINOR.PATCH` por versión, detrás de la interfaz `RegistroModelos`. Solo se publica lo que aprueba la compuerta.
- **Lógica en un paquete de Python probado**; los cuadernos solo orquestan.

## Consecuencias

- No se agrega infraestructura propia y todo es gratuito.
- Las interfaces permiten cambiar MLflow o Hugging Face (por ejemplo, por S3 en la funcionalidad 017) sin modificar las etapas.
- El backend necesita un *token* de lectura de Hugging Face, o una copia del modelo en S3, para descargar una versión concreta y verificar su huella.
- Los registros de MLflow no se consultan en línea: para comparar ejecuciones se descargan y se abren localmente.
