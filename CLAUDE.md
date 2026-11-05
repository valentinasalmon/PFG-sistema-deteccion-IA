# Instrucciones para agentes de IA

Este archivo forma parte del **arnés** del proyecto: define cómo debe trabajar cualquier agente de IA (Claude Code u otro) dentro de este repositorio. Las reglas de aquí tienen prioridad sobre los hábitos por defecto del agente.

El arnés completo (guías, sensores, memoria y persona en el circuito) está descripto en [docs/arnes/README.md](docs/arnes/README.md). Algunas reglas de este archivo **se hacen cumplir solas** con los ganchos de `.claude/hooks/` (configurados en `.claude/settings.json`): si un gancho bloquea una acción, no se busca otra forma de hacerla; se respeta el motivo.

## Antes de hacer cualquier cosa

1. Leer [docs/constitucion.md](docs/constitucion.md): principios no negociables.
2. Leer la especificación relevante en [docs/especificacion/](docs/especificacion/) y, si existe, la carpeta de la funcionalidad en [docs/funcionalidades/](docs/funcionalidades/).
3. Si el pedido no tiene especificación, **no implementar**: proponer primero la especificación con `/especificar`.
4. Atender el aviso de **estado del arnés** que aparece al iniciar la sesión (gancho `verificar_arnes.py`): lo que esté desactualizado y le corresponda al agente se corrige en la misma sesión.

## El arnés se revisa solo y mejora siempre

Pedido de la autora, 2026-11-05: el arnés trabaja todo el tiempo, se mejora día a día y distribuye la información de manera adecuada.

- **Lo declarado tiene que ser verdad.** Ningún documento afirma algo que el repositorio no cumpla: números, estados, índices, enlaces, comandos y controles. `verificar_arnes.py` lo comprueba al iniciar cada sesión, al cerrar cada etapa y en la integración continua (con errores, no se integra).
- **Nada se da por verificado sin haberlo corrido.** Si un control no se pudo ejecutar (por ejemplo, falta una herramienta o el acceso a un servicio), se informa como «no verificado».
- **Cada error repetido deja un control nuevo.** Si algo falla dos veces por la misma causa, se propone la regla, el comando, el gancho o el control que lo evite, y se anota en el registro de cambios del arnés.
- **Revisión periódica**: `/revisar-arnes` al menos una vez por semana y siempre que el aviso de inicio de sesión muestre problemas.
- **El agente no debilita controles por su cuenta**: puede agregar controles con sus pruebas; cambiar o quitar uno existente queda como propuesta para la autora en `docs/arnes/`.

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
- **Nunca** subir secretos, archivos `.env`, imágenes de casos reales ni modelos entrenados al repositorio. El gancho `proteger_secretos.py` bloquea leer, editar o usar en un comando `.env`, `terraform.tfvars`, `backend.hcl` y el estado de Terraform.
- **Integraciones externas** (Hedera, Cresium, Google, AWS y las que vengan): no se dan por terminadas con las pruebas automáticas solas. Se prueban contra el servicio real (o la autora lo hace, con una guía) y su estado se ve en la página `/estado` cuando corresponde.

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

**Ramas y Pull Requests** (política de la funcionalidad 039): una funcionalidad, una rama, un Pull Request; las tandas o etapas de una funcionalidad van en su misma rama; el seguimiento viaja en el mismo Pull Request que el código; para traer `desarrollo` a una rama propia se usa `rebase`; al integrar, la rama se borra (`infraestructura/scripts/limpiar_ramas.sh`) y cada paso a `main` se etiqueta.

## Documentación obligatoria al cerrar una etapa

El comando `/cerrar-etapa` recorre estos pasos en orden.

- **Red neuronal** (pedido de la autora, 2026-10-30): todo cambio en la red neuronal (código de `red_neuronal/`, configuración, datos, cuadernos, entrenamientos, resultados o decisiones) actualiza en el mismo commit el capítulo que corresponde de [docs/red-neuronal/](docs/red-neuronal/README.md). Cada corrida de entrenamiento se registra en su capítulo 11. Esa carpeta tiene que alcanzar por sí sola para entender la red de punta a punta.

- Agregar una entrada en [docs/bitacora/](docs/bitacora/) con lo realizado, las decisiones y lo pendiente.
- Si se tomó una decisión de arquitectura, registrarla como ADR en [docs/arquitectura/decisiones/](docs/arquitectura/decisiones/).
- Agregar a [docs/informe-final/insumos.md](docs/informe-final/insumos.md) todo hallazgo, investigación, problema o decisión que deba quedar en el informe final del proyecto (pedido de la autora, 2026-10-25). Las investigaciones van completas en [docs/investigacion/](docs/investigacion/).
- Si se cambió una regla, un comando, un gancho o un control del arnés, registrarlo con su motivo en [docs/arnes/registro-de-cambios.md](docs/arnes/registro-de-cambios.md).
- **Actualizar el tablero de Trello sin esperar a que se pida** (pedido de la autora, 2026-10-29): al terminar cualquier trabajo, mover las tarjetas afectadas y agregar las que falten, siguiendo [docs/guias/tablero-trello.md](docs/guias/tablero-trello.md).

## Comandos del flujo guiado por especificaciones

| Comando | Qué hace |
|---|---|
| `/especificar <descripción>` | Crea `docs/funcionalidades/NNN-nombre/especificacion.md` |
| `/planificar [NNN]` | Crea el `plan.md` técnico de la funcionalidad |
| `/tareas [NNN]` | Crea el `tareas.md` con los pasos ejecutables y los implementa |
| `/cerrar-etapa` | Calidad, bitácora, seguimiento, decisiones, insumos, registro del arnés y Trello |
| `/revisar-arnes` | Verifica que el arnés funcione como declara, pone al día su documentación y propone mejoras |
