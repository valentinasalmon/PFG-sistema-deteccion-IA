# 039 — Arnés del informe final

**Estado:** Implementada · **Rama:** `claude/gracious-thompson-9slyyn` · **Requisitos:** RNF19 (calidad y documentación), RNF17 (arquitectura verificable) · **Pedido de la autora:** 2026-11-05

## Problema

El informe final se escribe con asistencia de IA y por partes. Aparecieron errores que un evaluador detecta enseguida:

- secciones pegadas en el lugar equivocado y párrafos duplicados;
- capítulos con la numeración repetida;
- citas sin entrada en la bibliografía;
- datos del sistema desactualizados o presentados como hechos cuando estaban previstos;
- diagramas que no seguían la notación UML ni coincidían con el código (la autora los descartó el 2026-10-29).

El arnés del código no cubría el documento.

## Qué se construye

1. **Guías:**
   - una guía de redacción con la estructura del protocolo, las reglas de redacción, de evidencia y de APA 7, y el criterio del evaluador por capítulo;
   - una fuente única de hechos del sistema;
   - una guía para contar el trabajo con IA (con la declaración de uso);
   - un plan de negocios con el contexto argentino.
2. **Comandos:**
   - `/redactar-informe`;
   - `/revisar-informe`, que actúa como evaluador de tesis;
   - `/generar-diagramas`.
3. **Sensores:**
   - un revisor mecánico del informe;
   - el cálculo de las cifras del proceso desde el repositorio;
   - un generador y verificador de diagramas desde el código, que controla la fidelidad, la notación, la ortografía y el tamaño.
4. **Memoria:**
   - el estado del informe por capítulo;
   - la última revisión con sus correcciones.

## Criterios de aceptación

- [x] **CA1:** `revisar_informe.py` detecta:
  - secciones vacías, párrafos duplicados y numeración de capítulos, tablas y figuras;
  - citas sin entrada y entradas sin citar;
  - viñetas, tiempo pasado, marcadores, términos, veredictos y formato de números.

  Devuelve 1 si hay errores.
- [x] **CA2:** `cifras_del_proyecto.py` calcula desde git y desde los archivos los commits, la coautoría de IA, los pull requests, las pruebas, las funcionalidades, los ADR, la bitácora y los requisitos, con la fecha y el commit.
- [x] **CA3:** El diagrama entidad-relación, el de componentes y los de casos de uso se generan desde el código y la especificación, sin importar la aplicación.
- [x] **CA4:** `verificar` falla si:
  - un diagrama generado no coincide con el código;
  - el de despliegue omite un dato real de la infraestructura (instancia, región, sistema operativo, puertos, servicios);
  - se viola la notación (nodos sin estereotipo, rutas sin protocolo, `rectangle` en UML, asociaciones con flecha, relaciones sin estereotipo);
  - falta una tilde en una etiqueta;
  - una imagen está recortada o es demasiado alargada.
- [x] **CA5:** Los comandos `/revisar-informe` y `/generar-diagramas` exigen leer el documento completo y mirar cada imagen antes de entregar.
- [x] **CA6:** Pruebas automáticas de las tres herramientas, en verde.
- [x] **CA7:** El inventario de casos de uso refleja lo implementado (CU33 a CU38).

## Fuera de alcance

- Detectar automáticamente la superposición de textos en una imagen: se controla mirando cada imagen, paso obligatorio de `/generar-diagramas`.
- Escribir en el documento de Google Docs: la autora pega los textos.
