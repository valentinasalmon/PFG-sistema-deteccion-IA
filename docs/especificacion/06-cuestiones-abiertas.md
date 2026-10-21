# 6. Cuestiones abiertas

Decisiones pendientes de confirmación por la autora del proyecto. Cada cuestión indica la propuesta adoptada provisoriamente en la especificación y los requisitos afectados. Al resolverse, se registra la decisión y se actualizan los documentos correspondientes.

| ID | Cuestión | Propuesta provisoria | Afecta |
|---|---|---|---|
| **CP-01** | ¿Cómo se contratan y cobran los planes de las organizaciones? | **Resuelta (2026-10-19)**: el cobro en línea queda en el modelo de negocios como trabajo futuro, porque la entrega es un producto mínimo viable. La plataforma incluye un flujo de **pago simulado**: el Referente elige el plan, ve el resumen y confirma; no se piden ni se guardan datos de pago, la pantalla aclara que es una simulación y el plan se aplica de verdad, con sus límites, registrándose en la auditoría como pago simulado. El Administrador también puede modificar el plan de una organización, única excepción a su rol de solo lectura | RF19, RF20, RF22, CU16 |
| **CP-02** | ¿Qué planes existen y qué límites tiene cada uno? | **Resuelta (2026-10-19)**: se adoptan los valores de la tabla siguiente, guardados como datos configurables (RF19 CA3) | RN15, RF19 |
| **CP-03** | ¿A quién pertenecen los casos de una organización cuando un miembro se va o cuando la organización se elimina? | Los casos pertenecen a la organización: el miembro que se va debe transferirlos, y si es desvinculado pasan al Referente. Eliminar la organización elimina sus casos. El espacio de un caso no puede cambiarse después de creado. | RN09, RN12, RN14, RF14, RF17, RF18 |
| **CP-04** | ¿Con qué fórmula se calcula el Índice de Calidad del Software (QI ≥ 0,75)? | Si la cátedra no define una, proponer un promedio ponderado normalizado de cobertura de pruebas, puntuación de pylint, complejidad ciclomática y duplicación de código, medido en la integración continua. | RNF19 |
| **CP-05** | ¿Durante cuánto tiempo se conserva el registro de auditoría? | **Resuelta (2026-10-16)**: 5 años (el 2026-10-19 se aplicó el mismo plazo a los datos de los casos, RN30), en línea con el plazo genérico de prescripción del Código Civil y Comercial (art. 2560), de modo que la trazabilidad esté disponible mientras puedan existir reclamos. | RNF06 |
| **CP-06** | ¿Se implementa despliegue continuo hacia EC2? | **Resuelta (2026-10-19)**: sí. Al integrar en `main`, GitHub Actions despliega en la EC2 después de que pasa la integración continua (funcionalidad 017). La infraestructura se crea con Terraform en la cuenta de AWS de la autora, con los créditos gratuitos | RNF20 |
| **CP-07** | ¿Qué conjunto de datos y qué umbral de desempeño se exigen a la red neuronal? | Arquitectura base EfficientNet-B0 preentrenada, conjunto público de imágenes reales y generadas (CIFAKE o un subconjunto de GenImage), entrenamiento en Colab o Kaggle. Umbral de aceptación: área bajo la curva ROC ≥ 0,90 sobre el conjunto de prueba, reportando además el desempeño frente a generadores no vistos. | RF42, RNF24 |
| **CP-08** | ¿Es correcta la renumeración de los requisitos? | Los requisitos originales se integraron y renumerados por módulo (RF01 – RF51, RNF01 – RNF24), sin huecos. Los requisitos RF14 – RF17 y los RNF faltantes del borrador original se cubrieron con los módulos de análisis, informes, seguridad, desempeño y fiabilidad. | Todos |
| **CP-09** | ¿Cuál es el tamaño máximo por imagen? | 20 MB por imagen; la cantidad de imágenes por caso la define cada plan. | RN22, RF34 |
| **CP-10** | ¿Se permite prorrogar la retención? | Sí, por 1 año renovable, con motivo obligatorio registrado en la auditoría. | RN32, RF51, CU31 |
| **CP-11** | ¿Cómo se transfiere un caso del espacio personal? | A otro usuario registrado, indicando su correo; el destinatario debe aceptar la transferencia. | RF33, CU23 |
| **CP-12** | ¿Puede un usuario cambiar su perfil (Abogado o Aseguradora) después de registrarse? | **Resuelta (2026-10-10)**: no. El perfil se elige al registrarse y no puede modificarse. | RN01, RF07 |
| **CP-13** | ¿Se mantiene el tipo de organización "Independiente"? | No. Con la existencia del espacio personal gratuito, los profesionales independientes usan ese espacio; los tipos de organización son Estudio Jurídico y Aseguradora. | RF10 |
| **CP-14** | ¿Qué tipos de commit en español se adoptan? | Ver la convención propuesta a continuación. | RNF20 |
| **CP-15** | Repositorio existente de metadatos y firma digital. | **Resuelta**: analizado; ver `docs/arquitectura/reutilizacion-repositorio-tif.md`. | RF39, RF40 |
| **CP-16** | ¿Cuál es la fecha de entrega del proyecto? | **Resuelta (2026-10-19)**: la entrega final, con la plataforma y el informe completos, es en menos de un mes (antes del 2026-11-19). Se priorizan los requisitos **Debe**; la capa 4 avanza en paralelo, a cargo de la autora. El dominio se compra al final; hasta entonces la plataforma se publica con la dirección de la EC2. Los correos usan Amazon SES en modo de prueba (sandbox) con destinatarios verificados (la autora y los tutores) | Planificación |
| **CP-17** | ¿Los abogados pueden usar la plataforma como usuarios individuales y las aseguradoras solo como organizaciones? | **Resuelta (2026-10-16)**: sí. Los abogados trabajan de forma individual y pueden crear un estudio jurídico. La aseguradora se registra como empresa desde el catálogo de la SSN, el Administrador aprueba el registro, los empleados se suman solo por invitación y, si se quedan sin aseguradora, su cuenta se desactiva (RN36 a RN40, funcionalidad 021). | RN01, RN35, RF01, RF10, RF19 |
| **CP-18** | ¿Se valida el nombre de la aseguradora contra un catálogo? | **Resuelta (2026-10-16)**: sí. Al registrarse con el perfil Aseguradora, la empresa se elige o se valida contra el catálogo "Entidades activas" de la Superintendencia de Seguros de la Nación (datos abiertos), aportado por la autora: 332 entidades con `cia_id`, `cia_denominacion`, `cia_cuit`, `cia_sociedad_tipo`, `cia_actividad_principal` y país. **Se excluyen las 140 reaseguradoras** (125 "Reaseg. Admitida" y 15 "Reaseg. Local"), por decisión de la autora: una reaseguradora asegura a otras aseguradoras y no gestiona siniestros ni reclamos de asegurados, así que no recibe ni evalúa las imágenes que presentan las personas, que es el uso del perfil Aseguradora; además, las 125 admitidas son entidades extranjeras sin CUIT argentino, el dato que permite identificar a la empresa. Quedan 192 aseguradoras argentinas (seguros generales, vida, retiro, ART, sepelio, caución, crédito y transporte público). Implementado en la funcionalidad 021 (`backend/recursos/catalogos/aseguradoras_ssn.csv`, se actualiza reemplazando el archivo). Pendiente: confirmar la licencia del conjunto de datos. | RN02, RF01 |
| **CP-19** | ¿Se verifica que el abogado esté habilitado para ejercer? | **Resuelta (2026-10-16)**: no. Los abogados no se verifican, como indica la visión (validación de matrículas excluida). Se evaluó el Registro Público de Graduados Universitarios (Resolución ME 3723-E/2017, administrado por el SIU): acredita el título pero no la matrícula ni la habilitación, que otorgan los colegios de abogados, no cubre todos los títulos anteriores a 2012 y su consulta automática exigiría revisar sus términos de uso y la Ley N.° 25.326. | RN02, RF01, visión (Excluido) |
| **CP-20** | Al eliminar una cuenta, ¿qué pasa con los correos que quedaron en el detalle de la auditoría (inicios de sesión fallidos, RNF06 CA7, y cambios de correo)? | Se conservan sin modificar hasta que venzan los 5 años de CP-05. El registro es de solo inserción (RNF06 CA3) y su finalidad es la trazabilidad ante reclamos. La entrada ya no queda vinculada a la cuenta (RN34), y la Política de Privacidad lo informa. Alternativa, si los tutores la piden: reemplazar el correo por una huella SHA-256 al registrarlo. Así se pueden detectar ataques sin guardar el correo. Pendiente de validar con los tutores (funcionalidad 019). | RN34, RNF06, RNF08, RF08 |
| **CP-21** | ¿Quién entrena la red neuronal de la capa 4 y en qué entorno? | **Resuelta (2026-10-19)**: la autora entrena el modelo en Kaggle con el paquete `red_neuronal/` (funcionalidad 010, otra sesión de trabajo). Hasta que termine, las funcionalidades que dependen del modelo (012) quedan en espera y se avanza con las demás. El modelo entrenado no se sube al repositorio | RF42, RNF24 |
| **CP-22** | ¿Se incluyen peritos y criminalistas como destinatarios? Recomendación de Federico Miskinich, entrevista del 02/10/2026 | **Descartada (2026-10-22)**: la autora decidió no considerarla en el proyecto. Se mantiene el alcance actual | RF01, ADR-0017 |
| **CP-23** | ¿Con qué se complementa o reemplaza ELA, que se considera superado desde 2018? | **Descartada (2026-10-22)**: la autora decidió no considerarla en el proyecto. Se mantiene el alcance actual | RF41, RF42 |
| **CP-24** | ¿Se agregan tipos de caso para aseguradoras, como robo, incendio o daños presentados por talleres? | **Descartada (2026-10-22)**: la autora decidió no considerarla en el proyecto. Se mantiene el alcance actual | RF23 |
| **CP-25** | ¿Qué se hace si el servicio de sello de tiempo de BFA no está disponible para la entrega? | El 2026-10-22 el servicio Sello de Tiempo 2.0 (`tsa2.buenosaires.gob.ar`, el que usa `bfa.ar/sello2`) respondía 404 y la propia página de BFA daba error al sellar. Propuesta provisoria: el código queda listo para BFA y en producción el sello sigue desactivado; la autora repite la prueba cada pocos días y lo activa cuando responda. Si no vuelve antes de la entrega, el informe lo documenta como limitación por un servicio externo y la demostración usa el modo simulado, que se marca como tal en la pantalla y en el PDF. Alternativa a decidir por la autora: otro servicio de sello de tiempo (por ejemplo, OpenTimestamps sobre Bitcoin o una TSA RFC 3161), que cambia el valor probatorio local | RF37 |

