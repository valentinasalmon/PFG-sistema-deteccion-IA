# Guía de redacción del informe final

Esta guía reúne **todo lo que un evaluador de un Proyecto Final de Grado de Ingeniería en Sistemas mira** y cómo resolverlo en el informe de evidentIA. La usan la autora, el comando `/redactar-informe` (que escribe secciones) y el comando `/revisar-informe` (que corrige como un evaluador). Las reglas mecánicas las verifica además `backend/herramientas/revisar_informe.py`.

> Un informe de diez cumple tres cosas a la vez: **dice lo que el sistema hace de verdad** (cada afirmación tiene su evidencia), **está completo según el protocolo** (ningún capítulo vacío ni contradictorio) y **está bien escrito** (prosa académica, en presente, con APA 7 sin errores).

## 1. Marco de la cátedra

- **Universidad de la Cuenca del Plata**, Facultad de Ingeniería, Tecnología y Arquitectura, Ingeniería en Sistemas de Información. Modalidad: *diseño y desarrollo de un sistema de información* (Reglamento General del Proyecto Integrador Final, RR N.° 97/23, art. 23.2).
- **Entregas:** AE1 (Resumen, Capítulos I y II), AE2 (Capítulos III a VI), AE3 (capítulos restantes). El documento se presenta completo para la evaluación, que tiene hasta 20 días (art. 8.2.6), y la copia al tribunal va cinco días hábiles antes de la defensa (art. 14). La exposición dura hasta 45 minutos (art. 16).
- **Docentes:** Sergio Lapertosa, Augusto Portillo y Martín Jones (revisor técnico).
- **Pedidos explícitos de la cátedra registrados en el repositorio:**
  - el catálogo de requisitos con trazabilidad al hallazgo;
  - el prototipo v1 con etiqueta, instrucciones y evidencia de la integración continua;
  - los mapas de empatía (3 interesados en la versión 2 y 5 en la versión 3);
  - el acta de validación con el referente;
  - la bitácora individual con la declaración de uso de IA;
  - la exposición del arnés (*harness engineering*).

## 2. Estructura obligatoria (orden del protocolo)

| N.° | Capítulo | Secciones |
|---|---|---|
| — | Portada, Resumen, Índice general, Índice de tablas, Índice de figuras | El resumen va en un solo bloque de prosa de 150 a 300 palabras |
| I | Definición del proyecto | Origen; Misión, visión y objetivos (general y específicos); Necesidad o problema al que responde; ODS asociadas y diferenciales; Descripción breve; Descripción detallada |
| II | Relevamiento e investigación de mercado | Fuentes de datos; Instrumentos, dinámicas y alcance; Presentación de datos; Gráficos y variables; Análisis de información |
| III | Entorno y dominio del sistema | Entorno; Dominio; Alcance (del sistema y del proyecto); Límites y limitaciones; Catálogo de requisitos |
| IV | Modelo de negocios | Definición de negocios (actividades, mercado, planes, tecnología); Visión y misión; Rivalidad amplificada (competencia, potenciales, sustitutos, proveedores, clientes); Mapeo de competencia |
| V | Planificación | Iteraciones; Entregables por etapa; Organización del equipo; Cronograma (planificado y real); MVP |
| VI | Metodologías de gestión | Técnicas y prácticas; Trazabilidad; Gestión de la configuración; Testing; Prototipo v1 |
| VII | Marketing | Producto y experiencia; Dinámicas de intercambio por perfil; Publicidad y promoción; *Engagement* |
| VIII | Propiedad intelectual | Marca y activos; Clases de Niza; Búsqueda en el INPI |
| IX | Diseño de solución | Arquitectura; Diseño; Modelo de datos; Infraestructura; Entornos; Solución (capturas) |
| X | Recursos | Humanos; Físicos y materiales; Financieros; Tecnológicos; Otros |
| XI | Oportunidades | CANVAS; Oportunidades futuras |
| XII | Lecciones aprendidas | Aspectos positivos; Aspectos a mejorar |
| XIII | Entregables | Prototipo v1, v2 y v3 (con mapas de empatía); Código fuente; Documentación |
| — | Conclusiones, Bibliografía, Anexos | |

Los capítulos se numeran **sin repetir ni saltear**. Los subtítulos de un mismo nivel usan el mismo estilo de título de Google Docs, para que el índice se genere solo.

## 3. Cómo se redacta

