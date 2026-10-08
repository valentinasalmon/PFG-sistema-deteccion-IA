# 2026-10-08 — Especificación inicial y estructura del repositorio

## Qué se hizo

1. Se instalaron skills de apoyo para el asistente de IA: diseño de interfaces (`ui-ux-pro-max`), revisión de código (`code-review`), análisis crítico (`the-fool`), diagramas (`excalidraw-diagram-generator`), diseño de módulos (`codebase-design`), PostgreSQL (`postgresql-optimization`) y `using-superpowers`.
2. Se relevaron los requisitos con la autora y se redactó la especificación general en `docs/especificacion/`: visión y alcance, 35 reglas de negocio, 51 requisitos funcionales, 24 no funcionales, 32 casos de uso y 16 cuestiones abiertas.
3. Se analizó el repositorio anterior (TIF) y se decidió qué reutilizar ([análisis](../arquitectura/reutilizacion-repositorio-tif.md)).
4. Se creó la estructura completa de carpetas del monorepositorio ([mapa](../arquitectura/estructura-del-repositorio.md)).
5. Se armó el arnés del proyecto: `CLAUDE.md`, la constitución, los comandos `/especificar`, `/planificar` y `/tareas`, y las plantillas de funcionalidades.
6. Se registraron las primeras ocho decisiones de arquitectura.

## Decisiones tomadas

- Monorepositorio ([ADR-0001](../arquitectura/decisiones/0001-monorepositorio.md)).
- React con API REST; Jinja2 solo para correos y PDF ([ADR-0002](../arquitectura/decisiones/0002-react-y-api-rest.md)).
- Sesión en cookie con Flask-Login y CSRF ([ADR-0003](../arquitectura/decisiones/0003-sesion-con-cookies.md)).
- Análisis en segundo plano con RQ y Redis ([ADR-0004](../arquitectura/decisiones/0004-procesamiento-asincrono-rq.md)).
- PostgreSQL en la EC2, propuesta ([ADR-0005](../arquitectura/decisiones/0005-postgresql-en-ec2.md)).
- Capas como Strategy y sin puntaje global ([ADR-0006](../arquitectura/decisiones/0006-capas-de-analisis-strategy.md)).
- Todo en español, incluidos los tipos de commit ([ADR-0007](../arquitectura/decisiones/0007-idioma-espaniol.md)).
- Migraciones con Alembic ([ADR-0008](../arquitectura/decisiones/0008-migraciones-con-alembic.md)).
- Modelo de ramas `main` / `desarrollo` / `funcionalidad/*` ([flujo de trabajo](../guias/flujo-de-trabajo.md)).
- Modelo de negocio: espacio personal gratuito sin compartir; organizaciones con planes pagos.

## Tecnologías incorporadas

Ninguna todavía en código. Quedan definidas en los ADR.

## Pendientes

- Validar con los tutores las cuestiones abiertas (`docs/especificacion/06-cuestiones-abiertas.md`).
- Funcionalidad 001: base del proyecto (configuración, calidad e integración continua).
- Verificar qué lista de confianza C2PA reconoce a los firmantes de OpenAI y Google.
