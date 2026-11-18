# 044 · Perfiles de la portada y verificación de identidad simulada en producción

**Estado**: implementada (2026-11-16). **Rama**: `funcionalidad/044-portada-y-identidad`. **Pedido**: la autora, con una captura de producción.

## Problema

- En la portada, las tarjetas de «Abogados y estudios» y «Aseguradoras» flotaban entre el encabezado y «Qué miramos»: más angostas que el resto, sin título y pegadas a la sección siguiente.
- En producción no aparecía la verificación de identidad simulada de las aseguradoras, a diferencia del cobro simulado con Cresium: la variable `verificacion_identidad` valía `desactivado` por defecto.
- La autora informó que una aseguradora registrada no llegaba al Administrador.

## Alcance

- Perfiles en una banda gris propia, con título a la izquierda («Para quién es · Una plataforma, dos rubros») y alineada con «Qué miramos». Se mostraron dos propuestas; la autora eligió la A y pidió menos cajas: los perfiles quedan como dos columnas abiertas separadas por una línea, con el enlace como botón.
- `verificacion_identidad` pasa a `simulado` por defecto en Terraform.
- Reproducción del registro de una aseguradora con la configuración de producción.

## Criterios de aceptación

- [x] **CA1**: La sección de perfiles queda alineada con «Qué miramos», con título y separada por el fondo; en el celular, título y perfiles en una columna.
- [x] **CA2**: Sensor de diseño, sensor de accesibilidad, sensor de teclado y recorridos del abogado (pc y celular) sin problemas.
- [x] **CA3**: Con `verificacion_identidad` sin definir en `terraform.tfvars`, producción usa el modo simulado.
- [x] **CA4**: Con la configuración de producción, una aseguradora que paga queda pendiente, al Administrador le llega el correo, la ve en Administración y la aprueba (recorrido de la aseguradora en local).
