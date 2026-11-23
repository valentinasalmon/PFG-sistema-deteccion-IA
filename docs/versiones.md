# Versiones

Las versiones se marcan con una etiqueta de Git sobre `main` cuando se alcanza un hito de la [hoja de ruta](guias/hoja-de-ruta.md). Desde el cambio a GitHub Flow ([ADR-0023](arquitectura/decisiones/0023-flujo-de-trabajo-github-flow.md)) se publican como **GitHub Releases**, con notas armadas solas a partir de los títulos de los Pull Requests. La versión la crea la autora.

| Versión | Estado | Qué trae |
|---|---|---|
| **v0.1** | Etiquetada | Primer flujo completo: cuentas, casos, carga de imágenes con huella, capa 1 (metadatos) e informe PDF (001 a 008). |
| v0.2 | Hito alcanzado, sin etiqueta | Cuatro capas (009, 011, 012), organizaciones e invitaciones, correos, panel y planes (004, 013, 014). |
| v0.3 | Hito alcanzado, sin etiqueta | Plataforma publicada en AWS con HTTPS y despliegue automático (017). |
| **v1.0** | En preparación | Todo lo anterior, más lo que sigue. |

## Contenido de la v1.0

- **Análisis**: metadatos, C2PA, ELA y clasificador de la red neuronal (la capa 4 se activa al publicar el modelo final, 012).
- **Informe**: por rubro (legal o seguros), breve, con la huella del PDF y de cada imagen sellada en Hedera, verificación pública y dos QR (análisis detallado y verificación) (022, 023, 025, 026, 029, 039).
- **Cuentas y organizaciones**: registro por pasos con pago del plan, inicio con Google, abogados con estudio, aseguradoras del catálogo de la SSN con aprobación del Administrador y verificación de identidad, invitaciones (020, 021, 027, 032, 035, 038).
- **Carga**: desde la computadora, desde el celular por QR de un solo uso (con HEIC) y por enlace para la persona afectada (024, 038).
- **Datos personales**: retención de 5 años, baja de cuenta y copia de los datos (015, 019).
- **Interfaz**: rediseño, portada con planes, vocabulario «caso» o «siniestro» según el rubro, diseño propio en computadora y celular, accesibilidad WCAG 2.1 AA (022, 028, 033, 034, 037, 038, 041).
- **Operación y calidad**: dominio propio con DNS, DKIM y DMARC por Terraform, revisión de seguridad, integración continua con sensor de diseño, sensor de accesibilidad y recorridos de punta a punta, Índice de Calidad (017, 018, 030, 036, 039, 040, 041).

## Antes de etiquetar la v1.0

- [ ] Dominio `evidentiaa.com.ar` funcionando con HTTPS y correos desde el dominio (040).
- [ ] Prueba de usabilidad hecha y QI final calculado con el SUS (018).
- [ ] Modelo final de la red neuronal publicado y capa 4 activa (012).
- [ ] Clarity quitado al terminar las pruebas (CP-37).
- [ ] Integración continua en verde sobre `main`.

Para publicarla: en GitHub, **Releases → Draft a new release**, etiqueta `v1.0` sobre `main`, **Generate release notes** y **Publish release** (paso a paso en [configurar GitHub](guias/configurar-github.md), punto 6).

Hedera se queda en la red de prueba (*testnet*), también para la defensa (decisión de la autora del 2026-11-23, CP-26). Cualquiera puede comprobar los sellos en HashScan sin depender de evidentIA (048).
