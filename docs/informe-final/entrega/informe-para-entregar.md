UNIVERSIDAD DE LA CUENCA DEL PLATA · FACULTAD DE INGENIERÍA, TECNOLOGÍA Y ARQUITECTURA

Ingeniería en Sistemas de Información

# Proyecto Final de Grado

Actividad de Evaluación N.° 4 [confirmar número de la entrega]

***evidentIA: plataforma de apoyo a la decisión para la detección de indicios de generación o manipulación por inteligencia artificial en la prueba fotográfica de siniestros de tránsito y laborales en Argentina***

Autora: Valentina Salmón · 45.940.232

Docentes: Sergio Lapertosa · Augusto Portillo · Martín Jones

Corrientes · 2026

# **Resumen**

La proliferación de herramientas de inteligencia artificial capaces de generar imágenes fotorrealistas, o de modificar fotografías reales sin que la alteración se perciba a simple vista, introduce un riesgo creciente en el sistema judicial y asegurador argentino: que esas imágenes se presenten como prueba en causas y siniestros por accidentes de tránsito y laborales.

El relevamiento, que combina una encuesta a 11 abogados con entrevistas a dos peritas, a un productor de seguros y a un referente de LegalTech, muestra una brecha entre la duda y la acción: el 72,7 % de los abogados dudó o tal vez dudó alguna vez de la autenticidad de una imagen presentada como prueba, pero ninguno solicitó una pericia formal. El problema se concentra en el circuito informal, donde las imágenes llegan sin certificación de origen.

A partir de este diagnóstico se desarrolla evidentIA, una plataforma web de apoyo a la decisión humana que permite a abogados y aseguradoras organizar las imágenes por caso y obtener un informe, en el lenguaje de cada rubro, sobre los indicios de generación o manipulación. El análisis combina cuatro capas: los metadatos y las credenciales de procedencia C2PA, de naturaleza determinista; el análisis de niveles de error; y un clasificador de redes neuronales que alcanza un área bajo la curva ROC de 0,961 con generadores conocidos. El sistema no emite veredictos: presenta valores y umbrales, incluye un descargo de resultado parcial y recomienda consultar a un perito. La huella de cada imagen, de cada informe y de cada versión del software se registra en la red pública Hedera, y cualquier tercero puede verificar un informe. El desarrollo sigue una metodología guiada por especificaciones, con un agente de inteligencia artificial que trabaja dentro de un arnés de reglas y controles automáticos, bajo la supervisión de la autora.

**Palabras clave:** detección de imágenes generadas por IA; prueba fotográfica digital; fraude en seguros; apoyo a la decisión; trazabilidad.

[Índice general, índice de tablas e índice de figuras: regenerarlos en el documento después de pegar los capítulos.]


# **CAPÍTULO I: DEFINICIÓN DEL PROYECTO**
## **Origen del Proyecto**
El proyecto se origina en la identificación de una brecha tecnológica y normativa en el sistema judicial y asegurador argentino, motivada por la masificación de herramientas de inteligencia artificial con capacidad de generar imágenes fotorrealistas sintéticas o de modificar fotografías reales con un nivel de realismo suficiente para superar la inspección visual, entre ellas Midjourney, DALL-E 3 y Stable Diffusion. 
Esta dificultad está documentada empíricamente: en un experimento preregistrado con 210 participantes que debían distinguir videos *deepfake* de videos auténticos, la precisión promedio de detección alcanzó apenas el 57,6 %, cerca del azar (50 %), y los participantes tendieron a sobreestimar su propia capacidad de detección (Köbis et al., 2021). El fenómeno tampoco es exclusivo de Argentina: McLarens, firma británica de peritaje de siniestros, reportó un aumento del 300 % en los documentos sospechados de falsos en reclamos durante el primer trimestre de 2023, y Allianz advirtió que las imágenes, videos y documentos manipulados se triplicaron en uno de sus períodos de informe (Lars, 2026). Además, el informe SONAR 2025 de Swiss Re ubica a los *deepfakes* entre los riesgos emergentes más relevantes para el sector asegurador, con impacto directo en la evaluación de siniestros (Swiss Re Institute, 2025). 
El proyecto se trabaja desde el primer cuatrimestre del 2026, con un planteo inicial formulado en la cátedra Gestión de Proyectos, y dirigido a peritos técnicos judiciales. La idea inicial, en marzo de 2026, apunta a un detector de imágenes falsas para medios periodísticos y ciudadanos, que se descarta porque ese tipo de detector genérico ya existe y no aporta un valor diferencial; el foco se desplaza entonces a la imagen presentada como prueba judicial, para la que no se identifican herramientas pensadas para el contexto argentino. El trabajo de campo del Proyecto Final de Grado reformula luego la hipótesis del usuario. Dos entrevistas a peritos en ejercicio, realizadas el 20 de agosto y el 2 de septiembre de 2026, coinciden en que la cadena de custodia formal resuelve la autenticidad en su circuito, por lo que ese perfil no necesita el sistema como usuario, y una de ellas señala a las aseguradoras como el actor de mayor exposición al problema. El perito permanece, sin embargo, como destinatario natural del informe: el sistema se concibe como herramienta auxiliar de apoyo a la decisión humana, cuyos resultados son parciales y cuyo informe se diseña para que un perito pueda revisarlo y reproducirlo, criterio que se contrasta en una reunión con un referente de LegalTech.
Se identifican cuatro desencadenantes, jerarquizados según la solidez de la evidencia que los acredita. El principal es una disfunción operativa: las entrevistas al circuito pericial confirman que ese circuito no necesita el sistema, porque la cadena de custodia ya resuelve la autenticidad, y la entrevista al actor asegurador, realizada el 7 de septiembre de 2026, confirma lo inverso: en ese circuito la imagen llega sin ningún mecanismo que certifique su origen. Subordinados a este, se identifican una exigencia normativa larvada, pues la Ley de Seguros Nº 17.418 faculta al asegurador a requerir prueba instrumental razonable para verificar el siniestro (art. 46) y sanciona con la pérdida del derecho a la indemnización el uso de pruebas falsas para acreditar los daños (art. 48), sin prever un mecanismo para evaluar la autenticidad técnica de una imagen, en un contexto donde el sector asegurador internacional ya identifica a los *deepfakes* como riesgo emergente (Swiss Re Institute, 2025); una obsolescencia tecnológica relativa, pues los generadores de imágenes se democratizan sin una contraparte de verificación accesible y los sistemas de detección automatizados generalizan mal frente a técnicas no vistas (Williams, 2025); y, de menor jerarquía por depender aún de un relevamiento en curso, una oportunidad de negocio en las aseguradoras, señaladas como el actor de mayor exposición (Lars, 2026), oportunidad que el referente de LegalTech consultado extiende a otros ramos, como robo e incendio, donde asegurados o talleres pueden presentar fotografías fraudulentas de daños. El primero se sostiene con evidencia de campo primaria y directa; los restantes son condiciones de contexto que refuerzan, sin reemplazar, esa evidencia. 
## **Misión, Visión y Objetivos**
### **Misión**
Proveer a abogados litigantes y aseguradoras de una herramienta técnica accesible, explicable y ajustada al marco normativo argentino, que apoye la decisión humana al evaluar preliminarmente la autenticidad de imágenes fotográficas presentadas como prueba en causas por accidentes de tránsito y laborales. 
### **Visión**
Constituirse en una instancia de verificación técnica de referencia, previa al peritaje formal y complementaria del criterio pericial, reconocida progresivamente en el ámbito judicial y asegurador argentino como insumo confiable para fundamentar decisiones sobre la admisibilidad de la prueba fotográfica. 
### **Objetivo General**
Diseñar y desarrollar un sistema de apoyo a la decisión que permita a profesionales sin formación técnica especializada evaluar los indicios de que una imagen fotográfica haya sido generada o manipulada mediante inteligencia artificial generativa, a través de un informe explicativo en lenguaje accesible que presente los valores y umbrales que sustentan cada hallazgo. 

### **Objetivos Específicos**
**OE1: **Relevar la necesidad real de los actores involucrados mediante evidencia de campo directa, entrevistas y encuestas. 
**OE2: **Definir un enfoque metodológico multicapa que combine el análisis de metadatos EXIF/XMP, la verificación de credenciales de procedencia C2PA, el análisis de compresión de la imagen y la clasificación mediante redes neuronales convolucionales, de modo que las capas se compensen entre sí frente a las limitaciones de generalización de los sistemas de detección automatizados (Williams, 2025). 
**OE3:** Diseñar e implementar la arquitectura, los roles y permisos, el control de acceso, la auditoría, la trazabilidad de los archivos mediante una huella digital con sello de tiempo en una red pública, y las medidas de seguridad y de retención de datos, conforme a la Ley N.° 25.326 (República Argentina, 2000).
**OE4:** Construir, entrenar y validar las capas de análisis, con un clasificador cuyo desempeño alcance el valor de referencia acordado con los tutores un área bajo la curva ROC de al menos 0,90 sobre un conjunto de validación de generadores conocidos, y con un tiempo de análisis menor a 30 segundos por imagen.
**OE5: **Elaborar un informe explicativo que incluya los valores numéricos, los umbrales y un descargo de resultado parcial, y validar su comprensión sin intervención de un perito con al menos un abogado y un analista de siniestros. 
**OE6: **Desplegar el sistema en un entorno de producción y documentar su funcionamiento, alcance y limitaciones. 
## **Necesidad o Problema al que Responde**

La Tabla 1 resume los componentes del problema. Los abogados litigantes y las aseguradoras que intervienen en causas por accidentes de tránsito y laborales en Argentina no cuentan con una vía técnica accesible para verificar la autenticidad de las imágenes fotográficas presentadas como prueba, pese a que la duda se presenta con frecuencia en su práctica. La inspección visual no suple esa vía: en un experimento con videos, las personas no distinguieron de forma confiable los *deepfakes* de los contenidos auténticos y sobreestimaron su capacidad de detección (Köbis et al., 2021), evidencia que, aunque referida a video, es consistente con la duda que manifiestan los profesionales consultados. El problema se concentra, además, en el circuito informal: las imágenes llegan al abogado o a la aseguradora enviadas por las propias partes, por canales como WhatsApp o correo electrónico, sin intervención de un tercero que certifique su origen.
##### **Tabla 1.** Componentes del problema
|  |  |
| :- | :- |
| **Componente** | **Descripción** |
| Población afectada | Abogados litigantes y aseguradoras en causas por accidentes de tránsito y laborales en Argentina. |
| Situación observable | Ausencia de una vía técnica accesible para verificar la autenticidad de una imagen antes de admitirla o cuestionarla como prueba. |
| Circuito donde se presenta  | Circuito informal: imágenes enviadas por las propias partes por WhatsApp o correo, sin certificación de origen. En el circuito pericial, la cadena de custodia formal resuelve la autenticidad.  |
| Línea de base numérica | n= 11 abogados: 72,7 % dudó alguna vez de la autenticidad de una imagen; 100 % nunca solicitó una pericia técnica formal; 54,5 % no conoce herramientas adecuadas para detección y 45,5 % considera limitadas las que conoce.  |
| Ubicación/contexto | Ámbito judicial y asegurador de Corrientes y el NEA, extensible al sistema judicial argentino.  |
| Momento de referencia | agosto-septiembre de 2026. |

*Nota. Elaboración propia a partir de la entrevista a Flavia Veron (UFIE, 20/08/2026), la entrevista a Gisela Insaurralde (02/09/2026), la entrevista a Jorge Silva de Ariel Silva Asesores de Seguros SRL (07/09/2026) y la encuesta aplicada a profesionales del derecho (n=11, agosto-septiembre de 2026). *
De esta línea de base se deriva el criterio de éxito del proyecto: reducir la brecha entre duda y acción hoy detectada, mediante una vía de verificación que los usuarios puedan utilizar sin intervención de un perito, medida en un caso de prueba con imágenes de prueba, evaluado por al menos un abogado y un analista de siniestros (OE5). Se derivan también dos requisitos de diseño. El primero es que el sistema entregue un resultado interpretable sin intervención de un perito, condición priorizada por el 63,6 % de los encuestados, evitando la interpretación ambigua que la literatura atribuye a los resultados binarios sin contexto (Williams, 2025). El segundo es que el resultado se presente como apoyo a la decisión humana, con los valores y umbrales que lo sustentan y un descargo que aclara que es parcial. 
El riesgo principal identificado es que el método no alcance reconocimiento en el ámbito judicial, requisito priorizado por el 82 % de los encuestados y es el más alto de la encuesta, lo cual limitaría su adopción real con independencia del desempeño técnico del sistema. Esto es consistente con que, aun en jurisdicciones con mayor desarrollo, las reglas de autenticación de pruebas digitales frente a contenido sintético recién están en elaboración (Lars, 2026). 
Cabe distinguir, por último, el sector donde se presenta el problema del sector del que provienen los recursos del proyecto: el primero es el sector jurídico-judicial y asegurador; el segundo es el ámbito académico de la Universidad de la Cuenca del Plata, sin financiamiento del sector judicial ni asegurador.
## **ODS Asociadas y Diferenciales**
Este proyecto se enmarca dentro de los Objetivos de Desarrollo Sostenible (Naciones Unidas, 2020) en tanto responde a una necesidad concreta de integridad institucional y de innovación tecnológica aplicada a un dominio de utilidad pública. A continuación se identifican los objetivos asociados, y la Tabla 2 presenta las metas a las que contribuye el sistema.
**ODS 16 – Paz, Justicia e Instituciones Sólidas**. Constituye el objetivo asociado principal, el proyecto aporta una herramienta de verificación técnica que contribuye a la integridad de la prueba dentro del proceso judicial y asegurador, en un contexto donde la confianza en la evidencia visual está siendo cuestionada a nivel internacional por la industria aseguradora, la práctica forense y los propios tribunales (Lars, 2026). 
**ODS 9 – Industria, Innovación e Infraestructura. **Se asocia de modo secundario, en tanto el proyecto aplica inteligencia artificial a un dominio de utilidad pública para el que el relevamiento realizado no identifica soluciones locales específicas. 
##### **Tabla 2.** Metas de los ODS a las que contribuye el sistema 
|  |  |  |
| :- | :- | :- |
| ODS | Meta | Contribución del sistema |
| 16 | 16.3: promover el estado de derecho y garantizar la igualdad de acceso a la justicia  | Ofrece a profesionales sin formación técnica una vía accesible para evaluar la autenticidad de la prueba fotográfica  |
| 16 | 16.6: crear instituciones eficaces y transparentes que rindan cuentas  | Registra cada análisis con huella digital, sello de tiempo y auditoría, y explicita valores, umbrales y limitaciones  |
| 9 | 9.5: mejorar la capacidad tecnológica  | Aplica técnicas de análisis forense e inteligencia artificial a un problema local, con un clasificador que se reentrena por versiones frente a los generadores nuevos  |

*Nota. Elaboración propia a partir de Naciones Unidas (2020). *
### **Diferenciales del Proyecto **
Los diferenciales responden a una lógica de posicionamiento estratégico: el sistema no compite en generalidad de detección frente a las herramientas internacionales, sino en la adecuación al marco normativo y a los requisitos del usuario judicial y asegurador argentino (Porter, 2018). En primer lugar, la explicabilidad del resultado: el informe presenta una clasificación acompañada de los valores numéricos y los umbrales que sustentan cada hallazgo, en lenguaje accesible y sin exponer el código del algoritmo, lo que responde al problema de interpretación ambigua atribuido a las herramientas de detección disponibles (Williams, 2025). En segundo lugar, el enfoque multicapa, que combina dos capas deterministas, verificables y reproducibles (metadatos EXIF/XMP y credenciales de procedencia C2PA), una capa intermedia de análisis de compresión y un clasificador probabilístico. El informe distingue así los indicios verificables de las estimaciones estadísticas, en línea con la práctica forense que prioriza el origen y la trazabilidad del archivo por sobre su apariencia (Lars, 2026).
En tercer lugar, el apoyo a la decisión humana: el sistema no emite conclusiones definitivas, incluye un descargo que aclara que el resultado es parcial y no reemplaza el dictamen de un perito, y toma como marco de referencia para su auditabilidad el Reglamento de Inteligencia Artificial de la Unión Europea (Parlamento Europeo y Consejo de la Unión Europea, 2024) y la norma ISO/IEC 42001 (International Organization for Standardization \[ISO\], 2023). En cuarto lugar, la trazabilidad de los archivos y del propio sistema: cada imagen recibe al cargarse una huella digital SHA-256, cuyo sello de tiempo se registra en Hedera Consensus Service, una red pública que guarda únicamente la huella y no el archivo (Hedera Hashgraph, s. f.). El mismo mecanismo sella cada informe en PDF, que cualquier tercero puede verificar mediante un código QR sin acceder a los datos del caso, y cada versión desplegada del software, de modo que puede acreditarse con qué código se realiza cada análisis. El plan original contemplaba Blockchain Federal Argentina, que se reemplaza durante el desarrollo por las razones expuestas en el Capítulo IX.
En quinto lugar, el encuadre normativo argentino desde el diseño: la infraestructura se aloja en Amazon Web Services, región Irlanda, jurisdicción reconocida por la Agencia de Acceso a la Información Pública (AAIP) como de nivel adecuado de protección conforme al artículo 12 de la Ley N.° 25.326 (República Argentina, 2000) y alcanzada además por el Reglamento General de Protección de Datos de la Unión Europea (Amazon Web Services, 2026). En sexto lugar, la adecuación al rubro: el informe adopta el vocabulario de cada perfil, con expediente, prueba y pericia para el abogado, y siniestro, liquidación e inspección para la aseguradora, y se reduce a dos páginas, porque quien analiza imágenes todos los días no puede leer un documento extenso.
## **Descripción Breve del Sistema de Información **
Plataforma web de apoyo a la decisión humana que permite a abogados litigantes y a personal de aseguradoras organizar por caso las imágenes fotográficas presentadas como prueba y obtener un informe explicativo, en el lenguaje de cada rubro, con los indicios que sustentan la posibilidad de que dichas imágenes hayan sido generadas o manipuladas mediante inteligencia artificial generativa. El análisis combina los metadatos, las credenciales de procedencia, la compresión y el contenido visual del archivo, y cada imagen e informe queda registrado con un sello de tiempo verificable públicamente. 
## **Descripción Detallada del Sistema de Información**
El sistema opera como una instancia de apoyo a la decisión, categoría que se distingue de un sistema transaccional en que provee información estructurada para sostener un juicio humano (Kendall y Kendall, 2005), dentro de la evaluación preliminar que realiza el abogado o el área de siniestros de una aseguradora. Cada usuario se registra con un perfil, Abogado o Aseguradora, que no puede modificarse después y que define el lenguaje de la plataforma y del informe; el registro admite además la cuenta de Google, mediante OpenID Connect. El abogado trabaja en un espacio personal gratuito y puede crear un estudio jurídico. La aseguradora, en cambio, se registra eligiendo su empresa del catálogo de entidades activas de la Superintendencia de Seguros de la Nación; el administrador aprueba ese registro, y los empleados se incorporan solo por invitación. En cada organización, un referente invita a los miembros y define los permisos sobre cada caso: responsable, colaborador o lector. El administrador consulta estadísticas agregadas y gestiona los planes, sin acceder nunca al contenido de los casos. La contratación de los planes de organización se cobra en línea mediante Mercado Pago, con un pago simulado mientras se completa la integración, y la verificación de la identidad de quien registra una aseguradora se realiza mediante Identik [integración con su entorno de pruebas en curso]. El rol de perito, contemplado al inicio del proyecto, queda excluido conforme a la evidencia de campo relevada, aunque el informe se diseña para que un perito pueda revisarlo y reproducirlo.
El uso del sistema comienza cuando el usuario crea un caso, cuya pantalla se organiza en tres etapas sucesivas: carga, análisis e informe. Las imágenes ingresan por tres caminos: desde la computadora; desde el celular del propio usuario, mediante un código QR que abre un enlace de un solo uso; o mediante un enlace que se envía a la persona afectada, quien sube sus fotografías sin crear una cuenta, después de aceptar una declaración expresa. Cada imagen registra por cuál de esos caminos ingresa, lo que suma información a la cadena de custodia. Al recibirla, el sistema valida el formato real del archivo, que puede ser JPEG, PNG o HEIC (el formato nativo del iPhone), calcula su huella digital SHA-256 y registra su sello de tiempo en la red pública Hedera. Luego ejecuta en segundo plano las cuatro capas de análisis, de forma independiente, y muestra el progreso por imagen y por capa.
Las cuatro capas se complementan entre sí. La primera lee los metadatos EXIF/XMP con ExifTool y Pillow, y aplica reglas de severidad (directo, fuerte, moderado, débil y neutro) a hallazgos como el software de edición declarado, el historial de ediciones o las fechas imposibles. La segunda lee el manifiesto C2PA, o credenciales de contenido, y verifica su firma con c2pa-python contra la lista de confianza del consorcio (C2PA, s. f.). Un manifiesto válido que declara generación por IA constituye el indicio más fuerte del sistema; su ausencia, en cambio, no se interpreta como evidencia de autenticidad, porque el manifiesto se pierde con la recompresión o con una captura de pantalla. Estas dos capas son deterministas, es decir, verificables, reproducibles y comprobables por terceros. La tercera aplica un análisis de niveles de error (ELA) por bloques, que señala regiones con una historia de compresión distinta al resto de la imagen y produce un mapa visual. Se utiliza como señal complementaria, con validez limitada en los formatos HEIC y PNG. La cuarta es un clasificador de redes neuronales convolucionales, entrenado en PyTorch mediante transferencia de aprendizaje y ejecutado en producción con ONNX Runtime, que estima la probabilidad de que la imagen sea íntegramente sintética aun cuando no conserve ningún metadato. Cada capa devuelve un estado (evaluada, no evaluable o error), un nivel de indicio y una lista de anomalías, y el motor de reglas expresa la conclusión final como sin indicios o con indicios débiles, moderados o fuertes, nunca como veredicto.
El informe que resulta de ese proceso adopta el vocabulario de cada rubro (expediente, prueba y pericia para el abogado; siniestro, liquidación e inspección para la aseguradora) y se reduce a dos páginas. Presenta la cronología de custodia de cada imagen y separa los resultados deterministas de los probabilísticos, dado que un indicio determinista tiene mayor peso. Para cada hallazgo expone los valores y los umbrales aplicados, sin revelar el código del algoritmo, e indica con qué versión del sistema se realiza el análisis. Incluye además el descargo de resultado parcial y la recomendación de consultar a un profesional experto. La huella del propio PDF también se registra en Hedera, y un código QR, junto con un código de doce caracteres, conduce a una página pública donde el navegador de quien verifica calcula la huella del archivo y la compara con el registro, sin subir el documento y sin mostrar datos del caso. Una guía pública explica además cómo realizar esa comprobación directamente en Hedera, sin depender de la plataforma, a partir de la red y el tema que el propio informe indica.
Todo esto se apoya en una arquitectura de software organizada en capas (rutas, servicios, repositorios y modelos), separación que responde al principio de modularidad como criterio de diseño para facilitar el mantenimiento y la incorporación de funcionalidades (Pressman, 2011), y que una herramienta automática verifica en cada cambio. El backend usa Flask 3.1 sobre Python y expone una API REST; persiste los datos en PostgreSQL mediante SQLAlchemy y Alembic, y procesa los análisis en segundo plano con Redis y RQ. La interfaz es una aplicación React, servida como archivos estáticos. El acceso a datos aplica el patrón Repository, la lógica de negocio se organiza como Service Layer, y el patrón Strategy permite intercambiar las capas de análisis, el almacenamiento, la cola de trabajos y el proveedor del sello de tiempo sin modificar el resto del sistema. Esa flexibilidad se pone a prueba durante el desarrollo, cuando el sello debe migrar de Blockchain Federal Argentina a Hedera.
El sistema se despliega en Amazon Web Services, región Irlanda, con la infraestructura definida como código en Terraform. La aplicación, la base de datos y la cola corren en una instancia de Amazon EC2, detrás de Nginx y Gunicorn, con tráfico cifrado mediante certificado TLS. Las imágenes y los informes se guardan en buckets privados de Amazon S3, con cifrado en reposo, versionado y acceso mediante URL firmadas de corta duración, y los secretos se resguardan en Parameter Store. Cada cambio integrado que supera las pruebas automatizadas se despliega de forma automática, con retorno a la versión anterior si la nueva no responde, y la huella de cada versión desplegada se registra también en Hedera. El sello se registra en la red de pruebas de Hedera (*testnet*), que es pública y verificable, decisión que se mantiene para la defensa del proyecto (Capítulo IX).
Dado que las imágenes de siniestros pueden contener datos de salud, se tratan como información de máxima confidencialidad. Se aplica una política de retención de cinco años, con aviso previo y destrucción de los datos cuando dejan de ser necesarios (República Argentina, 2000, art. 4, inc. 7), y cada operación relevante queda en un registro de auditoría. Por último, la calidad del código se gestiona con pytest, flake8, pylint y ESLint, integrados en un flujo de integración continua en GitHub Actions.

