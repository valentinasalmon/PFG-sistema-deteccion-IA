# ADR-0008: Migraciones de esquema con Alembic

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RNF17, RNF22

## Contexto

El repositorio anterior creaba las tablas con `db.create_all()`, que no modifica tablas existentes ni deja historial de cambios del esquema.

## Decisión

Usar Flask-Migrate (Alembic). Cada cambio de modelo genera una migración versionada en `backend/migraciones/`, que se revisa y se incluye en el commit.

## Consecuencias

- El esquema de producción se actualiza de forma controlada y reversible.
- Las pruebas crean el esquema desde las migraciones o desde los modelos sobre una base de pruebas.
