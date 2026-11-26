# 2026-11-26 · Catálogo de aseguradoras de la SSN, actualizado solo (052)

## Qué se hizo

- Tarea semanal que baja de datos.gob.ar el CSV vigente de entidades activas de la SSN, lo transforma igual que el original, lo valida y lo aplica si cambió.
- La copia actualizada se guarda fuera de las versiones (`/opt/plataforma/datos/catalogos`). Todos los procesos la ven sin reiniciarse, porque el catálogo se relee cuando cambia la fecha del archivo.
- Correo a los Administradores con altas, bajas, cambios y revocaciones, y entrada de auditoría.
- Fila en `/estado`.
- El archivo del repositorio quedó al día con la versión de la SSN del 2026-10-26.

## Decisiones tomadas

- **Se consulta la API del portal (CKAN) y no una dirección fija del CSV**: si la SSN publica el archivo en otro lugar, la tarea lo encuentra igual.
- **Una vez por semana**: la SSN actualiza el conjunto de datos cada pocos meses. Semanal alcanza y no carga al portal.
- **Validar antes de aplicar, y no aplicar una lista mucho más corta sin una persona**: un archivo roto no puede dejar a nadie sin poder registrarse.
- **Archivo y no tabla en la base**: son ~200 filas que se reemplazan enteras, y si se pierde se vuelve a bajar. Un archivo con escritura atómica es más simple y no necesita migración.
- **Las bajas no desactivan organizaciones solas**: lo decide el Administrador con el aviso (persona en el circuito).

## Hallazgo

En la primera prueba contra el portal real aparecieron 4 cambios desde el 2026-10-16:

- **2 revocaciones en trámite** que la SSN anota en la denominación:
  - PRODUCTORES DE FRUTAS ARGENTINAS («Revocación autorización para operar no firme RESOL-2026-443-APN-SSN#MEC»);
  - SOCIAL SAN JUAN SEGUROS DE PERSONAS (RESOL-2026-369).
- **2 cambios de denominación ya inscriptos**: Serena y La Palabra.

Por eso el servicio detecta la palabra «revocación» y la destaca.

## Problemas encontrados y cómo se resolvieron

- El gancho `proteger_secretos.py` bloqueó un comando de la terminal que escribía la unidad de systemd. Ese comando nombra la ruta del archivo de entorno del servidor, como las demás unidades; no lee ningún secreto.
  - **Cómo se resolvió**: la unidad se escribió con la herramienta de archivos. El caso ya está descripto en la propuesta pendiente `docs/arnes/propuesta-ajuste-gancho-secretos.md`.
- El portal duplicaba espacios en una actividad («Seguros  Gen.-ART»): se normalizan.

## Pendientes

- Ver el temporizador en producción después de integrar (052 CA6).