# **CAPÍTULO II: RELEVAMIENTO E INVESTIGACIÓN DE MERCADO**
## **Fuentes de Datos Utilizadas**
El proyecto se apoya de diferentes fuentes primarias y secundarias.
Las fuentes primarias comprenden cuatro entrevistas, una encuesta y un conjunto de pruebas experimentales propias. La primera entrevista se inicia el 20 de agosto de 2026, de forma asincrónica por WhatsApp (mensajes de texto y audios, estos últimos transcritos mediante una herramienta de IA), a Flavia Veron, Licenciada en Criminalística de la Unidad Fiscal de Investigaciones Estratégicas (UFIE) del Poder Judicial de la provincia de Corrientes, y se completa con las respuestas recibidas el 24 de agosto; su objetivo es relevar de manera exploratoria si el circuito pericial constituye un usuario con necesidad real del sistema. La segunda entrevista se realiza el 2 de septiembre de 2026, por videollamada, a la perito Gisela Insaurralde, con el objetivo de contrastar esa primera conclusión con un segundo perfil pericial. La tercera se realiza el 7 de septiembre de 2026, por teléfono, a Jorge Silva, de Ariel Silva Asesores de Seguros SRL, productor de seguros de alcance regional en Corrientes, Chaco y el NEA, y aporta la perspectiva del lado asegurador. La cuarta se realiza el 2 de octubre de 2026, por Google Meet, a Federico Miskinich, referente de LegalTech en Corrientes, con el objetivo de contrastar el diseño del sistema con la mirada del sector tecnológico-jurídico local, y aporta el enfoque de apoyo a la decisión humana, los marcos de referencia para la auditabilidad y la propuesta de trazabilidad mediante Blockchain Federal Argentina. A estas entrevistas se suma la encuesta aplicada a profesionales del derecho, mediante un formulario autoadministrado difundido por muestreo de conveniencia entre el 24 de agosto y el 1 de septiembre de 2026, con 11 respuestas registradas al corte de esta entrega. Completan el relevamiento primario las pruebas de canales realizadas en septiembre de 2026 sobre imágenes generadas con ChatGPT y Gemini, que verifican de forma empírica la persistencia de las credenciales de procedencia C2PA según el canal de envío.
Como fuentes secundarias se utilizan normas nacionales, la Ley de Seguros N.° 17.418 (República Argentina, 1967) y la Ley N.° 25.326 de Protección de Datos Personales (República Argentina, 2000); normas y estándares internacionales de referencia, el Reglamento (UE) 2024/1689 de Inteligencia Artificial (Parlamento Europeo y Consejo de la Unión Europea, 2024), la norma ISO/IEC 42001 (International Organization for Standardization \[ISO\], 2023) y la especificación técnica del estándar C2PA (C2PA, s. f.); bibliografía técnica y de divulgación sobre detección de contenido generado o manipulado por IA (Köbis et al., 2021; Lars, 2026; Williams, 2025; Swiss Re Institute, 2025); y bibliografía de referencia en análisis de sistemas (Kendall y Kendall, 2005), ingeniería de software (Pressman, 2011) y estrategia competitiva (Porter, 2018), aplicada para fundamentar las decisiones de arquitectura y de posicionamiento del sistema, respectivamente.
Cada dato estadístico tomado de fuentes secundarias se somete a la regla de las tres preguntas: quién lo produjo, con qué método y universo, y para qué período de referencia. La precisión de detección del 57,6 % es producida por Köbis et al. (2021) mediante un experimento preregistrado con 210 participantes, que debían distinguir videos *deepfake* de videos auténticos, publicado en 2021 y vigente como referencia académica. El incremento del 300 % en documentos sospechados de ser falsos es reportado por McLarens, firma británica de peritaje de siniestros, para el primer trimestre de 2023, y el triple de imágenes, videos y documentos manipulados es advertido por Allianz en uno de sus períodos de informe, ambos según recoge Lars (2026). Dado que se trata de datos informados por las propias empresas y no de mediciones independientes, se toman como indicio de tendencia y no como medida del fenómeno.
## **Instrumentos Utilizados, Dinámicas Aplicadas y Alcance**
Se elabora un guion de entrevista (Anexo C) con las preguntas relevantes para indagar el protocolo de verificación de autenticidad en el trabajo pericial: en qué se basa el perito para dar por auténtica una imagen, si revisa datos ocultos del archivo, qué herramientas utiliza, por qué canal recibe el material y qué ocurre cuando ese material es de baja calidad. A Flavia Veron, Licenciada en Criminalística de la UFIE, se le consulta un subconjunto de esas preguntas, las de mayor interés para el diagnóstico, de forma asincrónica por WhatsApp, con transcripción de los audios mediante una herramienta de IA y revisión manual posterior, con el propósito de explorar si el perito constituye un usuario con necesidad real del sistema.
La entrevista a la perito Gisela Insaurralde se realiza con el propósito de contrastar lo relevado en la primera entrevista con un segundo perfil pericial y de identificar otros actores expuestos al problema. Se aplica por videollamada sincrónica en la plataforma Webex, con notas tomadas durante la sesión.
A Jorge Silva, de Ariel Silva Asesores de Seguros SRL, se lo entrevista a partir de un guion elaborado para el actor asegurador (Anexo B), del cual se seleccionan y adaptan las preguntas más pertinentes a medida que fluye la conversación: si la autenticidad de las imágenes constituye un problema en su práctica y por qué circuito llegan habitualmente esas imágenes hasta la aseguradora. Se aplica por teléfono, con el propósito de obtener una primera aproximación desde el lado asegurador.
La reunión con Federico Miskinich se desarrolla por Google Meet y combina una demostración preliminar de la plataforma, con la pantalla compartida, y una conversación semiestructurada sobre el diseño del sistema: las capas de análisis, la redacción de las advertencias para que la herramienta no sea considerada una verdad absoluta, la estructura del informe, los marcos de referencia para la auditabilidad y la trazabilidad de las operaciones. El registro se realiza mediante las notas automáticas que genera la plataforma, revisadas manualmente (Anexo I), y la grabación de la sesión. Su propósito es contrastar el diseño con la mirada del sector tecnológico-jurídico local.
La encuesta a profesionales del derecho se construye con 16 preguntas cerradas y abiertas (Anexo A) sobre perfil profesional, frecuencia de la prueba fotográfica en sus causas, dudas previas sobre autenticidad, conocimiento de herramientas de IA generativa y requisitos priorizados para una eventual herramienta de verificación. Se difunde mediante un formulario autoadministrado, por muestreo de conveniencia, con el propósito de cuantificar la necesidad relevada de forma cualitativa en las entrevistas.
Las pruebas de canales (Anexo J) consisten en generar una imagen en cada plataforma, ChatGPT y Gemini, descargarla directamente y enviarla por cinco vías: descarga directa, WhatsApp como foto, WhatsApp como documento, correo electrónico como archivo adjunto y captura de pantalla. Los envíos se realizan desde un teléfono móvil y desde una cuenta de Gmail. Para cada archivo se calcula el SHA-256, se vuelcan los metadatos con ExifTool 13.59 y se busca el manifiesto C2PA; el original se contrasta además con el verificador oficial de Content Credentials. Su propósito es comprobar de forma empírica qué información de procedencia sobrevive en cada canal.
El alcance de los instrumentos es exploratorio. El muestreo no probabilístico no permite generalizar estadísticamente al universo de abogados ni de productores de seguros de la región, y el lado asegurador se apoya en una única entrevista, por lo que se lo toma como una primera aproximación. Las pruebas de canales se limitan a dos generadores y a una imagen por generador, y sus resultados valen para el dispositivo, la versión y el servicio utilizados. Aun así, los instrumentos permiten relevar tendencias consistentes entre los distintos actores consultados y contrastar los supuestos de diseño.
## **Presentación de Datos Recabados**
##### **Tabla 3**. Perfil de la muestra, años de ejercicio profesional
|  |  |
| :- | :- |
| **Años de ejercicio profesional** | **%** |
| Menos de 5 años | 27,3 % |
| 5 a 10 años | 36,4 % |
| 10 a 20 años  | 9,1 % |
| Más de 20 años | 27,3 % |

*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026. *
##### **Tabla 4**.  Perfil de la muestra, ámbito de trabajo 
|  |  |
| :- | :- |
| **Ámbito de trabajo** | **%** |
| Independiente | 36,4 % |
| Ambos (independiente + estudio) | 27,3 % |
| Estudio jurídico | 18,2 % |
| Poder Judicial | 9,1 % |
| Superior Tribunal de Justicia | 9,1 % |

*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026. *
##### **Tabla 5.** Resultados de la encuesta a abogados 
|  |  |
| :- | :- |
| **Pregunta** | **Resultado** |
| Frecuencia con que la prueba fotográfica es central en la causa  | Siempre 9,1 % ; Casi siempre 45,5 % ;  A veces 36,4 % ; Casi nunca 9,1 %  |
| Dudó alguna vez de la autenticidad de una imagen probatoria  | Sí 45,5 %; Tal vez 27,3 % ; No 27,3 %  |
| Conocía previamente herramientas de IA generativa fotorrealista  | Sí 90,9 % ; No 9,1 %  |
| Solicitó alguna vez una pericia técnica para resolver esa duda  | No, en el 100 % de los casos  |
| Considera que existen hoy herramientas suficientes de verificación  | No conoce ninguna 54,5 % ; Conoce, pero son limitadas 45,5  %  |
| Requisitos priorizados para una herramienta de verificación (selección múltiple)  | Método validado/reconocido judicialmente 81,8 %;  Reporte comprensible sin perito 63,6 %; Resultado en pocos segundos 54,5 %; Confidencialidad total 45,5 %  |
| Utilidad de un reporte técnico para fundamentar un pedido de pericia o una presentación judicial  | Sí 90,9 %; como apoyo, pero no como prueba en sí 9,1 %  |
| Usaría el sistema si estuviera disponible  | Sí, seguro 72,7 %; Probablemente sí 27,3 %  |

*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026. Instrumento: formulario autoadministrado de 16 preguntas, difundido por muestreo de conveniencia. *
Flavia Veron, Licenciada en Criminalística de la UFIE, entrevistada el 20 de agosto de 2026, señala que sus informes periciales se basan en material obtenido directamente por el propio equipo pericial, o certificado por un perito de policía interviniente, de modo que no suele recibir ni necesitar verificar imágenes de fuentes externas. 
La perito Gisela Insaurralde, entrevistada el 2 de septiembre de 2026, confirma el mismo circuito: al trasladarse ella misma al lugar del hecho y obtener el material original, la cadena de custodia queda resuelta desde el origen. Señala, a las aseguradoras como el actor más expuesto al problema. Considera, además, que el problema es real y que la idea del sistema tiene sentido 
Jorge Silva, de Ariel Silva Asesores de Seguros SRL, entrevistado el 7 de septiembre de 2026, indica que en los siniestros de particulares generalmente son los propios accidentados quienes envían las imágenes del hecho, sin intervención de un tercero que certifique su origen, y que en ese circuito existe el problema de la autenticidad.  
Federico Miskinich, entrevistado el 2 de octubre de 2026, recomienda que el sistema funcione como herramienta de apoyo con intervención humana, con un descargo que aclare que el resultado es parcial, y que su auditabilidad se base en el Reglamento de Inteligencia Artificial de la Unión Europea y en la norma ISO/IEC 42001. Sugiere que el informe incluya los valores esperados y los recuperados que justifican cada hallazgo, expresados en porcentajes y términos estadísticos y no como certezas, sin revelar el algoritmo, y que se evalúe Blockchain Federal Argentina para registrar la huella digital y la fecha de cada archivo. Señala además que el análisis de niveles de error (ELA) se considera desactualizado desde 2018 como método principal de detección, aunque sigue siendo funcional, y que conviene investigar métodos más recientes. Advierte, por último, que los peritos y criminalistas pueden reaccionar con resistencia si perciben que el sistema busca reemplazarlos, por lo que aconseja presentarlo como herramienta auxiliar, y propone extender el caso de uso a robo e incendio en el sector asegurador. 
##### **Tabla 6.** Persistencia del manifiesto C2PA según el canal de envío 
|  |  |  |
| :- | :- | :- |
| Canal | ChatGPT | Gemini |
| Descarga directa  | Manifiesto presente  | Manifiesto presente  |
| WhatsApp como documento  | Archivo idéntico, manifiesto intacto  | Archivo idéntico, manifiesto intacto  |
| Correo como adjunto | Archivo idéntico, manifiesto intacto  | Archivo idéntico, manifiesto intacto  |
| WhatsApp como foto  | Convertido a JPEG, manifiesto perdido  | Recomprimido, manifiesto perdido  |
| Captura de pantalla  | Manifiesto perdido  | Manifiesto perdido  |

*Nota. Elaboración propia. Una imagen por generador (ChatGPT: PNG de 1536 × 1024 px; Gemini: JPEG de 2816 × 1536 px). Resultado preliminar. *
## **Presentación de Gráficos y Variables de Análisis**
El formulario aplicado a los abogados consta de 16 preguntas. Cuatro corresponden a datos de identificación y perfil profesional (nombre, área de práctica, años de ejercicio y ámbito de trabajo), ya presentadas en las Tablas 3 y 4. La pregunta sobre cómo se resuelve la necesidad de pericia queda sin respuestas, dado que ningún encuestado solicitó pericia técnica, y la de sugerencias adicionales es abierta y se retoma como comentario cualitativo. Dos preguntas cerradas resultan unánimes, la importancia percibida de contar con una herramienta de verificación y la expectativa de que esa necesidad sea mayor en los próximos años, ambas con el 100 % de las respuestas en la misma opción; junto con la de solicitud de pericia técnica (100 % de respuestas negativas), estos tres resultados se retoman como dato puntual en el análisis, sin graficar. Las siete preguntas cerradas restantes, con variación real de respuesta, se presentan como variables de análisis en las siguientes figuras. 
Las Figuras 1 a 7 presentan las siete variables de la encuesta con variación de respuesta.

