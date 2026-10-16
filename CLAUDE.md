# Instrucciones para agentes de IA

Este archivo forma parte del **arnés** del proyecto: define cómo debe trabajar cualquier agente de IA (Claude Code u otro) dentro de este repositorio. Las reglas de aquí tienen prioridad sobre los hábitos por defecto del agente.

## Antes de hacer cualquier cosa

1. Leer [docs/constitucion.md](docs/constitucion.md): principios no negociables.
2. Leer la especificación relevante en [docs/especificacion/](docs/especificacion/) y, si existe, la carpeta de la funcionalidad en [docs/funcionalidades/](docs/funcionalidades/).
3. Si el pedido no tiene especificación, **no implementar**: proponer primero la especificación con `/especificar`.

## Forma de trabajo con la autora

- **Reparto del trabajo** (decisión de la autora, 2026-10-10):
  - **La autora** escribe el código central de cada funcionalidad (modelos, servicios, esquemas, rutas, seguridad, cliente de la API, contextos y pantallas), crea las ramas y abre los Pull Requests. El agente le entrega el contenido de cada archivo y verifica lo que ella sube.
  - **El agente** escribe y sube con commits propios las pruebas, los estilos, las plantillas y los textos, la configuración de herramientas y dependencias, los componentes de presentación y la documentación de seguimiento. Cada commit del agente lleva la línea `Co-Authored-By` que identifica la asistencia de IA.
  - El agente avanza de a poco: antes de cada commit avisa qué va a subir y, después, pide a la autora `git pull` antes de que continúe.
- Cada paso que hace la autora indica: qué archivo crear y dónde, su contenido completo, por qué existe, qué rama usar y el mensaje de commit sugerido.
- Ante cualquier ambigüedad, **preguntar antes de asumir**.
- **Documentación de seguimiento a cargo del agente** (decisión de la autora, 2026-10-10): la entrada de bitácora, el marcado de casillas en `tareas.md` y `especificacion.md`, el estado de cada funcionalidad y la actualización de la especificación general ante decisiones nuevas. El agente sube esos cambios en un commit propio a la rama `funcionalidad/NNN` en curso, avisa antes qué va a cambiar y pide a la autora `git pull` antes de que continúe.
- En cada mensaje se indica en qué rama debe estar la autora y si corresponde o no abrir un Pull Request.

## Reglas de código

- **Todo en español**: identificadores, comentarios, docstrings, commits, ramas y documentación. Sin tildes ni ñ en identificadores (`anio`, `contrasenia`). Se exceptúan los nombres impuestos por bibliotecas.
- **Arquitectura en capas** (backend): `rutas → servicios → repositorios → modelos`. Una capa solo depende de la inmediatamente inferior. Ver la constitución para el detalle.
- **Documentar siempre**: todo módulo, clase y función pública lleva docstring que explique qué hace, por qué y qué requisito realiza (por ejemplo, `Realiza: RF34, RN22`).
- **Nunca** emitir veredictos en textos de análisis: solo indicios y recomendación de consultar a un profesional (RN27).
- **Nunca** subir secretos, archivos `.env`, imágenes de casos reales ni modelos entrenados al repositorio.

## Calidad mínima antes de dar algo por terminado

```bash
# backend
flake8 app/ && pylint app/ && pytest --cov=app --cov-fail-under=80
# frontend
npm run lint && npm run test
```

## Commits

`tipo(ámbito): descripción` con tipos en español: `funcionalidad`, `correccion`, `documentacion`, `estilo`, `refactorizacion`, `rendimiento`, `pruebas`, `construccion`, `integracion`, `tarea`, `revertir`. Ver [docs/guias/flujo-de-trabajo.md](docs/guias/flujo-de-trabajo.md).

## Documentación obligatoria al cerrar una etapa

- Agregar una entrada en [docs/bitacora/](docs/bitacora/) con lo realizado, las decisiones y lo pendiente.
- Si se tomó una decisión de arquitectura, registrarla como ADR en [docs/arquitectura/decisiones/](docs/arquitectura/decisiones/).

## Comandos del flujo guiado por especificaciones

| Comando | Qué hace |
|---|---|
| `/especificar <descripción>` | Crea `docs/funcionalidades/NNN-nombre/especificacion.md` |
| `/planificar [NNN]` | Crea el `plan.md` técnico de la funcionalidad |
| `/tareas [NNN]` | Crea el `tareas.md` con los pasos ejecutables |
