# 2026-11-11 — Segunda revisión del informe final

## Qué se hizo

- Revisión completa del documento de Google Docs y de los catorce anexos de la carpeta de Drive, con `/revisar-informe` (`docs/informe-final/revisiones/2026-11-11.md`, que reemplaza a la del 5/11).
- Integración de `desarrollo` y regeneración de los diagramas: la Figura 12 (componentes) muestra la capa 4 y el modelo completo suma las columnas nuevas de `enlaces_carga`. `verificar` confirma que coinciden con el código.
- Actualización de `hechos-del-sistema.md` (capa 4 integrada; cifras al 11/11: 395 commits, 92,2 % con coautoría de IA, 77 pull requests, 810 pruebas) y de `estado-del-informe.md`.

## Hallazgos

- El documento no cambió desde el 5/11: todas las correcciones siguen pendientes.
- Los Anexos F, G y H del Drive están desactualizados (32 casos de uso, BFA, retención de 2 años, RF hasta 51, bitácora hasta el 8/10) y contradicen al sistema; se recomienda reemplazarlos por el repositorio. Hay dos anexos «B», el K enlaza un diagrama obsoleto y el M no tiene evidencia.
- OpenID Foundation y Hedera están en la bibliografía pero no se citan en el texto.
- El entrenamiento del 5/11 cumple los dos criterios de CP-07 (AUC 0,961; F1 0,904): el informe puede cerrar el valor del OE4.

## Pendiente

- La autora aplica las correcciones en el documento; decisiones CP-34, CP-37 y CP-38; validaciones con personas.

## Diagramas con aspecto de hechos a mano (pedido de la autora)

- **Componentes (08):** de arriba hacia abajo, una sola dependencia de los servicios hacia el paquete de integraciones, interfaces al pie de cada paquete (la línea ya no pisa el nombre) y grilla de tres columnas.
- **Despliegue (07):** pasa de PlantUML a un SVG con posiciones fijas (`backend/herramientas/diagrama_despliegue.py`). Rutas ortogonales sin cruces, servicios de AWS en una columna y sistemas externos en otra. Los datos siguen saliendo de Terraform, systemd y Nginx, y `verificar` los comprueba en el SVG.
- **Casos de uso (09):** actores repartidos a los dos lados del sistema y casos ordenados por actor: el de imágenes y análisis pasa de una docena de cruces a ninguno.
- **Modelo de datos (04) y secuencia (05):** líneas rectas en lugar de ortogonales superpuestas y estilo en blanco y negro.
- Decisión: no se usó FigJam (Figma) porque no admite notación UML de despliegue, componentes ni casos de uso; sí puede servir para versiones editables de la secuencia, el modelo de datos o el cronograma si la autora lo pide.
