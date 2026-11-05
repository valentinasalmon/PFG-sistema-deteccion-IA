# El trabajo con inteligencia artificial en el informe

El proyecto se desarrolla con un agente de IA (Claude Code) que escribe la mayor parte del código bajo un arnés de reglas, controles y supervisión humana. La cátedra pide exponerlo (*harness engineering*) y declararlo. Este documento reúne **qué contar, dónde contarlo y el texto listo para pegar**, en prosa y en presente. Las cifras se recalculan con `backend/herramientas/cifras_del_proyecto.py`.

## Dónde va en el informe

| Lugar | Qué se cuenta |
|---|---|
| Resumen | Una oración: metodología guiada por especificaciones, con un agente de IA dentro de un arnés y supervisión de la autora |
| Cap. V, Organización del equipo | El reparto del trabajo entre la autora y el agente |
| Cap. VI, Técnicas | El arnés completo: guías, sensores, memoria, persona en el circuito y mejora continua |
| Cap. VI, Trazabilidad | La línea `Co-Authored-By`, las cuestiones abiertas y el registro de cambios del arnés |
| Cap. X, Recursos | El agente como recurso tecnológico y el costo de su suscripción |
| Cap. XII, Lecciones | Lo que el arnés enseña: las reglas solo escritas no alcanzan, y probar contra el servicio real |
| Conclusiones | El aporte metodológico |
| Anexo | Declaración de uso de IA, registro de cambios del arnés y mapa del arnés (`docs/arnes/`) |

## Texto para el Capítulo VI (arnés)

El proyecto incorpora un arnés para el trabajo asistido por inteligencia artificial, entendido como el sistema que rodea al agente para que trabaje de forma confiable dentro del repositorio. Sus guías son la constitución del proyecto, un archivo de instrucciones para el agente, la especificación general y los comandos para especificar, planificar, generar tareas, cerrar cada etapa, redactar y revisar el informe y generar los diagramas. Estas guías obligan al agente a escribir el código y la documentación en español, a respetar la arquitectura en capas, a documentar en cada función el requisito que realiza, a no redactar nunca veredictos, a seguir la guía de identidad visual y a no subir secretos ni imágenes reales al repositorio. Como una regla escrita depende de que el agente la recuerde, el arnés suma sensores que la hacen cumplir: ganchos que se ejecutan antes y después de cada acción del agente, controles previos a cada commit, la verificación automática de la arquitectura en capas, la integración continua y, en producción, una página pública de estado. La regla de no acceder a secretos, por ejemplo, deja de ser solo texto y se convierte en un control que bloquea la acción. La memoria del proceso se conserva en la bitácora, en los registros de decisiones, en las cuestiones abiertas, en el tablero de gestión y en los insumos del informe, de modo que cada sesión de trabajo parte de lo decidido en las anteriores. La autora ocupa el lugar de la persona en el circuito: revisa e integra el trabajo, toma las decisiones que exceden al agente y es la única que maneja los secretos.

El funcionamiento del arnés se comprueba en la práctica. En su primera prueba, el gancho de secretos bloquea un commit del propio agente, y el control de permisos de la herramienta impide que el agente modifique ese gancho, por tratarse de un control de seguridad: la corrección queda como propuesta para que la autora la apruebe. El arnés se mejora además de forma continua, y un registro de cambios documenta cada ajuste con el problema que lo motivó, como la regla de probar cada integración externa contra el servicio real después de que el sello en Hedera supera todas las pruebas automáticas y aun así presenta una falla en producción. El mismo criterio se aplica al informe: una guía de redacción, una fuente única de hechos verificados, un revisor automático que detecta los errores mecánicos que marca un evaluador y un generador de diagramas que los obtiene del código, para que el documento diga exactamente lo que el sistema hace. Todo commit del agente lleva una línea de coautoría que identifica la asistencia de IA, lo que permite distinguir en el historial el trabajo asistido: al 5 de noviembre de 2026, 301 de los 332 commits del repositorio (90,7 %), integrados mediante 73 pull requests. Ningún cambio ingresa sin pasar antes la integración continua y la revisión de la autora, bajo su responsabilidad.

## Texto para el Capítulo V (organización del equipo)

*Reemplaza la parte del agente si el capítulo ya la tiene.*

El reparto del trabajo con el agente evoluciona durante el proyecto. En un primer esquema, la autora copia en el repositorio los archivos que propone el asistente, lo que resulta lento y propenso a errores. Desde el 16 de octubre de 2026, el agente escribe y sube con commits propios todo el trabajo de cada funcionalidad (especificación, plan, tareas, código, pruebas y documentación de seguimiento), mientras que la autora revisa ese trabajo, abre e integra los pull requests y toma las decisiones de alcance, legales, de privacidad, de costos y de arquitectura de impacto. Cuando una decisión excede al agente, este la registra como cuestión abierta con una propuesta provisoria y continúa con lo que no depende de ella. El trabajo se reparte además entre dos sesiones de agente con un traspaso explícito entre ellas, una dedicada a la red neuronal y otra al resto del sistema, para que una misma sesión no mezcle contextos distintos.

## Texto para el Capítulo XII (lecciones)

El trabajo con un agente de inteligencia artificial muestra que la calidad no se le pide al modelo, sino que se construye alrededor de él. Las reglas que solo están escritas se olvidan o quedan desactualizadas: los comandos del flujo, por ejemplo, siguen describiendo un reparto del trabajo dos semanas después de que cambia, hasta que una revisión del arnés los corrige. Convertir las reglas críticas en controles automáticos, registrar cada cambio del arnés con su motivo y reservar a la persona las decisiones y los secretos permite aprovechar la velocidad del agente sin perder el control del proceso. La contracara es que el agente no llega a todos los entornos (producción, servicios externos con restricciones de red), por lo que esas verificaciones dependen de guías que la autora ejecuta.

## Declaración de uso de inteligencia artificial

*Va como anexo y la firma la autora.*

En el desarrollo de este proyecto se utiliza Claude Code, un agente de programación basado en un modelo de lenguaje de Anthropic, como herramienta de asistencia. El agente redacta especificaciones, planes, código, pruebas, documentación técnica y borradores de secciones del presente informe, bajo las reglas del arnés descripto en el Capítulo VI. Cada contribución del agente queda identificada en el historial del repositorio mediante la línea `Co-Authored-By`. La autora define el problema, realiza el relevamiento y las entrevistas, toma las decisiones de alcance, diseño, legales y de negocio, revisa, corrige e integra todo el material producido con asistencia de IA, y asume la responsabilidad total por el contenido de este trabajo. Las imágenes de casos reales y los datos personales nunca se comparten con el agente ni con servicios externos de IA. **[Fecha y firma.]**

## Episodios que conviene contar en la defensa

- **El gancho de secretos bloquea al propio agente** y la herramienta le impide desactivarlo. El arnés protege sus controles y la decisión final es humana.
- **Hedera pasa todas las pruebas y falla en producción**, porque los dobles de prueba no reproducían la demora del *mirror node*. De ahí sale la regla de probar contra el servicio real y la página `/estado`.
- **Los diagramas del informe se descartan** porque no estaban en notación estándar ni coincidían con el código. De ahí sale el generador de diagramas desde el código y su verificación automática.
- **La marca evidentIA no es registrable.** La búsqueda en el INPI llega tarde: conviene verificarla antes de construir la identidad.
