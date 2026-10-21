# Entrevista a Federico Miskinich (02/10/2026)

**Fuente**: notas automáticas de Gemini de la videollamada con la autora, revisadas el 21/10/2026. La grabación y la transcripción completa quedan en poder de la autora; no se suben al repositorio.

## Resumen

La autora presentó evidentIA: casos, huella digital de los archivos y análisis en 4 capas (metadatos, credenciales C2PA, ELA y red neuronal). Federico Miskinich hizo varias recomendaciones:

- respaldar el sistema en estándares internacionales;
- presentarlo como **herramienta auxiliar** con una persona que decide;
- publicar en el informe los umbrales sin revelar los algoritmos;
- actualizar o complementar ELA;
- considerar la Blockchain Federal Argentina para la trazabilidad;
- incluir a peritos y criminalistas en el planteo, para evitar que lo rechacen.

## Recomendaciones y cómo se atendieron

| # | Recomendación | Estado | Dónde |
|---|---|---|---|
| 1 | Descargo en el informe: resultado parcial, brindado por IA, que no reemplaza a un perito humano | **Aplicada** (22/10/2026) | Informe PDF: recuadro inicial y sección 6. Pantalla de resultados: recuadro «Herramienta auxiliar». Correo de fin de análisis. `DESCARGO` en `backend/app/informes/informe_analisis.py`. RNF23 CA4 |
| 2 | Persona en el circuito: el sistema asesora y la persona decide | **Aplicada** | [ADR-0017](../arquitectura/decisiones/0017-marco-normativo-y-supervision-humana.md). Sección «Uso previsto y supervisión humana» del informe. RN27 sin cambios: no hay veredictos |
| 3 | Auditabilidad según el Reglamento europeo de IA y la norma ISO/IEC 42001 | **Aplicada como marco de referencia** | ADR-0017. El informe los cita en «Uso previsto» |
| 4 | Tablas con valores esperados y valores obtenidos, sin revelar el algoritmo | **Aplicada** | Tabla «Criterio · Referencia sin edición · Valor obtenido» en cada capa del informe. La capa ELA guarda además el desvío máximo. RNF23 CA5 |
| 5 | Porcentajes y términos estadísticos en lugar de certezas, con la recomendación de consultar a un experto | **Aplicada** (ya existía; ahora con una escala única) | Escala Sin indicios / débiles / moderados / fuertes, igual en la pantalla y en el informe |
| 6 | Trazabilidad con métodos deterministas y funciones hash | **Aplicada** (ya existía; ahora visible) | Sección «Evidencia analizada y cadena de custodia»: SHA-256 al cargar y verificación antes del análisis. Cronología. Auditoría (RNF06) |
| 7 | Blockchain Federal Argentina para hashes y marcas de tiempo | **Planificada** | Funcionalidad 016 (RF37). El informe ya reserva el campo «Sello de tiempo» |
| 8 | ELA se considera superado desde 2018: investigar métodos más actuales | **Descartada por la autora** (22/10/2026) | CP-23. ELA sigue como señal complementaria que nunca supera el nivel moderado |
| 9 | Incluir a peritos y criminalistas como destinatarios, para mitigar la resistencia institucional | **Descartada por la autora** (22/10/2026) | CP-22. El público sigue siendo abogados y aseguradoras; el descargo igual recomienda consultar a un perito |
| 10 | Ampliar los casos de uso de aseguradoras: robo, incendio, fotos de talleres | **Descartada por la autora** (22/10/2026) | CP-24 |
| 11 | Mantener un corpus de investigación sólido: datos de entrenamiento, bibliografía | **En curso** | Funcionalidad 010 (RNF24 CA2: el conjunto de datos queda documentado) |

## Validación del problema

En la entrevista se mencionó que un contacto (Sergio) y un ejecutivo de una aseguradora del NEA confirmaron algo importante para el proyecto: los asegurados suelen enviar las fotos por WhatsApp o por correo, sin inspección presencial. Esto respalda el caso de uso principal de las aseguradoras.
