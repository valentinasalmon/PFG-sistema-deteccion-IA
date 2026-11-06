# 2026-11-04 — Funcionalidad 018: materiales del cierre

## Qué se hizo

- **Índice de Calidad (QI)**: fórmula propuesta para CP-04 con seis componentes: cobertura del backend y del frontend, pylint, complejidad, duplicación y SUS. Script `backend/herramientas/indice_calidad.py` con 7 pruebas, sin dependencias nuevas.
- **Primera medición**: QI provisorio de 0,977 sin la usabilidad. El umbral es 0,75.
- **Protocolo de la prueba de usabilidad** (`docs/guias/prueba-de-usabilidad.md`): participantes, consentimiento, guion, 8 tareas con criterio de éxito, planilla y cuestionario SUS en español.
- **Guía de usuario** (`docs/guias/guia-de-usuario.md`) para abogados y aseguradoras.

## Decisiones

- La usabilidad pesa 0,30 en el QI: es la única medida que viene de personas.
- Hallazgo: como el código ya está cerca del máximo, el QI se cumpliría con un SUS de apenas 23. Por eso la usabilidad tiene su propio objetivo (SUS ≥ 68 y 80 % de éxito). Queda para conversar con el tutor.
- La tarea T5 del protocolo comprueba RN27: que la persona entienda indicios, no veredictos.
- La red neuronal figura en la guía como «se suma con la 012», porque la capa todavía no está en el sistema.

## Pendiente

- Validar la fórmula con el tutor (CP-04).
- Hacer la prueba con al menos 5 participantes (la autora) y calcular el QI final con el SUS.
- Revisión de accesibilidad con herramientas automáticas (RNF11) sobre la versión final.
