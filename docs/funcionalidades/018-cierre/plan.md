# Plan técnico: 018 — Cierre

| Pieza | Archivo | Qué hace |
|---|---|---|
| Fórmula del QI | `docs/calidad/indice-de-calidad.md` | Componentes, pesos, fuentes de medición y valor actual |
| Script del QI | `backend/herramientas/indice_calidad.py` | Lee las coberturas, corre pylint y flake8 y calcula el QI; también calcula el puntaje SUS de un participante |
| Pruebas | `backend/pruebas/unitarias/test_indice_calidad.py` | Fórmula, reescalado sin SUS, lectores de cada herramienta y línea de comandos |
| Protocolo | `docs/guias/prueba-de-usabilidad.md` | Guion completo de la prueba con participantes |
| Guía de usuario | `docs/guias/guia-de-usuario.md` | Uso de la plataforma para abogados y aseguradoras |

## Decisiones

- **Sin dependencias nuevas**: la complejidad la mide flake8 (mccabe) y la duplicación, pylint. Así el QI se puede correr en la integración continua sin instalar nada más.
- **El script vive fuera de `app/`**: es una herramienta del proyecto, no parte del sistema, y no altera la cobertura de la aplicación.
- **La usabilidad pesa 0,30**: es la mitad «del usuario» de la calidad y la única que no mide una herramienta.
