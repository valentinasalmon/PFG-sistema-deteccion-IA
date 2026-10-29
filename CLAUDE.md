# Instrucciones para agentes de IA

Este archivo forma parte del **arnés** del proyecto: define cómo debe trabajar cualquier agente de IA (Claude Code u otro) dentro de este repositorio. Las reglas de aquí tienen prioridad sobre los hábitos por defecto del agente.

## Antes de hacer cualquier cosa

1. Leer [docs/constitucion.md](docs/constitucion.md): principios no negociables.
2. Leer la especificación relevante en [docs/especificacion/](docs/especificacion/) y, si existe, la carpeta de la funcionalidad en [docs/funcionalidades/](docs/funcionalidades/).
3. Si el pedido no tiene especificación, **no implementar**: proponer primero la especificación con `/especificar`.

## Forma de trabajo con la autora

- **Reparto del trabajo** (decisión de la autora, 2026-10-16, reemplaza la del 2026-10-10):
  - **El agente** escribe y sube con commits propios todo el trabajo de cada funcionalidad: especificación, plan, tareas, código del backend y del frontend, pruebas, estilos, textos, configuración y documentación de seguimiento. Crea las ramas `funcionalidad/NNN-nombre` desde `desarrollo`. Cada commit del agente lleva la línea `Co-Authored-By` que identifica la asistencia de IA; nunca se quita ni se oculta.
  - **La autora** revisa el trabajo, abre los Pull Requests hacia `desarrollo`, los integra y toma las decisiones importantes: alcance del producto, cuestiones legales y de privacidad, cambios de arquitectura con impacto grande y todo lo que deba validarse con los tutores.
  - El agente no pregunta por detalles que pueda resolver con la especificación y la constitución: decide, lo deja registrado en la bitácora con su justificación y avisa a la autora cuando una funcionalidad está lista para su Pull Request.
- Ante una decisión importante (ver la lista anterior), el agente no la toma: la registra como cuestión abierta en `docs/especificacion/06-cuestiones-abiertas.md` con una propuesta provisoria y sigue con lo que no dependa de ella.
- **Documentación de seguimiento a cargo del agente**: la entrada de bitácora, el marcado de casillas en `tareas.md` y `especificacion.md`, el estado de cada funcionalidad y la actualización de la especificación general ante decisiones nuevas.
- En cada mensaje se indica en qué rama debe estar la autora y si corresponde o no abrir un Pull Request.

## Reglas de código

- **Todo en español**: identificadores, comentarios, docstrings, commits, ramas y documentación. Sin tildes ni ñ en identificadores (`anio`, `contrasenia`). Se exceptúan los nombres impuestos por bibliotecas.
- **Arquitectura en capas** (backend): `rutas → servicios → repositorios → modelos`. Una capa solo depende de la inmediatamente inferior. Ver la constitución para el detalle.
- **Documentar siempre**: todo módulo, clase y función pública lleva docstring que explique qué hace, por qué y qué requisito realiza (por ejemplo, `Realiza: RF34, RN22`).
- **Nunca** emitir veredictos en textos de análisis: solo indicios y recomendación de consultar a un profesional (RN27).
- **Interfaz**: toda pantalla, correo o documento nuevo sigue la [guía de identidad visual](docs/guias/identidad-visual.md).
- **Resultados**: toda salida de análisis respeta [ADR-0017](docs/arquitectura/decisiones/0017-marco-normativo-y-supervision-humana.md): descargo de IA, persona en el circuito y umbrales publicados.
- **Nunca** subir secretos, archivos `.env`, imágenes de casos reales ni modelos entrenados al repositorio.

## Calidad mínima antes de dar algo por terminado

```bash
# backend
flake8 app/ && pylint app/ && pytest --cov=app --cov-fail-under=80
# frontend
npm run lint && npm run test
# red neuronal (desde red_neuronal/)
flake8 clasificador/ && pylint clasificador/ && pytest --cov=clasificador --cov-fail-under=80
```

## Commits

`tipo(ámbito): descripción` con tipos en español: `funcionalidad`, `correccion`, `documentacion`, `estilo`, `refactorizacion`, `rendimiento`, `pruebas`, `construccion`, `integracion`, `tarea`, `revertir`. Ver [docs/guias/flujo-de-trabajo.md](docs/guias/flujo-de-trabajo.md).

## Documentación obligatoria al cerrar una etapa

- Agregar una entrada en [docs/bitacora/](docs/bitacora/) con lo realizado, las decisiones y lo pendiente.
- Si se tomó una decisión de arquitectura, registrarla como ADR en [docs/arquitectura/decisiones/](docs/arquitectura/decisiones/).
- Agregar a [docs/informe-final/insumos.md](docs/informe-final/insumos.md) todo hallazgo, investigación, problema o decisión que deba quedar en el informe final del proyecto (pedido de la autora, 2026-10-25). Las investigaciones van completas en [docs/investigacion/](docs/investigacion/).
- **Actualizar el tablero de Trello sin esperar a que se pida** (pedido de la autora, 2026-10-29): al terminar cualquier trabajo, mover las tarjetas afectadas y agregar las que falten, siguiendo [docs/guias/tablero-trello.md](docs/guias/tablero-trello.md).

## Comandos del flujo guiado por especificaciones

| Comando | Qué hace |
|---|---|
| `/especificar <descripción>` | Crea `docs/funcionalidades/NNN-nombre/especificacion.md` |
| `/planificar [NNN]` | Crea el `plan.md` técnico de la funcionalidad |
| `/tareas [NNN]` | Crea el `tareas.md` con los pasos ejecutables |
