# Diagramas del sistema

Cada diagrama tiene su fuente editable y su imagen (`.png`), que es la que va al informe final. Se generaron a partir del código el 2026-10-29.

- Los diagramas 01 a 03 se dibujan con la identidad visual de evidentIA: la fuente es un script de Python en `fuentes/` que genera el `.svg`.
- Los diagramas 04 a 06 tienen su fuente en Mermaid (`.mmd`).

| Archivo | Qué muestra | Dónde va en el informe |
|---|---|---|
| `01-arquitectura-general` | Componentes del sistema y servicios externos | Capítulo IX, arquitectura (reemplaza el Anexo K) |
| `02-capas-del-backend` | Capas del backend y piezas intercambiables (Strategy) | Capítulo IX, diseño de solución |
| `03-infraestructura-y-despliegue` | Integración continua, despliegue y recursos de AWS | Capítulo IX, infraestructura |
| `04-modelo-de-datos` | Diagrama entidad-relación (tablas reales de `backend/app/modelos`) | Capítulo IX, modelo de datos |
| `05-flujo-de-un-caso` | Secuencia desde la carga hasta la verificación pública del informe | Capítulo IX, diseño de solución |
| `06-cronograma` | Cronograma planificado frente al real | Capítulo V, cronograma |

Si cambia el modelo de datos o la infraestructura, se actualiza el `.mmd` y se vuelve a exportar la imagen.
