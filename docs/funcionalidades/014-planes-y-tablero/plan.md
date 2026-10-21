# Plan técnico · 014

## Backend

- **Repositorio de estadísticas** (`repositorios/repositorio_estadisticas.py`):
  - consultas agregadas;
  - las series por mes se agrupan en Python, para que anden igual en PostgreSQL y en SQLite (pruebas);
  - cuenta los análisis del mes de un espacio: el de una organización, o el personal por su Responsable.
- **`ServicioPlanes`**:
  - límites del caso;
  - control del límite mensual, que `ServicioAnalisis.solicitar` usa antes de crear el análisis;
  - plan y consumo;
  - cambio de plan con pago simulado y auditoría.
- **`ServicioAdministracion`**: tablero y listados, solo para el rol Administrador.
- **Rutas**:
  - `GET /api/administracion/tablero`, `GET /api/administracion/usuarios` y `GET /api/administracion/organizaciones`;
  - `GET` y `POST /api/organizaciones/<id>/plan`;
  - `GET /api/perfil/plan`.
- **Configuración**: `PLANES[...]["analisis_mes"]`, `PLAN_PERSONAL["analisis_mes"]` y `precio` = «[PRECIO A DEFINIR]».

## Frontend

- **Administración**: tablero con 4 indicadores, gráficos por mes (columnas con el valor escrito) y distribuciones en barras, rango de fechas, pendientes de aprobación y listados con selector Cuentas/Organizaciones.
- **`SeccionPlan`**: barras de consumo (`role="meter"`), «Cambiar de plan» con tarjetas de plan y recuadro «Pago simulado». La usan la pantalla de la organización y «Mi perfil» (plan personal).

## Decisiones

- **Sin tablas nuevas**: el plan sigue en `organizaciones.plan` y los límites en la configuración, como pide RF19 CA3, sin migración.
- **Período**: el consumo es por mes calendario y se renueva el día 1. Es lo más fácil de explicar a la persona usuaria.