##### **Figura 1. **Frecuencia de la prueba fotográfica como elemento central en la causa \[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026.*
##### **Figura 2. **Dudas sobre la autenticidad de una imagen presentada como prueba
\[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026.*
##### **Figura 3.** Conocimiento previo de herramientas de IA generativa fotorrealista 
\[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026. *
##### **Figura 4.** Percepción sobre la disponibilidad actual de herramientas de verificación 
##### \[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026.*
##### **Figura 5.** Utilidad percibida de un reporte técnico para fundamentar un pedido de pericia o una presentación judicial 
\[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026.*
##### **Figura 6.** Requisitos priorizados para una herramienta de verificación
\[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026. *
##### **Figura 7.** Intención de uso del sistema propuesto
\[image\]
*Nota. n = 11. Elaboración propia a partir de la encuesta aplicada a profesionales del derecho, agosto-septiembre de 2026. *
## **Análisis de Información **
De las tres entrevistas realizadas a actores del circuito de la prueba, dos se ubican en el circuito formal (los dos peritos) y una en el circuito informal (asegurador). Esta proporción no debe leerse como una medida de qué circuito predomina, porque la muestra es demasiado pequeña e intencional para eso, sino como una confirmación de la hipótesis de diseño formulada al inicio: el circuito formal, donde la autenticidad ya está resuelta por diseño, corresponde al perito, descartado como usuario; el circuito informal, donde el problema efectivamente se presenta, corresponde al actor que el sistema busca asistir (aseguradores, junto con los abogados litigantes que reciben la misma clase de material sin certificación de origen). La coincidencia entre quién resuelve el problema por su propio circuito y quién queda fuera del sistema y, en el otro extremo, entre quién no lo resuelve y quién es el usuario objetivo es la validación cualitativa más sólida del reposicionamiento de usuario.
La brecha entre duda y acción es el hallazgo cuantitativo central: el 72,7 % de los abogados dudó o tal vez dudó de la autenticidad de una imagen probatoria (45,5 % "sí", 27,3 % "tal vez"), pero el 100 % nunca solicitó una pericia formal para resolver esa duda. Esto es consistente con el hallazgo de Köbis et al. (2021), referido a video, sobre la tendencia a adoptar una heurística de "ver para creer" antes que a cuestionar activamente el contenido visual. Esta brecha también puede leerse como una escalera de demanda: la demanda imaginada y declarada es alta y coincidente, pues el 100 % calificó como "muy importante" contar con una herramienta de este tipo y el 100 % espera que esa necesidad sea mayor en los próximos años, mientras que la demanda revelada por la conducta efectiva es nula, porque nadie solicitó una pericia pese a haber dudado. Esa distancia entre lo declarado y lo revelado confirma que el problema no se resuelve solo, y que la ausencia de una vía accesible, no la falta de interés, es la barrera real.
El 90,9 % de los encuestados (10 de 11) considera que un reporte técnico de este tipo sería útil para fundamentar un pedido de pericia o una presentación judicial. El único caso que matiza esa respuesta (podría servir como apoyo, pero no como prueba en sí) es significativo: anticipa, desde la propia encuesta, la misma tensión que después aparece como riesgo principal del proyecto, entre el valor de un reporte técnico como insumo de decisión y su reconocimiento como prueba autónoma en un proceso judicial. Esa reserva coincide con la recomendación del referente de LegalTech consultado de presentar el sistema como herramienta de apoyo con intervención humana.
Los requisitos más priorizados, la validación judicial del método y la comprensibilidad sin perito, superan a la velocidad y la confidencialidad, que prioriza una proporción menor de los encuestados (Tabla 5), en línea con la advertencia de Williams (2025) sobre el riesgo de resultados ambiguos. El 90,9 % ya conocía la existencia de herramientas de IA generativa fotorrealista y ninguno percibe que existan hoy herramientas suficientes: el problema radica en la ausencia de una respuesta técnica accesible, no en el desconocimiento de la amenaza.
El riesgo principal identificado es que el requisito más priorizado, la validación judicial del método, dependa de factores externos al desarrollo técnico. Esto es consistente con que, aun en jurisdicciones con mayor desarrollo, las reglas de autenticación de pruebas digitales frente a contenido sintético recién están en elaboración (Lars, 2026), y con la reserva expresada por el único encuestado que no considera al reporte técnico una prueba autónoma.
Los hallazgos se traducen en decisiones de diseño. La demanda de un resultado comprensible sin perito se resuelve con un informe que presenta la clasificación junto con los indicios, los valores y los umbrales que la sustentan. La demanda de validación judicial se aborda priorizando capas deterministas y reproducibles y registrando la versión de cada componente en cada resultado. La confidencialidad, aun en una arquitectura cloud, se resuelve con almacenamiento privado y cifrado en la región Irlanda de AWS, control de acceso por rol y auditoría.
Las pruebas de canales muestran que el manifiesto C2PA sobrevive cuando el archivo llega sin recodificar (WhatsApp como documento, correo como adjunto) y se pierde con la recompresión o la captura de pantalla (Tabla 6). Su presencia constituye un indicio fuerte; su ausencia no prueba nada. Como el circuito informal descrito por el productor de seguros es el envío de imágenes por WhatsApp o correo, es plausible que muchas imágenes lleguen sin credenciales, lo que fundamenta combinar la capa C2PA con el análisis de metadatos, de compresión y de contenido visual. Se trata de una inferencia a partir de pruebas preliminares, con dos generadores y una imagen por generador.
La reunión con el referente de LegalTech aporta tres contrastes. Refuerza el enfoque de apoyo con intervención humana, en línea con la reserva del encuestado que no considera al reporte una prueba autónoma. Señala que el análisis de niveles de error se considera desactualizado como método principal de detección, por lo que se conserva como señal complementaria y se evalúan alternativas más recientes. Y advierte que peritos y criminalistas pueden resistirse a un sistema que perciban como sustituto, por lo que se lo presenta como auxiliar. Esta advertencia se contrasta con las dos entrevistas periciales, que no identifican necesidad del sistema en su propio circuito, sin que ello desconozca el rol del perito como destinatario del informe.

# **CAPÍTULO III: ENTORNO Y DOMINIO DEL SISTEMA DE INFORMACIÓN**
## **Entorno del Sistema de Información**
La Tabla 7 resume el entorno. El entorno comprende los actores, organismos, normas y servicios externos con los que el sistema se relaciona sin formar parte de él. Los actores del circuito de la prueba fotográfica se distribuyen entre los usuarios del sistema y otros participantes que condicionan su uso. Los organismos y normas fijan las exigencias de protección de datos y de admisibilidad de la prueba. Los servicios externos proveen la infraestructura y las fuentes de verificación sobre las que opera el sistema. 
##### **Tabla 7**. Entorno del sistema 
|  |  |  |
| :- | :- | :- |
| **Elemento** | **Tipo** | **Relación con el sistema** |
| Abogado litigante  | Usuario | Crea casos, carga imágenes y obtiene informes; puede crear un estudio jurídico.  |
| Aseguradora (analista de siniestros)  | Usuario | Evalúa imágenes de siniestros antes de aceptar o cuestionar un reclamo, dentro de la organización de su empresa. |
| Administrador | Usuario Interno | Aprueba el registro de aseguradoras, gestiona los planes y consulta estadísticas agregadas; no accede al contenido de los casos, imágenes ni informes. |
| Partes y asegurados (persona afectada) | Actor externo  | Envían las imágenes por WhatsApp o correo, o las suben directamente al caso mediante un enlace, sin cuenta y con una declaración expresa  |
| Perito  | Actor externo  | Destinatario del informe, que puede revisarlo y reproducirlo; no es usuario  |
| Productores y asesores de seguros  | Actor externo  | Canal por el que llegan los reclamos a las aseguradoras  |
| Poder Judicial  | Actor externo  | Decide la admisibilidad y el valor de la prueba; no usa el sistema  |
| Agencia de Acceso a la Información Pública (AAIP)  | Organismo  | Fija el criterio de adecuación para las transferencias internacionales de datos  |
| Superintendencia de Seguros de la Nación (SSN)  | Organismo  | Supervisa a las aseguradoras y publica el catálogo de entidades con el que se valida el registro  |
| Hedera Consensus Service  | Servicio | Registra el sello de tiempo de la huella de cada imagen, de cada informe y de cada versión del sistema  |
| Google | Servicio | Permite el registro y el inicio de sesión mediante OpenID Connect  |
| Amazon Web Services  | Servicio  | Aloja la aplicación, la base de datos y los archivos  |
| Mercado Pago | Servicio | Gestiona el cobro en línea de los planes de organización (integración en curso; reemplaza a Cresium, evaluado antes)  |
| Identik | Servicio | Verifica la identidad de quien registra una aseguradora (integración con su entorno de pruebas en curso)  |
| Microsoft Clarity  | Servicio | Registra, durante el período de prueba, mapas de calor y recorridos de uso, con el contenido enmascarado  |
| Lista de confianza de C2PA  | Servicio  | Permite verificar la firma de los manifiestos de procedencia  |
| Generadores de imágenes (ChatGPT, Gemini, entre otros)  | Servicio  | Emiten credenciales de procedencia en los archivos que producen  |
| Canales de transmisión (WhatsApp, correo, captura de pantalla)  | Canal  | Condicionan qué información conserva el archivo al llegar  |
| Servicio de correo electrónico (Amazon SES)  | Servicio | Envía las notificaciones del sistema desde el dominio propio  |
| Registrador de dominio (DonWeb, NIC Argentina)  | Servicio | Registra el dominio evidentiaa.com.ar  |
| Hugging Face  | Servicio | Provee los conjuntos de datos de entrenamiento y guarda las versiones del clasificador en un registro privado  |

*Nota. Elaboración propia a partir del relevamiento del Capítulo II. *
El marco normativo del entorno comprende la Ley N.° 25.326 de Protección de Datos Personales (República Argentina, 2000), en particular los artículos 4, 9 y 12, relativos a la destrucción de los datos, su seguridad y las transferencias internacionales; la Ley de Seguros N.° 17.418 (República Argentina, 1967), cuyo artículo 46 faculta al asegurador a requerir prueba instrumental razonable para verificar el siniestro y cuyo artículo 48 sanciona el fraude por prueba falsa;  y el Código Procesal Civil y Comercial de la Provincia de Corrientes, Ley N.° 6556 (Provincia de Corrientes, 2021), que rige la prueba en los procesos civiles de la jurisdicción donde se releva el problema. Como referencia para la auditabilidad, y no como exigencia de cumplimiento, se toman el Reglamento de Inteligencia Artificial de la Unión Europea (Parlamento Europeo y Consejo de la Unión Europea, 2024) y la norma ISO/IEC 42001 (International Organization for Standardization \[ISO\], 2023). 
## **Dominio del Sistema de Información**
El dominio es la verificación técnica de la autenticidad de la prueba fotográfica digital en causas judiciales por accidentes de tránsito y laborales y en la evaluación de siniestros por parte de aseguradoras. En ese dominio, la fotografía se presenta como prueba documental de daños, lesiones y circunstancias del hecho, y su valor depende de que refleje lo que efectivamente ocurrió. Los conceptos que estructuran el dominio son los de la Tabla 8. 
##### **Tabla 8.** Conceptos del dominio 
|  |  |
| :- | :- |
| **Concepto** | **Definición aplicada** |
| Imagen generada  | Imagen creada desde cero por un modelo de IA generativa, sin captura de una escena real  |
| Imagen manipulada  | Fotografía real alterada mediante edición, convencional o generativa  |
| Circuito formal  | Circuito en el que el perito obtiene el material directamente de la fuente y la cadena de custodia certifica su origen  |
| Circuito informal  | Circuito en el que las partes envían las imágenes por WhatsApp o correo, sin certificación de origen  |
| Indicio determinista  | Hallazgo verificable y reproducible a partir de reglas explícitas, como un metadato o una firma criptográfica  |
| Indicio probabilístico  | Estimación estadística de un modelo entrenado, no justificable regla por regla  |
| Credencial de procedencia (C2PA)  | Manifiesto firmado, incrustado en el archivo, que registra su origen y las ediciones aplicadas  |

*Nota. Elaboración propia a partir de Köbis et al. (2021), Lars (2026) y el relevamiento del Capítulo II. *
La operación del dominio presenta dos circuitos con necesidades distintas. En el formal, la autenticidad se resuelve por la cadena de custodia y no requiere el sistema. En el informal, donde las imágenes llegan por los canales de las partes, no existe un mecanismo que certifique su origen, y es allí donde el sistema aporta valor. 
## **Alcance **
### **Del Sistema de Información**
El sistema permite registrarse con correo y contraseña o con la cuenta de Google, en los perfiles Abogado o Aseguradora, y trabajar en un espacio personal o dentro de una organización, sea un estudio jurídico o una aseguradora, con invitación de miembros y permisos por caso. Una portada pública presenta el servicio y los planes, y conduce al registro con el plan ya elegido. El sistema incluye la gestión de casos con ciclo de vida, búsqueda y colaboración, y la carga de imágenes JPEG, PNG y HEIC desde la computadora, desde el celular mediante un código QR, o por parte de la persona afectada mediante un enlace con declaración expresa. Cada imagen recibe su huella SHA-256 y su sello de tiempo en Hedera, y se analiza con cuatro capas: metadatos EXIF/XMP, credenciales C2PA, análisis de niveles de error y clasificación por redes neuronales convolucionales. El sistema combina los resultados en una conclusión expresada como sin indicios o con indicios débiles, moderados o fuertes, y genera un informe en PDF por rubro, con los valores y umbrales de cada hallazgo, el descargo de resultado parcial y un código de verificación pública. La contratación de los planes de organización se cobra en línea mediante Mercado Pago, con un pago simulado mientras se completa la integración. 
Se incorporan además la verificación de la identidad de quien registra una aseguradora mediante Identik [integración en curso], una guía pública para verificar los sellos directamente en Hedera y una página pública que muestra qué información conserva una fotografía según cómo se la sube desde el celular. El sistema se aplica a causas por accidentes de tránsito y laborales y a la evaluación preliminar de siniestros por parte de las aseguradoras.
Quedan fuera del alcance el video, el audio y los documentos; el análisis del ruido de sensor (PRNU) y la verificación con SynthID; la localización de las zonas manipuladas mediante la red neuronal; el rol de perito y el dictamen pericial; la validación de matrículas profesionales; las aplicaciones móviles nativas; las notificaciones por WhatsApp; el examen del dispositivo de origen; la interfaz de consulta del registro de auditoría; otros ramos del seguro, como robo e incendio; y la integración con sistemas del Poder Judicial.
##### **Tabla 9.** Trazabilidad entre hallazgo, requisito y componente 
|  |  |  |  |  |
| :- | :- | :- | :- | :- |
| Hallazgo | Requisito | Prioridad | Componente | Verificación |
| El 63,6 % prioriza un reporte comprensible sin perito  | RF44 y RF54: informe por rubro con valores y umbrales  | Debe | Generador de informes  | Pruebas del contenido del PDF  |
| El 81,8 % prioriza un método validado judicialmente  | RF39 y RF40: capas deterministas reproducibles; RNF07: versión de cada componente  | Debe | Capas 1 y 2; versión del sistema en Hedera  | Pruebas de regresión con imágenes reales  |
| El manifiesto C2PA se pierde por WhatsApp (Tabla 6)  | RF41 y RF42: análisis de niveles de error y clasificador  | Debe | Capas 3 y 4  | Evaluación por condición de degradación  |
| Las imágenes llegan sin certificación de origen  | RF37, RF53 y RF55: huella, sello, origen de cada imagen e informe verificable  | Debe | Sello en Hedera; carga desde el celular  | Verificación en el *mirror node*  |
| El 45,5 % prioriza la confidencialidad  | RNF01 a RNF08 y RF49 a RF51: cifrado, roles, auditoría y retención  | Debe | Seguridad y retención  | Pruebas de autorización y revisión OWASP  |
| El referente de LegalTech recomienda apoyo con intervención humana  | RN27: el sistema no emite veredictos  | Debe | Textos del sistema y del informe  | Revisión de textos  |

*Nota. Elaboración propia a partir del relevamiento del Capítulo II y de la especificación del sistema (Anexo G). *
### **Del Proyecto**
El proyecto comprende el diseño, el desarrollo, el despliegue y la documentación de un producto mínimo viable, bajo la modalidad de diseño y desarrollo de un sistema de información (Universidad de la Cuenca del Plata, 2023, art. 23.2). Se desarrolla de forma individual, con la asistencia supervisada de un agente de inteligencia artificial; el desarrollo de la versión entregada concluye en noviembre de 2026 y continúa, con las correcciones de los tutores, hasta enero de 2027, antes de la defensa oral, prevista para febrero de 2027. El proyecto se ejecuta con imágenes de prueba y conjuntos de datos públicos, sin imágenes de causas reales. 
## **Límites**
### **Límites del sistema**
Dentro del sistema se encuentran la interfaz, la API, la base de datos, la cola de análisis, el almacenamiento de archivos, las cuatro capas de análisis, el generador de informes, la página de verificación pública y el registro de auditoría. Quedan fuera los actores y servicios del entorno, el valor probatorio que el Poder Judicial asigne al informe y las decisiones que los usuarios adopten a partir de él. El sistema opera como una única instancia, en la que cada caso pertenece a un espacio personal o al de una organización, y solo acceden a él su responsable y los miembros a quienes este otorga permiso. El aislamiento entre usuarios y organizaciones es lógico, mediante control de acceso y verificación de permisos en cada operación, y no físico, mediante infraestructura dedicada. Esta decisión responde a la escala y al presupuesto del proyecto, y la capa de acceso a datos permite incorporar un aislamiento más fuerte en una evolución futura. 
### **Limitaciones técnicas**
El sistema analiza el archivo recibido y no el dispositivo de origen, cuyo examen ofrece, según la práctica forense, una base de autenticidad más confiable, y una imagen generada por IA y luego fotografiada en una pantalla se registra como una foto nueva (Lars, 2026). La presencia de un manifiesto C2PA constituye un indicio fuerte; su ausencia no prueba nada, porque el manifiesto se pierde con la recompresión y la captura de pantalla, y los metadatos se pierden por la misma razón. El clasificador reconoce las familias de generadores vistas durante el entrenamiento, y su desempeño disminuye frente a generadores nuevos y a imágenes comprimidas (Williams, 2025; Lars, 2026). El análisis de niveles de error opera sobre JPEG, puede dar falsos positivos en bordes de alto contraste y se utiliza como señal complementaria. El sistema no localiza las zonas manipuladas de una imagen ni detecta fotografías reales reutilizadas fuera de contexto. Todos los resultados son parciales y de apoyo a la decisión humana. El formato HEIC se analiza sin convertir el original, pero el análisis de niveles de error tiene en él una validez limitada. El sello de tiempo acredita que una huella existía en una fecha, no que la imagen sea auténtica. 
### **Limitaciones del relevamiento**
El muestreo es exploratorio y de conveniencia: 11 abogados, una entrevista del lado asegurador y dos peritos. Las pruebas de canales se limitan a dos generadores y a una imagen por generador. El reconocimiento judicial del método depende de factores externos al desarrollo técnico. 
## **Catálogo de requisitos**
Los requisitos se especifican en el repositorio del proyecto y se presentan completos en el Anexo G: 56 requisitos funcionales (RF01 a RF56), 24 requisitos no funcionales (RNF01 a RNF24), 41 reglas de negocio y 38 casos de uso. Cada requisito cuenta con identificador, enunciado, tipo, prioridad (Debe, Debería o Podría), criterios de aceptación comprobables y trazabilidad al hallazgo que lo origina. La Tabla 9 muestra esa cadena para los requisitos principales, desde el hallazgo del relevamiento hasta el componente que lo realiza y la prueba que lo verifica. 


Los actores del sistema y sus casos de uso se presentan en las Figuras 8 y 9; los casos de uso de los demás módulos se encuentran en el Anexo F.

##### **Figura 8.** Actores del sistema

![](diagramas/09-casos-de-uso-actores.png)

*Nota. Elaboración propia, en notación UML 2.5.*

##### **Figura 9.** Casos de uso: imágenes, análisis e informes

![](diagramas/09d-casos-de-uso.png)

*Nota. Elaboración propia, en notación UML 2.5.*


# **CAPÍTULO IV: MODELO DE NEGOCIOS DEL PROYECTO**
## **Definición de Negocios **
### **Actividades**
El negocio consiste en proveer, como servicio web, la verificación técnica preliminar de imágenes fotográficas presentadas como prueba. Sus actividades son la recepción segura de imágenes organizadas por caso, el análisis multicapa, la elaboración de un informe que presenta los valores de cada capa y una conclusión final, la conservación auditable de cada análisis con su huella digital, la administración de usuarios y la actualización periódica del clasificador frente a nuevos generadores de imágenes. 
### **Mercado general**
El mercado comprende dos segmentos. El primero es el sector jurídico litigante en causas por accidentes de tránsito y laborales, relevado mediante la encuesta a abogados de Corrientes (Capítulo II). El segundo es el sector asegurador: la Superintendencia de Seguros de la Nación informa los balances de 186 de las 188 entidades autorizadas a operar al 31 de marzo de 2026 (Superintendencia de Seguros de la Nación, 2026), a las que se suman los productores y asesores de seguros de alcance regional, como el entrevistado en el NEA. El contexto internacional es consistente con la demanda: un estudio de Verisk de marzo de 2026 indica que el 36 % de los consumidores consultados alteraría una foto para fortalecer un reclamo (Verisk, s. f.). No se dispone de un dato verificado del universo de abogados litigantes del país, por lo que el tamaño de ese segmento queda sin cuantificar.  
### **Planes**
La contratación de los planes de organización se cobra en línea. En una primera etapa se evalúa Cresium, una empresa financiera argentina que cobra por transferencia a una cuenta virtual generada para cada pedido, adecuada al pago contra factura de las aseguradoras (Cresium, s. f.); el 23 de noviembre de 2026 la autora decide reemplazarla por Mercado Pago, que admite tarjetas, transferencias y otros medios habituales en Argentina mediante su solución de pagos en línea (Mercado Pago, s. f.). El estudio jurídico o la aseguradora elige el plan durante el registro y lo paga; el plan se aplica con sus límites cuando el proveedor confirma la acreditación, y la operación queda en la auditoría. Mientras se completa la integración, el pago se simula sin pedir ni guardar datos de pago. La Tabla 10 resume los planes.
##### **Tabla 10**. Planes de uso
|  |  |  |  |
| :- | :- | :- | :- |
| Capacidad | Personal (gratuito) | Organización Básico | Organización Profesional |
| Compartir casos y colaborar | No | Sí | Sí |
| Miembros | 1 | Hasta 5 | Hasta 25 |
| Análisis por mes | 10 | 100 | 500 |
| Imágenes por caso | 20 | 50 | 100 |
| Almacenamiento | 1 GB | 20 GB | 100 GB |
| Precio mensual | Sin costo | [a definir con los tutores; propuesta: US$ 49 sin IVA] | [a definir con los tutores; propuesta: US$ 149 sin IVA] |


*Nota. Elaboración propia. Los precios propuestos surgen del plan de negocios (Anexo P) y quedan sujetos a validación.*
### **Tecnología**
La solución combina análisis de metadatos, verificación de credenciales de procedencia C2PA, análisis de niveles de error y clasificación por redes neuronales convolucionales, alojados en Amazon Web Services, región Irlanda (Capítulo IX). 
## **Definiciones Estratégicas: Visión y Misión **
**Misión:** Proveer a abogados litigantes y aseguradoras de una herramienta técnica accesible, explicable y ajustada al marco normativo argentino, que apoye la decisión humana al evaluar preliminarmente la autenticidad de imágenes fotográficas presentadas como prueba en causas por accidentes de tránsito y laborales.
**Visión: **Constituirse en una instancia de verificación técnica de referencia, previa al peritaje formal y complementaria del criterio pericial, reconocida progresivamente en el ámbito judicial y asegurador argentino como insumo confiable para fundamentar decisiones sobre la admisibilidad de la prueba fotográfica.
## **Análisis de Rivalidad Amplificada**
El análisis aplica el esquema de fuerzas competitivas de Porter (2018), ampliado con los competidores potenciales, los sustitutos, los proveedores y los clientes. Los precios provienen de sitios oficiales y de reseñas de terceros.
### **Competencia actual de mercado**
Los jugadores se agrupan en tres familias. La primera son las suites forenses profesionales. Amped Authenticate permite determinar si un archivo es un original sin alteraciones, si proviene de un dispositivo específico o si resulta de una manipulación con software de edición, y localizar las regiones manipuladas (Amped Software, s. f.). Sus usuarios son laboratorios forenses y fuerzas de seguridad, y una reseña especializada advierte que quienes carecen de formación en forense de imágenes digitales pueden tener dificultad para comprender todos sus resultados (James, s. f.). Su precio no figura en las fuentes consultadas. 
La segunda familia son los detectores de contenido generado por IA. Hive ofrece detección de imágenes por API a 6 USD por cada 1.000 solicitudes, y Sightengine ofrece planes desde 10 USD por mes (Fritz AI, s. f.). Reality Defender ofrece 50 análisis mensuales gratuitos de audio o imagen, con tarifas personalizadas en sus planes superiores (Reality Defender, s. f.). AI or Not es un clasificador de autoservicio con un nivel gratuito de 20 verificaciones de imagen, e Illuminarty se distingue por un mapa de calor que indica qué regiones activaron la señal de IA (CheckThat.ai, s. f.). Estas herramientas apuntan a moderación de contenido, verificación de identidad y empresas, y entregan en general un puntaje o una clasificación global. 
La tercera familia son las herramientas web de uso general, algunas gratuitas y varias con interfaz en español. FotoForensics permite a cualquier usuario subir una imagen y obtener un análisis forense sin conocimientos técnicos, aunque sus propios desarrolladores advierten que puede generar falsos positivos en imágenes comprimidas y recomiendan usarla como complemento y no como prueba única (Noticias NQN, 2026). Otros detectores web analizan las imágenes con credenciales C2PA, análisis forense de metadatos y varios motores de detección, devuelven conclusiones con la evidencia nombrada en lugar de un único porcentaje y ofrecen un informe forense en PDF (Creati.ai, s. f.). Estas herramientas se orientan al verificador individual: no se identifica en ellas gestión de casos, control de acceso por titular ni un tratamiento de la conservación y la protección de los datos adaptado a la normativa argentina. Por ello, el idioma no es un diferencial del sistema: lo son la gestión de casos, la seguridad y la retención de los datos bajo la Ley N.° 25.326, la trazabilidad de los archivos y un informe pensado para que un perito pueda revisarlo y reproducirlo. 
### **Competidores potenciales**
Se identifican cuatro vías de ingreso. Los proveedores de suites forenses amplían sus funciones: Amped ya ofrece una línea forense de fotografía, video y *deepfakes*. Las plataformas globales de siniestros incorporan verificación visual, como la alianza de Truepic con Verisk. Los generadores de imágenes expanden sus credenciales de procedencia, y el verificador público de Content Credentials ya permite contrastar un archivo sin intermediarios. Finalmente, desarrolladores locales de LegalTech e insurtech pueden replicar la propuesta. La barrera técnica es baja, por el uso de componentes de código abierto; las barreras efectivas son la confianza de los usuarios y la validación judicial. 
### **Competidores sustitutos**
Se identifican cuatro sustitutos. El peritaje informático formal es un sustituto parcial y, a la vez, un complemento: resuelve la autenticidad con garantía institucional, pero con mayor costo y tiempo, y ningún abogado encuestado lo solicitó, de modo que el sistema funciona como verificación previa para decidir si pedirlo. La captura controlada evita el problema en origen: Truepic autentica cada imagen en el momento de la captura y la somete a más de 50 controles de fraude (Verisk, s. f.), y su integración llegó también a las aseguradoras canadienses (Truepic, s. f.). El protocolo de extracción directa desde la fuente, descrito por la UFIE, funciona en el circuito pericial pero no en el informal. Por último, la revisión visual del abogado, que la evidencia disponible, referida a video, muestra cercana al azar (Köbis et al., 2021). 
### **Proveedores**
Los proveedores de infraestructura son Amazon Web Services, para el cómputo, el almacenamiento y el envío de correo electrónico, y DonWeb como registrador del dominio evidentiaa.com.ar. Hedera provee el sello de tiempo, con un costo aproximado de US$ 0,0008 por registro, Google, el servicio de identidad para el inicio de sesión; Mercado Pago, el cobro de los planes; e Identik, la verificación de identidad de las aseguradoras. Los insumos técnicos son ExifTool, c2pa-python, PyTorch, ONNX Runtime y Google Colab, más conjuntos de datos públicos para el entrenamiento. Todos son sustituibles, por lo que su poder de negociación es bajo; la sustitución del sello de tiempo, de hecho, se concreta durante el desarrollo. Los emisores de credenciales C2PA, como OpenAI y Google, y el consorcio que mantiene la lista de confianza actúan como proveedores de señal, de los que el sistema depende sin poder influir en ellos. 
### **Clientes**
Los abogados litigantes, independientes o en estudios, tienen alto poder de negociación individual por la baja barrera de cambio, ya que cuentan con alternativas gratuitas, pero priorizan la validez judicial del resultado. Las aseguradoras compran en volumen y pueden integrar soluciones globales, lo que les da el mayor poder de negociación. Los productores y asesores de seguros funcionan como canal de acceso al segmento asegurador. El Poder Judicial es un usuario indirecto: no contrata el sistema, pero decide la admisibilidad de sus informes. 
### **Mapeo de competencia**
La Tabla 11 ordena las alternativas relevadas según lo que ofrece cada una y la brecha que el sistema propuesto cubre frente a ellas. Se incluyen las suites forenses profesionales, los detectores de contenido generado por IA, las herramientas web de uso general, la captura verificada en origen y el peritaje formal, que son las opciones a las que hoy puede recurrir un abogado o una aseguradora para verificar una imagen. La información proviene de la documentación pública de cada proveedor y de reseñas de terceros, por lo que describe el posicionamiento declarado de cada alternativa y no un ensayo comparativo de desempeño.  
##### **Tabla 11. **Mapeo de competencia 
|  |  |  |
| :- | :- | :- |
| **Alternativa** | **Qué ofrece** | **Brecha que cubre el sistema** |
| Amped Authenticate  | Autenticación forense de imagen y video, para expertos  | Informe accesible para usuarios sin formación forense  |
| Hive, AI or Not, Sightengine  | Detección por clasificador mediante API o autoservicio, con puntaje o calificación global  | Valores por capa con indicios deterministas y probabilísticos diferenciados, y conclusión final  |
| Herramientas web de uso general (FotoForensics y detectores con interfaz en español)  | Análisis de compresión, metadatos o clasificación, con informe descargable  | Gestión de casos, control de acceso, retención de datos y encuadre normativo argentino  |
| Truepic con Verisk  | Captura verificada en origen  | Analiza imágenes que ya llegaron por canales no controlados  |
| Peritaje informático  | Dictamen profesional con garantía institucional  | Verificación previa, más rápida y económica  |

*Nota. Elaboración propia a partir de documentación pública de cada proveedor y reseñas de terceros. *
El sistema se posiciona entre las suites forenses profesionales, orientadas a expertos, y las herramientas de uso general y los detectores por API, orientados al verificador individual o a plataformas. Busca combinar la accesibilidad para usuarios sin formación técnica con la explicabilidad de sus hallazgos, presentados por capa junto con una conclusión final, y con la gestión de casos, el control de acceso, la auditoría y la retención de datos adaptados al contexto judicial y asegurador argentino. En la documentación consultada no se identifica una alternativa que ofrezca esa combinación para ese contexto.

# **CAPÍTULO V: PLANIFICACIÓN DEL PROYECTO**
## **Definición de Iteraciones, Sprints o Etapas del Proyecto**
El proyecto se organiza bajo un ciclo de vida iterativo e incremental, gestionado con Kanban (Anderson, 2010). La planificación del trabajo de Gestión de Proyectos, de 32 semanas, se reformula a partir del trabajo de campo y de la fecha prevista para el cierre del desarrollo, el 20 de noviembre de 2026, y se estructura en siete iteraciones. El 18 de noviembre la autora decide extender el desarrollo hasta enero de 2027, para incorporar las correcciones de los tutores y las validaciones con usuarios antes de la defensa.
La iteración 0, de concepción y relevamiento, abarca desde mayo hasta el 9 de septiembre de 2026 y comprende la definición del problema y de los usuarios, las entrevistas, la encuesta y la primera entrega parcial del informe. La iteración 1, de base técnica, se desarrolla entre el 6 y el 19 de agosto, en paralelo con el relevamiento, e incluye la autenticación, los roles, la gestión de casos, la arquitectura en capas y la integración continua. La iteración 2, de capas deterministas, va del 15 de septiembre al 5 de octubre e incluye el análisis de metadatos, la lectura de credenciales C2PA, las pruebas de canales y una demostración preliminar.
La iteración 3, de repositorio limpio, motor de análisis integrado y despliegue, se extiende del 6 al 25 de octubre. Comienza con la creación de un repositorio nuevo, organizado según la arquitectura propuesta y las prácticas del Capítulo VI, en el que se reorganiza lo desarrollado en las iteraciones 1 y 2, y continúa con la verificación de firmas C2PA, la integración de las capas en un orquestador, la conexión del análisis con la carga de imágenes, el almacenamiento en la nube, el análisis de niveles de error y el despliegue de una primera versión en Amazon Web Services. La iteración 4, del clasificador, va del 26 de octubre al 8 de noviembre y comprende la preparación de los datos, el entrenamiento, la evaluación por condición de degradación, la exportación del modelo y su integración. La iteración 5, de informe y gobierno, ocupa del 9 al 15 de noviembre y construye el informe en PDF que genera el sistema, el registro de la huella digital, las notificaciones por correo y la auditoría completa. La iteración 6, de cierre, del 16 al 20 de noviembre, comprende las pruebas de aceptación, las correcciones, la documentación técnica y de usuario y el cierre del desarrollo.
La ejecución real se aparta del plan en un sentido favorable. La combinación de especificaciones escritas antes de programar, un arnés de pruebas automatizadas y un agente de inteligencia artificial que trabaja bajo reglas explícitas adelanta varias iteraciones: el informe en PDF, el sello de tiempo, las notificaciones y la auditoría, previstos para la iteración 5, quedan integrados antes del 26 de octubre. En cambio, el clasificador concentra la incertidumbre, tal como se anticipa en el plan de riesgos, y se desarrolla en una pista paralela a cargo de la autora: su entrenamiento completo se realiza el 5 de noviembre y la versión 1.0.0 se activa en producción el 10 de noviembre. La Tabla 13 y la Figura 10 contrastan el plan con la ejecución real.
## **Descripción de Entregables de cada etapa de la planificación**
La iteración 0 entrega la primera entrega parcial del informe (Resumen y Capítulos I y II), la base de respuestas de la encuesta, los guiones de entrevista y el prototipo inicial. La iteración 1 entrega la autenticación con recuperación de contraseña, el control de acceso por rol, la gestión de casos, la arquitectura en capas con sus patrones y el flujo de integración continua. La iteración 2 entrega el servicio de metadatos con 7 pruebas automatizadas, el servicio C2PA con 20 y una demostración de carga y análisis.
La iteración 3 entrega un repositorio nuevo, con la estructura, las especificaciones y la integración continua definidas, y con las pruebas de las iteraciones anteriores en verde; el servicio C2PA con verificación de firma; el orquestador de capas con una salida unificada; la ruta de carga con análisis automático; la capa de almacenamiento con implementaciones local y en la nube; el módulo de análisis de niveles de error; y la primera versión desplegada con certificado TLS y copias de respaldo. La iteración 4 entrega el conjunto de datos preparado, el modelo entrenado, el informe de F1-score por condición, el modelo exportado a ONNX y los umbrales calibrados. La iteración 5 entrega el motor de reglas de conclusión, el informe en PDF con valores por capa y descargo, el sello de tiempo de la huella digital, las notificaciones y el registro de auditoría. La iteración 6 entrega el informe de pruebas de aceptación, la documentación técnica y de usuario, el código fuente final y el sistema en producción.
## **Organización del Equipo de Proyecto**
Dado el carácter individual del proyecto, la autora, Valentina Salmón, asume las funciones de analista, diseñadora del producto, responsable de las decisiones y gestora del proceso, con el apoyo de un agente de inteligencia artificial, Claude Code, que opera dentro del repositorio bajo reglas escritas: una constitución del proyecto y un archivo de instrucciones para agentes. El reparto de trabajo se define de forma explícita. El agente redacta las especificaciones, los planes y las tareas de cada funcionalidad, escribe el código, las pruebas y la documentación de seguimiento, y registra cada commit con una línea de coautoría que identifica la asistencia de IA. La autora revisa ese trabajo, lo integra mediante pull requests y toma las decisiones de alcance, las cuestiones legales y de privacidad, y los cambios de arquitectura de impacto. Las decisiones que exceden al agente se registran como cuestiones abiertas, con una propuesta provisoria, hasta que la autora o los tutores las resuelven. Esta organización es coherente con un método, Kanban, que no prescribe roles (Anderson, 2010). Los docentes de la cátedra, Sergio Lapertosa, Augusto Portillo y Martín Jones, realizan el seguimiento y la evaluación, y este último actúa como revisor técnico. Federico Miskinich, referente de LegalTech en Corrientes, aporta el contraste del diseño con el sector. Los abogados y el productor de seguros consultados aportan la validación de las necesidades y, en la última iteración, la de la comprensión del informe que genera el sistema.
El trabajo se gestiona en un tablero de Trello de cinco columnas (Backlog, En análisis, En desarrollo, En pruebas y Completado), en el que cada funcionalidad integrada conserva su pull request y su fecha de integración, de modo que el historial refleja la cronología real (Anexo L). No se fija un límite de trabajo en curso, porque la autora y el agente avanzan en paralelo: por ejemplo, la autora entrena el clasificador en Google Colab mientras se integran otras funcionalidades. El proceso se registra durante el desarrollo en una bitácora de trabajo, que documenta qué se hizo, qué se decide y qué queda pendiente en cada etapa (Anexo H), y el informe escrito se redacta a partir de ella. La dedicación prevista es de 40 horas semanales.

El tablero se reorganiza el 26 de octubre para alinearlo con este capítulo: cada tarjeta lleva etiquetas de prioridad (P1 a P3), de responsable (autora, agente de IA o tutores) y de área (desarrollo, infraestructura, documento, relevamiento y gestión), y cada funcionalidad integrada conserva su especificación, su pull request y su fecha real. El agente actualiza el tablero al cerrar cada trabajo, y una revisión periódica lo concilia con el repositorio. El trabajo con el agente se organiza, además, en sesiones separadas por tema, con un traspaso explícito entre ellas: una para el desarrollo del sistema, otra para la red neuronal, otra para el tablero y otra para la redacción de este informe, de modo que ninguna mezcle contextos distintos; la memoria común entre todas es el propio repositorio.
## **Cronograma del Proyecto**
El cronograma cubre las siete semanas que van del 5 de octubre al 20 de noviembre de 2026. La Tabla 12 detalla el plan. Las semanas 1 a 3 corresponden a la iteración 3, las semanas 4 y 5 a la iteración 4, la semana 6 a la iteración 5 y la semana 7 a la iteración 6. 
##### **Tabla 12.** Cronograma de ejecución 
|  |  |  |  |
| :- | :- | :- | :- |
| **Período** | **Etapa** | **Actividades** | **Hito** |
| Mayo - 09/09  | Iteración 0: concepción y relevamiento  | Definición del problema y de los usuarios, entrevistas (20/08, 02/09 y 07/09), encuesta (24/08 al 01/09), primera entrega parcial del informe  | Entrega parcial del informe (09/09)  |
| 06/08 - 19/08  | Iteración 1: base técnica  | Autenticación, roles, gestión de casos, arquitectura en capas, integración continua  | Base técnica integrada  |
| 15/09 - 05/10  | Iteración 2: capas deterministas  | Metadatos EXIF/XMP, lectura C2PA, pruebas de canales (16 al 28/09), investigación de infraestructura, reunión con el referente de LegalTech (02/10) y demostración  | Demostración de las capas deterministas  |
| 05/10 - 11/10  | Iteración 3, semana 1  | Creación del repositorio nuevo con la arquitectura propuesta (6 al 8/10): estructura, especificaciones, integración continua y reorganización del código y las pruebas existentes; verificación de firma C2PA  | H1: repositorio nuevo operativo y capas deterministas completas  |
| 12/10 - 18/10  | Iteración 3, semana 2  | Orquestador y salida unificada, conexión con la carga de imágenes, almacenamiento, pruebas de autorización, cuenta de AWS y dominio  | \- |
| 19/10 - 25/10  | Iteración 3, semana 3  | Despliegue inicial con TLS y respaldos, análisis de niveles de error  | H2: sistema desplegado con tres capas  |
| 26/10 - 01/11  | Iteración 4, semana 4  | Preparación de datos y entrenamiento del clasificador  |  |
| 02/11 - 08/11  | Iteración 4, semana 5  | Evaluación por condición, exportación, integración y calibración de umbrales  | H3: cuatro capas integradas  |
| 09/11 - 15/11  | Iteración 5, semana 6  | Informe en PDF, sello de la huella digital, notificaciones y auditoría  | H4: funcionalidad completa  |
| 16/11 - 20/11  | Iteración 6, semana 7  | Pruebas de aceptación, correcciones, documentación técnica y de usuario, y cierre del desarrollo  | H5: cierre del desarrollo  |
| Noviembre de 2026 a enero de 2027  | Redacción del informe escrito  | Capítulos restantes, conclusiones, bibliografía y anexos, a partir de la bitácora, con las correcciones de los tutores  | Informe escrito completo  |
| [Completar fecha de entrega]  | Evaluación del informe  | Evaluación por el equipo docente, que dispone de hasta 20 días (Universidad de la Cuenca del Plata, 2023, art. 8.2.6)  | Informe aprobado para la defensa  |
| Febrero de 2027  | Defensa oral  | Envío de la copia al tribunal cinco días hábiles antes (art. 14) y exposición de hasta 45 minutos (art. 16)  | Defensa oral  |

*Nota. Elaboración propia a partir del Reglamento General del Proyecto Integrador Final. *
Las pruebas automatizadas, las medidas de seguridad y el registro en la bitácora de trabajo se realizan de forma continua en todas las iteraciones y no constituyen etapas separadas. El clasificador concentra la mayor incertidumbre, dado que su desempeño frente a generadores recientes es menor que frente a los antiguos. Si el hito H3 no se cumple al 8 de noviembre, el clasificador se entrega en versión experimental con sus métricas documentadas, y el sistema opera con las demás capas. Si el servicio de sello de tiempo no está disponible, la huella digital se calcula y se informa igualmente, y el diseño permite reemplazar el proveedor del sello sin modificar el resto del sistema. Si la creación del repositorio nuevo excede los tres días previstos, se prioriza que las pruebas existentes pasen en el repositorio nuevo antes de continuar con las funcionalidades de la iteración. 
La ejecución real difiere del plan en el orden y en el alcance, como resume la Tabla 13.

##### **Tabla 13.** Ejecución real del desarrollo

| Período | Etapa | Qué se ejecuta | Diferencia con el plan |
| :- | :- | :- | :- |
| Marzo a julio de 2026 | Antecedentes | Cambio del foco a la prueba judicial, TP de Gestión de Proyectos (de Scrum a Kanban), mapeo sistemático, propuesta aprobada por el tutor | No figuraba en el plan de 32 semanas |
| Agosto | Base técnica e inicio del relevamiento | Autenticación, roles, casos y arquitectura en capas con plantillas Jinja2; integración continua; primera entrevista y encuesta; descarte del perito | Según lo previsto |
| Septiembre | Relevamiento y capas deterministas | Entrevistas restantes, región Irlanda, módulo de metadatos, C2PA con verificación de firma, prueba de canales y elección de la infraestructura | C2PA, descartado el 14/9, se incorpora el 16/9; PRNU se descarta |
| 1 al 8 de octubre | Referente y repositorio nuevo | Reunión con el referente de LegalTech, repositorio nuevo con especificación, constitución y arnés | El repositorio nuevo se adelanta para ordenar lo hecho |
| 9 al 31 de octubre | Desarrollo acelerado | Más de 30 funcionalidades: interfaz React, cuentas, organizaciones, casos, capas 1 a 3, informe PDF, despliegue en AWS, cambio de BFA a Hedera, celular, Google, seguridad, portada | Se adelantan las iteraciones 5 y 6; BFA se reemplaza por Hedera |
| Noviembre | Red neuronal, calidad y cierre de la versión entregada | Entrenamiento y capa 4, Hedera probado en producción, revisión integral de la interfaz, accesibilidad, dominio, GitHub Flow, verificación independiente, Mercado Pago | El desarrollo se extiende hasta enero de 2027 |

*Nota. Elaboración propia a partir de la bitácora de trabajo (Anexo H) y de las bitácoras de cada actividad de evaluación.*

##### **Figura 10.** Cronograma planificado y ejecución real

![](diagramas/06-cronograma.png)

*Nota. Elaboración propia a partir de la bitácora de trabajo (Anexo H).*

## **Descripción del MVP**
El producto mínimo viable, según la modalidad de diseño y desarrollo (Universidad de la Cuenca del Plata, 2023, art. 23.2), comprende el alcance definido para el sistema en el Capítulo III: el registro con los perfiles Abogado y Aseguradora, las organizaciones con permisos por caso, la carga de imágenes JPEG, PNG y HEIC asociadas a un caso, el análisis con las cuatro capas, la conclusión combinada, el informe en PDF con los valores de cada capa y el descargo de resultado parcial, la huella digital con sello de tiempo, el registro de auditoría, las notificaciones por correo y el despliegue en la nube con tráfico cifrado.
Dentro del MVP se distinguen dos niveles de prioridad. Son indispensables la verificación de metadatos y de credenciales C2PA, el clasificador, el informe con descargo, la auditoría, la separación entre espacios de trabajo y el despliegue. Son deseables el análisis de niveles de error, el sello de tiempo y las notificaciones más allá de la recuperación de contraseña, todos ellos implementados. Durante el desarrollo se incorporan además funcionalidades no previstas, que surgen de la validación con la autora, con el tutor y con sugerencias externas: la carga desde el celular, el informe verificable públicamente, la huella de cada versión del sistema, el inicio de sesión con Google, la portada pública con los planes, el cobro de los planes mediante Cresium y el registro de la experiencia de uso con Microsoft Clarity.
El MVP se considera aceptado cuando el análisis de una imagen demora menos de 30 segundos, el clasificador alcanza un área bajo la curva ROC de al menos 0,90 sobre un conjunto de validación de generadores conocidos, con el desempeño reportado por separado bajo recompresión, reescalado y captura de pantalla, la cobertura de las pruebas automatizadas es de al menos 80 % y al menos un abogado y un analista de siniestros evalúan la comprensión del informe que genera el sistema. Si el clasificador no alcanza el valor de referencia, se informa el valor obtenido y se documenta como limitación. Al 26 de noviembre de 2026 se cumplen la cobertura (97,5 % en el backend) y el valor del clasificador (área bajo la curva ROC de 0,961); quedan pendientes la medición del tiempo de análisis en producción [completar] y la evaluación de la comprensión del informe por un abogado y un analista de siniestros (OE5).

# **CAPÍTULO VI: METODOLOGÍAS DE GESTIÓN**
## **Técnicas o Prácticas de la Ingeniería de Software para el Proyecto**
El desarrollo sigue un ciclo de vida iterativo e incremental, gestionado con Kanban (Anderson, 2010) en un tablero de cinco columnas. Cada decisión y cada avance se registran en una bitácora de trabajo con el formato qué se hizo, qué se decide y qué queda pendiente, que constituye la fuente del informe escrito, y cada decisión de arquitectura se documenta en un registro de decisiones (ADR) con sus alternativas y consecuencias.
Cada funcionalidad parte de una especificación escrita antes de la implementación, que define qué se construye y cómo se verifica, seguida de un plan técnico y de una lista de tareas, siguiendo la estructura del marco Spec Kit (GitHub, s. f.). Al cerrarla se agrega una entrada en la bitácora. El conjunto se rige por una constitución del proyecto que fija los principios de arquitectura y de proceso. A cada especificación le corresponde un arnés de pruebas que verifica el comportamiento esperado y no la implementación, de modo que si un componente se sustituye, como ocurre con el proveedor del sello de tiempo, el arnés permanece y solo cambia lo que lo atraviesa. Al 26 de noviembre de 2026, el repositorio reúne 48 funcionalidades planificadas, 23 registros de decisiones de arquitectura y 71 entradas de bitácora, más una bitácora por cada actividad de evaluación. 
La arquitectura se organiza en capas (rutas, servicios, repositorios y modelos), en la que cada capa depende solo de la inmediatamente inferior, regla que import-linter verifica en cada cambio. Se aplican los patrones Factory para la configuración por entorno, Strategy para las piezas intercambiables, Repository para el acceso a datos, Service Layer para la lógica de negocio y Decorator para el control de acceso (Pressman, 2011). El código se valida con flake8, pylint y ESLint, y los mensajes de commit siguen una adaptación al español de la convención Conventional Commits (Conventional Commits, s. f.), con tipos como funcionalidad, corrección o documentación, verificada por la integración continua.
El proyecto incorpora además un arnés para el trabajo asistido por inteligencia artificial, entendido como el sistema que rodea al agente para que trabaje de forma confiable dentro del repositorio. Sus guías son la constitución del proyecto, un archivo de instrucciones para el agente, la especificación general y los comandos para especificar, planificar, generar tareas y cerrar cada etapa. Estas guías obligan al agente a escribir el código y la documentación en español, a respetar la arquitectura en capas, a documentar en cada función el requisito que realiza, a no redactar nunca veredictos, a seguir la guía de identidad visual y a no subir secretos ni imágenes reales al repositorio. Como una regla escrita depende de que el agente la recuerde, el arnés suma sensores que la hacen cumplir: ganchos que se ejecutan antes y después de cada acción del agente, controles previos a cada commit, la verificación automática de la arquitectura en capas y la integración continua. La regla de no acceder a secretos, por ejemplo, deja de ser solo texto y se convierte en un control que bloquea la acción. La memoria del proceso se conserva en la bitácora, en los registros de decisiones, en las cuestiones abiertas y en el tablero de gestión, de modo que el trabajo de cada sesión parte de lo decidido en las anteriores. La autora ocupa el lugar de la persona en el circuito: revisa e integra el trabajo, toma las decisiones que exceden al agente y es la única que maneja los secretos.
El funcionamiento del arnés se comprueba en la práctica. En su primera prueba, el gancho de secretos bloquea un commit del propio agente, y el control de permisos de la herramienta impide que el agente modifique ese gancho, por tratarse de un control de seguridad: la corrección queda como propuesta, que la autora aprueba recién el 24 de noviembre. El arnés se mejora de forma continua, y un registro de cambios documenta cada ajuste con el problema que lo motivó. Así se incorporan, por ejemplo, la regla de probar cada integración externa contra el servicio real, después de que el sello en Hedera supera todas las pruebas automáticas y aun así falla en producción; un sensor de diseño que recorre las pantallas en computadora y en celular, después de que un cambio en un estilo compartido deja cortadas pantallas que no se habían revisado; sensores de accesibilidad y de uso con teclado; un verificador que comprueba al iniciar cada sesión que lo que declaran los documentos sea cierto (números, índices, enlaces y comandos); y un control del formato de cada commit. La Figura 11 presenta el ciclo completo. Todo commit del agente lleva una línea de coautoría que identifica la asistencia de IA, lo que permite distinguir en el historial el trabajo asistido: al 26 de noviembre de 2026, 394 de los 425 commits del repositorio (92,7 %), integrados mediante 88 pull requests. Ningún cambio ingresa sin pasar antes la integración continua y la revisión de la autora, bajo su responsabilidad. El Anexo O detalla el uso de la inteligencia artificial en cada parte del proyecto.

##### **Figura 11.** Ciclo de trabajo asistido por inteligencia artificial

![](diagramas/10-ciclo-de-trabajo-con-ia.png)

*Nota. Elaboración propia, diagrama de actividad en notación UML 2.5.*

El mismo criterio se aplica a la redacción de este informe, que cuenta con un arnés propio. Sus guías son una guía de redacción, que fija la voz, la estructura y la forma de evidenciar cada afirmación, y una fuente única de hechos verificados del sistema, de la que salen los datos del texto. Sus sensores son tres herramientas del repositorio: un revisor que detecta en el documento los errores mecánicos que marca un evaluador (numeración de capítulos, tablas y figuras, citas sin entrada en la bibliografía y entradas sin cita, tiempo verbal, listas con viñetas, extranjerismos sin cursiva y frases que puedan leerse como un veredicto), un cálculo de las cifras del proceso a partir del historial de Git y un generador de diagramas que obtiene el modelo de datos, los componentes y los casos de uso del propio código y verifica que el diagrama de despliegue coincida con la infraestructura declarada en Terraform. La autora revisa cada texto y cada figura antes de incorporarlos, y las versiones descartadas se eliminan del repositorio para conservar solo la vigente. La Figura 12 resume el circuito. Este arnés surge de una experiencia concreta: los primeros diagramas del informe se descartan porque no respetan la notación UML ni coinciden con el sistema, y desde entonces ninguna figura se incorpora sin pasar esa verificación.

##### **Figura 12.** Arnés del informe final

![](diagramas/11-arnes-del-informe.png)

*Nota. Elaboración propia, diagrama de actividad en notación UML 2.5.*
La seguridad y la protección de datos se incorporan desde el diseño. Los activos de información se clasifican por nivel de confidencialidad conforme a la norma ISO/IEC 27001 (International Organization for Standardization \[ISO\], 2022), y las imágenes de siniestros y los informes se tratan como información de máxima confidencialidad. Se aplica el principio de mínimo privilegio: cada rol accede solo a lo necesario para su función, y el administrador gestiona usuarios y revisa la auditoría sin acceder al contenido de los casos. La protección de los datos personales sigue la Ley N.° 25.326 (República Argentina, 2000): seguridad de los datos (art. 9), destrucción de los datos que dejan de ser necesarios (art. 4, inc. 7) y tratamiento reforzado de los datos sensibles, categoría que puede alcanzar a imágenes con lesiones (art. 2). La norma ISO/IEC 27701 (ISO, 2019) orienta los controles de minimización, retención y supresión. Para la auditabilidad del componente de inteligencia artificial se toman como referencia el Reglamento de Inteligencia Artificial de la Unión Europea (Parlamento Europeo y Consejo de la Unión Europea, 2024) y la norma ISO/IEC 42001 (ISO, 2023): cada resultado registra la versión del modelo y de los componentes que lo produjeron, y el clasificador cuenta con una ficha técnica que documenta el conjunto de datos, el procedimiento de entrenamiento y las métricas obtenidas.
## **Trazabilidad del Proyecto**
La trazabilidad es bidireccional entre la necesidad relevada, el requisito, la especificación, la implementación y la prueba. Cada requisito del Anexo G se vincula con un caso de uso y con la especificación que lo desarrolla; cada especificación, con los commits y el pull request que la implementan; y cada pull request, con las pruebas que la verifican y con la tarjeta del tablero que la originó. Los mensajes de commit referencian la especificación en el pie, de modo que desde cualquier cambio de código se llega al requisito que lo motivó, y desde cualquier requisito, al código y a las pruebas que lo cubren.
Las decisiones de diseño y sus fundamentos quedan en la bitácora, con fecha, y los hallazgos del relevamiento se vinculan con los requisitos que originan. Así, por ejemplo, la preferencia de los abogados por un informe comprensible sin perito se traduce en el requisito del informe con valores por capa, en su especificación, en la implementación del generador de informes y en las pruebas que verifican su contenido. Esa cadena permite justificar cada componente del sistema ante la evaluación del proyecto. La línea de coautoría de cada commit agrega una dimensión adicional a la trazabilidad, porque permite identificar qué cambios se producen con asistencia de inteligencia artificial. Las cuestiones que requieren una decisión de la autora o de los tutores se enumeran y quedan registradas con su propuesta, su resolución y los requisitos que afectan. 
### **Evolución de las decisiones del proyecto**

El proyecto es incremental, y varias decisiones cambian a medida que el relevamiento, las pruebas y la experiencia de uso aportan información nueva. La Tabla 14 registra los cambios principales, con lo que se pensaba antes, lo que se adopta y el motivo, de modo que la versión entregada se pueda leer como resultado de ese recorrido y no como un diseño cerrado de antemano.

##### **Tabla 14.** Evolución de las decisiones del proyecto

| Tema | Decisión inicial | Decisión vigente | Motivo del cambio |
| :- | :- | :- | :- |
| Usuarios | Peritos técnicos judiciales | Abogados y aseguradoras; el perito como destinatario del informe | Las dos peritas entrevistadas resuelven la autenticidad con la cadena de custodia (agosto y septiembre) |
| Gestión | Scrum | Kanban | Proyecto individual, sin roles de Scrum (abril) |
| Interfaz | Plantillas Jinja2 en Flask | React con API REST | Separar interfaz y servidor y facilitar el trabajo en celular (8/10) |
| Base de datos e infraestructura | Amazon RDS en us-east-1 | PostgreSQL en una instancia EC2 en Irlanda | Adecuación a la Ley N.° 25.326 y costo (septiembre) |
| Credenciales C2PA | Descartadas por suponer que las fotos de celular no las traen | Capa 2 del análisis | ChatGPT y Gemini firman sus imágenes con C2PA (16/9) |
| Ruido del sensor (PRNU) | Capa determinista prevista | Descartado | Sin la cámara original es poco confiable y caro de implementar (septiembre) |
| Huella SHA-256 | Descartada por no detectar IA | Base de la cadena de custodia y del sello | Recomendación del referente de LegalTech (2/10) |
| Sello de tiempo | Blockchain Federal Argentina | Hedera Consensus Service | BFA rechaza las conexiones desde el exterior (21 al 25/10) |
| Red de Hedera | Pasar a la red principal antes de la defensa | Red de pruebas, con guía de verificación independiente | Decisión de la autora; costo y suficiencia para demostrar la verificación (23/11) |
| Retención | 2 años | 5 años | Plazo de prescripción del Código Civil y Comercial (19/10) |
| Cobro | Asignación manual del plan; luego Cresium por transferencia | Mercado Pago, con pago simulado durante la integración | Medios de pago más habituales en Argentina (23/11) |
| Entrenamiento | Kaggle | Google Colab Pro | Preferencia de la autora y suscripción disponible (28/10) |
| Conjunto propio de la red | Solo para evaluar | Evaluación fija y parte de ajuste | Mejorar el modelo por versiones sin perder una medición honesta (11/11) |
| Flujo de ramas | `main`, `desarrollo` y una rama por funcionalidad | GitHub Flow, con `main` protegida | Demasiados pull requests y ramas por cambios chicos (18/11) |
| Diagramas del informe | Dibujados sin verificar | Generados desde el código y verificados | Los primeros no respetaban UML ni coincidían con el sistema (29/10) |
| Fin del desarrollo | 19 de noviembre de 2026 | Enero de 2027 | Incorporar correcciones y validaciones antes de la defensa (18/11) |

*Nota. Elaboración propia a partir de la bitácora de trabajo, de los registros de decisiones de arquitectura y de las cuestiones abiertas del proyecto.*

## **Gestión de la Configuración del Proyecto**
El código se versiona en Git y se aloja en GitHub, en un repositorio nuevo creado el 8 de octubre de 2026 con la arquitectura propuesta; el repositorio anterior se conserva como antecedente. Hasta el 18 de noviembre, la rama `main` refleja la versión en producción, la rama `desarrollo` integra las funcionalidades terminadas y cada funcionalidad se trabaja en una rama propia. Ese esquema genera demasiadas ramas y pull requests por cambios chicos, y el proyecto adopta GitHub Flow: `main` es la única rama permanente, protegida para que nada se integre sin todas las verificaciones en verde; el trabajo se organiza en ramas cortas por objetivo, con el área adelante (por ejemplo, `hedera/verificacion-independiente`), y cada objetivo ingresa con un único pull request que se integra combinando sus commits. Los hitos se marcan con versiones etiquetadas.
El flujo de integración continua ejecuta en cada cambio el análisis de estilo y calidad, las pruebas automatizadas con su cobertura, la verificación de la arquitectura en capas y la validación de los mensajes de commit. Incorpora además una auditoría de dependencias vulnerables, que se ejecuta en cada pull request y una vez por semana, como condición para desplegar. Al integrar un cambio en main, el despliegue hacia la instancia en la nube se realiza de forma automática, con credenciales temporales y sin claves guardadas, y la huella de la versión desplegada se registra en Hedera. Las actualizaciones de dependencias las propone Dependabot, agrupadas una vez por mes por ecosistema, salvo los parches de seguridad, que llegan en el momento.
La configuración se separa por entorno (desarrollo, pruebas y producción). Los secretos viven en variables de entorno, nunca en el repositorio, con una plantilla sin valores reales como referencia; en producción, el acceso al almacenamiento se concede mediante un rol de la instancia con permisos mínimos sobre el bucket. Las dependencias se fijan en versión exacta, incluidas ExifTool y c2pa-python, porque la reproducibilidad de un resultado forense depende de la versión del componente que lo produjo. La lista de confianza de C2PA se versiona junto con el código, el modelo se versiona con su ficha técnica, y la base de datos se respalda de forma periódica hacia el almacenamiento con versionado.
## **Testing del Proyecto**
Las pruebas se organizan en cuatro niveles. Las pruebas unitarias y de integración verifican los servicios, los repositorios, las reglas de severidad, el orquestador de capas, la carga, el almacenamiento, el cobro y la base de datos, e incluyen pruebas de regresión sobre imágenes reales de ChatGPT y Gemini enviadas por distintos canales. Al 16 de noviembre de 2026, el proyecto ejecuta 898 pruebas automatizadas, 612 del backend y 286 de la interfaz, más las de los controles del arnés y de la red neuronal. El backend alcanza una cobertura superior al 97 %, frente a un mínimo exigido del 80 %, y una calificación de pylint de 10/10. Las integraciones con servicios externos se prueban además contra el servicio real: el sello en Hedera, que supera todas las pruebas automáticas con dobles de prueba, se comprueba en producción contra la red de pruebas (*testnet*) mediante una página pública de estado que solo informa «Funciona» cuando el *mirror node* devuelve la huella sellada. Las pruebas de desempeño del clasificador miden su rendimiento por separado para la imagen original, la recompresión, el reescalado y la captura de pantalla, y verifican que el análisis demore menos de 30 segundos. La interfaz se verifica además con tres sensores automáticos que recorren el sistema en un navegador real, en computadora y en celular. El sensor de diseño detecta contenido cortado, superpuesto o fuera de la pantalla; el sensor de accesibilidad evalúa catorce pantallas con axe-core según las pautas WCAG 2.1 de nivel AA (World Wide Web Consortium [W3C], 2018) y falla ante cualquier infracción seria o crítica, lo que permite corregir dos problemas de contraste; y el sensor de uso con teclado comprueba que nueve pantallas puedan recorrerse solo con la tecla Tab, con el foco siempre visible. Para la prueba de usabilidad se prepara un kit imprimible con el consentimiento, el guion de tareas, la planilla de registro y el cuestionario SUS (Brooke, 1996). El índice de calidad provisorio, calculado sin el componente de usabilidad, es de 0,975. Se prevén pruebas de aceptación con al menos un abogado y un analista de siniestros, pruebas de usabilidad con entre tres y cinco participantes mediante el cuestionario SUS y la medición del índice de calidad del software. 
Un conjunto específico de pruebas verifica la seguridad: que un usuario no pueda acceder a los casos de otro, que el administrador reciba un rechazo al abrir el contenido de un caso, que los enlaces de recuperación y de carga expiren, y que la recuperación de contraseña no revele qué correos están registrados. La seguridad se revisa además según el OWASP Top 10 (OWASP Foundation, 2021), con la evidencia y los riesgos aceptados documentados. Como resultado de esa revisión se incorporan límites de pedidos por dirección IP, cabeceras de seguridad adicionales y una búsqueda de secretos en todo el historial del repositorio, que no arroja hallazgos reales. Todas las pruebas usan únicamente imágenes de prueba propias y conjuntos de datos públicos: ninguna imagen de una causa real se utiliza en el desarrollo ni se sube a verificadores externos.
## **Prototipo v1**
El prototipo v1 corresponde al esqueleto caminante del sistema, integrado el 10 de octubre de 2026. Recorre de extremo a extremo un caso de uso vertical completo (interfaz, API, servicio, persistencia y respuesta), con la integración continua activa. Se entrega el enlace al repositorio con la etiqueta v0.1, que marca ese primer flujo completo, las instrucciones de ejecución en el archivo de lectura y la evidencia de la última corrida exitosa en GitHub Actions.

# **CAPÍTULO VII: MARKETING DEL PROYECTO**
## **Descripción de Producto y/o Experiencia**
evidentIA se presenta bajo el eslogan (Tu primera línea de defensa contra el fraude visual). Su elemento distintivo son las esquinas de un visor, en verde lima, que enmarcan lo que se examina: el logotipo en el acceso, la imagen elegida o el estado vacío de una pantalla. La paleta combina un azul institucional para las acciones con un verde bosque para el panel de marca. La escala de indicios utiliza gris, amarillo, ámbar y naranja, siempre acompañados del nombre escrito, y el verde nunca representa una imagen auténtica, para no sugerir un veredicto.
La experiencia se diseña para profesionales sin formación técnica. Una portada pública presenta el problema, las cuatro capas del análisis y los planes, y conduce al registro con el plan ya elegido. El registro se reduce de entre cuatro y seis pasos a entre dos y tres, sin volver a preguntar lo que la persona ya elige. Un caso se recorre en tres etapas (cargar, analizar e informar), el progreso del análisis se muestra por imagen y por capa, y el informe ocupa dos páginas, en el vocabulario del rubro. Esta experiencia resulta de una auditoría heurística de las 19 pantallas del sistema, en computadora y en celular, y de sucesivas rondas de validación de diseños de alta fidelidad con la autora antes de programar, en las que se descartan propuestas y se combinan partes de distintas direcciones. Como resultado, la pantalla del caso pasa de unos 8.800 píxeles de alto a una etapa por vez, y el perfil, de cinco tarjetas apiladas a cuatro pestañas.
## **Descripción de dinámicas de intercambio por cada perfil de interesado y/o usuario**
El abogado litigante se registra de forma gratuita y trabaja en su espacio personal. Recibe las fotografías de su cliente desde su propio celular o mediante el enlace para la persona afectada, y obtiene un informe que puede utilizar para fundamentar un pedido de pericia; cuando trabaja en equipo, crea un estudio jurídico y accede a un plan de pago. La aseguradora registra a la empresa desde el catálogo de la SSN y, una vez aprobada por el administrador, su referente invita a los analistas de siniestros. El valor que obtiene es la verificación previa a la liquidación, con la trazabilidad del origen de cada fotografía.
La persona afectada, sin crear una cuenta, sube sus fotografías mediante un enlace, después de una declaración expresa, y gana así una vía directa que evita las recompresiones intermedias de canales como WhatsApp. El perito y el juez, destinatarios indirectos, reciben un informe reproducible, con las versiones de los componentes, que pueden verificar escaneando el código QR sin necesidad de una cuenta.
## **Descripción de estrategias de publicidad y promoción del proyecto**
La estrategia de promoción constituye un plan para la etapa posterior al proyecto y prevé dos canales. En el canal profesional, contempla presentaciones en colegios profesionales de la región [confirmar contacto con el Colegio de Abogados de Corrientes] y en jornadas de LegalTech, con el respaldo del referente consultado. En el canal asegurador, contempla el contacto a través de los productores y asesores de seguros, que funcionan como vía de acceso a las compañías (Capítulo IV), con una demostración del informe verificable. Se prevé complementarla con contenido educativo breve, por ejemplo sobre cómo se pierde el manifiesto C2PA al enviar una imagen por WhatsApp, apoyado en las pruebas de canales propias (Tabla 6). La presentación del trabajo en el congreso CoNaIISI 2026, en noviembre, constituye la primera difusión académica del proyecto. La portada pública funciona como punto de llegada de esas acciones, y el propio producto actúa como medio de promoción, ya que cada informe verificado por un tercero expone la marca en la página pública de verificación. 
## **Iniciativas de engagement**
El plan personal gratuito, con diez análisis por mes, busca generar el hábito de uso antes del pase a un plan de organización. Las notificaciones por correo, al terminar un análisis y antes del vencimiento de la retención, mantienen el contacto con el usuario. Durante el período de prueba, la autora utiliza Microsoft Clarity para observar de forma agregada dónde se traban los usuarios, con todo el contenido de la página enmascarado. La herramienta se retira antes de la versión final (Microsoft, s. f.) [pendiente: confirmar con los tutores el momento del retiro]. Se prevé además un programa piloto con un estudio jurídico y una aseguradora del NEA, con devolución sobre el informe, y la medición de la usabilidad mediante el cuestionario SUS. 



# **CAPÍTULO VIII: PROPIEDAD INTELECTUAL**
## **Definición de Marca y/o activos a proteger**
El proyecto se identifica con la denominación evidentIA, acompañada de un logotipo construido a partir de las esquinas de un visor, que enmarcan lo que se examina. Como se expone en los resultados de la búsqueda en el INPI, la denominación se mantiene como nombre del proyecto académico, pero no resulta registrable como marca en las clases del servicio, por lo que la protección de la propiedad intelectual se apoya principalmente en los demás activos del proyecto.
El principal activo a proteger es el software. El código fuente puede registrarse como obra inédita en la Dirección Nacional del Derecho de Autor, dado que la Ley N.° 11.723 incluye a los programas de computación entre las obras protegidas (República Argentina, 1933). Se protegen además, como información confidencial, la base de reglas de severidad del análisis de metadatos, los textos del informe adaptados a cada rubro y el modelo entrenado del clasificador, que no se publica en el repositorio. Los componentes de terceros que integran el sistema, como ExifTool, c2pa-python, PyTorch y ONNX Runtime, se utilizan bajo sus respectivas licencias de código abierto, que se documentan en el repositorio.
## **Definición de clases internacionales a seleccionar**
Según la Clasificación de Niza, en su 13.ª edición, vigente en Argentina desde el 1 de enero de 2026 (Instituto Nacional de la Propiedad Industrial, 2026a), el servicio corresponde principalmente a la clase 9, que comprende el software descargable y las aplicaciones informáticas para el análisis de imágenes, y a la clase 42, que comprende el software como servicio, los servicios de análisis e investigación tecnológica y la autenticación de datos. De forma complementaria, se consideran la clase 45, por los servicios vinculados al ámbito jurídico, y la clase 36, por los servicios de evaluación de reclamos de seguros. Estas clases orientan la búsqueda de antecedentes y el eventual registro de una denominación comercial. 
## **Resultados de búsquedas en la Plataforma INPI**
La búsqueda se realiza el 29 de octubre de 2026 en la base pública de marcas del Instituto Nacional de la Propiedad Industrial (Instituto Nacional de la Propiedad Industrial [INPI], 2026b), mediante la búsqueda avanzada de la denominación evidentIA en las clases seleccionadas, y sus resultados se presentan en la Tabla 15 (Anexo M). 
##### **Tabla 15.** Resultados de la búsqueda de antecedentes en el INPI 
|  |  |  |  |  |  |  |
| :- | :- | :- | :- | :- | :- | :- |
| Acta | Denominación | Tipo de marca | Clase | Fecha de ingreso | Estado | Vencimiento |
| 4689054  | EVIDENTIA  | Denominativa | 42 | 04/04/2026  | Concedida | 01/06/2036 |
| 4689058  | EVIDENTIA | Denominativa | 9 | 04/04/2026 | Concedida | 01/06/2036 |
| 4756953  | EVIDENTIA ESTUDIO PERICIAL | Mixta | 42 | 29/07/2026 | Concedida | 29/09/2036 |

*Nota. Elaboración propia a partir de la base de marcas del INPI, consultada el 29/10/2026. Se omiten los datos de los titulares. *
La búsqueda identifica la denominación EVIDENTIA concedida a un tercero como marca denominativa en las clases 9 y 42, que son precisamente las que corresponden al servicio, y la marca mixta EVIDENTIA ESTUDIO PERICIAL en la clase 42, perteneciente a un actor del mismo sector pericial. Dado que la parte denominativa es idéntica, la incorporación de un logotipo no resulta suficiente para distinguir la marca, por lo que la denominación evidentIA no puede registrarse en las clases del servicio. En consecuencia, evidentIA se mantiene como nombre del proyecto en el ámbito académico, y la adopción de una denominación registrable queda como condición previa a una eventual explotación comercial. La búsqueda cumple así su función preventiva: detecta el conflicto antes de invertir en el registro y en la difusión de la marca. 

# **CAPÍTULO IX: DISEÑO DE SOLUCIÓN**

## **Arquitectura del Sistema de Información**

El sistema se organiza en un único repositorio que contiene una interfaz React, construida con Vite, y un backend Flask que expone una API REST bajo la ruta /api, en el mismo dominio. La sesión se mantiene mediante cookies seguras, guardadas en Redis, con protección contra falsificación de pedidos (CSRF). El backend respeta la secuencia rutas, servicios, repositorios y modelos, en la que cada capa depende solo de la inmediatamente inferior, regla que la integración continua verifica en cada cambio. Los análisis se encolan en Redis y los procesa un trabajador independiente, que actualiza el progreso que la interfaz consulta cada pocos segundos, de modo que el usuario ve avanzar el análisis, la carga desde el celular y la acreditación del pago sin recargar la página. La evolución desde la propuesta inicial, con plantillas Jinja2, hacia esta arquitectura queda documentada en los registros de decisiones del proyecto (Tabla 14). La Figura 13 presenta el despliegue y la Figura 14, los componentes del backend.

##### **Figura 13.** Diagrama de despliegue

![](diagramas/07-despliegue-uml.png)

*Nota. Elaboración propia, en notación UML 2.5. Datos verificados contra la infraestructura declarada en Terraform.*

## **Diseño de Solución**

El diseño aplica Strategy para las capas de análisis, el almacenamiento, la cola, el sello de tiempo, el cobro y la verificación de identidad; Repository para el acceso a datos; Service Layer para la lógica de negocio; Factory para la configuración por entorno; y Decorator para el control de acceso. Cada pieza intercambiable cuenta con una implementación real y una simulada, de modo que el sistema puede probarse sin servicios externos y un proveedor puede reemplazarse sin modificar el resto, como muestra la Figura 14. Los textos de análisis siguen una decisión de diseño específica sobre el marco normativo y la supervisión humana, que exige el descargo de IA, la presencia de una persona en el circuito de decisión y la publicación de los umbrales.

##### **Figura 14.** Diagrama de componentes del backend

![](diagramas/08-componentes-uml.png)

*Nota. Elaboración propia, en notación UML 2.5, generado desde el código.*

La Figura 15 muestra la secuencia completa de un caso: la carga de las imágenes con su huella y su sello, el análisis en segundo plano por las cuatro capas, la generación del informe una vez confirmados los sellos, y la verificación pública por parte de un tercero.

##### **Figura 15.** Secuencia de un caso, desde la carga hasta la verificación

![](diagramas/05-secuencia-de-un-caso.png)

*Nota. Elaboración propia, en notación UML 2.5.*

La migración del sello de tiempo constituye el caso de diseño más ilustrativo. El plan original utiliza Blockchain Federal Argentina (Blockchain Federal Argentina, s. f.), sugerida por el referente de LegalTech por su valor probatorio local. Entre el 21 y el 22 de octubre se diagnostica, mediante pruebas desde la computadora de la autora y desde el servidor de AWS, que la dirección documentada no existe, que el servicio en su versión 2.0 responde con error 404 y que la versión 1.0 funciona, pero bloquea las conexiones desde fuera de Argentina, donde se ubica el servidor. Se evalúa y se descarta solicitar el sello desde el navegador del usuario, y se adopta Hedera Consensus Service (Hedera Hashgraph, s. f.) por su bajo costo, de aproximadamente US$ 0,0008 por registro; por su verificación pública en HashScan y en su *mirror node*; por contar con un SDK oficial; y porque permite reutilizar el mismo mecanismo para sellar informes y versiones del sistema. La clave privada se guarda únicamente en Parameter Store. Gracias al patrón Strategy, el cambio de proveedor no modifica el resto del sistema. El sello se prueba contra el servicio real el 2 de noviembre: la página pública de estado informa «Funciona» solo cuando el *mirror node* devuelve la huella sellada, porque antes el sello superaba todas las pruebas automáticas y aun así fallaba en producción.

La autora decide, el 23 de noviembre, mantener el sello en la red de pruebas de Hedera (*testnet*), también para la defensa, en lugar de pasar a la red principal, como estaba previsto. La red de pruebas es pública y verificable, y no tiene costo, pero se reinicia periódicamente y borra los mensajes antiguos; por eso la plataforma conserva los recibos de cada sello y la guía de verificación lo advierte. Para que la verificación no dependa de la plataforma, el informe indica la red y el tema públicos donde se registra su huella, y una guía pública explica cómo calcular la huella SHA-256 del PDF en Windows, Mac o Linux y encontrarla en HashScan. El informe no puede incluir el enlace a su propio registro, porque el sello se solicita después de generarlo; la persona busca la huella entre los mensajes de la fecha del informe [integración pendiente en la rama de la funcionalidad 048].

El inicio de sesión con Google se implementa con OpenID Connect (OpenID Foundation, 2014; Google, s. f.), mediante código de autorización y PKCE del lado del servidor, sin JavaScript de terceros. El diseño evita el llamado secuestro previo de cuentas: si otra persona registró un correo sin verificarlo, la contraseña asociada se anula al vincular la cuenta de Google.

El cobro y la verificación de identidad siguen el mismo patrón que el sello. El cobro se diseña primero con Cresium, por transferencia a una cuenta virtual, y el 23 de noviembre se reemplaza por Mercado Pago, mediante su API de órdenes para pagos en línea, con avisos firmados que la plataforma valida antes de acreditar el plan (Mercado Pago, s. f.). La verificación de la identidad de quien registra una aseguradora se integra con Identik, que no guarda datos biométricos en la plataforma: el sistema conserva solo el resultado y una huella del enlace. Ambas integraciones funcionan hoy con su implementación simulada, y la conexión con los servicios reales queda en curso [completar cuando se prueben contra los entornos de prueba de cada proveedor].

Las fotografías tomadas con el celular plantean dos dudas, que se resuelven midiendo antes de cambiar. Las fuentes no coinciden sobre si el iPhone elimina los metadatos al subir una foto desde el navegador, por lo que se incorpora una página pública, «Probar mi celular», que muestra qué información llega por cada camino (galería, cámara o archivos) sin guardar la foto. En el análisis de niveles de error, un experimento con fotografías guardadas al 97 %, como las de un celular, muestra que lo que hacía parecer «alterada» toda la imagen era la escala del mapa, que amplificaba el ruido de una foto sin cambios; con un piso de escala, la proporción de píxeles marcados en una foto limpia baja de alrededor del 7 % a menos del 1 %, mientras una zona alterada se sigue destacando [integración pendiente en la rama de la funcionalidad 047].

## **Clasificador de imágenes sintéticas**

La cuarta capa de análisis estima la probabilidad de que una imagen haya sido generada por inteligencia artificial a partir de las huellas que deja el proceso de generación en la textura de la imagen, aun cuando la imagen no conserva metadatos ni credenciales de procedencia. Los detectores de este tipo alcanzan resultados altos con los generadores que conocen, pero pierden desempeño frente a generadores nuevos (Wang et al., 2020), y su eficacia depende más de la diversidad de los generadores de entrenamiento que de su cantidad de imágenes (Park y Owens, 2025). Por eso el clasificador se diseña desde el inicio como un componente que se mide con generadores que no ve durante el entrenamiento y con imágenes propias de las escenas del sistema, y que se reentrena por versiones. Su resultado se presenta siempre como un indicio que se combina con las otras tres capas y nunca como un veredicto.

### **Datos de entrenamiento**

El entrenamiento utiliza dos conjuntos públicos elegidos tras explorar ocho candidatos en cuanto a licencia, formato y contenido. Community Forensics reúne imágenes de miles de generadores, en su mayoría variantes de Stable Diffusion, y aporta diversidad de modelos (Park y Owens, 2025); OpenFake incorpora generadores comerciales recientes, como GPT Image 1, DALL·E 3, Midjourney 6, Ideogram 3 y FLUX 1.1 Pro (Livernoche et al., 2025). De cada conjunto se fija una revisión exacta, porque sus licencias, ambas no comerciales, cambian entre versiones; los demás candidatos se excluyen por licencia no verificable, por formato o por acceso pendiente. La muestra final se compone de 17 500 fotografías reales y 17 500 imágenes sintéticas de 210 generadores, con un máximo de imágenes por generador para que ninguno domine el entrenamiento (Tabla 16). La familia de generadores de Google (Imagen 4, Imagen 3 y Nano Banana 2, que es la que utiliza Gemini) se reserva completa fuera del entrenamiento, para medir cómo responde el modelo ante una herramienta comercial que no conoce.

##### **Tabla 16.** Datos de entrenamiento del clasificador

| Fuente | Fotografías reales | Imágenes sintéticas | Generadores | Licencia |
| :- | :- | :- | :- | :- |
| Community Forensics (subconjunto *Small*) | 7 500 | 7 500 | Variantes de Stable Diffusion, GAN y otros de código abierto | CC BY-NC-SA 4.0 |
| OpenFake | 10 000 | 10 000 | Comerciales y de código abierto recientes | CC BY-NC 4.0 en la revisión utilizada |
| **Total** | **17 500** | **17 500** | **210** | Uso no comercial |

*Nota. Elaboración propia. Se excluyen el contenido explícito, 66 generadores que no producen fotografías y las imágenes de menos de 256 píxeles de lado menor. La familia de Google queda fuera del entrenamiento.*

### **Control de calidad y normalización de los datos**

La exploración de los conjuntos revela un sesgo que, sin corrección, invalidaría el modelo: en OpenFake las fotografías reales son archivos JPEG de alta calidad con un lado menor mediano de 3 349 píxeles, mientras que las sintéticas rondan los 880 píxeles y llegan en PNG, JPEG o WebP; en Community Forensics, las sintéticas son PNG cuadrados de 512 píxeles. Un modelo entrenado así aprende a distinguir el formato o el tamaño, y no la generación. Para evitarlo, todas las imágenes de las dos clases atraviesan el mismo proceso: se convierten a RGB, se llevan a un lado menor elegido al azar entre 256 y 512 píxeles, sin agrandar nunca una imagen, y se guardan como JPEG con una calidad elegida al azar entre 75 y 95. Antes de entrenar, una etapa de validación detiene el proceso si encuentra imágenes corruptas, duplicadas, filtraciones de una misma imagen entre entrenamiento y prueba, generadores reservados presentes en el entrenamiento o un desbalance entre clases mayor al 5 %. Las imágenes se reparten en entrenamiento (80 %), validación (10 %) y prueba (10 %) de forma estratificada por clase y por generador, con una semilla fija que hace reproducible la partición. Cada versión de los datos queda identificada por la huella SHA-256 de su manifiesto, que se registra en la ficha del modelo.

### **Conjunto propio de evaluación**

Ningún conjunto público contiene imágenes generadas con las herramientas que usaría hoy quien falsifica una prueba, en las escenas de los casos del sistema y en las formas en que llegan a la plataforma. Por eso el proyecto construye un conjunto propio, con un protocolo escrito: imágenes generadas con ChatGPT, Gemini y Copilot a partir de una lista de 90 indicaciones numeradas, iguales para todas las herramientas, sobre siete escenas de los casos automovilísticos y laborales (choques, daños leves, vidrios rotos, lugar del siniestro, lesiones, lugar del accidente de trabajo y herramientas o elementos de protección dañados), cada una en su versión original y como captura de pantalla. Las lesiones se generan en seis tonos de piel, siguiendo de forma aproximada la escala de Fitzpatrick, para comprobar que el modelo responda igual para todas las personas. El protocolo exige además fotografías reales de las mismas escenas, porque si las reales mostraran otros temas, el modelo podría distinguir el tema en lugar de la generación. Al 16 de noviembre de 2026, el conjunto propio contiene 49 imágenes generadas de choques (12 de ChatGPT, 17 de Copilot y 20 de Gemini, en versión original y captura) y todavía no incluye fotografías reales, que se suman a partir de fotografías tomadas por la autora y del conjunto público CarDD (Wang et al., 2023), cuyo acceso requiere un acuerdo de uso para investigación. El conjunto se guarda en una carpeta privada y nunca se sube al repositorio.

### **Arquitectura, entrenamiento y calibración**

El modelo parte de una red EfficientNet-B0 (Tan y Le, 2019) preentrenada con ImageNet, a la que se reemplaza la última capa por una salida única que estima la probabilidad de que la imagen sea sintética. Se elige por su equilibrio entre precisión y velocidad en un procesador común, lo que permite ejecutarla en el servidor sin una placa gráfica. El entrenamiento ajusta toda la red mediante transferencia de aprendizaje, con el optimizador AdamW (Loshchilov y Hutter, 2019), una tasa de aprendizaje inicial de 0,0003 que decrece con una curva de coseno, lotes de 64 imágenes y un máximo de 15 épocas con parada temprana tras tres épocas sin mejora, conservando siempre la mejor época según el área bajo la curva ROC en validación. Durante el entrenamiento, cada imagen recibe transformaciones al azar que simulan lo que le ocurre a una fotografía antes de llegar al sistema: reducción de tamaño, recompresión JPEG con calidad entre 50 y 95, recorte de 224 × 224 píxeles en cualquier zona y espejado horizontal. Al terminar, las probabilidades se calibran mediante escalado por temperatura (Guo et al., 2017), de modo que un 70 % signifique efectivamente que siete de cada diez imágenes con ese valor son sintéticas; el error de calibración en validación baja de 0,069 a 0,020. El modelo calibrado se exporta al formato ONNX, se comprueba que su salida coincida con la del modelo original con una diferencia máxima de 0,001, y en la plataforma analiza cada imagen mediante cinco recortes (las cuatro esquinas y el centro), cuyo resultado se promedia, en unos 23 milisegundos por imagen. El entrenamiento se ejecuta en Google Colab Pro, y cada etapa del proceso puede retomarse sin rehacer las anteriores si la sesión se interrumpe.

### **Evaluación y compuerta de publicación**

El modelo se evalúa sobre tres conjuntos que miden cosas distintas: el conjunto de prueba, con generadores que el modelo conoce; los generadores reservados, que miden la capacidad de generalizar a una herramienta comercial nueva; y el conjunto propio, que mide el desempeño en las condiciones reales del sistema, con las imágenes tal como llegan, sin normalizar. Una compuerta automática solo publica una versión si cumple cinco condiciones: un área bajo la curva ROC de al menos 0,90 en el conjunto de prueba, la coincidencia entre el modelo exportado y el original, una ficha técnica completa, la correspondencia entre la huella de los datos declarados y la de los datos utilizados, y un código sin cambios pendientes de registrar. La ficha técnica de cada versión se genera de forma automática, siguiendo la propuesta de fichas de modelo de Mitchell et al. (2019), con el uso previsto, las limitaciones, los datos y sus licencias, el entrenamiento, el entorno, las métricas por generador y los datos para reproducirlo (Anexo Q). El proceso completo, desde la obtención de los datos hasta el uso del modelo en la plataforma, se presenta en la Figura 16.

##### **Figura 16.** Pipeline del clasificador de imágenes

![](diagramas/12-pipeline-red-neuronal.png)

*Nota. Elaboración propia, diagrama de actividad en notación UML 2.5.*

### **Resultados**

La versión 1.0.0 cumple el valor de referencia del proyecto con margen: alcanza un área bajo la curva ROC de 0,961 y un F1-score de 0,904 en el conjunto de prueba, y conserva un área de 0,938 frente a la familia de Google, que no participa del entrenamiento (Tabla 17). El análisis por generador muestra que el modelo supera el 0,99 con las variantes de Stable Diffusion y con StyleGAN2, y que los generadores comerciales más difíciles son Midjourney 6, del que detecta el 68 %, y FLUX 1.1 Pro, del que detecta el 54 %. El resultado sobre el conjunto propio es, en cambio, el hallazgo más importante de esta capa: de las 49 imágenes de choques generadas con ChatGPT, Gemini y Copilot, el modelo identifica como sintéticas solo 5 con el umbral de 0,5, y la primera prueba en producción con una imagen de ese conjunto arroja una probabilidad cercana a cero. Como el conjunto propio todavía no incluye fotografías reales de las mismas escenas, no es posible calcular su área bajo la curva y, por lo tanto, no se puede distinguir si el modelo ordena correctamente esas imágenes con otro umbral o si directamente no las reconoce. Las causas posibles son dos: las herramientas comerciales de 2025 y 2026 son más recientes que los generadores de los conjuntos públicos, y las escenas de autos dañados no forman parte de los datos de entrenamiento. Este resultado confirma la decisión de diseño de no basar la conclusión en una sola capa y de presentar la probabilidad como un indicio.

##### **Tabla 17.** Resultados del clasificador, versión 1.0.0

| Conjunto de evaluación | Imágenes | Área bajo la curva ROC | Otras métricas (umbral 0,5) |
| :- | :- | :- | :- |
| Prueba: generadores conocidos | 1 750 reales y 1 696 sintéticas | 0,961 | Exactitud 0,909; precisión 0,940; exhaustividad 0,870; F1 0,904 |
| Generadores no vistos: familia de Google | 1 750 reales y 219 sintéticas | 0,938 | Detecta 161 de 219 (74 %) |
| Conjunto propio: choques generados con ChatGPT, Gemini y Copilot | 49 sintéticas, sin reales | No calculable | Detecta 5 de 49 (10 %): Gemini 3 de 20, ChatGPT 1 de 12, Copilot 1 de 17 |

*Nota. Elaboración propia a partir del entrenamiento del 5 de noviembre de 2026. El área bajo la curva requiere imágenes de las dos clases; el conjunto propio todavía no tiene fotografías reales [actualizar cuando se sumen].*

### **Mejora continua por versiones**

El bajo desempeño con las herramientas comerciales lleva a una decisión de diseño: el clasificador se mejora de forma continua y por versiones, sin perder la posibilidad de medir esa mejora con honestidad. El conjunto propio se divide de antemano en dos partes que nunca se mezclan: una evaluación fija, que nunca se utiliza para entrenar y contra la que se compara cada versión, y una parte de ajuste, que se suma al entrenamiento de la versión siguiente. La unidad que se asigna a cada parte es la indicación de generación y no el archivo, de modo que las imágenes de una misma escena producidas con distintas herramientas o en distintas variantes quedan siempre del mismo lado; de lo contrario, el modelo vería durante el entrenamiento la misma escena con la que luego se lo evalúa. La asignación sigue una regla reproducible que no depende de las demás imágenes: las 89 indicaciones de la lista se reparten mitad y mitad dentro de cada escena y de cada tono de piel, y las imágenes nuevas se asignan mediante una huella con semilla fija, por lo que sumar imágenes no cambia de lado a ninguna. Cada reentrenamiento produce una versión nueva, que solo se publica si, además de superar la compuerta, mejora a la anterior sobre la evaluación fija y no empeora con los generadores reservados; si no lo logra, se registra y se descarta. Este criterio sigue el nivel de madurez de MLOps con un pipeline automatizado y reentrenamiento a pedido (Google Cloud, s. f.). Las imágenes de los usuarios del sistema nunca se utilizan para entrenar, porque son confidenciales.

### **Integración en la plataforma**

El modelo publicado se guarda en un repositorio privado de modelos de Hugging Face, identificado por su número de versión, y la plataforma lo descarga, verifica su huella antes de usarlo y lo conserva fuera de cada despliegue. La versión 1.0.0 se publica el 10 de noviembre de 2026 y se activa en producción como cuarta capa. Cada resultado guarda la probabilidad, la versión y la huella del modelo, la huella de los datos con que se entrena, el commit que lo produce y la versión del motor de ejecución, de modo que cualquier análisis puede reproducirse y auditarse. Por debajo de una probabilidad del 50 %, la capa no aporta indicios; por encima, su nivel equivale a la probabilidad calibrada, con un tope de 90, porque el máximo queda reservado a la evidencia criptográfica de la capa de credenciales de procedencia. La conclusión de la capa enuncia siempre sus tres limitaciones: no detecta ediciones parciales sobre una fotografía real, puede fallar con generadores que no conoce y una probabilidad baja no indica que la imagen sea real. Si el modelo no está disponible o su archivo no coincide con la huella registrada, la capa se informa como no disponible, con el motivo, y las otras tres se presentan igual.

### **Limitaciones y consideraciones éticas**

El clasificador presenta limitaciones que el informe de cada caso declara. Su desempeño con las herramientas comerciales actuales en las escenas del sistema es bajo, y su medición en condiciones reales todavía no incluye fotografías reales de esas escenas. No detecta ediciones localizadas sobre una fotografía auténtica, que quedan a cargo del análisis del nivel de error. Los datos de entrenamiento no se depuran de casi duplicados ni de fotografías reales de OpenFake que no son fotografías de cámara, y los temas de las imágenes reales y sintéticas difieren entre conjuntos, lo que se mitiga en parte con la evaluación por generador y en condiciones reales. Las licencias de los conjuntos utilizados permiten el uso con fines de investigación, como el de este proyecto, pero una explotación comercial requiere reentrenar con datos de licencia compatible y verificar los términos de uso de las herramientas generativas para el entrenamiento de un detector. En el plano ético, el diseño mide el desempeño por tono de piel en las imágenes de lesiones, nunca utiliza imágenes de usuarios ni de causas reales, y presenta el resultado como una probabilidad calibrada y explicada, acompañada del descargo de que no constituye un dictamen pericial, conforme al principio de supervisión humana que orienta al sistema (Parlamento Europeo y Consejo de la Unión Europea, 2024).

El clasificador de imágenes sintéticas no garantiza la detección de imágenes producidas con herramientas posteriores a su entrenamiento ni de ediciones parciales sobre una fotografía auténtica, y su desempeño en las escenas del sistema depende de su reentrenamiento periódico.

El entrenamiento utiliza además timm para la arquitectura preentrenada, MLflow para registrar cada experimento y Hugging Face como fuente de los conjuntos de datos y como registro privado de las versiones del modelo.

Google Cloud. (s. f.). *MLOps: Continuous delivery and automation pipelines in machine learning*. https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning

Guo, C., Pleiss, G., Sun, Y., y Weinberger, K. Q. (2017). On calibration of modern neural networks. En *Proceedings of the 34th International Conference on Machine Learning* (pp. 1321-1330). PMLR.

Livernoche, V., Arodi, A., Musulan, A., Yang, Z., Salvail, A., Marceau Caron, G., Godbout, J.-F., y Rabbany, R. (2025). *OpenFake: An open dataset and platform toward large-scale deepfake detection* (arXiv:2509.09495). arXiv. https://arxiv.org/abs/2509.09495

Loshchilov, I., y Hutter, F. (2019). Decoupled weight decay regularization. En *International Conference on Learning Representations*. https://openreview.net/forum?id=Bkg6RiCqY7

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., y Gebru, T. (2019). Model cards for model reporting. En *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 220-229). https://doi.org/10.1145/3287560.3287596

Park, J., y Owens, A. (2025). Community Forensics: Using thousands of generators to train fake image detectors. En *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 8245-8257).

Tan, M., y Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. En *Proceedings of the 36th International Conference on Machine Learning* (pp. 6105-6114). PMLR.

Wang, S.-Y., Wang, O., Zhang, R., Owens, A., y Efros, A. A. (2020). CNN-generated images are surprisingly easy to spot… for now. En *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 8695-8704).

Wang, X., Li, W., y Wu, Z. (2023). CarDD: A new dataset for vision-based car damage detection. *IEEE Transactions on Intelligent Transportation Systems, 24*(7), 7202-7214. https://doi.org/10.1109/TITS.2023.3258480

## **Modelo de Datos**

El modelo se compone de las siguientes entidades, que la Figura 17 presenta con sus claves. El usuario registra su perfil y su estado. La organización registra su tipo, su plan y sus miembros con el rol de cada uno. El caso registra su número interno, el expediente, el espacio al que pertenece, su estado, su plazo de retención y los permisos por usuario. La imagen guarda su huella SHA-256, su formato, su origen y el recibo de su sello de tiempo. El análisis guarda los resultados por capa, la conclusión y la versión del sistema que lo realiza, incluida la versión y la huella del modelo del clasificador, y el informe guarda su huella, su código de verificación y su recibo. El enlace de carga guarda solo la huella de su código, junto con su vencimiento, su cupo y el dispositivo que lo usa por primera vez. La versión del sistema guarda el commit, la huella del artefacto desplegado y su recibo. El cobro registra el plan, el monto, el estado y la referencia de cada pago, y la verificación de identidad registra solo su resultado. Por último, las entradas de auditoría registran las operaciones relevantes. El modelo completo, con todas las columnas, se encuentra en el Anexo K.

##### **Figura 17.** Modelo de datos

![](diagramas/04-modelo-de-datos.png)

*Nota. Elaboración propia, generado desde los modelos del sistema. Se muestran las claves; el modelo completo está en el Anexo K.*

## **Infraestructura de comunicaciones y servidores**

La infraestructura se aloja en Amazon Web Services, región Irlanda, y se define por completo como código en Terraform. Una instancia EC2 t3.small, con disco cifrado y dirección IP fija, ejecuta Nginx (con TLS, límites de pedidos y cabeceras de seguridad), Gunicorn, PostgreSQL, Redis, el trabajador de análisis y las tareas programadas de sellos, retención y respaldo. Dos buckets privados de Amazon S3, cifrados y versionados, guardan respectivamente las imágenes con los informes y los respaldos de la operación, que vencen a los 30 días. Amazon SES envía los correos, Parameter Store resguarda los secretos y un presupuesto con alertas controla el gasto. La plataforma se publica en el dominio propio evidentiaa.com.ar, registrado en NIC Argentina. Su zona de DNS se administra en Amazon Route 53 y se define también en Terraform, junto con la identidad del dominio en Amazon SES, sus firmas DKIM y una política DMARC, de modo que los correos salen desde el dominio y los receptores pueden comprobar su origen. El certificado HTTPS se obtiene de Let's Encrypt, sin costo, y se renueva de forma automática [confirmar que la delegación del dominio y el certificado funcionan; si no, indicar que la plataforma migra al dominio y que hasta entonces se publica en la dirección de la instancia].

## **Entornos de trabajo**

El desarrollo local se realiza en Windows con WSL2, con los servicios auxiliares en contenedores; las pruebas se ejecutan en la integración continua de GitHub Actions, que además levanta el sistema completo para recorrer sus pantallas con los sensores de diseño, accesibilidad y teclado; la producción corre en Amazon Web Services; y el entrenamiento del clasificador se realiza en Google Colab Pro. La configuración se separa por entorno, y los secretos nunca ingresan al repositorio.

## **Solución**

Las Figuras 18 a 23 presentan las pantallas principales del sistema en producción, con datos de prueba.

[Insertar capturas del sistema en producción con datos de prueba: Figura 18, portada pública con los planes; Figura 19, registro por pasos; Figura 20, caso con sus tres etapas (carga, análisis e informe); Figura 21, resultado del análisis por capa con el mapa del ELA; Figura 22, informe PDF por rubro; Figura 23, página pública de verificación. Nota de cada una: *Elaboración propia, captura del sistema en producción con datos de prueba.*]


# **CAPÍTULO X: RECURSOS DEL PROYECTO**

## **Recursos humanos del proyecto**

El proyecto cuenta con la autora, Valentina Salmón, que asume las funciones de analista, diseñadora del producto, responsable de las decisiones y gestora del proceso. Su dedicación se estima en unas [460] horas, a partir de las fechas del relevamiento, de los días con actividad registrada en el repositorio y en la bitácora, y de la dedicación de 40 horas semanales declarada para la etapa de desarrollo [estimación a validar por la autora]. Los docentes de la cátedra, Sergio Lapertosa, Augusto Portillo y Martín Jones, realizan el seguimiento y la evaluación, y este último actúa además como revisor técnico. Federico Miskinich, referente de LegalTech en Corrientes, aporta el contraste del diseño con el sector, y los participantes del relevamiento (once abogados, dos peritas y un productor de seguros) aportan la validación de las necesidades. El desarrollo se apoya, por último, en un agente de inteligencia artificial, Claude Code, utilizado como herramienta de desarrollo bajo la supervisión de la autora, quien revisa e integra todo el trabajo que produce (Anexo O).

## **Recursos físicos y materiales**

Se utiliza la computadora personal de la autora, con un procesador AMD Ryzen 5 5600G de 3,90 GHz con gráficos integrados Radeon, 16 GB de memoria RAM y una unidad de almacenamiento de 447 GB, sobre Windows con WSL2. Con ella se realizan el desarrollo, la ejecución local del sistema, la redacción del informe y la gestión del proyecto. Se utilizan además dos teléfonos celulares, un [completar modelo] con sistema Android y un iPhone 15 Pro Max, con los que se realizan las pruebas de canales, la carga de imágenes mediante el código QR, incluido el formato HEIC, y la revisión de las pantallas en el ancho de un celular. No se requiere equipamiento especializado, porque el entrenamiento del clasificador se realiza en la nube, en Google Colab, y la placa gráfica integrada de la computadora no interviene en ese proceso.

## **Recursos financieros**

Las herramientas de desarrollo, gestión e integración continua se utilizan en sus versiones gratuitas, con excepción de la suscripción al agente de inteligencia artificial y del dominio propio. El sello en la red de pruebas de Hedera no tiene costo. El cobro mediante Mercado Pago implica una comisión por operación, y la verificación con Identik, un costo por verificación (Identik, s. f.), de US$ 0,80 por verificación biométrica según la cotización que el proveedor envía en noviembre de 2026; ambos se trasladan al precio de los planes. Al registrar el dominio se adquiere también un certificado SSL comercial que la plataforma no utiliza, porque el servidor obtiene un certificado gratuito de Let's Encrypt; el gasto se informa por transparencia y el certificado no se renueva. La Tabla 18 resume los costos del proyecto.

##### **Tabla 18.** Presupuesto del proyecto

| Concepto | Detalle | Costo |
| :- | :- | :- |
| Amazon Web Services | Instancia EC2, almacenamiento S3, correo SES, Route 53 y transferencia de datos | [completar con la factura de AWS; cubierto por créditos gratuitos] |
| Dominio evidentiaa.com.ar | Registro anual en NIC Argentina por medio de DonWeb | ARS 17.900 por año, IVA incluido |
| Certificado SSL comercial | Adquirido junto con el dominio, no utilizado | ARS 12.540 (no se renueva) [o quitar si DonWeb lo reintegra] |
| Certificado HTTPS en uso | Let's Encrypt, con renovación automática | Sin costo |
| Hedera | Sello de tiempo en la red de pruebas | Sin costo |
| Agente de inteligencia artificial | Suscripción a Claude | [US$ 20 por mes × cantidad de meses; completar] |
| Google Colab Pro | Entrenamiento del clasificador | Incluido en la suscripción de la autora |
| Hugging Face | Conjuntos de datos y registro privado de modelos | Sin costo |
| Mercado Pago | Comisión por cobro de los planes | [completar porcentaje por operación] |
| Identik | Verificación de identidad de la aseguradora | US$ 0,80 por verificación |
| Microsoft Clarity, GitHub, Trello y Terraform | Uso, repositorio, integración continua, gestión e infraestructura como código | Sin costo |
| Horas de trabajo de la autora | [460] horas estimadas | [horas × valor hora de referencia; citar la fuente del valor] |
| **Total** | | [completar] |

*Nota. Elaboración propia. Valores en dólares estadounidenses o en pesos argentinos, según el proveedor.*

## **Recursos tecnológicos**

El backend se desarrolla en Python con Flask, SQLAlchemy y Alembic, sobre una base de datos PostgreSQL, y procesa los análisis en segundo plano con Redis y RQ. La interfaz se construye con React y Vite. Las capas de análisis utilizan ExifTool y Pillow para los metadatos, c2pa-python para las credenciales de procedencia, y PyTorch, timm y ONNX Runtime para el entrenamiento y la ejecución del clasificador, con MLflow para registrar los experimentos y Hugging Face como fuente de datos y registro de modelos. Los informes se generan con WeasyPrint, y el sello de tiempo se registra mediante el SDK oficial de Hedera. La infraestructura se define con Terraform sobre Amazon Web Services, con el DNS en Route 53, y la integración y el despliegue continuos se ejecutan en GitHub Actions, con Dependabot para las actualizaciones. La calidad se controla con pytest, flake8, pylint, import-linter, ESLint, Vitest, Playwright y axe-core, y la gestión del trabajo se realiza en Trello.

## **Otros recursos del proyecto**

El proyecto se apoya también en recursos de información de acceso público: los conjuntos de datos de imágenes reales y generadas utilizados para entrenar el clasificador, el catálogo de entidades activas de la Superintendencia de Seguros de la Nación, publicado como datos abiertos, la lista de confianza del consorcio C2PA y la bibliografía técnica, normativa y metodológica citada en el informe. Se suman las imágenes de prueba generadas con ChatGPT, Gemini y Copilot para las pruebas de canales y para el conjunto propio del clasificador, que reemplazan el uso de imágenes de causas reales.


# **CAPÍTULO XI: OPORTUNIDADES DEL PROYECTO**

## **CANVAS del Proyecto**

El modelo de negocios se sintetiza en el lienzo de Osterwalder y Pigneur (2011), que la Tabla 19 presenta con los nueve bloques del proyecto.

##### **Tabla 19.** CANVAS del proyecto

| Bloque | Contenido |
| :- | :- |
| Segmentos de clientes | Estudios jurídicos y abogados litigantes en causas por accidentes de tránsito y laborales; aseguradoras con ramo automotor o de riesgos del trabajo y sus analistas de siniestros. Usuarios indirectos: personas afectadas que aportan imágenes y peritos que revisan el informe |
| Propuesta de valor | Verificación preliminar de imágenes en minutos, sin perito, con un informe por rubro que no emite veredictos, que expone valores y umbrales y que un tercero puede verificar mediante la huella registrada en Hedera, incluso sin depender de la plataforma |
| Canales | Plataforma web en evidentiaa.com.ar, portada con los planes, colegios profesionales, productores y asesores de seguros, congresos académicos y la página pública de verificación de cada informe |
| Relación con los clientes | Autoservicio con espacio personal gratuito, pilotos acompañados en Corrientes y soporte directo de la autora |
| Fuentes de ingresos | Suscripción mensual por organización (planes Básico y Profesional), cobrada con Mercado Pago, y, a futuro, convenios por volumen con aseguradoras |
| Recursos clave | Motor de análisis en cuatro capas, clasificador entrenado y su ciclo de reentrenamiento, infraestructura en AWS definida como código y conocimiento del dominio relevado |
| Actividades clave | Mantenimiento y reentrenamiento del clasificador, operación segura de la plataforma, soporte y validación con usuarios |
| Socios clave | Amazon Web Services, Hedera, Google (inicio de sesión), Mercado Pago, Identik, la Superintendencia de Seguros de la Nación (catálogo de aseguradoras) y la universidad |
| Estructura de costos | Infraestructura en la nube, dominio, comisiones de cobro, verificación de identidad, suscripción al agente de IA y horas de desarrollo |

*Nota. Elaboración propia, según el lienzo de Osterwalder y Pigneur (2011).*

## **Oportunidades futuras para escalar o innovar en el proyecto y futuros proyectos**

El proyecto deja abiertas varias líneas de crecimiento. La primera es una integración por API con los sistemas de gestión de siniestros de las aseguradoras, de modo que la verificación se dispare al recibir las fotografías, sin carga manual. La segunda es la extensión a otros rubros donde la imagen funciona como prueba, como los seguros de hogar, robo e incendio, propuesta por el referente de LegalTech y descartada para esta versión, que requiere ampliar el conjunto propio a esas escenas. La tercera es el análisis de video, en la medida en que los generadores de video realista se vuelven accesibles. La cuarta es la firma digital del informe, que sumaría al sello de tiempo la identificación del firmante, y el paso del sello a la red principal de Hedera para una explotación comercial. Por último, el ciclo de reentrenamiento del clasificador por versiones, con una evaluación fija sobre imágenes propias, constituye por sí mismo la base de un servicio de actualización continua frente a los generadores nuevos, y el patrón de piezas intercambiables permite incorporar detectores de terceros como capas adicionales sin modificar el resto del sistema.

# **CAPÍTULO XII: LECCIONES APRENDIDAS DEL PROYECTO**

## **Aspectos positivos del proyecto**

El relevamiento de campo previo al diseño resulta decisivo: la encuesta a abogados y las entrevistas con peritas y con el sector asegurador definen el informe por rubro, el lenguaje sin veredictos y la carga desde el celular, decisiones que no figuraban en la propuesta inicial, y descartan al perito como usuario antes de construir funciones para él. La especificación escrita antes de cada funcionalidad, junto con el arnés que rodea al agente de inteligencia artificial, permite sostener un ritmo alto de desarrollo con una cobertura de pruebas superior al 97 % y sin perder la trazabilidad entre el requisito, el código y la prueba. El diseño con piezas intercambiables demuestra su valor tres veces: cuando el servicio de sello previsto deja de estar disponible desde el exterior y se migra a Hedera, cuando el cobro pasa de Cresium a Mercado Pago, y cuando la verificación de identidad se integra con Identik, sin modificar el resto del sistema en ningún caso. Finalmente, probar cada integración contra el servicio real, y no solo con dobles de prueba, permite detectar en producción fallas que las pruebas automáticas no reproducen, y medir antes de cambiar, como en el caso de las fotografías del celular, evita corregir problemas que no existen.

## **Aspectos a mejorar para el proyecto**

La verificación de la marca en el INPI se realiza cuando la identidad visual ya está construida y revela que la denominación no es registrable: en un proyecto con fines comerciales conviene hacer esa búsqueda al inicio. El conjunto propio de imágenes para evaluar el clasificador se arma tarde y sin fotografías reales, lo que impide medir a tiempo su desempeño en las escenas del sistema; con más tiempo, ese conjunto se construye en paralelo con el entrenamiento. Las validaciones con usuarios, como la prueba de usabilidad y la evaluación del informe por un abogado y un analista de siniestros, se concentran al final del proyecto, cuando su resultado ya no puede modificar el diseño con la misma facilidad. Al registrar el dominio se adquiere un certificado comercial innecesario, porque la arquitectura ya obtenía uno gratuito: antes de contratar un servicio conviene verificar si el sistema ya lo resuelve. En cuanto al trabajo con el agente de inteligencia artificial, las reglas que solo están escritas se olvidan o quedan desactualizadas, los diagramas del informe se descartan en una primera versión por no respetar la notación ni coincidir con el sistema, y el flujo de ramas genera demasiados pull requests por cambios chicos; las tres experiencias llevan a convertir las reglas críticas en controles automáticos y a simplificar el proceso.

# **CAPÍTULO XIII: ENTREGABLES**

## **Prototipo**

El prototipo evoluciona en tres versiones, desde los bocetos iniciales hasta el sistema desplegado en producción, con validaciones de los interesados en cada etapa.

## **Versión 1: Mockups**

La primera versión comprende los bocetos de pantallas realizados en Excalidraw durante la iteración 0 (Anexo E), que corresponden a la etapa de ideación. Se suman los diseños de alta fidelidad elaborados durante el desarrollo, que la autora valida en sucesivas rondas antes de programarlos: la pantalla del caso por etapas, el perfil en pestañas, el registro por caminos y la portada pública. Las capturas de antes y después de cada ronda se conservan en el repositorio, junto con la especificación de cada funcionalidad.

## **Versión 2: prototipo funcional + feedback (Al menos 3 mapas de empatía, correspondiente a mínimo 3 STK)**

[Pendiente. La versión 2 es el sistema publicado en producción. Sus mapas de empatía se obtienen en la misma sesión que la prueba de usabilidad, con al menos tres interesados (por ejemplo, un abogado, un analista o productor de seguros y una persona afectada), mediante la plantilla del repositorio (Anexo N). Completar con los tres mapas, el puntaje SUS de cada sesión y los cambios que motivan.]

## **Versión 3: prototipo funcional + feedback (Al menos 3 mapas de empatía, correspondiente a mínimo 5 STK) y elementos mejorados.**

[Pendiente. Completar después de implementar los cambios de la versión 2, con al menos cinco interesados, sus mapas de empatía, el SUS final y la tabla «devolución → cambio realizado».]

## **Código Fuente del Proyecto**

El código fuente se aloja en GitHub, en el repositorio https://github.com/valentinasalmon/PFG-sistema-deteccion-IA, con la etiqueta v0.1 para el primer flujo completo y la etiqueta v1.0 para la versión final [crear la etiqueta v1.0 cuando el dominio, la prueba de usabilidad y el retiro de Clarity estén completos]. El repositorio anterior (https://github.com/valentinasalmon/TIF) se conserva como antecedente del código de agosto y septiembre. Las instrucciones para ejecutar el sistema se encuentran en el archivo de lectura y en la guía de instalación del entorno.

## **Documentación**

La documentación del proyecto se encuentra en el propio repositorio y comprende la constitución y la especificación general, con la visión, las reglas de negocio, los requisitos, los casos de uso y las cuestiones abiertas; la especificación, el plan y las tareas de cada funcionalidad; 23 registros de decisiones de arquitectura; la bitácora de trabajo, junto con una bitácora por cada actividad de evaluación; la documentación completa de la red neuronal, con su ficha técnica; la revisión de seguridad; la guía de identidad visual; las guías de instalación, ejecución local, despliegue y uso; el kit de la prueba de usabilidad y la plantilla de los mapas de empatía; los diagramas del sistema, generados y verificados contra el código; la página de versiones; y el mapa y el registro de cambios del arnés para el trabajo asistido por IA, incluido el arnés del informe final.

# **CONCLUSIONES DEL PROYECTO**

El proyecto parte de una brecha verificada en el campo: la mayoría de los abogados encuestados duda alguna vez de la autenticidad de una imagen, pero ninguno solicita una pericia, porque no dispone de una vía de verificación accesible. evidentIA responde a esa brecha con una plataforma web, publicada en producción, que analiza cada imagen en cuatro capas complementarias y entrega un informe por rubro, sin veredictos y verificable públicamente.

Los objetivos específicos se cumplen de la siguiente manera. El relevamiento de la necesidad (OE1) se realiza mediante una encuesta a abogados, entrevistas con peritas y con un productor de seguros, una reunión con un referente de LegalTech y una prueba propia del comportamiento de las imágenes al circular por mensajería. El enfoque multicapa (OE2) se define e implementa con el análisis de metadatos, la verificación de credenciales C2PA, el análisis del nivel de error y el clasificador de redes neuronales, de modo que las limitaciones de una capa se compensan con las otras. La arquitectura, los roles, la auditoría, la huella con sello de tiempo en Hedera y la retención conforme a la Ley N.° 25.326 (OE3) se implementan y se verifican con pruebas automáticas y en producción. El clasificador (OE4) alcanza un área bajo la curva ROC de 0,961 sobre el conjunto de prueba de generadores conocidos, por encima del valor de referencia de 0,90, aunque su desempeño con herramientas comerciales recientes en escenas de siniestros es bajo, lo que justifica su papel de indicio complementario y su reentrenamiento por versiones. [OE5: completar con el resultado de la validación del informe con el abogado y el analista de siniestros; hasta entonces: «La validación de la comprensión del informe sin intervención de un perito (OE5) se encuentra en curso».] El sistema se despliega en Amazon Web Services con despliegue automático y documentación completa de su funcionamiento, alcance y limitaciones (OE6).

El trabajo deja además una forma de desarrollar software con asistencia de inteligencia artificial en la que la calidad no depende del modelo, sino del arnés que lo rodea: especificaciones previas, controles automáticos que hacen cumplir las reglas críticas, memoria del proceso y una persona que decide. El recorrido del proyecto, con sus cambios de usuario, de infraestructura, de proveedor de sello y de cobro, muestra que las decisiones se sostienen mejor cuando se registran con su motivo y se revisan con evidencia nueva. El resultado no reemplaza la pericia ni la decisión humana, sino que le ofrece a quien debe decidir información estructurada, trazable y oportuna para hacerlo con fundamento.

# **AGRADECIMIENTOS**

[Redactar: docentes de la cátedra, referente de LegalTech, personas entrevistadas y encuestadas, familia.]


# **Bibliografía**

Amazon Web Services. (2026). *Ireland AWS Compliance Center — Financial Services*. https://aws.amazon.com/financial-services/security-compliance/compliance-center/ie/

Amped Software. (s. f.). *Amped Authenticate*. https://ampedsoftware.com

Anderson, D. J. (2010). *Kanban: Successful evolutionary change for your technology business*. Blue Hole Press.

Blockchain Federal Argentina. (s. f.). *BFA*. https://bfa.ar

Brooke, J. (1996). SUS: A «quick and dirty» usability scale. En P. W. Jordan, B. Thomas, B. A. Weerdmeester e I. L. McClelland (Eds.), *Usability evaluation in industry* (pp. 189-194). Taylor y Francis.

C2PA. (s. f.). *C2PA technical specification, version 2.4*. https://spec.c2pa.org/specifications/specifications/2.4/index.html

CheckThat.ai. (s. f.). *Best AI image detector tools 2026*. https://checkthat.ai/answers/what-are-the-best-ai-image-detector-tools

Conventional Commits. (s. f.). *Conventional Commits 1.0.0*. https://www.conventionalcommits.org/

Creati.ai. (s. f.). *Detector de Imágenes IA*. https://creati.ai/es/ai-tools/ai-image-detector/

Cresium. (s. f.). *Cresium*. https://cresium.com

Fritz AI. (s. f.). *The best AI image detectors*. https://fritz.ai/best-ai-image-detectors/

GitHub. (s. f.). *Spec Kit*. https://github.com/github/spec-kit

Google. (s. f.). *OpenID Connect*. Google for Developers. https://developers.google.com/identity/openid-connect/openid-connect

Google Cloud. (s. f.). *MLOps: Continuous delivery and automation pipelines in machine learning*. https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning

Guo, C., Pleiss, G., Sun, Y., y Weinberger, K. Q. (2017). On calibration of modern neural networks. En *Proceedings of the 34th International Conference on Machine Learning* (pp. 1321-1330). PMLR.

Hedera Hashgraph. (s. f.). *Hedera Consensus Service*. https://hedera.com/consensus-service

Identik. (s. f.). *Identik*. https://identik.me/

Instituto Nacional de la Propiedad Industrial. (2026a). *Clasificación Internacional de Productos y Servicios (Clasificación de Niza, 13.ª edición)*. https://portaltramites.inpi.gob.ar/

Instituto Nacional de la Propiedad Industrial. (2026b). *Búsqueda avanzada de marcas* \[Base de datos\]. https://portaltramites.inpi.gob.ar/

International Organization for Standardization. (2019). *ISO/IEC 27701:2019: Security techniques — Extension to ISO/IEC 27001 and ISO/IEC 29100 for privacy information management — Requirements and guidelines*.

International Organization for Standardization. (2022). *ISO/IEC 27001:2022: Information security, cybersecurity and privacy protection — Information security management systems — Requirements*.

International Organization for Standardization. (2023). *ISO/IEC 42001:2023: Information technology — Artificial intelligence — Management system*.

James, J. (s. f.). *Amped Authenticate from Amped Software*. Forensic Focus. https://www.forensicfocus.com/reviews/amped-authenticate-from-amped-software/

Kendall, K. E., y Kendall, J. E. (2005). *Análisis y diseño de sistemas* (6.ª ed.). Pearson Educación.

Köbis, N. C., Doležalová, B., y Soraperra, I. (2021). Fooled twice: People cannot detect deepfakes but think they can. *iScience, 24*(11), Artículo 103364. https://doi.org/10.1016/j.isci.2021.103364

Lars, D. (2026, 24 de febrero). El fraude perfecto llegó a los seguros: así están usando IA para inventar daños "creíbles". *Forbes Argentina*. https://www.forbesargentina.com/innovacion/el-fraude-perfecto-llego-seguros-asi-estan-usando-ia-inventar-danos-creibles-n86703

Livernoche, V., Arodi, A., Musulan, A., Yang, Z., Salvail, A., Marceau Caron, G., Godbout, J.-F., y Rabbany, R. (2025). *OpenFake: An open dataset and platform toward large-scale deepfake detection* (arXiv:2509.09495). arXiv. https://arxiv.org/abs/2509.09495

Loshchilov, I., y Hutter, F. (2019). Decoupled weight decay regularization. En *International Conference on Learning Representations*. https://openreview.net/forum?id=Bkg6RiCqY7

Mercado Pago. (s. f.). *Suscripciones* \[Documentación para desarrolladores\]. https://www.mercadopago.com.ar/developers/es/docs/subscriptions/landing

Microsoft. (s. f.). *Microsoft Clarity*. https://clarity.microsoft.com

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., y Gebru, T. (2019). Model cards for model reporting. En *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 220-229). https://doi.org/10.1145/3287560.3287596

