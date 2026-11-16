# Flujo de trabajo

Guía de cómo se trabaja en el repositorio: ramas, commits, integración de cambios y uso del asistente de IA.

## 1. Modelo de ramas

Decisión del 2026-11-16 (reemplaza al modelo de una rama por funcionalidad o corrección). Con un agente de IA trabajando todos los días, ese modelo producía decenas de ramas y Pull Requests chicos que no contaban nada; ramas permanentes por área, en cambio, se desincronizan de `desarrollo`. El punto medio es el de la práctica habitual: **ramas cortas, una por objetivo, agrupadas por área**.

```
main ──────────────●──────────────────────●──────   producción (se despliega sola) y etiquetas v1.0...
                    \                    /
desarrollo ──────────●──────●────●───────●───────   integración
                      \    /      \    /
interfaz/calidad-visual ●──●        \  /            una rama por objetivo, con el área adelante
                     hedera/mainnet  ●──●
```

| Rama | Para qué | Se crea desde | Se integra en |
|---|---|---|---|
| `main` | Producción: cada fusión se despliega en AWS. Lleva las etiquetas de versión. | — | — |
| `desarrollo` | Integración de los temas terminados y probados. | `main` | `main` |
| `<área>/<objetivo>` | Un objetivo de un área. Se cierra al integrarse. | `desarrollo` | `desarrollo` |

| Área | Qué abarca |
|---|---|
| `interfaz` | Pantallas, portada, diseño, accesibilidad, sensores visuales |
| `plataforma` | Funcionalidades del backend y del frontend: casos, análisis, informes, cuentas, organizaciones |
| `integraciones` | Servicios externos: Google, Identik, Cresium, correo |
| `hedera` | Sello de tiempo, verificación del informe, red real |
| `infraestructura` | AWS, Terraform, dominio, integración continua, despliegue |
| `documentacion` | Informe final, guías, decisiones (ADR) |
| `red-neuronal` | Clasificador de la capa 4 |

Reglas:

- **Un Pull Request por objetivo.** Todo lo del objetivo se acumula en su rama mientras el Pull Request no esté integrado. Un arreglo chico no abre rama propia: va a la rama abierta del tema.
- **Las ramas son cortas.** Integrada la rama, se guarda como etiqueta `archivo/<área>/<nombre>` y se borra: la lista de ramas muestra solo el trabajo en curso, y la historia completa sigue en las etiquetas y en los Pull Requests.
- El número `NNN` sigue identificando la carpeta de la especificación en `docs/funcionalidades/`.
- El [mapa de ramas](mapa-de-ramas.md) agrupa por área todas las ramas del proyecto, con sus Pull Requests: es la trazabilidad requisito → especificación → rama → Pull Request → versión.

Comandos habituales:

```bash
# empezar un objetivo
git switch desarrollo
git pull
git switch -c interfaz/calidad-visual

# guardar avances
git add ruta/al/archivo.py
git commit -m "funcionalidad(interfaz): sensor de composición"
git push -u origin interfaz/calidad-visual

# al terminar el objetivo: un Pull Request de interfaz/calidad-visual hacia desarrollo

# al integrarse: archivarla como etiqueta y borrar la rama
git tag archivo/interfaz/calidad-visual origin/interfaz/calidad-visual
git push origin archivo/interfaz/calidad-visual
git push origin --delete interfaz/calidad-visual
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

1. La rama pasa la integración continua (lint, pruebas, cobertura y commits).
2. La descripción indica la funcionalidad, los requisitos que realiza y cómo se verificó.
3. Se revisan los criterios de aceptación de la especificación.
4. Se integra con *merge* (se conservan los commits) y la rama se archiva como etiqueta `archivo/<área>/<nombre>`.

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
