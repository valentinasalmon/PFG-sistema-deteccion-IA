# Bitácora de desarrollo

Registro cronológico de lo realizado en cada etapa: qué se hizo, qué se decidió y por qué, qué bibliotecas o técnicas se incorporaron y qué quedó pendiente. Es la memoria del proyecto y la base para redactar el informe final.

## Formato

Un archivo por entrada: `AAAA-MM-DD-tema.md`, con las secciones:

- **Qué se hizo**
- **Decisiones tomadas** (con enlace a ADR si corresponde)
- **Tecnologías, bibliotecas o técnicas incorporadas** y para qué
- **Problemas encontrados y cómo se resolvieron**
- **Pendientes**

## Entradas

| Fecha | Tema |
|---|---|
| 2026-10-08 | [Especificación inicial y estructura del repositorio](2026-10-08-especificacion-y-estructura.md) |
| 2026-10-08 | [Hoja de ruta y entorno de desarrollo](2026-10-08-hoja-de-ruta-y-entorno.md) |
| 2026-10-09 | [Fase 0: entorno de desarrollo instalado](2026-10-09-fase-0-entorno.md) |
| 2026-10-10 | [Funcionalidad 001: esqueleto caminante](2026-10-10-funcionalidad-001-esqueleto-caminante.md) |
| 2026-10-11 | [Funcionalidad 002: avance](2026-10-11-funcionalidad-002-avance.md) |
| 2026-10-16 | [Funcionalidad 002: cuentas y sesión](2026-10-16-funcionalidad-002-cuentas-y-sesion.md) |
| 2026-10-16 | [Funcionalidad 020: registro guiado por pasos](2026-10-16-funcionalidad-020-registro-por-pasos.md) |
| 2026-10-16 | [Funcionalidad 003: auditoría](2026-10-16-funcionalidad-003-auditoria.md) |
| 2026-10-16 | [Funcionalidad 004: organizaciones e invitaciones](2026-10-16-funcionalidad-004-organizaciones.md) |
| 2026-10-16 | [Funcionalidad 021: organizaciones de aseguradoras](2026-10-16-funcionalidad-021-aseguradoras.md) |
| 2026-10-19 | [Funcionalidad 005: casos y permisos](2026-10-19-funcionalidad-005-casos.md) |
| 2026-10-19 | [Funcionalidad 019: eliminación de cuenta y copia de datos](2026-10-19-funcionalidad-019-baja-de-cuenta.md) |
| 2026-10-19 | [Funcionalidad 006: carga de imágenes, huella y almacenamiento](2026-10-19-funcionalidad-006-imagenes.md) |
| 2026-10-19 | [Funcionalidad 007: motor de análisis y capa de metadatos](2026-10-19-funcionalidad-007-motor-de-analisis.md) |
| 2026-10-19 | [Funcionalidad 008: informe PDF e historial (hito v0.1)](2026-10-19-funcionalidad-008-informe-pdf.md) |
| 2026-10-19 | [Funcionalidad 009: capa de credenciales de contenido (C2PA)](2026-10-19-funcionalidad-009-capa-c2pa.md) |
| 2026-10-19 | [Funcionalidad 010: especificación y plan de la red neuronal](2026-10-19-especificacion-red-neuronal.md) |
| 2026-10-19 | [Funcionalidad 010: pipeline del clasificador implementado](2026-10-19-funcionalidad-010-pipeline.md) |
| 2026-10-19 | [Decisiones de alcance y entrega](2026-10-19-decisiones-de-alcance-y-entrega.md) |
| 2026-10-19 | [Funcionalidad 017: infraestructura y despliegue en AWS (código)](2026-10-19-funcionalidad-017-infraestructura.md) |
| 2026-10-20 | [Funcionalidad 011: capa 3, niveles de error (ELA)](2026-10-20-funcionalidad-011-capa-ela.md) |
| 2026-10-21 | [Funcionalidad 013: panel principal y notificaciones](2026-10-21-funcionalidad-013-panel-y-notificaciones.md) |
| 2026-10-21 | [Funcionalidad 022: rediseño de la interfaz (primera entrega)](2026-10-21-funcionalidad-022-rediseno-interfaz.md) |
| 2026-10-22 | [Corrección de la 016: dirección real del sello de BFA](2026-10-22-correccion-016-sello-tsa2.md) |
| 2026-10-22 | [Corrección de la 016: Sello de Tiempo 1.0 de BFA](2026-10-22-correccion-016-sello-tsaapi.md) |
| 2026-10-22 | [Funcionalidad 014: planes, pago simulado y tablero](2026-10-22-funcionalidad-014-planes-y-tablero.md) |
| 2026-10-22 | [Funcionalidad 015: retención y destrucción de datos](2026-10-22-funcionalidad-015-retencion.md) |
| 2026-10-22 | [Funcionalidad 016: sello de tiempo en Blockchain Federal Argentina](2026-10-22-funcionalidad-016-sello-bfa.md) |
| 2026-10-25 | [Funcionalidad 023: sello de tiempo en Hedera](2026-10-25-funcionalidad-023-sello-hedera.md) |
| 2026-10-25 | [Cambio a Hedera y ampliaciones del alcance](2026-10-25-plan-hedera-y-ampliaciones.md) |
| 2026-10-26 | [Reorganización del tablero de Trello](2026-10-26-reorganizacion-del-tablero.md) |
| 2026-10-26 | [Funcionalidad 024, etapa 1: carga desde el celular y HEIC](2026-10-26-funcionalidad-024-etapa-1.md) |
| 2026-10-26 | [Funcionalidades 025 y 026: informe breve por rubro y verificable](2026-10-26-funcionalidades-025-y-026-informe.md) |
| 2026-10-27 | [Ajustes del informe (025) y versión en Hedera (029)](2026-10-27-ajustes-informe-y-029.md) |
| 2026-10-28 | [Integración continua en verde e inicio con Google (027)](2026-10-28-funcionalidad-027-inicio-con-google.md) |
| 2026-10-28 | [Revisión y refuerzo de la seguridad (030)](2026-10-28-funcionalidad-030-seguridad.md) |
| 2026-10-28 | [Mejoras de interfaz (028): auditoría, frames y primera tanda](2026-10-28-funcionalidad-028-interfaz.md) |
| 2026-10-28 | [Funcionalidad 010: la red neuronal pasa a Google Colab](2026-10-28-red-neuronal-en-colab.md) |
| 2026-10-29 | [Interfaz (028), tercera tanda, y propuesta del pago en el registro (032)](2026-10-29-funcionalidad-028-tercera-tanda.md) |
| 2026-10-29 | [Funcionalidad 032: pago del plan en el registro](2026-10-29-funcionalidad-032-pago-en-el-registro.md) |
| 2026-10-29 | [Funcionalidad 033: portada pública con los planes](2026-10-29-funcionalidad-033-portada.md) |
| 2026-10-29 | [Funcionalidad 034: pulido de UX/UI, primera tanda](2026-10-29-funcionalidad-034-pulido-ux.md) |
| 2026-10-29 | [Borrador del informe final y sugerencias de integración](2026-10-29-redaccion-del-informe-y-sugerencias.md) |
| 2026-10-30 | [Funcionalidad 010: primera corrida en Colab](2026-10-30-red-neuronal-primera-corrida-en-colab.md) |
| 2026-10-30 | [Funcionalidad 010: prueba de concepto de la red neuronal](2026-10-30-prueba-de-concepto-red-neuronal.md) |
| 2026-10-30 | [Funcionalidad 010: documentación, plan de entrenamientos y búsqueda de datos](2026-10-30-datos-y-plan-de-entrenamientos.md) |
| 2026-10-30 | [Funcionalidad 010: exploración de datos, receta v1 y cuaderno de entrenamiento completo](2026-10-30-red-neuronal-exploracion-y-receta-v1.md) |
| 2026-10-30 | [Funcionalidad 031: Microsoft Clarity instalado](2026-10-30-funcionalidad-031-clarity.md) |
| 2026-10-30 | [Funcionalidad 034: pulido de UX/UI, segunda tanda](2026-10-30-funcionalidad-034-segunda-tanda.md) |
| 2026-10-31 | [Funcionalidad 034, cuarta tanda: organización, administración, verificar y estado](2026-10-31-funcionalidad-034-cuarta-tanda.md) |
| 2026-10-31 | [Funcionalidad 034, tercera tanda: portada, acceso, registro, privacidad y estado de Hedera](2026-10-31-funcionalidad-034-tercera-tanda.md) |
| 2026-11-02 | [Corrección: el informe decía «Pendiente de confirmación en Hedera»](2026-11-02-correccion-sello-en-el-informe.md) |
| 2026-11-02 | [Decisiones de la autora, revisión de Hedera e investigación de Cresium](2026-11-02-decisiones-hedera-y-cresium.md) |
| 2026-11-02 | [Funcionalidad 034, quinta tanda: portada más limpia](2026-11-02-funcionalidad-034-quinta-tanda.md) |
| 2026-11-02 | [Funcionalidad 036: arnés para el trabajo asistido por IA](2026-11-02-funcionalidad-036-arnes.md) |
| 2026-11-02 | [Hedera funcionando en *testnet* en producción](2026-11-02-prueba-hedera-testnet.md) |
| 2026-11-04 | [Funcionalidad 018: materiales del cierre](2026-11-04-funcionalidad-018-materiales.md) |
| 2026-11-04 | [Funcionalidad 035: verificación de identidad de aseguradoras](2026-11-04-funcionalidad-035-identidad.md) |
| 2026-11-05 | [Funcionalidad 038: revisión continua del arnés](2026-11-05-funcionalidad-038-revision-del-arnes.md) |
| 2026-11-05 | [Funcionalidad 039: orden del repositorio y del flujo de integración](2026-11-05-funcionalidad-039-orden-del-repositorio.md) |
