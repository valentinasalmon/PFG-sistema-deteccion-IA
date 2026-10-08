# ADR-0005: PostgreSQL en la misma instancia EC2

- **Estado**: Propuesta (a confirmar en la etapa de infraestructura)
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RNF15, RNF22

## Contexto

La propuesta del proyecto ubica la base de datos en la misma EC2 que la aplicación. El Terraform del repositorio anterior creaba una base de datos administrada (Amazon RDS).

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| **PostgreSQL en la EC2** | Menor costo; arquitectura simple; coincide con la propuesta | Respaldos y actualizaciones a cargo propio; un único punto de falla |
| Amazon RDS | Respaldos automáticos, parches, alta disponibilidad opcional | Mayor costo mensual |

## Decisión

PostgreSQL en la EC2, con respaldo diario cifrado a S3 y vencimiento de 30 días (RNF15). Se documenta RDS como mejora futura.

## Consecuencias

- Hay que escribir y probar el script de respaldo y restauración.
- El Terraform se rehace sin RDS.
