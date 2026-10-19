# Catálogos

## `aseguradoras_ssn.csv`

Aseguradoras habilitadas en la Argentina, usadas para validar la empresa al registrar una aseguradora (funcionalidad 021, CP-18).

- **Fuente**: Superintendencia de Seguros de la Nación (SSN), conjunto de datos abiertos "Entidades activas". Aportado por la autora el 2026-10-16.
- **Licencia**: pendiente de confirmar (los datos abiertos del Estado argentino suelen publicarse con licencia Creative Commons Atribución 4.0).
- **Transformación**: se quitaron las 140 reaseguradoras ("Reaseg. Admitida" y "Reaseg. Local"), porque no gestionan siniestros de asegurados (ver CP-18), y se conservaron solo las columnas que usa la plataforma. Quedan 192 aseguradoras, todas argentinas y con CUIT único.
- **Columnas**: `cia_id` (registro de la entidad ante la SSN), `cia_denominacion`, `cia_cuit` y `cia_actividad_principal`.
- **Actualización**: reemplazar el archivo por una versión nueva del conjunto de datos, aplicando la misma transformación. Las organizaciones ya registradas guardan su CUIT, así que no dependen de que la empresa siga en el archivo.
