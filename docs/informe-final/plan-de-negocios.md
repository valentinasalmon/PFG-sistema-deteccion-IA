# Plan de negocios de evidentIA (Argentina)

Borrador del plan de negocios del proyecto, con el contexto argentino. Alimenta los Capítulos IV (modelo de negocios), X (recursos financieros) y XI (CANVAS), y responde la cuestión CP-38 (precios). Cada número tiene su fuente o está marcado como **supuesto**. Antes de pasarlo al informe, la autora valida los supuestos y completa los datos marcados.

## 1. Resumen ejecutivo

evidentIA ofrece, como servicio web, la verificación preliminar de imágenes presentadas como prueba en siniestros de tránsito y laborales. Analiza cada imagen en cuatro capas y entrega un informe por rubro, sin veredictos y verificable públicamente gracias a la huella registrada en Hedera. Sus clientes son estudios jurídicos y aseguradoras. El modelo es una suscripción mensual por organización, con un espacio personal gratuito que funciona como puerta de entrada. La estructura de costos es liviana y mayormente fija (una instancia en la nube), y el costo variable por análisis es despreciable, por lo que el margen crece con cada cliente. El principal riesgo comercial no es técnico, sino de confianza: que el método sea aceptado en el ámbito judicial y asegurador. Por eso, la estrategia empieza con pilotos acompañados en la región NEA.

## 2. Problema, solución y propuesta de valor

| Segmento | Problema (evidencia) | Propuesta de valor |
|---|---|---|
| Abogados litigantes y estudios jurídicos | El 72,7 % dudó de una imagen y ninguno pidió una pericia (encuesta, n = 11) | Una verificación previa, en minutos, para decidir si pedir una pericia, con un informe que se adjunta y que un tercero puede verificar |
| Aseguradoras (analistas de siniestros) | Las fotos de los siniestros llegan sin certificación de origen (entrevista al productor de seguros); el sector identifica a los *deepfakes* como un riesgo emergente (Swiss Re Institute, 2025) | Una verificación antes de liquidar, con trazabilidad del origen de cada foto (celular, enlace a la persona afectada) y auditoría |
| Personas afectadas y peritos (indirectos) | Las fotos se recomprimen por WhatsApp; el perito necesita poder reproducir el análisis | Un enlace directo de carga y un informe con versiones, valores y umbrales |

## 3. Mercado

**Mercado total (TAM).** Comprende el sector asegurador argentino y la abogacía litigante. La Superintendencia de Seguros de la Nación informa 188 entidades autorizadas al 31 de marzo de 2026 (Superintendencia de Seguros de la Nación, 2026). No hay un dato oficial y reciente del total de abogados del país. Como referencia, un estudio de la UNNE registra entre 4.325 y 5.607 abogados matriculados en Corrientes hacia 2014, según la fuente (Goldfarb, s. f.), y el Colegio Público de la Capital Federal tiene un padrón de 86.524 matriculados habilitados para votar. **[Completar con el dato actual de la FACA o del Superior Tribunal de Justicia de Corrientes.]**

**Mercado al que se apunta primero (SAM).** Son las aseguradoras con ramo automotor o de riesgos del trabajo y los estudios jurídicos que litigan accidentes en la región NEA (Corrientes y Chaco). **[Supuesto a validar: cantidad de aseguradoras con esos ramos según la SSN y cantidad de estudios dedicados a accidentes en Corrientes.]**

**Participación alcanzable (SOM) en tres años.** Es la base de la proyección de la sección 7: entre 15 y 40 organizaciones pagas, según el escenario.

## 4. Competencia y precios de referencia

Las alternativas cobran por uso o por suscripción, y ninguna combina la gestión de casos, la verificación pública del informe y el encuadre normativo argentino (Capítulo IV del informe, Tabla 9).

| Alternativa | Precio de referencia | Fuente |
|---|---|---|
| Hive (API de detección) | US$ 6 cada 1.000 solicitudes | Fritz AI (s. f.) |
| Sightengine | Desde US$ 10 por mes | Fritz AI (s. f.) |
| Reality Defender | 50 análisis gratis por mes; planes superiores a medida | Reality Defender (s. f.) |
| AI or Not | 20 verificaciones gratis | CheckThat.ai (s. f.) |
| Amped Authenticate | Licencia profesional, sin precio público | Amped Software (s. f.) |
| Pericia informática formal | Honorarios profesionales, mayor costo y plazo | **[Completar con un arancel de referencia del Consejo Profesional de Ciencias Informáticas o del colegio de peritos]** |

## 5. Modelo de ingresos y precios propuestos (propuesta para CP-38)

La suscripción es mensual y por organización. El espacio personal es gratuito y limitado, y sirve como puerta de entrada y prueba del producto. Los límites son los de la Tabla 12 del informe.

