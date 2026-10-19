# Funcionalidades

Cada funcionalidad del sistema se desarrolla con el flujo de **desarrollo guiado por especificaciones**, inspirado en GitHub Spec Kit y heredado del repositorio anterior.

## Flujo

```
/especificar  →  especificacion.md   QUÉ se construye y cómo se verifica (sin detalles técnicos)
/planificar   →  plan.md             CÓMO se construye: capas, patrones, contratos, datos
/tareas       →  tareas.md           PASOS ordenados y verificables para implementarlo
implementación siguiendo tareas.md, con pruebas
```

1. **Especificar**: se toma de `docs/especificacion/` el subconjunto de requisitos, reglas y casos de uso que cubre la funcionalidad, y se precisan sus criterios de aceptación.
2. **Planificar**: se diseña la solución respetando la constitución. Si algo la contradice, se justifica en *Excepciones a la constitución*.
3. **Tareas**: se descompone el plan en pasos chicos, cada uno verificable por sí mismo.
4. **Implementar**: cada tarea se marca como hecha al terminarla; al cerrar la funcionalidad se registra una entrada en la bitácora.

## Convenciones

- Carpeta por funcionalidad: `NNN-nombre-corto/` (tres dígitos, minúsculas, guiones).
- La rama de trabajo lleva el mismo nombre: `funcionalidad/NNN-nombre-corto`.
- Plantillas en [plantillas/](plantillas/).

## Plan de funcionalidades

| N.° | Funcionalidad | Fase | Requisitos | Estado |
|---|---|---|---|---|
| 001 | Esqueleto caminante: estructura, configuración, servicios, calidad e integración continua | 1 | RNF17 – RNF22 | Pendiente |
| 002 | Cuentas y sesión | 2 | RF01 – RF09 | Pendiente |
| 003 | Auditoría | 2 | RNF06 | Pendiente |
| 004 | Organizaciones e invitaciones | 3 | RF10 – RF18 | Pendiente |
| 005 | Casos y permisos | 3 | RF23 – RF33 | Pendiente |
| 006 | Carga de imágenes, huella y almacenamiento | 4 | RF34 – RF36 | Pendiente |
| 007 | Motor de análisis y capa 1 (metadatos) | 4 | RF38, RF39, RF43, RF46 | Pendiente |
| 008 | Informe PDF e historial | 4 | RF44, RF45 | Pendiente |
| 009 | Capa 2 (C2PA) | 5 | RF40 | Pendiente |
| 010 | [Red neuronal: ciclo de vida, entrenamiento y exportación](010-red-neuronal/especificacion.md) (pista paralela) | 2 – 5 | RNF24 | Especificada |
| 011 | Capa 3 (ELA) | 5 | RF41 | Pendiente |
| 012 | Capa 4 (ONNX) | 5 | RF42 | Pendiente |
| 013 | Notificaciones y panel principal | 6 | RF47, RF48 | Pendiente |
| 014 | Planes y tablero de administración | 6 | RF19 – RF22 | Pendiente |
| 015 | Retención y destrucción de datos | 7 | RF49 – RF51 | Pendiente |
| 016 | Sello de tiempo en Blockchain Federal Argentina | 7 | RF37 | Pendiente |
| 017 | Infraestructura y despliegue en AWS | 8 | RNF02, RNF03, RNF15, RNF22 | Pendiente |
| 018 | Cierre: usabilidad, índice de calidad y documentación final | 9 | RNF10, RNF11, RNF19 | Pendiente |

Las fases, los hitos y el ciclo de trabajo están en [docs/guias/hoja-de-ruta.md](../guias/hoja-de-ruta.md).
