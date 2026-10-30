# 2026-10-30 — Red neuronal (010): documentación, plan de entrenamientos y búsqueda de datos

## Qué se hizo

- **Documentación completa de la red neuronal** en `docs/red-neuronal/`: 12 capítulos y un glosario. Regla nueva en `CLAUDE.md`: todo cambio en la red actualiza esa documentación en el mismo commit.
- **Investigación de conjuntos de datos** (`docs/investigacion/2026-10-30-conjuntos-de-datos-imagenes-sinteticas.md`): OpenFake, Treasure, AIGenImages2026, TrueFake, Semi-Truths y otros, con licencia y uso propuesto.
- **Protocolo del conjunto propio** (T26, `docs/guias/protocolo-conjunto-propio.md`): escenas del ámbito del sistema, prompts en español, fotos reales y editadas, variantes original, WhatsApp y captura, carpetas, nombres, planilla y privacidad.

## Decisiones de la autora

- **Se entrena en Colab Pro**, a mano. Se analizó automatizarlo (GitHub Actions + API de Kaggle, Hugging Face Jobs, GPU en AWS) y se dejó como opción futura.
- **Se sigue buscando datos y generando imágenes** para mejorar la red: mejora con datos nuevos, no con repetir entrenamientos.
- **Plan de entrenamientos:** 2 obligatorios (completo y repetición para reproducibilidad), 1 o 2 de ajuste si no llega a AUC 0,90, y una **demostración de reentrenamiento** (versión 1.0.0 con Gemini como no visto → 1.1.0 con Gemini incluido) para mostrar el ciclo de vida en el informe.

## Pendiente

- T25: cuaderno de exploración en Colab que verifique las licencias en la revisión exacta.
- T27: receta v1. Cuaderno de entrenamiento completo que saltee etapas ya hechas.
- E04 (autora): empezar a generar el conjunto propio con el protocolo.
