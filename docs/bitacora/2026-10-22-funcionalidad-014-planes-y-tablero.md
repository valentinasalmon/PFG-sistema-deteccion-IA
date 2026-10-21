# 2026-10-22 — Funcionalidad 014: planes, pago simulado y tablero

**Rama**: `funcionalidad/014-planes-y-tablero`. Sale de `funcionalidad/022-rediseno-interfaz`, porque usa el menú lateral y los estilos nuevos. Hay que integrarla después de la 013 y la 022.

## Qué se hizo

- **Planes**:
  - cada espacio ve su plan y su consumo del mes;
  - el Referente cambia de plan con un pago simulado: se aplica de verdad, no se cobra nada y queda auditado;
  - el límite mensual de análisis se controla al pedir un análisis.
- **Tablero del Administrador**:
  - indicadores, análisis y altas por mes, distribuciones de casos, organizaciones y cuentas, con rango de fechas;
  - listados de cuentas y organizaciones con búsqueda y paginado, de solo lectura.
- **Pruebas**: 10 de integración en el backend y 2 nuevas en el frontend.

## Decisiones

- Los precios quedan como «[PRECIO A DEFINIR]» hasta que la autora los fije en el modelo de negocio.
- Los límites siguen en la configuración y no en la base: no hace falta una migración y cumple RF19 CA3.

## Pendiente

- El límite de almacenamiento por plan (RF19) no se controla: el MVP no mide el espacio usado.