| Plan | Límites | Precio propuesto (sin IVA) | Justificación |
|---|---|---|---|
| Personal | 1 persona, 10 análisis por mes, sin compartir | Sin costo | Adquisición: el abogado prueba el producto con sus propios casos |
| Organización Básico | Hasta 5 miembros, 100 análisis por mes | **US$ 49 por mes** (supuesto) | Por debajo del costo de una sola pericia y en el rango de las herramientas por suscripción, con gestión de casos e informe verificable |
| Organización Profesional | Hasta 25 miembros, 500 análisis por mes | **US$ 149 por mes** (supuesto) | Pensado para aseguradoras y estudios grandes; cuesta menos de US$ 0,30 por análisis al usar el cupo completo |
| Aseguradoras por volumen (futuro) | Integración por API y cupo a medida | A convenir | Fuera del MVP (Capítulo XI) |

**Moneda.** Por la inflación, se propone fijar el precio en dólares y facturar en pesos al tipo de cambio oficial del día de emisión, o actualizar la lista en pesos cada mes. El cobro se realiza por transferencia con Cresium (funcionalidad 032), que encaja con la forma de pago de las empresas.

## 6. Estructura de costos

**Costos fijos mensuales de operación.**

| Concepto | Costo mensual | Fuente o supuesto |
|---|---|---|
| Instancia EC2 t3.small (eu-west-1) | Unos US$ 17 | Tarifa bajo demanda aproximada; **[verificar en la calculadora de AWS]** |
| Disco, S3, transferencia, dirección IP pública y SES | Unos US$ 8 a 12 | Supuesto con el uso de un MVP; **[verificar en la factura de AWS]** |
| Dominio | **[completar: costo anual / 12]** | NIC Argentina o registrador elegido |
| Herramientas de desarrollo con IA | **[completar]** | Suscripción a Claude |
| Contador y obligaciones fiscales | **[completar]** | Según la forma jurídica (sección 8) |
| **Total operativo estimado** | **Unos US$ 40 a 60, más los datos a completar** | |

Mientras dura el proyecto, la infraestructura se cubre con los créditos gratuitos de AWS (Capítulo X).

**Costos variables.** Son casi nulos por análisis:

- el sello de una imagen o de un informe en Hedera cuesta unos US$ 0,0008 (ADR-0018), menos de US$ 0,01 por caso típico;
- la verificación de identidad con Identik cuesta US$ 0,80 por verificación biométrica, según precios publicados al 4 de noviembre de 2026 (insumos de la 035), y se paga una sola vez por aseguradora;
- la comisión de Cresium por cobro está **[a completar con el proveedor]**.

**Costo de oportunidad.** Son las horas de la autora para mantener, vender y dar soporte: **[supuesto: dedicación y valor hora de referencia]**.

## 7. Punto de equilibrio y proyección

**Punto de equilibrio operativo.** Con costos fijos de unos US$ 60 por mes, alcanza con **2 organizaciones del plan Básico**, o con 1 del Profesional.

**Punto de equilibrio con remuneración.** Si se incluye una remuneración de referencia de **[supuesto: US$ 1.000 por mes]** para sostener el proyecto, hacen falta unas 22 organizaciones Básicas, unas 8 Profesionales, o una combinación (por ejemplo, 10 Básicas y 4 Profesionales).

**Proyección a tres años.** Los escenarios son ilustrativos y sus supuestos se validan con los pilotos.

| Escenario | Año 1 | Año 2 | Año 3 | Supuestos |
|---|---|---|---|---|
| Pesimista | 3 Básicas | 6 Básicas y 1 Profesional | 10 Básicas y 2 Profesionales | La adopción depende del boca a boca local |
| Base | 5 Básicas y 1 Profesional (piloto con una aseguradora) | 12 Básicas y 3 Profesionales | 20 Básicas y 6 Profesionales | Pilotos en Corrientes y convenio con un colegio profesional |
| Optimista | 8 Básicas y 2 Profesionales | 20 Básicas y 6 Profesionales | 30 Básicas y 10 Profesionales | Una aseguradora regional lo adopta y lo recomienda a sus productores |

**Ingresos mensuales al cierre de cada año (escenario base):**

- año 1: 5 × 49 + 1 × 149 = **US$ 394**;
- año 2: 12 × 49 + 3 × 149 = **US$ 1.035**;
- año 3: 20 × 49 + 6 × 149 = **US$ 1.874**.

En el escenario base, el proyecto cubre su operación desde el primer piloto y alcanza el equilibrio con remuneración durante el segundo año.

## 8. Forma jurídica, impuestos y normativa (Argentina)

