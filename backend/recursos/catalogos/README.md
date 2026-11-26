# Catálogos

## `aseguradoras_ssn.csv`

Aseguradoras habilitadas en la Argentina, usadas para validar la empresa al registrar una aseguradora (funcionalidad 021, CP-18).

- **Fuente**: Superintendencia de Seguros de la Nación (SSN), conjunto de datos abiertos «Entidades aseguradoras y reaseguradoras activas» en [datos.gob.ar](https://datos.gob.ar/dataset/entidades-aseguradoras-y-reaseguradoras). Lo aportó la autora el 2026-10-16; se actualizó desde la fuente el 2026-11-26 (versión de la SSN del 2026-10-26).
- **Licencia**: Creative Commons Atribución 4.0 (CC-BY-4.0), según el portal de datos abiertos.
- **Transformación**: se quitaron las 140 reaseguradoras ("Reaseg. Admitida" y "Reaseg. Local"), porque no gestionan siniestros de asegurados (ver CP-18), y se conservaron solo las columnas que usa la plataforma. Quedan 192 aseguradoras, todas argentinas y con CUIT único.
- **Columnas**: `cia_id` (registro de la entidad ante la SSN), `cia_denominacion`, `cia_cuit` y `cia_actividad_principal`.
- **Actualización automática (funcionalidad 052)**: un temporizador semanal (`flask catalogos actualizar-aseguradoras`) baja la versión vigente, le aplica la misma transformación, la valida y la guarda en `CARPETA_CATALOGOS`, fuera de la carpeta de la versión. La plataforma usa esa copia; este archivo queda como punto de partida y se puede actualizar de vez en cuando con el mismo comando. Las organizaciones ya registradas guardan su CUIT, así que no dependen de que la empresa siga en el archivo; si deja de figurar o la SSN anota una revocación, se avisa al Administrador.
