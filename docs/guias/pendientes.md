# Lo que falta para llegar al 100 % (al 2026-10-27)

Esta lista está volcada en el [tablero de Trello](https://trello.com/b/FE1lU3cm), que es la referencia de seguimiento desde el 2026-10-26 y que el agente actualiza solo desde el 2026-10-29 ([convenciones](tablero-trello.md)) (ver la [bitácora](../bitacora/2026-10-26-reorganizacion-del-tablero.md)). Las tareas nuevas se cargan primero allá. La entrega es antes del 2026-11-19 (CP-16). La prioridad es una propuesta:

- **P1**: imprescindible para la entrega y la defensa.
- **P2**: suma mucho y conviene hacerlo.
- **P3**: opcional o trabajo futuro.

## Producto

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Red neuronal (010 y 012)**: terminar el entrenamiento, exportar a ONNX y conectarla como capa 4 probabilística | Modelo de la autora; conjunto de datos y desempeño mínimo (CP-07) | Autora entrena, agente integra |
| P1 | **Mejoras de interfaz (028)**: página de carga desde el celular, pantalla del caso, coherencia general | Lista de ajustes de la autora | Agente |
| P2 | **Inicio de sesión con Google (027)**: implementado; falta crear el cliente OAuth y probarlo | La autora crea el cliente en Google Cloud (guía en `despliegue-aws.md`) | Autora |
| P2 | **Probar la 029 en producción**: que la verificación de un informe nuevo muestre la versión | Próximo despliegue | Autora |
| P3 | Código de carga de 6 dígitos y "compartir desde la galería" (Web Share Target en Android, Atajo de Apple en iPhone) | — | Agente |
| P3 | Firma digital del PDF (CP-27) | Certificado | Agente |
| P3 | Importar fotos desde un enlace de Drive o Dropbox de un tercero (con declaración de autorización, Ley 25.326) | Decisión de alcance | Autora decide |

## Infraestructura y puesta en producción

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Comprar el dominio** y configurarlo (Terraform, HTTPS, correo) | Compra | Autora compra, agente configura |
| P1 | **Sacar SES del modo de prueba**, para que cualquiera reciba los correos y se pueda registrar | Dominio | Autora pide a AWS |
| P1 | **Pasar Hedera a la red real (*mainnet*)** antes de la defensa: cuenta nueva, unos US$ 10 de HBAR, tema nuevo (CP-26) | Compra de HBAR | Autora compra, agente guía |
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
| P2 | Guía de uso para la persona usuaria (abogado y aseguradora) | — | Agente |

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
