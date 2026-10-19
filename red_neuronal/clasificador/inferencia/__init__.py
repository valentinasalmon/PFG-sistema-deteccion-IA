"""Inferencia del clasificador en CPU, sin dependencias de PyTorch.

Este subpaquete define el contrato de entrada del modelo y es el único
código que comparten el entrenamiento y el backend: así el preprocesamiento
existe una sola vez y no puede divergir (ADR-0013). Solo depende de numpy,
Pillow y onnxruntime.

Realiza: RF42, RNF24 CA1.
"""