1. **Presente impersonal.** «Se realiza», «se obtiene», «el sistema registra». El pasado se usa solo para un hecho externo fechado («McLarens reportó en 2023…»). Lo que todavía no existe se escribe como **previsto** («se prevé», «la estrategia contempla»), **nunca como hecho**.
2. **Prosa, sin viñetas.** Las enumeraciones van en una oración, separadas por comas o por punto y coma. Solo las tablas, con número, título y nota, ordenan información.
3. **Un párrafo, una idea**, con oración temática al inicio. Párrafos de 4 a 8 oraciones.
4. **Sin primera persona** («yo», «decidí»). La autora aparece como «la autora».
5. **Sin veredictos** (RN27). El sistema informa **indicios**, con valores y umbrales. Nunca se escribe «detecta que la imagen es falsa» ni «garantiza».
6. **Precisión antes que adjetivos.** En lugar de «muy seguro», escribir «cifrado en reposo, control de acceso por roles y auditoría». En lugar de «rápido», escribir «menos de 30 segundos por imagen».
7. **Terminología única.** Usar siempre el mismo término para lo mismo:
   - evidentIA, con minúscula inicial;
   - huella digital SHA-256;
   - sello de tiempo;
   - persona afectada;
   - indicio determinista y probabilístico;
   - análisis de niveles de error (ELA);
   - Hedera Consensus Service.

   Los extranjerismos van en cursiva: *deepfake*, *mirror node*, *testnet*, *webhook*.
8. **Números a la española:**
   - coma decimal: 0,85;
   - espacio antes del signo de porcentaje: 45,5 %;
   - punto de miles: 1.536;
   - fechas en letras dentro del texto (2 de noviembre de 2026);
   - siglas desarrolladas la primera vez que aparecen.
9. **Ortografía actual:** «guion» va sin tilde; las mayúsculas de los títulos se usan solo al inicio y en los nombres propios.

## 4. Cómo se evidencia (lo que distingue un informe de diez)

Cada afirmación sobre el sistema o el proceso tiene una evidencia que un evaluador puede comprobar. La tabla indica cuál corresponde.

| Tipo de afirmación | Evidencia válida | Dónde está |
|---|---|---|
| «El sistema hace X» | Captura del sistema en producción con datos de prueba (figura con nota) o referencia a la funcionalidad con su especificación | `docs/funcionalidades/NNN-*/`, capturas en cada carpeta |
| Cifras del proceso (commits, pruebas, ADR, coautoría de IA) | Tabla calculada con `backend/herramientas/cifras_del_proyecto.py`, con su fecha y commit | `docs/informe-final/hechos-del-sistema.md` |
| Calidad del código | Integración continua en verde, cobertura y pylint del último Pull Request, índice de calidad | GitHub Actions, `backend/herramientas/indice_calidad.py` |
| Integración externa funcionando | La página `/estado` y el registro público (HashScan para Hedera); nunca solo las pruebas automáticas | Captura de `/estado` y del mensaje en HashScan |
| Decisión de diseño | ADR con las alternativas evaluadas | `docs/arquitectura/decisiones/` |
| Decisión de alcance, legal o de negocio | Cuestión abierta resuelta (CP-NN), con la fecha | `docs/especificacion/06-cuestiones-abiertas.md` |
| Hallazgo del relevamiento | Instrumento y dato (encuesta n = 11, entrevista con fecha) | Capítulo II y anexos A a D, I y J |
| Diagrama | Generado desde el código y verificado (`/generar-diagramas`) | `docs/arquitectura/diagramas/` |
| Trabajo asistido por IA | Línea `Co-Authored-By` en cada commit, registro de cambios del arnés y bitácora | `docs/arnes/`, `docs/bitacora/` |
| Validación con usuarios | Acta, cuestionario SUS, mapas de empatía (pendientes) | Anexo N |

**Regla de oro:** distinguir siempre entre:

- **implementado y probado con dobles de prueba**;
- **probado contra el servicio real**;
- **previsto**.

Mezclarlos es el error que más baja la nota, porque el evaluador lo detecta en la demostración.

## 5. Tablas, figuras y citas (APA 7)

- **Tabla:** el rótulo «**Tabla N.**» va en negrita y el título en cursiva, arriba. Debajo, la nota en cursiva: *Nota. Elaboración propia a partir de…*. Toda tabla se menciona en el texto antes de aparecer.
- **Figura:** «**Figura N.**» y el título, arriba; la imagen; y la nota debajo. Los diagramas llevan además la notación usada (*UML 2.5*).
- **Numeración** correlativa en todo el documento. Hay dos índices separados, uno de tablas y otro de figuras.
- **Citas en el texto:**
  - entre paréntesis: (Autor, año);
  - narrativa: Autor (año);
  - tres o más autores: «et al.»;
  - sin fecha: «s. f.»;
  - con sigla: (International Organization for Standardization \[ISO\], 2023) la primera vez y (ISO, 2023) después.
