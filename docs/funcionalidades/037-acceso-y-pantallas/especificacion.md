# Especificación: 037 — Tamaños del acceso y mejoras de pantallas internas

- **Rama**: `funcionalidad/037-acceso-y-pantallas`
- **Estado**: En curso: acceso, paleta, flujo, vocabulario por perfil, informe y textos legales implementados; quedan 6 decisiones de la autora
- **Requisitos que realiza**: RNF10, RNF12
- **Reglas de negocio aplicadas**: RN27
- **Casos de uso**: inicio de sesión, registro y flujo del caso

## Problema

La autora revisó el inicio de sesión y el registro (2026-11-04). En computadora, los recuadros eran chicos y no se adaptaban a la pantalla: la tarjeta del inicio de sesión medía unos 370 px en una pantalla de 1440 px, y en el registro las opciones se cortaban en cuatro renglones. En el celular, todo quedaba apretado. También pidió revisar otras pantallas y proponer mejoras.

## Alcance

### Incluido
- Inicio de sesión, registro y demás páginas de acceso: tarjeta más ancha, campos de 56 px, etiquetas y títulos más grandes y más espacio entre campos. En el celular, la tarjeta ocupa todo el ancho y llega hasta el pie.
- Propuesta de mejoras de las pantallas internas, priorizada, para que la autora elija.

### Excluido
- Cambios de textos o de flujo del registro: la autora dijo que el resto «está relativamente bien».

## Criterios de aceptación

- [x] **CA1**: Dado una pantalla de 1440 px, cuando se abre el inicio de sesión, entonces la tarjeta mide 34rem (544 px) y los campos 56 px de alto.
- [x] **CA2**: Dado el registro en computadora, cuando se elige el camino, entonces las tres opciones entran sin cortar los títulos en más de dos renglones y los campos usan todo el ancho de la tarjeta.
- [x] **CA3**: Dado un celular de 390 px, cuando se abre el acceso, entonces la tarjeta ocupa todo el ancho, sin márgenes laterales, y llega hasta el pie sin franja gris.
- [x] **CA4**: Las pantallas internas usan la paleta de la portada (opción A elegida por la autora el 2026-11-04): menú verde bosque, acción lima, rubro en píldora blanca, sin buscador en la barra en computadora y pasos del caso en horizontal.
- [x] **CA5**: Una cuenta de aseguradora ve «siniestro» en lugar de «caso» en el menú, el inicio, la lista, el alta, el caso, el buscador y el informe PDF.
- [x] **CA6**: En un celular de 390 px ninguna pantalla tiene contenido cortado o fuera del ancho.
- [x] **CA7**: El informe PDF lleva el aviso de que no emite veredictos en la primera página y la escala de lectura no se corta entre páginas.
- [x] **CA8**: La política de privacidad cubre Google, los pagos, la verificación de identidad, las fotos de terceros y quién trata los datos; los términos explican la diferencia entre abogado y aseguradora.
- [x] **CA9**: Decisiones 1, 3, 4, 5 y 6 de la revisión integral aplicadas (2026-11-05).
- [ ] **CA10**: Decisión 2: el análisis en pantalla tiene un solo descargo arriba y los datos técnicos plegados.
- [x] **CA11**: El informe PDF es breve, arriba lleva una sola línea de herramienta de apoyo y enlaza con QR al análisis detallado en la plataforma.
- [ ] **CA12**: La pantalla del caso, el login (con Google), el registro y el resto de las pantallas siguen el diseño nuevo, sin elementos flotando en el celular.

Capturas del antes y el después en [`capturas/`](capturas/).
