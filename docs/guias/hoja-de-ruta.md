# Hoja de ruta

Plan completo para llevar el proyecto desde la especificación hasta la plataforma funcionando en producción.

## 1. Estrategia: desarrollo por funcionalidades verticales

### Alternativas consideradas

| Estrategia | Cómo se trabaja | Ventajas | Desventajas |
|---|---|---|---|
| **Por capas técnicas** | Primero todo el backend, después todo el frontend | Concentración en una tecnología por vez | Nada funciona de punta a punta hasta el final; los errores de integración aparecen tarde; no hay nada que mostrar a los tutores durante meses |
| **Por funcionalidades verticales** ✅ | Cada funcionalidad se construye completa: modelo, API, interfaz y pruebas | Siempre hay una plataforma que funciona; cada entrega es demostrable; los errores de integración aparecen temprano; encaja con el desarrollo guiado por especificaciones | Hay que alternar entre Python y React en cada funcionalidad |

### Decisión

Se trabaja por **funcionalidades verticales**, comenzando por un **esqueleto caminante** (*walking skeleton*): la versión mínima del sistema en la que todas las piezas (React, Flask, PostgreSQL, Redis, almacenamiento, integración continua) ya están conectadas y funcionando, aunque hagan muy poco. Sobre ese esqueleto, cada funcionalidad agrega una capacidad completa y probada.

**Excepción**: el entrenamiento de la red neuronal es un trabajo independiente y lento (descarga de datos, entrenamiento, evaluación), por lo que avanza **en paralelo** desde la fase 2, en su propia rama.

## 2. Fases y funcionalidades

```
Fase 0  Preparación del entorno ─────────────────────────────┐
Fase 1  001 Esqueleto caminante                              │
Fase 2  002 Cuentas y sesión · 003 Auditoría                 │   Pista paralela:
Fase 3  004 Organizaciones · 005 Casos y permisos            │   010 Red neuronal
Fase 4  006 Imágenes · 007 Motor de análisis + capa 1        │   (entrenamiento en
        008 Informe PDF        ← primer flujo completo  v0.1 │    Colab/Kaggle)
Fase 5  009 Capa 2 (C2PA) · 011 Capa 3 (ELA) · 012 Capa 4    │
Fase 6  013 Notificaciones y panel · 014 Planes y admin  v0.2┘
Fase 7  015 Retención · 016 Sello BFA
Fase 8  017 Infraestructura y despliegue en AWS          v0.3
Fase 9  018 Cierre: usabilidad, QI, documentación final  v1.0
```

| Fase | N.° | Funcionalidad | Requisitos | Resultado verificable |
|---|---|---|---|---|
| 0 | — | Preparación del entorno | — | Herramientas instaladas, repositorio clonado, ramas `main` y `desarrollo` creadas |
| 1 | 001 | Esqueleto caminante | RNF17 – RNF22 | `docker compose up` levanta los servicios; el frontend muestra "API conectada"; la integración continua pasa en verde |
| 2 | 002 | Cuentas y sesión | RF01 – RF09 | Registro, verificación de correo, inicio y cierre de sesión, recuperación de contraseña, perfil |
| 2 | 003 | Auditoría | RNF06 | Cada acción relevante queda registrada |
| 3 | 004 | Organizaciones e invitaciones | RF10 – RF18 | Crear organización, invitar por correo, aceptar, abandonar |
| 3 | 005 | Casos y permisos | RF23 – RF33 | Crear, buscar, editar, compartir, transferir, cerrar, archivar y eliminar casos |
| 4 | 006 | Imágenes | RF34 – RF36 | Carga con validación del formato real, huella SHA-256 y almacenamiento S3 |
| 4 | 007 | Motor de análisis y capa 1 | RF38, RF39, RF43, RF46 | Botón "Analizar", cola en segundo plano, progreso y resultado de metadatos |
| 4 | 008 | Informe PDF e historial | RF44, RF45 | Descarga del PDF con la capa 1 → **versión v0.1** |
| 5 | 009 | Capa 2: C2PA | RF40 | Verificación de manifiesto y firma |
| 5 | 011 | Capa 3: ELA | RF41 | Mapa ELA por bloques en el informe |
| — | 010 | Red neuronal (pista paralela) | RNF24 | Modelo entrenado, evaluado y exportado a ONNX |
| 5 | 012 | Capa 4: ONNX | RF42 | Probabilidad de imagen sintética en el informe |
| 6 | 013 | Notificaciones y panel | RF47, RF48 | Correos por evento y panel principal |
| 6 | 014 | Planes y administración | RF19 – RF22 | Límites por plan y tablero del Administrador → **versión v0.2** |
| 7 | 015 | Retención de datos | RF49 – RF51 | Destrucción automática, aviso y prórroga |
| 7 | 016 | Sello de tiempo BFA | RF37 | Huella registrada en Blockchain Federal Argentina |
| 8 | 017 | Infraestructura y despliegue | RNF02, RNF03, RNF15, RNF22 | Plataforma en AWS con dominio y TLS → **versión v0.3** |
| 9 | 018 | Cierre del proyecto | RNF10, RNF11, RNF19 | Pruebas de usabilidad, medición del QI, documentación final → **versión v1.0** |