## Planes propuestos (CP-02)

| Capacidad | Personal (gratuito) | Organización Básico | Organización Profesional |
|---|---|---|---|
| Compartir casos y colaborar | No | Sí | Sí |
| Miembros | 1 | Hasta 5 | Hasta 25 |
| Análisis por mes | 10 | 100 | 500 |
| Imágenes por caso | 20 | 50 | 100 |
| Almacenamiento | 1 GB | 20 GB | 100 GB |

Los valores se almacenan como datos configurables (RF19, CA3), por lo que pueden ajustarse sin modificar el código.

## Convención de commits propuesta (CP-14)

Se adopta la estructura de Conventional Commits, `tipo(ámbito): descripción`, con tipos traducidos al español y validados con commitlint mediante una configuración propia:

| Tipo | Equivalente estándar | Uso |
|---|---|---|
| `funcionalidad` | `feat` | Nueva funcionalidad |
| `correccion` | `fix` | Corrección de un defecto |
| `documentacion` | `docs` | Solo documentación |
| `estilo` | `style` | Formato, sin cambios de lógica |
| `refactorizacion` | `refactor` | Reestructuración sin cambio de comportamiento |
| `rendimiento` | `perf` | Mejora de desempeño |
| `pruebas` | `test` | Agregado o corrección de pruebas |
| `construccion` | `build` | Dependencias y empaquetado |
| `integracion` | `ci` | Integración continua |
| `tarea` | `chore` | Mantenimiento general |
| `revertir` | `revert` | Reversión de un commit |

Ejemplo: `funcionalidad(casos): agregar filtro por expediente`.

Las ramas siguen el mismo criterio: `funcionalidad/organizaciones`, `correccion/carga-de-imagenes`, `documentacion/casos-de-uso`.