- **Inicio como monotributista**, en la categoría de servicios. Es simple y barato, pero tiene un tope de facturación anual que ARCA actualiza cada semestre: la categoría K tenía un tope de unos $ 126,6 millones desde agosto de 2026, según fuentes secundarias. **[Verificar en ARCA.]** El monotributista emite factura C, que no le permite a una aseguradora computar el IVA como crédito fiscal. Por eso, para vender a aseguradoras conviene pasar al régimen general (responsable inscripto, factura A).
- **Sociedad por Acciones Simplificada (SAS)** cuando se sumen socios o crezcan las ventas a empresas. Limita la responsabilidad patrimonial y facilita los contratos con aseguradoras.
- **IVA del 21 %** sobre el servicio en el régimen general, e **Ingresos Brutos** de Corrientes, con la alícuota de servicios informáticos **[a verificar]**. Se factura electrónicamente con ARCA.
- **Régimen de Promoción de la Economía del Conocimiento (Ley N.° 27.506)**, vigente hasta el 31 de diciembre de 2029. Da estabilidad fiscal y una reducción de las contribuciones patronales a las empresas inscriptas que desarrollan software. Se evalúa al constituir la SAS, porque exige una persona jurídica y un porcentaje mínimo de facturación en actividades promovidas.
- **Protección de datos (Ley N.° 25.326):**
  - inscripción de la base de datos ante la Agencia de Acceso a la Información Pública;
  - política de privacidad y términos de uso;
  - un acuerdo de encargado del tratamiento con cada aseguradora o estudio, porque la plataforma trata datos que ellos le confían;
  - tratamiento reforzado de los datos sensibles (imágenes con lesiones; la biometría queda del lado de Identik);
  - transferencia internacional a la Unión Europea, jurisdicción con nivel adecuado.
- **Propiedad intelectual:** el software se registra como obra inédita (Ley N.° 11.723). La marca evidentIA no es registrable, así que antes de comercializar hay que elegir una denominación disponible (Capítulo VIII).

## 9. Estrategia comercial

1. **Pilotos acompañados** en Corrientes, con un estudio jurídico y una aseguradora o productor de seguros, durante tres meses sin costo, a cambio de devoluciones y de un testimonio.
2. **Canal institucional:** presentaciones en el Colegio de Abogados y en jornadas de LegalTech, con el respaldo del referente consultado.
3. **Canal asegurador:** los productores y asesores de seguros, que llegan a las compañías y ven el problema todos los días.
4. **Producto como canal:** cada informe verificado por un tercero muestra la marca en la página de verificación.
5. **Contenido educativo:** cómo se pierden las credenciales C2PA por WhatsApp (pruebas propias, Tabla 6).

## 10. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Falta de reconocimiento judicial del método | Capas deterministas y reproducibles, versiones registradas, informe pensado para que un perito lo revise y se presente como auxiliar |
| Precisión del clasificador frente a generadores nuevos | Reentrenamiento periódico (ciclo de vida en `docs/red-neuronal/`) y peso menor de las capas probabilísticas |
| Dependencia de proveedores (AWS, Hedera, Cresium, Identik) | Proveedores intercambiables (patrón Strategy), ya probado al migrar de BFA a Hedera |
| Inflación y tipo de cambio | Precio de referencia en dólares, facturado en pesos |
| Datos sensibles | Cifrado, mínimo privilegio, auditoría, retención con destrucción y biometría fuera de la plataforma |
| Competencia internacional | Diferenciarse por el encuadre local, la gestión de casos y la verificación pública, no por la precisión pura |

## 11. Financiamiento

El MVP se financia con recursos propios y con los créditos gratuitos de AWS. Para la etapa comercial se relevan programas vigentes de capital semilla, nacionales y de Corrientes, así como incubadoras universitarias y aceleradoras de LegalTech o *insurtech*, y se considera el régimen de la Ley 27.506 al constituir la sociedad. **[Completar con los programas abiertos al momento de la entrega.]**

## 12. Indicadores

- Organizaciones pagas y tasa de conversión del plan personal al pago.
- Análisis por organización por mes.
- Cancelaciones mensuales.
- Tiempo hasta el primer informe.
- Puntaje SUS.
- Informes verificados por terceros, como señal de que el informe circula.

## Fuentes para la bibliografía

- Goldfarb, M. (s. f.). *Evolución de la litigiosidad y la cantidad de abogados en la provincia de Corrientes, Argentina*. Repositorio institucional de la UNNE. https://repositorio.unne.edu.ar/handle/123456789/50152
- República Argentina. (2019). *Ley N.° 27.506 de Régimen de Promoción de la Economía del Conocimiento*. Boletín Oficial de la República Argentina.
- Las demás fuentes (SSN, Swiss Re, Fritz AI, Reality Defender, CheckThat.ai, Amped, Cresium, Identik) ya figuran en la bibliografía del informe.
