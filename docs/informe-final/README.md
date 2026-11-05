# Informe final: arnés de redacción

Todo lo necesario para que el informe final del Proyecto Final de Grado sea fiel al sistema, esté completo según el protocolo y esté bien escrito. Es la parte del [arnés](../arnes/README.md) dedicada al documento (funcionalidad 039).

| Pieza | Para qué sirve |
|---|---|
| [guia-de-redaccion.md](guia-de-redaccion.md) | Estructura del protocolo; reglas de redacción, de evidencia y de APA 7; qué mira el evaluador en cada capítulo; errores ya detectados |
| [hechos-del-sistema.md](hechos-del-sistema.md) | Fuente única de datos verificados: qué hace el sistema, en qué estado y con qué evidencia |
| [trabajo-con-ia.md](trabajo-con-ia.md) | Cómo se cuenta el trabajo con el agente de IA y el arnés, con textos listos y la declaración de uso de IA |
| [plan-de-negocios.md](plan-de-negocios.md) | Plan de negocios con el contexto argentino: mercado, precios, costos, punto de equilibrio, impuestos y riesgos |
| [estado-del-informe.md](estado-del-informe.md) | Qué falta, por capítulo |
| [revisiones/](revisiones/) | La última revisión de evaluador, con las correcciones listas para pegar |
| [insumos.md](insumos.md) | Registro cronológico de hallazgos y decisiones que van al informe |

## Comandos

- `/redactar-informe <sección>` escribe o actualiza una sección con la guía, los hechos y la evidencia.
- `/revisar-informe <enlace del documento>` revisa todo el informe como un evaluador y entrega las correcciones.
- `/generar-diagramas` genera los diagramas desde el código, los verifica y los revisa visualmente.

## Herramientas (desde la raíz del repositorio)

```bash
python backend/herramientas/revisar_informe.py informe.txt            # revisión mecánica
python backend/herramientas/cifras_del_proyecto.py                    # cifras del proceso al día
python backend/herramientas/diagramas_del_sistema.py verificar        # diagramas fieles al sistema
```
