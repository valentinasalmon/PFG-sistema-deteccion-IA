# Especificación: 033 — Portada pública (landing) con los planes

- **Rama**: `funcionalidad/033-portada`
- **Estado**: Implementada (combinación de las propuestas A y B elegida por la autora el 2026-10-29)
- **Requisitos que realiza**: RF19, RF20, RNF10
- **Reglas de negocio aplicadas**: RN01, RN27; ADR-0017
- **Casos de uso**: CU01 (registrarse)

## Problema

Quien llega a evidentIA sin cuenta ve directamente el inicio de sesión: no hay un lugar que explique qué problema resuelve la plataforma, para quién es y cuánto cuesta. La autora pidió una portada para promocionarla desde la que se elija un plan y se cree la cuenta con ese plan ya aplicado.

## Alcance

### Incluido
- Portada en `/` para quien no inició sesión (con sesión, `/` sigue siendo el Inicio) y en `/presentacion` para todos.
- Secciones, según la elección de la autora:
  - **Encabezado** (propuesta B): titular, bajada, botones y una vista de la aplicación con el análisis por capas.
  - **El problema** (propuesta A): tres tarjetas numeradas.
  - **La solución** (propuesta B): mosaico con las capas, la cadena de custodia en Hedera, el informe verificable, la carga desde el celular, el trabajo en equipo y la persona en el circuito.
  - **Para quién** (propuesta B): independientes, estudios jurídicos y aseguradoras, cada uno con su enlace al registro.
  - **Planes** (propuesta A): Personal, Básico y Profesional con los límites reales del sistema y el precio «A confirmar»; un selector «Estudio jurídico / Aseguradora» decide a qué registro lleva cada plan.
  - **Preguntas frecuentes, cierre y pie** (propuesta B).
- Cada botón de plan abre el registro con el camino y el plan elegidos (`/registro?tipo=...&plan=...`).
- Más diseño que las propuestas: animaciones suaves al aparecer, escaneo en la vista de la app y cinta de capas en movimiento, todo desactivado con «reducir movimiento».

### Excluido
- Precios reales (los define la autora).
- Contenido administrable, blog, testimonios o métricas de uso: no hay datos reales todavía.
- Formulario de contacto.

## Criterios de aceptación

- [x] **CA1**: Dado un visitante sin sesión, cuando abre `/`, entonces ve la portada; con sesión, `/` muestra el Inicio.
- [x] **CA2**: Dada la sección de planes, cuando el visitante elige «Aseguradora» en el selector, entonces los botones de Básico y Profesional llevan a `/registro?tipo=aseguradora&plan=...`; con «Estudio jurídico», a `tipo=estudio`; y Personal, a `tipo=independiente`.
- [x] **CA3**: Los límites de cada plan salen del sistema (`/api/catalogos/planes`) y el precio vacío se muestra «A confirmar».
- [x] **CA4**: La portada aclara que la plataforma ofrece indicios y no veredictos, y recomienda consultar a un perito (RN27, ADR-0017).
- [x] **CA5**: La portada sigue la identidad visual, se lee bien a 390 px de ancho, se recorre con el teclado y respeta «reducir movimiento» (RNF10).

## Preguntas abiertas

- Precios de los planes (autora).
- Si la portada debe vivir en un dominio propio separado de la aplicación (a decidir con el dominio definitivo).