> Respecto de la numeración inicial de `docs/funcionalidades/README.md`, se reordenó para obtener antes un flujo completo: el informe PDF pasa a la 008 (antes 012) y se agrega la 018 de cierre.

## 3. Ciclo de trabajo de cada funcionalidad

Todas las funcionalidades siguen los mismos pasos. El asistente guía cada uno.

| Paso | Qué se hace | Quién | Commit típico |
|---|---|---|---|
| 1 | Crear la rama desde `desarrollo`: `git switch desarrollo && git pull && git switch -c funcionalidad/NNN-nombre` | Autora | — |
| 2 | `/especificar`: el asistente redacta `especificacion.md`; la autora lo revisa, lo crea y lo confirma | Ambas | `documentacion(NNN): agregar especificacion` |
| 3 | `/planificar`: diseño técnico (capas, contratos, datos, bibliotecas) | Ambas | `documentacion(NNN): agregar plan tecnico` |
| 4 | `/tareas`: lista de pasos ejecutables | Ambas | `documentacion(NNN): agregar tareas` |
| 5 | Implementación tarea por tarea: el asistente entrega cada archivo documentado; la autora lo crea, lo ejecuta y hace el commit | Ambas | `funcionalidad(...)`, `pruebas(...)` |
| 6 | Verificación: pruebas, flake8, pylint, cobertura, ESLint y prueba manual en el navegador | Autora | — |
| 7 | Bitácora y ADR (si hubo decisiones) | Ambas | `documentacion(bitacora): registrar funcionalidad NNN` |
| 8 | Pull Request hacia `desarrollo`, revisión de la integración continua y *merge* | Autora | — |

Al alcanzar un hito (v0.1, v0.2, v0.3, v1.0) se abre un Pull Request de `desarrollo` hacia `main` y se crea la etiqueta de versión:

```bash
git switch main && git pull
git tag -a v0.1 -m "Primer flujo completo: casos, imagenes, metadatos e informe"
git push origin v0.1
```

## 4. Hitos para mostrar a los tutores

| Versión | Qué se puede demostrar |
|---|---|
| v0.1 | Una persona se registra, crea un caso, carga imágenes, las analiza y descarga un informe PDF con la capa de metadatos. |
| v0.2 | Las cuatro capas, organizaciones con casos compartidos, correos, panel y planes. |
| v0.3 | La plataforma publicada en AWS con dominio y HTTPS. |
| v1.0 | Producto final con retención, sello de tiempo, pruebas de usabilidad y métricas de calidad. |

## 5. Estado

El estado de cada funcionalidad se actualiza en [docs/funcionalidades/README.md](../funcionalidades/README.md) y cada avance queda registrado en la [bitácora](../bitacora/).
