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
| 001 | Esqueleto caminante: estructura, configuración, servicios, calidad e integración continua | 1 | RNF17 – RNF22 | Completado |
| 002 | Cuentas y sesión | 2 | RF01 – RF07 | Completado |
| 003 | Auditoría | 2 | RNF06 | Completado |
| 004 | Organizaciones e invitaciones | 3 | RF10 – RF18 (sin las reglas de casos) | Completado |
| 005 | Casos y permisos | 3 | RF23 – RF33 | Completado |
| 006 | Carga de imágenes, huella y almacenamiento | 4 | RF34 – RF36 | Completado |
| 007 | Motor de análisis y capa 1 (metadatos) | 4 | RF38, RF39, RF43, RF46 | Completado |
| 008 | Informe PDF e historial | 4 | RF44, RF45 | Completado |
| 009 | Capa 2 (C2PA) | 5 | RF40 | Completado |
| 010 | Red neuronal: entrenamiento y exportación (pista paralela) | 2 – 5 | RNF24 | Pendiente |
| 011 | [Capa 3 (ELA)](011-capa-ela/especificacion.md) | 5 | RF41 | Completado |
| 012 | Capa 4 (ONNX) | 5 | RF42 | Pendiente |
| 013 | [Notificaciones y panel principal](013-panel-y-notificaciones/especificacion.md) | 6 | RF47, RF48 | Completado |
| 014 | [Planes y tablero de administración](014-planes-y-tablero/especificacion.md) | 6 | RF19 – RF22 | Completado |
| 015 | [Retención y destrucción de datos](015-retencion/especificacion.md) | 7 | RF49 – RF51 | Completado |
| 016 | [Sello de tiempo en Blockchain Federal Argentina](016-sello-bfa/especificacion.md) | 7 | RF37 | Reemplazada por la 023 (ADR-0018) |
| 017 | [Infraestructura y despliegue en AWS](017-infraestructura-aws/especificacion.md) | 8 | RNF02, RNF03, RNF15, RNF22 | Desplegada (falta probar la restauración y el dominio) |
| 018 | Cierre: usabilidad, índice de calidad y documentación final | 9 | RNF10, RNF11, RNF19 | Pendiente |
| 019 | Eliminación de cuenta y copia de datos personales | 3 | RF08, RF09 | Completado |
| 020 | Registro guiado por pasos | 2 | RF01 (interfaz), RNF10 | Completado |
| 021 | Organizaciones de aseguradoras | 3 | RF01, RF10, RF12 – RF17 (ajustes), RN36 – RN40 | Completado |
| 022 | [Rediseño de la interfaz y del informe PDF](022-rediseno-interfaz/especificacion.md) | 9 | RNF10, RF44 | Completado |
| 023 | Sello de tiempo en Hedera (reemplaza a la 016) | 10 | RF37 | Pendiente |
| 024 | Carga de imágenes desde el celular (web móvil, QR y HEIC) | 10 | RF53 | Pendiente |
| 025 | Informe por rubro, breve y autosuficiente | 10 | RF44, RF54 | Pendiente (espera el detalle de la autora, CP-28) |
| 026 | Informe inalterable: huella en Hedera, firma digital y verificación pública | 10 | RF55 | Pendiente |
| 027 | Inicio de sesión y registro con Google | 10 | RF52 | Pendiente |
| 028 | Mejoras de usabilidad e interfaz | 10 | RNF10 | Pendiente |
| 029 | "Host tokenizado" | 10 | — | Por definir (CP-29) |

Las fases, los hitos y el ciclo de trabajo están en [docs/guias/hoja-de-ruta.md](../guias/hoja-de-ruta.md).
