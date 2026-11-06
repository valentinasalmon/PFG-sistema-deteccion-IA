# 12. Estado, decisiones y próximos pasos

## Estado al 2026-10-30

| Parte | Estado |
|---|---|
| Paquete `clasificador` (las siete etapas, inferencia, registro, compuerta, ficha, MLflow, exploración y estado) | ✔ Hecho, con 209 pruebas |
| Integración continua (`red_neuronal.yml`) | ✔ Hecha |
| Cuaderno de Colab | ✔ Hecho y corregido con la primera corrida |
| Prueba de concepto (CA1, T24) | ✔ Hecha: AUC 0,985, ≈ 11 min en T4 |
| Investigación de conjuntos de datos | ✔ Hecha el 2026-10-30 (falta verificar licencias en Colab con el cuaderno de exploración) |
| Exploración de datos y licencias (T25) | ✔ Hecha el 2026-11-04: Community Forensics y OpenFake incluidos; el resto, fuera de la v1 (capítulo 4) |
| Protocolo del conjunto propio (T26) | ✔ Hecho: [docs/guias/protocolo-conjunto-propio.md](../guias/protocolo-conjunto-propio.md) |
| Armado del conjunto propio (E04) | Pendiente (autora), con la [guía paso a paso](../guias/guia-paso-a-paso-conjunto-propio.md) y su lista de 90 prompts |
| Receta v1 (T27) | ✔ `configuracion/v1.yaml`: 17 500 reales y 17 500 sintéticas depuradas, la familia de Google como no vista |
| Datos en Drive (T28) | Pendiente: el cuaderno `03` los guarda solo |
| Cuaderno de entrenamiento completo en Colab que saltee las etapas ya hechas (T29) | ✔ Hecho: `03_entrenamiento_completo_colab.ipynb` |
| Entrenamiento completo, reproducibilidad y condiciones reales (T30 a T32) | Pendiente |
| Repositorio de modelos en Hugging Face (E03) y publicación de `1.0.0` (T33) | Pendiente |
| Integración en el backend y el informe (funcionalidad 012) | ✔ Código hecho el 2026-11-06 en `funcionalidad/012-capa-4-onnx` (capítulo 7). Falta publicar `1.0.0` y activarlo en producción con la [guía](../guias/despliegue-aws.md#capa-4-modelo-de-la-red-neuronal-funcionalidad-012) |

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
| 2026-10-30 | **Entrenar en Colab Pro**, a mano; Kaggle automático queda como opción futura | Decisión de la autora: 3 o 4 sesiones de 2 a 3 h con unos 15 min de atención cada una | Capítulo 10 |
| 2026-10-30 | Seguir buscando conjuntos de datos y generando imágenes propias | Pedido de la autora: la red mejora con datos nuevos, no con repeticiones | Capítulo 4 e investigación del 2026-10-30 |
| 2026-10-30 | Muestreo por archivos, generadores incluidos y cuota por generador en la receta | Lección de la prueba de concepto: métricas por generador con sentido y menos descargas | Capítulo 4 |
| 2026-10-30 | «No visto» se evalúa contra las reales de prueba | La partición solo tiene sintéticas y sin reales el AUC no se puede calcular | Capítulo 6 |
| 2026-10-30 | Las fotos reales de escenas del sistema (CarDD, SCIN, MOCS) no se usan para entrenar | No hay sintéticas de esas escenas en el entrenamiento: el modelo aprendería el tema | Capítulo 4 |
| 2026-10-30 | El cuaderno de entrenamiento saltea etapas terminadas con el mismo manifiesto y guarda los datos preparados en Drive | Pedido de la autora: no rehacer horas de trabajo si Colab corta | Capítulo 8 |
| 2026-10-30 | Sin escenas de viviendas en el conjunto propio (CP-39) | Decisión de la autora: el sistema solo tiene casos automovilísticos y laborales | Especificación, CA12 |
| 2026-10-30 | Sin la versión de WhatsApp en el conjunto propio: solo original y captura | Decisión de la autora: las fotos las sube la persona afectada desde el enlace de carga, como original, captura o generada | Capítulo 4 |
| 2026-11-04 | La familia de Google (Imagen 4, Imagen 3, Nano Banana 2) como generadores no vistos | Es lo que usa Gemini; está en OpenFake y permite la demostración de reentrenamiento planificada | Capítulo 4 |
| 2026-11-04 | Depuración: sin generadores que no hacen fotos, sin imágenes de menos de 256 px y sin agrandar al normalizar | Las reales son fotos; las ilustraciones y la interpolación serían atajos | Capítulo 4 |
| 2026-11-04 | Búfer de mezcla por fuente y borrado de las imágenes crudas después de preparar | Las reales de OpenFake pesan ~4 MB: memoria y disco de Colab | Capítulos 4 y 8 |
| 2026-10-30 | Plan de entrenamientos: 2 obligatorios (completo y repetición), 1 o 2 de ajuste y 1 o 2 de la demostración de reentrenamiento | Explicado a la autora | Capítulo 8 |

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

1. **Pull Request** de `funcionalidad/010-red-neuronal` hacia `desarrollo` (autora).
2. **Cuaderno 03 en Colab** (autora, GPU T4 o L4 con RAM amplia): obtener, validar, preparar y entrenar con la receta v1. Lleva unas 2 a 3 horas; si se corta, se vuelve a ejecutar y sigue desde donde quedó.
3. **Conjunto propio** (autora): prioridad A en dos o tres herramientas, original y captura. El agente prepara la copia de una muestra de CarDD a Drive.
4. **E03. Repositorio de modelos** en Hugging Face (autora).
5. **Repetición** para la reproducibilidad, **evaluación en condiciones reales** y publicación de `1.0.0`.
6. **Demostración de reentrenamiento:** sumar la familia de Google (y, si se puede leer, MLLM-Generated) y publicar `1.1.0`.
7. **Funcionalidad 012:** integrar el modelo en el análisis y el informe.
