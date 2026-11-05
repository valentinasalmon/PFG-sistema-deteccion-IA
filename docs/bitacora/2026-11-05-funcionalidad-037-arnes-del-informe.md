# 2026-11-05 — Funcionalidad 037: arnés del informe final

## Qué se hizo

- **Guías del informe** (`docs/informe-final/`):
  - la guía de redacción: protocolo, redacción, evidencia, APA 7, criterio del evaluador por capítulo y errores ya detectados;
  - los hechos verificados del sistema;
  - el trabajo con IA, con textos para los Capítulos V, VI y XII y la declaración de uso de IA;
  - el plan de negocios con el contexto argentino;
  - el estado del informe y el README.
- **Comandos:** `/redactar-informe`, `/revisar-informe` (evaluador de tesis) y `/generar-diagramas`.
- **Herramientas en `backend/herramientas/`**, con 15 pruebas:
  - `revisar_informe.py`;
  - `cifras_del_proyecto.py`;
  - `diagramas_del_sistema.py` (`er`, `componentes`, `casos-de-uso`, `renderizar`, `verificar`).
- **Diagramas nuevos en `docs/arquitectura/diagramas/`**, en PlantUML:
  - entidad-relación compacto y completo, y componentes UML, generados desde el código;
  - casos de uso por módulo, actores y relaciones, generados desde la especificación;
  - despliegue UML, verificado contra Terraform, systemd y Nginx;
  - secuencia, con los servicios reales;
  - cronograma.
- **Especificación:** CU33 a CU38 (carga desde el celular, persona afectada, verificación pública, pago del plan, verificación de identidad y aprobación de aseguradoras), porque estaban implementados y el inventario no los tenía.
- **Primera revisión de evaluador** del documento actual (`revisiones/2026-11-05.md`): 11 errores, 16 advertencias y las respuestas a los 36 comentarios de la autora.

## Decisiones

- **PlantUML con Graphviz** en lugar de Mermaid o de SVG hechos a mano. Tiene notación UML completa (nodos con estereotipo, interfaces provistas y requeridas, casos de uso) y la fuente es texto que se genera desde el código.
- **Los modelos se leen con el analizador sintáctico de Python, sin importar la aplicación.** Así el generador corre en cualquier máquina, sin las dependencias del backend.
- **Los casos de uso se dividen por módulo**, y las relaciones entre módulos van en un diagrama aparte. Un único diagrama con 38 casos era ilegible.
- **En la secuencia**, el sello de la imagen lo publica la API al cargarla, y el trabajador confirma los sellos antes de armar el informe, como en el código (`servicio_imagenes`, `servicio_sellos.confirmar_antes_de_informar`). La primera versión lo atribuía a la tarea programada, y eso no era fiel al sistema.
- **CP-34 reabierta:** la autora duda entre Cresium y Mercado Pago. El sistema no cambia; el informe usa un texto neutral.
- **Las versiones descartadas se borran** (pedido de la autora).

## Pendiente

- La autora aplica las correcciones de la revisión y pega los capítulos XI, XII y XIII y las conclusiones.
- Decisiones: CP-07, CP-34, CP-37 y CP-38.
- Mapas de empatía, prueba SUS y validación OE5.
- Integrar el clasificador y regenerar los diagramas de componentes y de secuencia cuando exista la capa 4.
