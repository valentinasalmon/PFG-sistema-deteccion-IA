# 041 · Accesibilidad y materiales del cierre al día

**Estado**: implementada (2026-11-16). **Rama**: `funcionalidad/041-accesibilidad`. **Pedido**: pendientes del cierre (018) que quedaban del lado del agente mientras se propaga el dominio.

## Problema

- RNF11 pide WCAG 2.1 AA, pero la revisión con herramientas automáticas sobre la versión final estaba pendiente desde la 018.
- El protocolo de la prueba de usabilidad describía la plataforma anterior a la 037 (sin «siniestros», sin QR de un solo uso ni el QR del análisis detallado, sin el dominio).
- La medición del Índice de Calidad era del 2026-11-04.

## Alcance

- Sensor de accesibilidad (`frontend/e2e/accesibilidad.cjs`) con axe-core, en computadora y celular, sumado al trabajo «Interfaz» de la integración continua.
- Corrección de lo que encuentre.
- Protocolo de usabilidad al día (producción en `evidentiaa.com.ar`, correos de participantes en SES, tareas T2, T6, T8 y T9 nueva).
- Segunda medición del QI.

## Resultado de la revisión

14 pantallas en computadora y celular, más un caso en sus cuatro etapas y Administración: **dos infracciones serias de contraste**, ninguna otra.

| Dónde | Problema | Corrección |
|---|---|---|
| Iniciales de la cuenta en el menú (todas las pantallas con sesión, en computadora) | Blanco sobre lima: 1,9:1 | Texto oscuro (`--tinta`) |
| Portada, tarjeta «Aseguradoras» | Etiqueta verde oscura sobre el fondo bosque: 2,4:1 | Etiqueta en lima, como los demás acentos sobre fondo oscuro |

## Criterios de aceptación

- [x] **CA1**: El sensor de accesibilidad termina sin infracciones serias ni críticas en todas las pantallas revisadas.
- [x] **CA2**: El sensor corre en el trabajo «Interfaz» de la integración continua.
- [x] **CA3**: Sensor de diseño y recorrido del abogado (pc y celular) sin problemas después de los cambios.
- [x] **CA4**: El protocolo de usabilidad describe la plataforma actual.

## Fuera de alcance

La revisión automática no reemplaza la prueba con lector de pantalla ni con teclado solo; queda para la prueba de usabilidad si hay un participante que los use.