- **Bibliografía:**
  - orden alfabético por autor;
  - sangría francesa;
  - en español se usa «y», no «&»;
  - letras de año (2026a, 2026b) solo si hay dos obras del mismo autor y año;
  - **toda cita tiene su entrada, y toda entrada se cita**.
- **Leyes argentinas:** República Argentina. (año). *Ley N.° …*. Boletín Oficial de la República Argentina.

## 6. Qué mira el evaluador en cada capítulo (criterio experto)

- **I. Definición.** Que el problema esté respaldado por evidencia (no por opinión). Que los objetivos específicos sean medibles y se puedan verificar al final, y que cada uno tenga su resultado en las conclusiones. Que los diferenciales sean concretos.
- **II. Relevamiento.** Que la muestra se declare como exploratoria y de conveniencia. Que cada dato secundario pase la regla de las tres preguntas (quién, cómo, cuándo). Que el análisis convierta los hallazgos en decisiones de diseño.
- **III. Entorno y dominio.** Que el marco normativo argentino sea correcto y esté aplicado:
  - la Ley 25.326, con la inscripción de la base de datos ante la AAIP, la seguridad (art. 9), los datos sensibles (art. 2 y art. 7) y las transferencias (art. 12);
  - la Ley 17.418 de Seguros;
  - el Código Procesal de Corrientes.

  También, que el alcance y las exclusiones sean coherentes con lo construido y que el catálogo de requisitos tenga trazabilidad.
- **IV. Negocios.** Que el mercado esté cuantificado con fuentes. Que Porter esté aplicado y no solo nombrado. Que los precios estén justificados por costos y competencia. Ver `plan-de-negocios.md`.
- **V. Planificación.** Que el plan y la ejecución real se contrasten con honestidad. Que los riesgos tengan plan de contingencia. Que el MVP tenga un criterio de aceptación medible y **el mismo valor que el OE4**.
- **VI. Metodología.** Que lo declarado se cumpla en el repositorio. El evaluador puede abrir GitHub, así que no se puede decir «límite de una tarea en curso» si no se cumplió. Que la trazabilidad sea demostrable y que el uso de IA esté declarado y controlado (ver `trabajo-con-ia.md`).
- **VII. Marketing.** Que sea un plan argumentado, propio del segmento profesional (abogados y aseguradoras: canales B2B, confianza, demostración) y escrito como previsto.
- **VIII. Propiedad intelectual.** Que haya una búsqueda real en el INPI con fecha y evidencia, las clases de Niza correctas y el software como obra (Ley 11.723).
- **IX. Diseño.** Que los diagramas usen **notación estándar (UML 2.5, entidad-relación de pata de gallo)** y coincidan con el código. Que las decisiones estén justificadas con ADR y que la seguridad tenga su lugar (OWASP).
- **X. Recursos.** Que el presupuesto esté completo, con el costo de oportunidad de las horas, y que sea coherente con los precios.
- **XI. Oportunidades.** Que el CANVAS sea coherente con el Capítulo IV y que las oportunidades estén priorizadas.
- **XII. Lecciones.** Que sean autocríticas, con causa y aprendizaje, y no una lista de logros.
- **XIII. Entregables.** Que el prototipo v1 tenga etiqueta, los mapas de empatía estén hechos y el repositorio y la documentación estén listados.
- **Conclusiones.** Que cada objetivo específico tenga su resultado (cumplido, parcial o no cumplido), con evidencia. Que aparezcan las limitaciones, el trabajo futuro y el aporte.

## 7. Errores frecuentes ya detectados en este informe

Se registran para que no se repitan. El revisor automático los busca.

- Un texto pegado en la sección equivocada, que duplica párrafos: pasó en «Diferenciales», donde quedó pegada la «Descripción detallada».
- Numeración de capítulos repetida (dos «VII») o fuera de orden («IV» en lugar de «IX»).
- La referencia a una tabla que no existe (la Tabla 11) y una tabla sin número («Tabla .»).
- BFA presentado como proveedor actual: es solo un antecedente, el sello se registra en Hedera.
- El criterio del clasificador distinto en el OE4 (F1) y en la especificación (AUC). Se resuelve con CP-07.
- Una cita sin entrada (OWASP, OpenID Foundation), entradas sin citar y una letra de año sin pareja (Amazon 2026b).
- El pasado en lugar del presente («la búsqueda se realizó»).
- Viñetas en un texto que va en prosa.
- Marcadores sin completar en la entrega («[completar]», «?»).