Naciones Unidas. (2020). *Objetivos y metas de desarrollo sostenible*. https://www.un.org/sustainabledevelopment/es/sustainable-development-goals/

Noticias NQN. (2026, 10 de abril). La herramienta gratuita que detecta imágenes falsas o manipuladas con IA en segundos. https://www.noticiasnqn.com.ar/noticias/2026/04/10/330769-la-herramienta-gratuita-que-detecta-imagenes-falsas-o-manipuladas-con-ia-en-segundos

OpenID Foundation. (2014). *OpenID Connect Core 1.0*. https://openid.net/specs/openid-connect-core-1\_0.html

Osterwalder, A., y Pigneur, Y. (2011). *Generación de modelos de negocio*. Deusto.

OWASP Foundation. (2021). *OWASP Top 10: 2021*. https://owasp.org/Top10/

Park, J., y Owens, A. (2025). Community Forensics: Using thousands of generators to train fake image detectors. En *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 8245-8257).

Parlamento Europeo y Consejo de la Unión Europea. (2024). *Reglamento (UE) 2024/1689 por el que se establecen normas armonizadas en materia de inteligencia artificial (Reglamento de Inteligencia Artificial)*. Diario Oficial de la Unión Europea. https://eur-lex.europa.eu/eli/reg/2024/1689/oj

