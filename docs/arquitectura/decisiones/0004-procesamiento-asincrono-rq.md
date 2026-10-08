# ADR-0004: Procesamiento de análisis en segundo plano con RQ y Redis

- **Estado**: Aceptada
- **Fecha**: 2026-10-08
- **Requisitos relacionados**: RF38, RF46, RF47, RNF13, RNF16

## Contexto

Un análisis de varias imágenes por cuatro capas puede tardar más de lo que Gunicorn y Nginx toleran en una solicitud HTTP. Además, se debe avisar por correo al finalizar, lo que implica que el usuario puede irse de la pantalla.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Procesar dentro de la solicitud | Simple | Cortes por tiempo de espera; bloquea procesos de Gunicorn |
| Celery + Redis | Muy completo | Configuración compleja para el tamaño del proyecto |
| **RQ + Redis** | Simple, en Python, reintentos y tareas programadas | Menos funciones que Celery |

## Decisión

RQ con Redis en la misma instancia. Un proceso trabajador ejecuta los análisis, los correos y la tarea diaria de retención. El modelo ONNX se carga una vez por proceso trabajador.

## Consecuencias

- Se agrega Redis a la infraestructura y un servicio de systemd para el trabajador.
- El estado del análisis se consulta por la API para mostrar el progreso.
