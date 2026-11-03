# 2026-11-02 — Corrección: el informe decía «Pendiente de confirmación en Hedera»

## Problema

Con Hedera real en producción, la autora vio que el PDF del informe decía, en el sello de cada imagen, «Pendiente de confirmación en Hedera».

Causa: al cargar una foto se publica su huella en Hedera y se consulta enseguida el *mirror node*, que tarda unos segundos en tener el mensaje. La imagen queda «enviada», y la confirmación llega recién con la tarea periódica, cada 15 minutos. El análisis termina antes, y el PDF, que no cambia una vez generado, queda con el sello pendiente. En las pruebas automáticas y en desarrollo no se veía, porque el sello simulado se confirma al instante.

## Corrección

Antes de armar el PDF, el trabajador de análisis llama a `ServicioSellos.confirmar_antes_de_informar`:
- pide o confirma el sello de cada imagen;
- si alguno sigue enviado, vuelve a consultar cada 3 segundos, hasta 15 segundos en total;
- nunca lanza ni impide el informe: si Hedera no confirma a tiempo, el PDF sale igual y la tarea periódica completa el sello en el sistema.

Pruebas nuevas: el sello que se confirma después de esperar, el corte a la espera máxima y el caso sin sellador o con la imagen ya sellada.

## Revisión del análisis

La autora sospechaba que el análisis fallaba después de los cambios. Se probó de punta a punta contra el backend real, con una base de demostración:
- sesión, caso, carga de un JPEG y un PNG, análisis, informe y descarga del PDF;
- en modo sincrónico y con la cola RQ y el trabajador, como en producción.

Los dos análisis terminaron en «Finalizado», con informe. El código del análisis no cambió desde el 2026-10-28, y el sello no puede interrumpir el análisis (los errores de Hedera se convierten en reintentos). Falta saber qué ve la autora en producción para seguir investigando ahí.