Porter, M. E. (2018). *Ser competitivo*. Deusto.

Pressman, R. S. (2011). *Ingeniería del software: un enfoque práctico* (7.ª ed.). McGraw-Hill.

Provincia de Corrientes. (2021). *Ley N.° 6556: Código Procesal Civil y Comercial de la Provincia de Corrientes*. Boletín Oficial de la Provincia de Corrientes. https://senadoctes.gov.ar/codigos/Ley6556.pdf

Reality Defender. (s. f.). *Reality Defender API*. https://www.realitydefender.com

República Argentina. (1933). *Ley N.° 11.723 de Propiedad Intelectual*. Boletín Oficial de la República Argentina.

República Argentina. (1967). *Ley N.° 17.418 de Seguros*. Boletín Oficial de la República Argentina. https://servicios.infoleg.gob.ar/infolegInternet/anexos/35000-39999/39520/norma.htm

República Argentina. (2000). *Ley N.° 25.326 de Protección de Datos Personales*. Boletín Oficial de la República Argentina.

República Argentina. (2001). *Ley N.° 25.506 de Firma Digital*. Boletín Oficial de la República Argentina.

Superintendencia de Seguros de la Nación. (2026, 25 de junio). *Entidades aseguradoras al 31 de marzo de 2026* \[Comunicación\]. https://100seguro.com.ar/wp-content/uploads/2026/06/IF-2026-62674667-ESTUDIOS.pdf

