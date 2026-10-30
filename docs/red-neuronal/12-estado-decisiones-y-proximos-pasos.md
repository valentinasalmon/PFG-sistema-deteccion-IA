# 12. Estado, decisiones y próximos pasos

## Estado al 2026-10-30

| Parte | Estado |
|---|---|
| Paquete `clasificador` (las siete etapas, inferencia, registro, compuerta, ficha, MLflow) | ✔ Hecho, con 177 pruebas |
| Integración continua (`red_neuronal.yml`) | ✔ Hecha |
| Cuaderno de Colab | ✔ Hecho y corregido con la primera corrida |
| Prueba de concepto (CA1, T24) | ✔ Hecha: AUC 0,985, ≈ 11 min en T4 |
| Exploración de datos y licencias (T25) | Pendiente |
| Protocolo del conjunto propio (T26) y armado (E04) | Pendiente |
| Receta v1 (T27) y datos en Drive (T28) | Pendiente |
| Cuaderno de entrenamiento que corra solo (Kaggle en segundo plano) | Pendiente |
| Entrenamiento completo, reproducibilidad y condiciones reales (T30 a T32) | Pendiente |
| Repositorio de modelos en Hugging Face (E03) y publicación de `1.0.0` (T33) | Pendiente |
| Integración en el backend y el informe (funcionalidad 012) | Pendiente |

Todo vive en la rama `funcionalidad/010-red-neuronal` hasta el entrenamiento completo.

## Decisiones tomadas y por qué

| Fecha | Decisión | Por qué | Dónde |
|---|---|---|---|
| 2026-10-19 | EfficientNet-B0 preentrenada, con una salida | Precisión suficiente, rápida en CPU, estándar defendible | ADR-0015 |
| 2026-10-19 | Calibración por temperatura dentro del ONNX | Probabilidades honestas (RN27) sin pasos extra en el backend | ADR-0015 |
| 2026-10-19 | Cinco recortes de 224 sin reescalar | No borrar las huellas de alta frecuencia de la generación | ADR-0015 |
| 2026-10-19 | Nivel 1 de MLOps; lógica en un paquete probado; cuadernos solo orquestan | Reproducibilidad (RN29) con un costo razonable | ADR-0014 |
| 2026-10-19 | MLflow con SQLite; registro en Hugging Face privado | Sin servidores que mantener; versiones inmutables | ADR-0014 |
| 2026-10-19 | La autora entrena; el agente prepara el código y analiza | El entrenamiento necesita GPU y las cuentas de la autora | CP-21 |
| 2026-10-26 | Pasar de Kaggle a Google Colab con respaldo en Drive | Preferencia de la autora; misma lógica | Bitácora del 2026-10-28 |
| 2026-10-30 | Colab Pro disponible por un año (suscripción a Gemini) | Ya no hace falta evaluar si pagarlo | CP-21 |
| 2026-10-30 | Documentación propia y siempre al día de la red neuronal | Pedido de la autora: entender la red de punta a punta | Esta carpeta |
| 2026-10-30 | Buscar que el entrenamiento completo corra solo (Kaggle en segundo plano) | Pedido de la autora: no depender de estar frente a la computadora | Capítulo 10 |

## Riesgos y cómo se mitigan

| Riesgo | Mitigación |
|---|---|
| El modelo aprende atajos (formato, tamaño) en vez de huellas de generación | Normalización anti-atajos igual para las dos clases; evaluación por generador y en condiciones reales |
| Bajo desempeño con generadores comerciales nuevos | Generadores reservados, conjunto propio, reentrenamiento (CA18) y la limitación declarada en la ficha |
| Cortes de sesión en Colab | Respaldo por etapa en Drive, puntos de control por época y opción de Kaggle en segundo plano |
| Un conjunto exige aceptar condiciones o deja de estar disponible | Verificación en la exploración (T25); las fuentes son intercambiables |
| Licencias solo para investigación | Registradas en la ficha; reentrenar con datos compatibles si se comercializa |
| Fuga de datos del conjunto propio | Drive privado; nunca se usa para entrenar ni se sube al repositorio |
| Credenciales expuestas | Solo como secretos; el cuaderno nunca las muestra |
| Umbral distinto entre el informe (F1 ≥ 0,85) y la especificación (AUC ≥ 0,90) | Validar con los tutores |

## Próximos pasos, en orden

1. **T25. Exploración de datos** (agente): cuaderno que revise cada fuente candidata (disponibilidad, licencia, generadores, formatos) y proponga la receta.
2. **T26. Protocolo del conjunto propio** (agente) y **E04. Armado** (autora).
3. **T27. Receta v1** (agente): menos generadores con más imágenes cada uno, generadores reservados, nuevas fuentes y más épocas.
4. **Cuaderno que corra solo** (agente): versión de Kaggle en segundo plano y salto automático de las etapas ya hechas.
5. **E03. Repositorio de modelos** en Hugging Face (autora).
6. **T28 a T33. Datos, entrenamiento completo, reproducibilidad, condiciones reales y publicación de `1.0.0`** (corre la autora, analiza y documenta el agente).
7. **Funcionalidad 012:** integrar el modelo en el análisis y el informe.
