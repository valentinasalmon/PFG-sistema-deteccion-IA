---
description: Genera, verifica y revisa visualmente los diagramas del informe a partir del código real.
---

Los diagramas del informe tienen que ser fieles al sistema, usar la notación estándar de su tipo y leerse sin esfuerzo. Seguí `docs/arquitectura/diagramas/README.md`.

1. **Generá desde el código** lo que se puede generar (desde `backend/`):
   `python herramientas/diagramas_del_sistema.py er --compacto > ../docs/arquitectura/diagramas/04-modelo-de-datos.puml`, lo mismo sin `--compacto` para `04b`, `componentes` para `08` y `casos-de-uso` para los `09`.
2. **Actualizá a mano** los que no se generan (secuencia, cronograma) solo con hechos verificados: leé el código, `infraestructura/` y la bitácora antes de dibujar. El despliegue se dibuja con `python herramientas/diagrama_despliegue.py` (posiciones fijas, datos leídos de la infraestructura). Nada supuesto; lo que no existe va como «previsto» y punteado. Seguí la regla 5 del README de diagramas: aspecto de diagrama hecho a mano (blanco y negro, líneas rectas, cajas alineadas, sin abanicos ni cruces).
3. **Renderizá**: `python herramientas/diagramas_del_sistema.py renderizar` (necesita Java y Graphviz).
4. **Verificá**: `python herramientas/diagramas_del_sistema.py verificar` tiene que decir «Los diagramas coinciden con el sistema». Si marca algo, corregilo y repetí.
5. **Mirá cada imagen** (abrila con la herramienta de lectura de imágenes) y comprobá: sin flechas ni textos superpuestos, sin elementos sueltos, sin recortes, notación correcta, colores con leyenda, ortografía. Si algo se ve mal, cambiá la disposición (dirección, agrupamientos, dividir el diagrama) y volvé al paso 3. **No entregues un diagrama que no miraste.**
6. Reemplazá los archivos existentes: no guardes versiones descartadas. Actualizá la tabla del README si cambió algún diagrama.
7. Entregale a la autora cada figura con su número, su título, la oración que la introduce y su nota (*Nota. Elaboración propia, en notación UML 2.5.*), y mandale las imágenes.
