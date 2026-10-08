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

| N.° | Funcionalidad | Requisitos | Estado |
|---|---|---|---|
| 001 | Base del proyecto: estructura, configuración, calidad e integración continua | RNF17 – RNF22 | Pendiente |
| 002 | Cuentas y sesión | RF01 – RF09 | Pendiente |
| 003 | Auditoría | RNF06 | Pendiente |
| 004 | Organizaciones e invitaciones | RF10 – RF18 | Pendiente |
| 005 | Casos y permisos | RF23 – RF33 | Pendiente |
| 006 | Carga de imágenes, huella y almacenamiento | RF34 – RF36 | Pendiente |
| 007 | Motor de análisis y capa 1 (metadatos) | RF38, RF39, RF43, RF46 | Pendiente |
| 008 | Capa 2 (C2PA) | RF40 | Pendiente |
| 009 | Capa 3 (ELA) | RF41 | Pendiente |
| 010 | Red neuronal: entrenamiento y exportación | RNF24 | Pendiente |
| 011 | Capa 4 (ONNX) | RF42 | Pendiente |
| 012 | Informe PDF e historial | RF44, RF45 | Pendiente |
| 013 | Notificaciones y panel principal | RF47, RF48 | Pendiente |
| 014 | Planes y tablero de administración | RF19 – RF22 | Pendiente |
| 015 | Retención y destrucción de datos | RF49 – RF51 | Pendiente |
| 016 | Sello de tiempo en Blockchain Federal Argentina | RF37 | Pendiente |
| 017 | Infraestructura y despliegue en AWS | RNF15, RNF22 | Pendiente |

El orden es tentativo y se ajusta según la fecha de entrega.
