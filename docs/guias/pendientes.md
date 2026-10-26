# Lo que falta para llegar al 100 % (al 2026-10-27)

Lista para ordenar con la autora y pasar a Trello. La entrega es antes del 2026-11-19 (CP-16). La prioridad es una propuesta:

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
| P3 | Limitar la cantidad de pedidos por minuto en las páginas públicas (verificación y carga desde el celular) | — | Agente |
| P3 | Borrar la rama abandonada `funcionalidad/016-sello-desde-navegador` | — | Autora |

## Calidad y cierre (018)

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Pruebas de usabilidad** con 3 a 5 abogados o liquidadores: guion, tareas, cuestionario SUS y conclusiones | Participantes | Agente arma, autora conduce |
| P1 | **Índice de calidad (QI ≥ 0,75)**: definir la fórmula y medir (cobertura, análisis estático, pruebas, usabilidad) | CP-04 (tutor) | Agente mide, tutor valida |
| P2 | Revisión final de seguridad (dependencias, cabeceras, permisos) | — | Agente |
| P2 | Guía de uso para la persona usuaria (abogado y aseguradora) | — | Agente |

## Documento final del proyecto (informe para la facultad)

| Prioridad | Tarea | Depende de | Quién |
|---|---|---|---|
| P1 | **Definir las secciones nuevas** que se agregan y las que se modifican (CP-31) | Autora y tutor | Autora |
| P1 | **Redactar el informe final** con lo reunido en `docs/informe-final/insumos.md` (Hedera, celular, PDF verificable, metodología, calidad) | Secciones definidas | Agente redacta, autora revisa |
| P1 | Preparar la **defensa**: presentación y demostración (QR, verificación, Hedera) | Informe final | Autora, con apoyo del agente |

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
