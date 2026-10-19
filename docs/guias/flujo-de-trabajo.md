# Flujo de trabajo

Guía de cómo se trabaja en el repositorio: ramas, commits, integración de cambios y uso del asistente de IA.

## 1. Modelo de ramas

```
main ─────────────●───────────────────●──────────   versiones entregables (etiquetadas v0.1, v0.2...)
                   \                 /
desarrollo ─────────●──●──●───●──●──●─────────────   integración de funcionalidades terminadas
                        \    /  \  /
funcionalidad/005-casos  ●──●    ●       una rama por funcionalidad o corrección
```

| Rama | Para qué | Se crea desde | Se integra en |
|---|---|---|---|
| `main` | Versión estable y entregable. Protegida: solo recibe integraciones desde `desarrollo`. | — | — |
| `desarrollo` | Integración de funcionalidades terminadas y probadas. | `main` | `main` |
| `funcionalidad/NNN-nombre` | Una funcionalidad de `docs/funcionalidades/`. | `desarrollo` | `desarrollo` |
| `correccion/descripcion` | Corrección de un defecto. | `desarrollo` | `desarrollo` |
| `documentacion/descripcion` | Cambios solo de documentación. | `desarrollo` | `desarrollo` |

Comandos habituales:

```bash
# empezar una funcionalidad
git switch desarrollo
git pull
git switch -c funcionalidad/005-casos

# guardar avances
git add ruta/al/archivo.py
git commit -m "funcionalidad(casos): agregar modelo de caso"
git push -u origin funcionalidad/005-casos

# al terminar: abrir un Pull Request de funcionalidad/005-casos hacia desarrollo en GitHub
```

## 2. Mensajes de commit

Formato **Conventional Commits** con tipos en español ([ADR-0007](../arquitectura/decisiones/0007-idioma-espaniol.md)):

```
tipo(ámbito): descripción en minúscula, en infinitivo y sin punto final

Cuerpo opcional: qué cambia y por qué.

Refs: RF34, RN22
```

| Tipo | Uso |
|---|---|
| `funcionalidad` | Nueva funcionalidad |
| `correccion` | Corrección de un defecto |
| `documentacion` | Solo documentación |
| `estilo` | Formato, sin cambios de lógica |
| `refactorizacion` | Reestructuración sin cambio de comportamiento |
| `rendimiento` | Mejora de desempeño |
| `pruebas` | Agregado o corrección de pruebas |
| `construccion` | Dependencias y empaquetado |
| `integracion` | Integración continua |
| `tarea` | Mantenimiento general |
| `revertir` | Reversión de un commit |

Ámbitos sugeridos: `cuentas`, `organizaciones`, `casos`, `imagenes`, `analisis`, `metadatos`, `c2pa`, `ela`, `red-neuronal`, `informes`, `notificaciones`, `retencion`, `auditoria`, `frontend`, `infraestructura`, `especificacion`.

Ejemplos:

```
funcionalidad(casos): agregar filtro por expediente
correccion(metadatos): tolerar fechas EXIF sin segundos
documentacion(especificacion): agregar casos de uso de organizaciones
pruebas(c2pa): cubrir manifiesto con firma no confiable
```

Los mensajes se validan automáticamente (commitlint en la integración continua y un hook local de pre-commit).

## 3. Pull Requests

1. La rama pasa la integración continua (lint, pruebas, cobertura y commits).
2. La descripción indica la funcionalidad, los requisitos que realiza y cómo se verificó.
3. Se revisan los criterios de aceptación de la especificación.
4. Se integra con *merge* y se elimina la rama.

## 4. Desarrollo guiado por especificaciones

Ver [docs/funcionalidades/README.md](../funcionalidades/README.md). Ninguna funcionalidad se implementa sin `especificacion.md`, `plan.md` y `tareas.md`.

## 5. Trabajo con el asistente de IA

- Desde la funcionalidad 003 el trabajo se reparte así (decisión de la autora, 2026-10-16; en la 002 y la 020 la autora escribía el código central):

  | Quién | Qué hace |
  |---|---|
  | Asistente | Todo el trabajo de cada funcionalidad: especificación, plan, tareas, código del backend y del frontend, pruebas, estilos, textos, configuración y documentación de seguimiento. Crea las ramas y sube commits propios con la línea `Co-Authored-By`. |
  | Autora | Revisión, Pull Requests e integración en `desarrollo`, y las decisiones importantes: alcance, cuestiones legales y de privacidad, cambios grandes de arquitectura y lo que deba validarse con los tutores. |

- El asistente registra en la bitácora cada decisión que toma y su justificación, para que la autora pueda revisarla y revertirla.
- Las decisiones importantes que surgen durante el trabajo se registran como cuestiones abiertas con una propuesta provisoria, sin bloquear el resto.
- Al iniciar una sesión, el asistente lee `CLAUDE.md` y la constitución.
- Comandos disponibles: `/especificar`, `/planificar`, `/tareas`.
