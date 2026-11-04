# 2026-10-30 — Red neuronal (010): primera corrida en Colab

## Qué pasó

- La autora corrió el cuaderno `01_prueba_de_concepto_colab.ipynb`. Problemas encontrados:
  - **Faltaba `HF_TOKEN`** en los secretos de Colab: la autora lo creó (token de lectura de Hugging Face).
  - **GitHub rechazó el primer `GITHUB_TOKEN`** (`could not read Username`): el token no tenía acceso al repositorio. La autora creó uno nuevo, de grano fino, con *Contents: Read-only* sobre este repositorio, y el clonado anduvo.
  - **La etapa «obtener» falló a los 111,5 s y no se veía el motivo:** el cuaderno lanzaba cada etapa como subproceso y Colab no muestra la salida de los subprocesos.
- Correcciones en el cuaderno:
  - la sección 2 se detiene con un mensaje claro si falta algún secreto;
  - la sección 3 explica qué revisar si GitHub rechaza el token;
  - las etapas muestran su salida en la celda, línea por línea, incluido el motivo si fallan.
- El paquete se verificó fuera de Colab: instala bien y pasan sus 177 pruebas, incluida la del pipeline completo.

## Decisiones

- **Colab Pro disponible:** la autora tiene Colab Pro por un año, incluido en su suscripción a Gemini. Ya no hace falta evaluar si pagarlo (CP-21). Esto permite sesiones más largas y GPU más potentes para el entrenamiento completo (T30).

## Pendiente

- Volver a correr el cuaderno con la versión corregida para ver por qué falla «obtener» (T24).
