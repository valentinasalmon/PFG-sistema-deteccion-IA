# Índice de Calidad del Software (QI)

RNF19 CA2 exige un QI de 0,75 o más al cierre del proyecto. La cátedra no fijó una fórmula (CP-04). Esta es la **propuesta para validar con el tutor**. Sigue la idea de CP-04: un promedio ponderado normalizado de métricas que el proyecto ya mide.

## Fórmula

```latex
QI = 0{,}20\,C_b + 0{,}15\,C_f + 0{,}15\,E + 0{,}10\,K + 0{,}10\,D + 0{,}30\,U
```

Cada componente vale entre 0 y 1:

| Símbolo | Componente | Cómo se mide | Peso | Característica (ISO/IEC 25010) |
|---|---|---|---|---|
| Cb | Cobertura de líneas del backend | coverage.py (`pytest --cov`) | 0,20 | Mantenibilidad (capacidad de prueba) |
| Cf | Cobertura de líneas del frontend | Vitest con `@vitest/coverage-v8` | 0,15 | Mantenibilidad (capacidad de prueba) |
| E | Análisis estático | Puntuación de pylint / 10 | 0,15 | Mantenibilidad |
| K | Complejidad acotada | Proporción de funciones con complejidad ciclomática ≤ 10 (flake8, mccabe) | 0,10 | Mantenibilidad (modificabilidad) |
| D | Código sin duplicar | 1 − líneas duplicadas / líneas totales (pylint, `duplicate-code`) | 0,10 | Mantenibilidad (reusabilidad) |
| U | Usabilidad | Puntaje SUS promedio de la prueba con participantes / 100 | 0,30 | Usabilidad |

**Por qué estos pesos:**
- **U pesa 0,30.** Es la única medida que viene de personas reales y RNF10 es de prioridad «Debe». Las demás miden el código.
- **El backend pesa más que el frontend.** Ahí están el análisis de las imágenes, la seguridad y las reglas de negocio.
- **K y D pesan menos.** Hoy ya están casi en su máximo y no distinguen mucho.

**Sin la prueba de usabilidad**, U se omite y los otros pesos se reescalan para sumar 1. El resultado se informa como **provisorio**.

## Cómo se mide

Desde `backend/`:

```bash
pytest --cov=app --cov-report=json:coverage.json
(cd ../frontend && npx vitest run --coverage --coverage.reporter=json-summary)
python herramientas/indice_calidad.py --cobertura-backend coverage.json \
    --cobertura-frontend ../frontend/coverage/coverage-summary.json --sus 78.5
```

El script imprime cada componente con su peso efectivo y el QI. Sale con código 0 si cumple el umbral y con 1 si no, así que se puede sumar a la integración continua.

## Primera medición (2026-11-04, provisoria)

| Componente | Valor |
|---|---|
| Cobertura del backend | 0,975 |
| Cobertura del frontend | 0,924 |
| Análisis estático (pylint 10/10) | 1,000 |
| Complejidad acotada (ninguna función supera 10) | 1,000 |
| Código sin duplicar | 0,999 |
| Usabilidad (SUS) | sin medir |
| **QI provisorio** | **0,977** |

**Sensibilidad.** Con los demás valores fijos, el QI final cumple el umbral si el SUS promedio es de 23 o más. Un SUS de 68 (el promedio de referencia de la industria) daría un QI de 0,888. Como el código ya está cerca del máximo, el QI solo no exige mucha usabilidad. Por eso la usabilidad tiene su propio objetivo: un SUS de 68 o más y 80 % de éxito en las tareas (RNF10).

## Para validar con el tutor (CP-04)

- ¿Alcanzan estos componentes o se suma otro? Por ejemplo, la tasa de éxito de las tareas o las vulnerabilidades de `pip-audit` y `npm audit`.
- ¿Están bien los pesos, sobre todo el 0,30 de la usabilidad?
- ¿El umbral de complejidad es 10 (el usual de McCabe)?
