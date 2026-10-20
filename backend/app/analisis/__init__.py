"""Capas de análisis forense (patrón Strategy, ADR-0006).

Cada capa es una función pura sobre el contenido de la imagen: no accede a la
base de datos ni al almacenamiento. ``ServicioAnalisis`` las ejecuta y guarda
sus resultados.
"""