Swiss Re Institute. (2025, 12 de junio). *How deepfakes, disinformation and AI amplify insurance fraud* \[SONAR 2025\]. Swiss Re. https://www.swissre.com/institute/research/sonar/sonar2025/how-deepfakes-disinformation-ai-amplify-insurance-fraud.html

Tan, M., y Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. En *Proceedings of the 36th International Conference on Machine Learning* (pp. 6105-6114). PMLR.

Truepic. (s. f.). *Truepic's authenticated photos and videos now available through the ISB Portal*. https://www.truepic.com/blog/isb-global-services-truepic-partner-canadian-insurer-workflows

Universidad de la Cuenca del Plata. (2023). *Reglamento General del Proyecto Integrador Final* (RR N.° 97/23). Facultad de Ingeniería, Tecnología y Arquitectura.

Verisk. (s. f.). *Truepic brings verified visual evidence to Verisk's ClaimSearch workflow*. https://www.verisk.com/company/newsroom/truepic-brings-verified-visual-evidence-to-verisks-claimsearch-workflow/

Wang, S.-Y., Wang, O., Zhang, R., Owens, A., y Efros, A. A. (2020). CNN-generated images are surprisingly easy to spot… for now. En *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 8695-8704).

Wang, X., Li, W., y Wu, Z. (2023). CarDD: A new dataset for vision-based car damage detection. *IEEE Transactions on Intelligent Transportation Systems, 24*(7), 7202-7214. https://doi.org/10.1109/TITS.2023.3258480

