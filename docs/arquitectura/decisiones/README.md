# Registros de decisiones de arquitectura (ADR)

Un ADR (*Architecture Decision Record*) documenta una decisión de arquitectura relevante: su contexto, las alternativas evaluadas, la decisión tomada y sus consecuencias. Permite entender **por qué** el sistema es como es, y no solo **cómo** es.

## Reglas

- Un archivo por decisión: `NNNN-titulo-corto.md`, numeración correlativa.
- Una decisión aceptada no se edita: si cambia, se crea un ADR nuevo que la **reemplaza** y el anterior pasa a estado *Reemplazada por ADR-NNNN*.
- Se usa la plantilla [plantilla.md](plantilla.md).

## Índice

| ADR | Decisión | Estado |
|---|---|---|
| [0001](0001-monorepositorio.md) | Monorepositorio con backend, frontend, red neuronal e infraestructura | Aceptada |
| [0002](0002-react-y-api-rest.md) | Interfaz en React y backend como API REST | Aceptada |
| [0003](0003-sesion-con-cookies.md) | Autenticación con sesión en cookie en lugar de JWT | Aceptada |
| [0004](0004-procesamiento-asincrono-rq.md) | Procesamiento de análisis en segundo plano con RQ y Redis | Aceptada |
| [0005](0005-postgresql-en-ec2.md) | PostgreSQL en la misma instancia EC2 | Propuesta |
| [0006](0006-capas-de-analisis-strategy.md) | Capas de análisis como Strategy, sin puntaje global | Aceptada |
| [0007](0007-idioma-espaniol.md) | Español en código, commits y ramas | Aceptada |
| [0008](0008-migraciones-con-alembic.md) | Migraciones de esquema con Alembic | Aceptada |
| [0009](0009-desarrollo-en-wsl2.md) | Entorno de desarrollo en WSL2 con Ubuntu | Aceptada |
| [0010](0010-sesiones-en-redis-y-enlaces-firmados.md) | Sesiones del servidor en Redis y enlaces firmados sin estado | Aceptada |
| [0011](0011-auditoria-en-la-misma-transaccion.md) | Registro de auditoría en la misma transacción que la acción | Aceptada |
| [0012](0012-almacenamiento-de-imagenes-intercambiable.md) | Almacenamiento de imágenes intercambiable (S3 y carpeta local) | Aceptada |
| [0013](0013-cola-de-analisis-intercambiable.md) | Cola de análisis intercambiable (RQ, hilo y sincrónica) | Aceptada |
| [0014](0014-ciclo-de-vida-y-mlops-del-clasificador.md) | Ciclo de vida y herramientas de MLOps del clasificador | Aceptada |
| [0015](0015-arquitectura-y-contrato-de-inferencia-del-clasificador.md) | Arquitectura y contrato de inferencia del clasificador | Aceptada |
| [0016](0016-despliegue-con-terraform-y-systems-manager.md) | Despliegue con Terraform, Systems Manager y OIDC | Aceptada |
| [0017](0017-marco-normativo-y-supervision-humana.md) | Marco normativo de referencia y supervisión humana | Aceptada |
| [0018](0018-sello-de-tiempo-en-hedera.md) | Sello de tiempo en Hedera en lugar de Blockchain Federal Argentina | Aceptada |
