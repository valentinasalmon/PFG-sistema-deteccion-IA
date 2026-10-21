# Plan técnico · 016

- **`integraciones/sello_tiempo.py`**:
  - `SelladorBFA`: servicio Sello de Tiempo 2.0 de BFA en `https://tsa2.buenosaires.gob.ar`, el mismo que usa `https://bfa.ar/sello2`. `POST /stamp` con `{"hashes": [huella]}` pide el sello; `GET /verify/<huella>` devuelve `{stamped, stamps}` con el bloque y la fecha. No hay recibo aparte: la huella identifica el sello. Usa `urllib`, sin dependencias nuevas, con un tiempo de espera de 10 s. (Corregido el 2026-10-22: la primera versión apuntaba a `tsa.bfa.ar`, que no existe.)
  - `SelladorSimulado` y `crear_sellador(config)`.
- **Modelo**: columnas `sello_*` en `imagenes` (migración `e5a1f0c3b016`).
- **`ServicioSellos`**:
  - `intentar(imagen)` avanza un paso y nunca lanza;
  - `procesar()` corre sobre las imágenes pendientes o enviadas;
  - 96 intentos como máximo; audita `imagen.sello` al confirmar.
- **Carga**: `ServicioImagenes.cargar` marca la imagen `pendiente` y hace el primer intento en el momento.
- **Tarea**: `flask --app wsgi sellos procesar`, que el servidor ejecuta cada 15 minutos con `plataforma-sellos.timer`.
- **Configuración**: `SELLO_TIEMPO` (`bfa`, `simulado` o `desactivado`) y `URL_SELLO_BFA`.
  - Desarrollo y pruebas: `simulado`.
  - Producción: la variable de Terraform `sello_tiempo`, `desactivado` por defecto, que se guarda como parámetro en Parameter Store.
- **Informe**: la fila «Sello de tiempo en Blockchain Federal Argentina» dice si la imagen está sellada (con fecha y bloque), pendiente, fallida o simulada.

## Por qué el modo real arranca desactivado

Desde el entorno de desarrollo del agente no se llega a BFA, y no está comprobado que el servidor de AWS en Irlanda llegue. El 2026-10-22 el servicio respondía 404 en `/stamp` y `/verify`, también desde la propia página de BFA (ver CP-25). La autora lo prueba primero y después lo activa: los pasos están en la bitácora y en la guía de despliegue.
