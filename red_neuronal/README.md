# Red neuronal (capa 4)

Entrenamiento, evaluación y exportación del clasificador de imágenes sintéticas. Se entrena en PyTorch mediante transferencia de aprendizaje y se exporta a ONNX para ejecutarse en el backend con ONNX Runtime (RF42, RNF24).

Los conjuntos de datos (`datos/`) y los modelos (`modelos/`) **no se suben al repositorio**. Cada versión del modelo se documenta en `informes/` con su conjunto de datos, hiperparámetros, semilla y métricas.

- Especificación: [docs/funcionalidades/010-red-neuronal/especificacion.md](../docs/funcionalidades/010-red-neuronal/especificacion.md)
- Plan técnico: [docs/funcionalidades/010-red-neuronal/plan.md](../docs/funcionalidades/010-red-neuronal/plan.md)
- Ciclo de vida, flujos y MLOps: [docs/guias/ciclo-de-vida-red-neuronal.md](../docs/guias/ciclo-de-vida-red-neuronal.md)

## Instalación para desarrollo

```bash
cd red_neuronal
python3 -m venv .venv
source .venv/bin/activate
# PyTorch para CPU (más liviano; la GPU solo se usa en Google Colab)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[entrenamiento,desarrollo]"
```

## Calidad

```bash
flake8 clasificador/ && pylint clasificador/ && pytest --cov=clasificador --cov-fail-under=80
```

> Se completa en la funcionalidad 010 (tarea T34).