Williams, K. (2025, 11 de marzo). *What journalists should know about deepfake detection in 2025: A nontechnical guide*. Columbia Journalism Review. https://www.cjr.org/tow\_center/what-journalists-should-know-about-deepfake-detection-technology-in-2025-a-non-technical-guide.php

World Wide Web Consortium. (2018). *Web Content Accessibility Guidelines (WCAG) 2.1*. https://www.w3.org/TR/WCAG21/


# **Anexos**

Anexo A · Formulario de encuesta a profesionales del derecho. https://docs.google.com/forms/d/e/1FAIpQLSfLrUt-NaQtR_3nKom9dHpbdbJvmMIA90crh0MVwTZWeeCNVw/viewform

Anexo B · Guion de entrevista para aseguradoras. https://docs.google.com/document/d/1mivndj5KMA93uqpCwSnU9ZwaPSZRUl0zYCJS--9YOBY/edit

Anexo C · Guion de entrevista para peritos. https://docs.google.com/document/d/1KqTVIAtHJ_N5mBSPB9MK-SaiHLWbm4U83lhGWEpYZJE/edit

Anexo D · Base de datos de respuestas de la encuesta (n = 11). https://docs.google.com/spreadsheets/d/1IthlQxUbYeKp648rhcqM16SrF-1An2pWSOlwdnPYOmI/edit

