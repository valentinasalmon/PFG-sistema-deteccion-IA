# Diagramas del sistema

Todos los diagramas del informe salen de aquí. **Representan el sistema real**: los que se pueden obtener del código se generan desde él, y los demás se verifican contra la infraestructura y la especificación. Se regeneran y controlan con el comando `/generar-diagramas` y con la herramienta `backend/herramientas/diagramas_del_sistema.py`.

| Archivo | Diagrama | Cómo se obtiene | Lugar en el informe |
|---|---|---|---|
| `04-modelo-de-datos` | Entidad-relación, notación de pata de gallo: tablas, claves primarias, foráneas y únicas | **Generado** desde `backend/app/modelos` | Cap. IX, Modelo de datos |
| `04b-modelo-de-datos-completo` | El mismo, con todas las columnas | **Generado** | Anexo K |
| `05-secuencia-de-un-caso` | Secuencia UML 2.5: carga, análisis, informe y verificación pública | A mano, siguiendo los servicios que nombra el encabezado | Cap. IX, Diseño de solución |
| `06-cronograma` | Gantt: planificado frente a real | A mano, desde la bitácora | Cap. V, Cronograma |
| `07-despliegue-uml` | Despliegue UML 2.5: nodos, entornos de ejecución, artefactos y protocolos | Dibujado con posiciones fijas (`diagrama_despliegue.py`, SVG) con los datos leídos de Terraform, systemd y Nginx; **verificado** | Cap. IX, Arquitectura |
| `08-componentes-uml` | Componentes UML 2.5: capas, interfaces provistas y requeridas (Strategy) | **Generado** desde `app/integraciones` y `app/analisis` | Cap. IX, Diseño de solución |
| `09-casos-de-uso-actores` | Actores y su generalización | **Generado** desde `docs/especificacion/05-casos-de-uso.md` | Cap. III, Catálogo de requisitos |
| `09a` a `09e` | Casos de uso por módulo (cuentas; organizaciones, planes y aseguradoras; casos; imágenes, análisis e informes; retención) | **Generado** | Cap. III o Anexo F |
| `09f-casos-de-uso-relaciones` | Relaciones «include» y «extend» entre casos de uso | **Generado** | Cap. III o Anexo F |

## Reglas que cumple todo diagrama

El revisor `diagramas_del_sistema.py verificar` controla automáticamente las reglas marcadas con (A). Las demás se controlan mirando la imagen, paso que el comando `/generar-diagramas` hace obligatorio.

1. **Fiel al sistema (A).** Nada que no exista en el código, la infraestructura o la especificación. Lo que todavía no existe va marcado como «previsto», con borde punteado; nunca se dibuja como hecho. El clasificador, por ejemplo, no aparece entre las capas hasta que esté en el código.
2. **Notación estándar del tipo de diagrama:**
   - **Despliegue UML (A):** nodos con estereotipo («device», «executionEnvironment», «cloud», «cloud service», «external system»), artefactos dentro de su nodo y cada ruta de comunicación con su protocolo. Sin `rectangle`.
   - **Componentes UML (A):** la interfaz provista se dibuja con una línea continua hacia el círculo, y la requerida con una dependencia punteada. Los agrupamientos son `package`, no `rectangle`.
   - **Casos de uso UML (A):** la asociación entre actor y caso es una línea sin flecha. «include» y «extend» van punteados y con su estereotipo. Hay un límite del sistema, y la generalización entre actores lleva flecha de triángulo hueco.
   - **Secuencia UML:** el mensaje sincrónico es una línea continua con punta llena, y la respuesta, una línea punteada. Los fragmentos `loop` llevan su condición y la numeración es automática.
   - **Entidad-relación:** la notación de pata de gallo sale de la clave foránea: si es obligatoria, «uno»; si es opcional, «cero o uno»; si es única, «uno a uno».
3. **Legible:**
   - sin flechas ni etiquetas superpuestas;
   - sin elementos sueltos;
   - sin recortes (A);
   - sin proporciones mayores a 4 a 1 (A), y si hace falta, el diagrama se divide;
   - un diagrama, una idea: los casos de uso van por módulo y las relaciones entre módulos, en un diagrama aparte.
4. **Color con significado.** Si un color se repite como código, va con su leyenda. Por ejemplo, en el de componentes: capa, implementación real, simulada y prevista.
5. **Aspecto de diagrama hecho a mano, no generado** (pedido de la autora, 2026-11-11). Blanco y negro con un solo color de acento, líneas rectas (`linetype polyline`) en lugar de curvas, cajas alineadas en filas o columnas y ninguna línea en abanico. Las dependencias hacia un grupo de interfaces van al paquete y no una por interfaz. En los casos de uso, los actores se reparten a los dos lados del sistema para que las asociaciones no se crucen. Cuando la disposición automática no logra esto (el despliegue, con nodos anidados y muchas rutas hacia servicios externos), el diagrama se dibuja con posiciones fijas en SVG.
6. **Ortografía (A).** Las etiquetas van en español con tildes. Las únicas excepciones son los identificadores del código y de la base (nombres de clases, tablas y archivos).

## Cómo se regeneran

Desde `backend/`:

```bash
python herramientas/diagramas_del_sistema.py er --compacto > ../docs/arquitectura/diagramas/04-modelo-de-datos.puml
python herramientas/diagramas_del_sistema.py er > ../docs/arquitectura/diagramas/04b-modelo-de-datos-completo.puml
python herramientas/diagramas_del_sistema.py componentes > ../docs/arquitectura/diagramas/08-componentes-uml.puml
python herramientas/diagramas_del_sistema.py casos-de-uso
python herramientas/diagrama_despliegue.py
python herramientas/diagramas_del_sistema.py renderizar
python herramientas/diagramas_del_sistema.py verificar
```

Para renderizar hacen falta Java y Graphviz (`dot`) para los `.puml`, y Node con Playwright para los `.svg` (`herramientas/svg_a_png.cjs`). La primera vez se descarga PlantUML 1.2024.7 desde Maven Central.

Las versiones descartadas no se guardan: si un diagrama se rehace, se reemplaza su archivo.
