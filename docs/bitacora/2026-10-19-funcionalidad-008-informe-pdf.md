# 2026-10-19 — Funcionalidad 008: informe PDF e historial (hito v0.1)

## Qué se hizo

Cada análisis termina con un informe PDF en español, sencillo y explicativo, que se descarga desde la pantalla del caso. Con esto se completa el primer flujo de punta a punta, que corresponde al **hito v0.1** de la hoja de ruta: registrarse, crear un caso, cargar imágenes, analizarlas y descargar el informe.

Documentos: [especificación](../funcionalidades/008-informe-pdf/especificacion.md), [plan](../funcionalidades/008-informe-pdf/plan.md) y [tareas](../funcionalidades/008-informe-pdf/tareas.md). La rama `funcionalidad/008-informe-pdf` parte de `desarrollo` con la 007 integrada.

- **Informe PDF**: se genera con WeasyPrint al finalizar el análisis. Incluye:
  - Datos del caso y de quién lo pidió (perfil, colegio o empresa) y la fecha y la hora en la hora de Argentina.
  - Por cada imagen: vista reducida, huella SHA-256 y estado del sello de tiempo (pendiente hasta la 016).
  - Por cada capa: nivel con barra, conclusión, hallazgos, metadatos y un recuadro **"¿Qué significa?"**.
  - Versiones de los componentes, y limitaciones y advertencia legal.
- **Inmutabilidad**: el PDF no se modifica nunca y se guarda la huella SHA-256 del propio PDF. Un análisis nuevo genera un informe nuevo.
- **Reglas pendientes de funcionalidades anteriores, ahora completas**:
  - Una imagen incluida en un informe ya no se puede eliminar (RN24).
  - Un caso con informes vuelve a Analizado al reabrirlo (RF29 CA1).
  - Al eliminar casos, organizaciones o cuentas también se borran sus PDF (RN21).
- **Si el PDF falla**, el análisis igual termina con sus resultados, el correo lo avisa y se puede volver a generar.
- **Pantalla**:
  - Botón "Descargar el informe PDF" en cada análisis, o "Generar el informe" si faltó.
  - Sección **"Informes"** con el historial: fecha, solicitante, imágenes y huella del PDF.
- **Refactorización**: entorno común de plantillas PDF (`app/informes/plantillas.py`), que ahora también usa la copia de datos de la 019.

## Verificación de los criterios de aceptación

| Criterios | Cómo se verificó | Resultado |
|---|---|---|
| CA1 Generar | Prueba de API: informe creado, PDF descargado idéntico a su huella, caso Analizado, correo con aviso del informe y auditoría | Cumplido |
| CA2, CA3 Contenido | Pruebas del HTML del informe con cada dato pedido y la hora de Argentina; búsqueda automática de términos de veredicto; PDF real generado | Cumplidos |
| CA4 Inmutabilidad | Un segundo análisis genera otro informe; el primero conserva su archivo y su huella | Cumplido |
| CA5 RN24 y reabrir | La imagen del informe no se elimina (409); la imagen alterada no queda marcada; reabrir vuelve a Analizado | Cumplido |
| CA6 Falla | Con la generación del PDF fallando: análisis finalizado sin informe, correo con aviso, regeneración y segundo intento rechazado | Cumplido |
| CA7, CA8 Historial y descarga | Lector consulta y descarga sin regenerar; sin permiso, 404; informe de otro caso, 404; pruebas de pantalla | Cumplidos |
| CA9 Eliminación | Al eliminar el caso se borra el PDF y la auditoría guarda su huella | Cumplido |

**Cifras:**
- Backend: 358 pruebas, cobertura del 99 %, flake8 sin errores, pylint 10/10 y los tres contratos de capas cumplidos.
- Frontend: 185 pruebas, cobertura del 98 %, ESLint sin errores y compilación correcta.
- Migración `7d203719a8cb`: probada con `upgrade`, `check` y `downgrade` en PostgreSQL.

**Recorrido en navegador real** con las mismas tres imágenes de la 007 (editada con Photoshop, PNG sin metadatos y una de ChatGPT):
- El análisis terminó y el botón descargó `informe-CASO-…-analisis-N.pdf`, de 5 páginas.
- Revisé el PDF página por página: datos del caso, solicitud, escala, una sección por imagen con miniatura, huella y sello, resultados, versiones y limitaciones.
- La imagen incluida en el informe muestra "Está en un informe" en lugar de "Eliminar".
- No hubo errores en la consola.

## Decisiones tomadas por el asistente

- **Si el PDF falla, el análisis no se pierde.** Los resultados ya están guardados y son lo más valioso, así que el análisis termina y el informe se regenera después. Marcar todo el análisis como fallido obligaría a analizar de nuevo.
- **Miniaturas embebidas en el PDF**, no enlaces: el documento es autónomo y no depende de enlaces que vencen a los 5 minutos.
- **Huella SHA-256 del PDF** guardada y visible en el historial: permite probar que un informe presentado no fue modificado.
- **Sello de tiempo**: el informe reserva su lugar con "todavía no disponible en esta versión de la plataforma", hasta la 016.
- **`Imagen.en_informe` pasa a ser una columna**, marcada al generar el informe. Así la regla RN24 se consulta sin recorrer los informes.
- **Hora de Argentina en el PDF** (la base guarda UTC), porque el documento se lee fuera de la plataforma.
- **Al regenerar el informe se actualiza la fecha del caso**, para que la pantalla refresque el historial.

## Problemas encontrados y cómo se resolvieron

| Problema | Solución |
|---|---|
| La prueba de términos prohibidos encontró "auténtica" en la explicación de la escala, aunque la frase la negaba | Se reescribió sin términos de veredicto ("No expresa una probabilidad sobre el origen de la imagen") |
| Después de regenerar el informe, la pantalla seguía mostrando "No se pudo generar" | El detalle del análisis se recarga solo y la fecha del caso se actualiza |
| El pie de página del PDF salía en otra tipografía | Se fijó la misma fuente en los márgenes de la página |
| Constructor repetido entre servicios, marcado por pylint | `ServicioInformes` guarda solo los dos valores de configuración que usa |

## Observación

- `VERSION_APLICACION` vale `0.2.0` desde funcionalidades anteriores, mientras que la etiqueta de este hito es `v0.1`. No lo cambié: lo decide la autora al crear la etiqueta (ver pendientes).

## Pendientes

- **Autora**:
  - Revisar e integrar el Pull Request de la 008.
  - Revisar con los tutores los textos de "¿Qué significa?" y de la advertencia legal.
  - **Hito v0.1**: con la 008 integrada, abrir el Pull Request de `desarrollo` hacia `main` y crear la etiqueta `v0.1`, como indica la [hoja de ruta](../guias/hoja-de-ruta.md).
  - Decidir si `VERSION_APLICACION` pasa a `0.1.0` para coincidir con la etiqueta.
- **016**: estado y referencia del sello de tiempo en el informe.
- **009, 011 y 012**: sus capas aparecen solas en el informe, cada una con su recuadro "¿Qué significa?".
