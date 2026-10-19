# 2026-10-19 — Especificación y plan técnico de la red neuronal

## Qué se hizo

1. Se resolvió la cuestión abierta CP-07 (datos y umbral de la red neuronal) y se completó el umbral de RNF24 CA3.
2. Se redactó la especificación de la funcionalidad 010 ([especificación](../funcionalidades/010-red-neuronal/especificacion.md)), ampliada para cubrir el ciclo de vida completo del modelo: prueba de concepto, pipeline por etapas, versionado de datos y modelos, seguimiento de experimentos, compuerta de promoción, integración continua y reentrenamiento.
3. Se redactó la guía conceptual [Ciclo de vida de la red neuronal](../guias/ciclo-de-vida-red-neuronal.md), con los flujos entre GitHub, Kaggle, Hugging Face y el backend, y las prácticas de MLOps (CI, CT y CD).
4. Se redactó el [plan técnico](../funcionalidades/010-red-neuronal/plan.md) de la funcionalidad 010 y se registraron [ADR-0010](../arquitectura/decisiones/0010-ciclo-de-vida-y-mlops-del-clasificador.md) (ciclo de vida y herramientas de MLOps) y [ADR-0011](../arquitectura/decisiones/0011-arquitectura-y-contrato-de-inferencia-del-clasificador.md) (arquitectura y contrato de inferencia).
5. Se ajustó el `CLAUDE.md`: ante decisiones técnicas el agente propone la mejor opción y la justifica, y pregunta solo lo que depende de la autora.

## Decisiones tomadas

- **Generadores objetivo**: las herramientas comerciales que usa cualquier persona (ChatGPT, Gemini, Copilot, Midjourney), no los generadores académicos. Motivo: son las que producirán las imágenes que reciben abogados y aseguradoras.
- **Datos de entrenamiento**: Community Forensics (versión *Small*, 4 803 generadores) como base, más OpenFake, MS COCOAI y ShareGPT-4o-Image para cubrir generadores comerciales. Se descartan CIFAKE y GenImage como base por cubrir solo generadores antiguos; un estudio de 2026 reporta entre 18 y 30 % de exactitud de detectores abiertos frente a generadores comerciales recientes.
- **Conjunto de prueba propio**: imágenes generadas por la autora con ChatGPT, Gemini y Copilot, y fotografías reales propias, de escenas del ámbito del sistema, evaluadas en versión original, enviada por WhatsApp y captura de pantalla. Nunca se suben al repositorio.
- **Umbral**: área bajo la curva ROC ≥ 0,90 sobre generadores conocidos; el desempeño frente a generadores no vistos, imágenes recomprimidas y ediciones se reporta sin umbral obligatorio.
- **Ediciones parciales**: RF42 no cambia; el modelo no promete detectarlas, pero su desempeño frente a ellas se mide y se declara.
- **Plataforma**: Kaggle (GPU T4 gratuita, sesiones de hasta 12 h, versiones de cuaderno guardadas).
- **Nivel de MLOps objetivo**: nivel 1 (pipeline automatizado, reentrenamiento a pedido). El nivel 2 queda fuera de alcance porque los datos de producción son confidenciales.
- **Lógica en módulos, no en cuadernos**: los cuadernos solo orquestan, para que el código pueda probarse en la integración continua.
- **Herramientas de MLOps** ([ADR-0010](../arquitectura/decisiones/0010-ciclo-de-vida-y-mlops-del-clasificador.md)): receta de datos en Git más Kaggle Dataset privado; MLflow para experimentos; repositorio privado de Hugging Face Hub como registro de modelos. Se descartó DVC por requerir almacenamiento propio sin aportar sobre datos ya versionados en su origen.
- **Modelo** ([ADR-0011](../arquitectura/decisiones/0011-arquitectura-y-contrato-de-inferencia-del-clasificador.md)): EfficientNet-B0 calibrada con *temperature scaling*; cinco recortes de 224 px sin reescalar para conservar las huellas de generación; preprocesamiento de inferencia en un subpaquete sin PyTorch, compartido con el backend.

## Tecnologías, bibliotecas o técnicas incorporadas

Ninguna en código todavía. El plan prevé PyTorch, timm, ONNX y ONNX Runtime, MLflow, Hugging Face `datasets` y `huggingface_hub`, scikit-learn y pydantic (detalle y justificación en el plan).

## Problemas encontrados y cómo se resolvieron

- El repositorio no tiene `.gitignore`, aunque la documentación indica carpetas ignoradas: se crea en la primera tarea de la funcionalidad 010.
- No hay conjuntos públicos de entrenamiento confirmados para Gemini y Copilot: se evalúan como generadores no vistos con el conjunto propio.
- Casi todos los conjuntos tienen licencia no comercial: alcanza para el proyecto final y queda registrado como trabajo futuro si la plataforma se comercializa.

## Pendientes

- Que la autora revise y apruebe la especificación de la funcionalidad 010.
- `/tareas 010`: descomponer el plan en pasos ejecutables, empezando por la prueba de concepto.
- Que la autora cree las cuentas de Kaggle (con teléfono verificado) y de Hugging Face, y cargue el *token* como secreto en Kaggle.
- Protocolo de recolección del conjunto propio (prompts por escena, nombres de archivo y recompresión).