Anexo E · Bocetos de pantallas en Excalidraw, correspondientes a la etapa de ideación; la interfaz final se presenta en las Figuras 18 a 23. https://excalidraw.com/#room=7bf55492d1fa8aafb41a,66NkSyJSKCl_zIyVfxF5Tw

Anexo F · Casos de uso (38), con sus diagramas por módulo y las relaciones entre casos. https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/blob/main/docs/especificacion/05-casos-de-uso.md [reemplaza el documento de agosto, que tenía 32 casos y reflejaba decisiones posteriormente modificadas]

Anexo G · Requisitos funcionales, no funcionales, reglas de negocio y limitaciones del sistema. https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/tree/main/docs/especificacion [reemplaza el documento de septiembre]

Anexo H · Bitácora de trabajo: bitácora original del Drive (agosto a octubre), bitácora del repositorio (desde el 8 de octubre) y bitácoras de cada actividad de evaluación (carpetas AE1 a AE4). https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/tree/main/docs/bitacora

Anexo I · Notas de la reunión con Federico Miskinich, referente de LegalTech (2 de octubre de 2026). https://docs.google.com/document/d/1m2DZ4mswxF3rE3gGuKn3c9-9MBzrOa0nnuh3UWIhrp4/edit

Anexo J · Pruebas de canales: procedimiento y resultados con ChatGPT y Gemini. https://docs.google.com/document/d/1X2QskrleJpsl_rCBYltWFaF8kvtr_KgdjLgxKnum6Ps/edit

Anexo K · Diagramas del sistema, generados y verificados contra el código, incluido el modelo de datos completo. https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/tree/main/docs/arquitectura/diagramas [reemplaza el diagrama de Lucidchart de septiembre]

Anexo L · Tablero de gestión (Trello). https://trello.com/invite/b/6a5e9b7c997771574cc7ad51/ATTI5b40aab54697c3aa9b11b9f0b5fffb48FA3FE163/proyecto-final-de-grado

Anexo M · Búsqueda de antecedentes en el INPI (captura de la búsqueda del 29 de octubre de 2026). [Subir la captura y enlazarla.]

Anexo N · Mapas de empatía de las versiones 2 y 3 del prototipo y plantilla utilizada. [Pendiente de las sesiones con interesados.]

Anexo O · Declaración de uso de inteligencia artificial (texto a continuación).

Anexo P · Plan de negocios para Argentina: mercado, precios propuestos, costos, punto de equilibrio y encuadre fiscal. https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/blob/main/docs/informe-final/plan-de-negocios.md

Anexo Q · Ficha técnica del clasificador, versión 1.0.0. [Exportar a PDF la ficha del modelo y enlazarla.]

Repositorios · Actual: https://github.com/valentinasalmon/PFG-sistema-deteccion-IA · Anterior (agosto y septiembre): https://github.com/valentinasalmon/TIF

[Los enlaces al repositorio apuntan a la rama `main`; algunos documentos del informe todavía están en ramas sin integrar y se actualizan cuando se integren.]

## **Anexo O. Declaración de uso de inteligencia artificial**

El presente proyecto utiliza herramientas de inteligencia artificial generativa como asistencia, con el alcance y los controles que se detallan a continuación. La autora define el problema, realiza el relevamiento, las entrevistas y la encuesta, toma todas las decisiones de alcance, de diseño, legales, de privacidad y de negocio, revisa, corrige e integra todo el material producido con asistencia de IA, y asume la responsabilidad total por el contenido del trabajo.

**Herramientas utilizadas.** Claude Code, un agente de programación basado en modelos de lenguaje de Anthropic, que trabaja dentro del repositorio del proyecto; Claude, en su versión de chat, como apoyo para la redacción y la búsqueda bibliográfica entre marzo y octubre de 2026; Gemini, de Google, para generar las notas automáticas de la reunión con el referente de LegalTech, revisadas a mano; una herramienta de transcripción con IA para los audios de la primera entrevista, también revisada a mano; y ChatGPT, Gemini y Copilot exclusivamente como generadores de imágenes de prueba, para las pruebas de canales y para el conjunto propio del clasificador.

**Uso en el código.** El agente escribe, con la revisión de la autora, la mayor parte del código del backend, de la interfaz, de la infraestructura como código y del paquete de la red neuronal, junto con sus pruebas automatizadas. Cada contribución del agente queda identificada en el historial del repositorio mediante la línea `Co-Authored-By`: al 26 de noviembre de 2026, 394 de los 425 commits (92,7 %) llevan esa línea. Ningún cambio ingresa a la rama principal sin pasar la integración continua y sin la revisión y la integración de la autora mediante un pull request. El entrenamiento del clasificador lo ejecuta la autora en Google Colab, con el código preparado por el agente.

**Uso en la documentación técnica.** El agente redacta las especificaciones, los planes y las tareas de cada funcionalidad, los registros de decisiones de arquitectura, la bitácora del repositorio, las guías de instalación, despliegue y uso, la documentación de la red neuronal y la documentación del arnés. Las decisiones que se registran en esos documentos son de la autora o se presentan a ella como propuestas, en las cuestiones abiertas, hasta que las aprueba.

**Uso en el informe.** El agente redacta borradores de secciones del informe a partir de la bitácora, de los hechos verificados del sistema y del relevamiento, con una guía de redacción y un revisor automático que controla la numeración, las citas y el tiempo verbal. La autora revisa, modifica y decide qué incorporar. Las cifras del proceso se calculan desde el repositorio y no se escriben de memoria. Las bitácoras de las actividades de evaluación de agosto a octubre se reconstruyen con asistencia del agente a partir de la bitácora original, del repositorio anterior y de los documentos entregados.

**Uso en los diagramas.** Los diagramas de modelo de datos, componentes y casos de uso se generan desde el código mediante herramientas del repositorio; el de despliegue se dibuja con los datos leídos de la infraestructura; y los de secuencia y actividad se redactan a mano. Todos pasan una verificación automática de fidelidad, notación y ortografía, y la autora los revisa visualmente antes de incorporarlos.

**Uso en la gestión.** El agente actualiza el tablero de Trello al cerrar cada trabajo y concilia su estado con el repositorio.

**Controles.** El trabajo del agente se rige por un arnés (Capítulo VI): una constitución y un archivo de instrucciones, comandos para cada etapa, ganchos que bloquean el acceso a secretos y controlan el estilo y el formato de cada commit, un verificador que comprueba que la documentación diga la verdad, sensores de diseño, accesibilidad y teclado, y la integración continua. Los secretos los maneja solo la autora.

**Datos.** Ninguna imagen de causas reales ni dato personal de terceros se comparte con herramientas de IA. Las imágenes de prueba son generadas con IA o provienen de conjuntos de datos públicos, y los datos de la encuesta se presentan de forma agregada.

[Fecha y firma de la autora.]


