# Flujo de trabajo

Guía de cómo se trabaja en el repositorio: ramas, commits, integración de cambios y uso del asistente de IA.

## 1. Modelo de ramas: GitHub Flow

**Decisión de mejora del 2026-11-16** ([ADR-0023](../arquitectura/decisiones/0023-flujo-de-trabajo-github-flow.md)). Hasta esa fecha el proyecto usó `main`, `desarrollo` y una rama por funcionalidad o corrección; con el ritmo de trabajo diario eso llevó a 72 ramas y a dos Pull Requests por cada cambio. Se pasó a GitHub Flow:

```
main ──●───────────●──────────●──────●─────────  producción: cada fusión se despliega; etiquetas v1.0, v1.1…
        \         /            \    /
interfaz/calidad-visual ●──●    hedera/mainnet ●──●   ramas cortas por objetivo, un Pull Request directo a main
```

| Rama | Para qué |
|---|---|
| `main` | Única rama permanente. Siempre en verde e igual a producción. Protegida: solo recibe Pull Requests con todas las verificaciones en verde. |
| `<área>/<objetivo>` | Un objetivo. Se crea desde `main`, vuelve a `main` con un Pull Request y GitHub la borra al integrarla. |

| Área | Qué abarca |
|---|---|
| `interfaz` | Pantallas, portada, diseño, accesibilidad, sensores visuales |
| `plataforma` | Funcionalidades del producto: casos, análisis, informes, cuentas, organizaciones |
| `integraciones` | Servicios externos: Google, Identik, Cresium, correo |
| `hedera` | Sello de tiempo, verificación del informe, red real |
| `infraestructura` | AWS, Terraform, dominio, integración continua, despliegue |
| `documentacion` | Informe final, guías, decisiones (ADR) |
| `red-neuronal` | Clasificador de la capa 4 |

Reglas:

- **Un Pull Request por objetivo.** Todo lo del objetivo se acumula en su rama mientras el Pull Request no esté integrado. Un arreglo chico no abre rama propia: va a la rama abierta del tema.
- **Fusión con *squash***: el Pull Request entra a `main` como un solo commit con su título y su número. El detalle de los commits queda en el Pull Request.
- **Nada entra a `main` sin todo en verde**: lo exige la protección de la rama ([configurar GitHub](configurar-github.md)).
- El número `NNN` sigue identificando la carpeta de la especificación en `docs/funcionalidades/`.
- Las ramas del modelo anterior se conservan como etiquetas `archivo/<área>/<nombre>`; el [mapa de ramas](mapa-de-ramas.md) las agrupa por área.
- Las ramas `claude/…` son de sesiones del agente en la nube, que solo pueden subir a su propia rama: se usan como una rama de objetivo más.
- **El seguimiento viaja con el trabajo**: la bitácora, las casillas de `tareas.md`, los estados y los insumos van en el mismo Pull Request que el código.
- **Para traer `main` a una rama propia se usa `git rebase`**, no un merge, mientras nadie más trabaje en esa rama.

Por qué se llegó acá: la funcionalidad 045 midió el proceso (2026-11-05): 353 commits y 73 Pull Requests en 18 días, 38 % de commits solo de documentación, 51 ramas sin borrar y 18 merges «traer desarrollo». Escribió una política de una funcionalidad, una rama y un Pull Request, pero en los once días siguientes no cambió nada (de 30 Pull Requests, 8 fueron pasos de `desarrollo` a `main`). La lección, que justifica el [ADR-0023](../arquitectura/decisiones/0023-flujo-de-trabajo-github-flow.md): **una regla que depende de que alguien se acuerde no se cumple; tiene que estar en la herramienta**. Por eso la protección de `main`, el *squash* y el borrado automático de ramas.

Herramientas:
- `herramientas/archivar_ramas.sh` archiva como etiqueta y borra las ramas del modelo anterior ya integradas en `main` (sin argumentos muestra qué haría).
- El verificador del arnés (`.claude/hooks/verificar_arnes.py`) avisa al iniciar cada sesión si hay ramas integradas sin borrar y si dos funcionalidades comparten número.

Comandos habituales:

```bash
# empezar un objetivo
git switch main
git pull
git switch -c interfaz/calidad-visual

# guardar avances (un commit por cambio completo)
git add ruta/al/archivo.py
git commit -m "funcionalidad(interfaz): sensor de composición"
git push -u origin interfaz/calidad-visual

# al terminar el objetivo: un Pull Request de interfaz/calidad-visual hacia main
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

Reglas (2026-11-16):

- **Un commit por cambio completo**: el código, sus pruebas y su documentación van juntos.
- **Título de 72 caracteres como máximo.**
- Nada de commits de «corrijo lo anterior»: se juntan con el anterior **antes** de subirlos. Lo ya subido no se reescribe.

Los mensajes se validan automáticamente: el gancho del arnés `revisar_commit.py` antes de crear cada commit del agente, un hook local de pre-commit y commitlint en la integración continua.

## 3. Pull Requests

1. El Pull Request va de la rama del objetivo a `main` y pasa la integración continua (lint, pruebas, cobertura, sensores, Terraform y commits).
2. La descripción indica la funcionalidad, los requisitos que realiza y cómo se verificó.
3. Se revisan los criterios de aceptación de la especificación.
4. Se integra con ***squash*** cuando todas las verificaciones están en verde (la protección de `main` no deja hacerlo antes). GitHub borra la rama sola.

## 4. Desarrollo guiado por especificaciones

Ver [docs/funcionalidades/README.md](../funcionalidades/README.md). Ninguna funcionalidad se implementa sin `especificacion.md`, `plan.md` y `tareas.md`.

## 5. Trabajo con el asistente de IA

- Desde la funcionalidad 003 el trabajo se reparte así (decisión de la autora, 2026-10-16; en la 002 y la 020 la autora escribía el código central):

  | Quién | Qué hace |
  |---|---|
  | Asistente | Todo el trabajo de cada funcionalidad: especificación, plan, tareas, código del backend y del frontend, pruebas, estilos, textos, configuración y documentación de seguimiento. Crea las ramas y sube commits propios con la línea `Co-Authored-By`. |
  | Autora | Revisión, Pull Requests e integración en `main`, y las decisiones importantes: alcance, cuestiones legales y de privacidad, cambios grandes de arquitectura y lo que deba validarse con los tutores. |

- El asistente registra en la bitácora cada decisión que toma y su justificación, para que la autora pueda revisarla y revertirla.
- Las decisiones importantes que surgen durante el trabajo se registran como cuestiones abiertas con una propuesta provisoria, sin bloquear el resto.
- Al iniciar una sesión, el asistente lee `CLAUDE.md` y la constitución.
- Comandos disponibles: `/especificar`, `/planificar`, `/tareas`, `/cerrar-etapa` y `/revisar-arnes` (ver [CLAUDE.md](../../CLAUDE.md)).
