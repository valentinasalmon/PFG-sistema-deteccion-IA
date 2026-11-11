# Lo que falta para llegar al 100 % (actualizado el 2026-11-05)

Esta lista está volcada en el [tablero de Trello](https://trello.com/b/FE1lU3cm), que es la referencia de seguimiento desde el 2026-10-26 y que el agente actualiza solo desde el 2026-10-29 ([convenciones](tablero-trello.md)) (ver la [bitácora](../bitacora/2026-10-26-reorganizacion-del-tablero.md)). Las tareas nuevas se cargan primero allá. La entrega es antes del 2026-11-19 (CP-16). La prioridad es una propuesta:

- **P1**: imprescindible para la entrega y la defensa.
- **P2**: suma mucho y conviene hacerlo.
- **P3**: opcional o trabajo futuro.

## Producto

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Red neuronal (010 y 012)**: terminar el entrenamiento, exportar a ONNX y conectarla como capa 4 probabilística. El sistema ya está preparado: es una clase y una línea en el registro (ver `docs/red-neuronal/07`); al integrarla, quitar el «Próximamente» de la portada y de los términos | Modelo de la autora; conjunto de datos y desempeño mínimo (CP-07) | Autora entrena, agente integra |
| ✓ | Mejoras de interfaz (028 y 034): implementadas en cuatro tandas; falta la revisión final de la autora | Revisión | Autora |
| P1 | **Revisión de la 034 pantalla por pantalla** (CA1, CA3, CA4, CA6, CA9) | PR de la tercera y la cuarta tanda | Autora revisa, agente corrige |
| P2 | **Cobro real con Cresium**: proveedor, aviso firmado y conciliación (ver `docs/investigacion/2026-11-02-integracion-cresium.md`) | Precios (CP-38) y cuenta de Cresium con entorno de pruebas | Autora abre la cuenta, agente integra |
| P2 | **Conectar Identik real (035)**: la verificación ya funciona con el proveedor simulado; falta el sandbox, el aviso firmado y la prueba real | Reunión técnica con Identik y CP-41 (qué servicio usar) | Autora (reunión y token), agente integra |
| P1 | **Quitar Clarity antes de la versión final** (CP-37): sacar el script, la excepción de la CSP y el apartado de la política de privacidad | Fin de las pruebas | Agente |
| P2 | **Inicio de sesión con Google (027)**: implementado; falta crear el cliente OAuth y probarlo | La autora crea el cliente en Google Cloud (guía en `despliegue-aws.md`) | Autora |
| ✓ | Hedera en *testnet* funcionando en producción (2026-11-02); falta comprobar la versión en un informe nuevo (029) | — | Autora |
| P2 | **Definir los precios** con el análisis de costos (CP-38) | Análisis de costos | Autora |
| P3 | Código de carga de 6 dígitos y "compartir desde la galería" (Web Share Target en Android, Atajo de Apple en iPhone) | — | Agente |
| P3 | Firma digital del PDF (CP-27) | Certificado | Agente |
| P3 | Importar fotos desde un enlace de Drive o Dropbox de un tercero (con declaración de autorización, Ley 25.326) | Decisión de alcance | Autora decide |

## Agregado el 2026-11-05 (revisión integral, 037)

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Integrar la 037** (Pull Request hacia `desarrollo` y después a `main`) y probar en producción: login con Google, siniestros, PDF breve con QR al detalle | Revisión de la autora | Autora |
| P1 | **Probar en Safari (iPhone) y Firefox**: en el entorno del agente solo hay Chromium; los recorridos de punta a punta pasaron en Chromium de computadora y en un iPhone 13 emulado | — | Autora, con `frontend/e2e/` y la guía de usuario |
| P1 | **CP-43**: ¿el enlace al análisis detallado del PDF se abre sin cuenta? Hoy exige una cuenta con acceso | Autora y tutor | Autora |
| ~~P2~~ | ~~Sumar los recorridos de `frontend/e2e/` y el sensor de diseño a la integración continua~~ — hecho en la 039 (trabajo «Interfaz») | — | Agente |
| ~~P2~~ | ~~Los correos todavía dicen «caso» también a las aseguradoras~~ — hecho en la 039 | — | Agente |

## Infraestructura y puesta en producción

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Comprar el dominio** y configurarlo (Terraform, HTTPS, correo): pasos completos en `docs/guias/despliegue-aws.md`, «Cuando compres el dominio» | Compra | Autora, con la guía |
| P1 | **Sacar SES del modo de prueba**, para que cualquiera reciba los correos y se pueda registrar | Dominio | Autora pide a AWS |
| P1 | **Pasar Hedera a la red real (*mainnet*)** en **febrero de 2027**, antes de la defensa (decisión de la autora, 2026-11-11): cuenta nueva, unos US$ 10 de HBAR, tema nuevo (CP-26). Hasta entonces sigue en *testnet* | Compra de HBAR | Autora compra, agente guía |
| P2 | Probar la restauración de la copia de seguridad de la base (pendiente de la 017) | — | Autora, con la guía |
| P2 | Logo como foto del remitente de los correos | Dominio; según el proveedor, BIMI | Agente investiga |
| ✓ | Limitar la cantidad de pedidos por minuto (030, hecho) | — | Agente |
| P3 | Borrar la rama abandonada `funcionalidad/016-sello-desde-navegador` | — | Autora |

## Calidad y cierre (018)

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Pruebas de usabilidad** con 3 a 5 abogados o liquidadores: guion, tareas, cuestionario SUS y conclusiones | Participantes | Agente arma, autora conduce |
| P1 | **Índice de calidad (QI ≥ 0,75)**: definir la fórmula y medir (cobertura, análisis estático, pruebas, usabilidad) | CP-04 (tutor) | Agente mide, tutor valida |
| ✓ | Revisión de seguridad (030, hecha: `docs/arquitectura/seguridad.md`) | — | Agente |
| ~~P2~~ | ~~Guía de uso para la persona usuaria~~ — hecha en `docs/guias/guia-de-usuario.md` (018); actualizada con la 037 y la 038 en la 039 | — | Agente |

## Documento final del proyecto (informe para la facultad)

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Definir las secciones nuevas** que se agregan y las que se modifican (CP-31) | Autora y tutor | Autora |
| P1 | **Redactar el informe final** con lo reunido en `docs/informe-final/insumos.md` (Hedera, celular, PDF verificable, metodología, calidad) | Secciones definidas | Agente redacta, autora revisa |
| P1 | Preparar la **defensa**: presentación y demostración (QR, verificación, Hedera) | Informe final | Autora, con apoyo del agente |

## Relevamiento y validación (agregado el 2026-10-26)

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Validar requisitos y dominio con el referente**, con acta (exigido por la AE2) | Referente | Autora |
| P1 | **Validar la comprensión del informe** con al menos un abogado y un analista de siniestros (OE5, aceptación del MVP) | Participantes | Autora |
| P1 | **Mapas de empatía**: al menos 3 interesados (versión 2) y 5 (versión 3) del Capítulo XIII | Participantes | Agente arma, autora conduce |
| P2 | Segunda entrevista del lado asegurador; mostrar el sistema actual a Federico Miskinich | — | Autora |

## Deudas de la AE1 y la AE2 y capítulos del protocolo (agregado el 2026-10-26)

| Prioridad | Tarea | Quién |
|---|---|---|
| P1 | Catálogo de requisitos con trazabilidad al hallazgo y matriz hallazgo → requisito → componente | Agente |
| P1 | Lienzo de modelo de negocio | Agente y autora |
| P1 | Prototipo v1: etiqueta `v1`, README con instrucciones de ejecución y evidencia de la integración continua | Agente prepara, autora etiqueta |
| P1 | Capítulos X (recursos), IX (diseño de solución, con diagrama de arquitectura actualizado y diagrama entidad-relación), VII (marketing), VIII (propiedad intelectual, búsqueda en el INPI), XII, XIII y conclusiones | Agente redacta, autora revisa |
| P1 | Actualizar los Capítulos I a VI a lo construido (Hedera, React, organizaciones, HEIC, Google, cronograma real, columnas del tablero) | Agente |
| P1 | Bitácora individual con la declaración de uso de IA y portafolio digital (instrumentos de la AE1 y la AE2, hoy sin hacer) | Autora, con apoyo del agente |
| P1 | Unificar el criterio del clasificador: F1 ≥ 0,85 (informe) o AUC ≥ 0,90 (010 y CP-07) | Tutores |
| P1 | Revisar la consigna de la AE3 cuando se publique | Autora |
| P2 | Prototipo v0 navegable, Capítulo XI, aspectos formales y comentarios abiertos del documento | Agente y autora |

## Cuestiones para validar con los tutores

- **CP-03**: a quién pertenecen los casos de una organización.
- **CP-04**: fórmula del índice de calidad.
- **CP-07**: conjunto de datos y desempeño de la red neuronal.
- **CP-08**: renumeración de requisitos.
- **CP-09**: 20 MB por imagen.
- **CP-10**: prórroga de 1 año.
- **CP-11**: transferencia de casos.
- **CP-13**: sin el tipo "Independiente".
- **CP-20**: correos en la auditoría al borrar una cuenta.
- **CP-26**: red de Hedera para la entrega.

## Orden sugerido hasta el 19/11

1. **27/10 – 02/11:**
   - interfaz (028);
   - inicio con Google (027);
   - comprar el dominio y sacar SES del modo de prueba;
   - definir las secciones del informe final.
2. **03/11 – 09/11:**
   - integrar la red neuronal (012);
   - pruebas de usabilidad;
   - índice de calidad;
   - empezar a redactar el informe final.
3. **10/11 – 15/11:**
   - Hedera en la red real;
   - prueba de restauración;
   - revisión de seguridad;
   - terminar el informe final.
4. **16/11 – 19/11:** congelar el código, ensayar la defensa y entregar.
