# 2026-11-02 — Funcionalidad 034, quinta tanda: portada más limpia

## Qué se hizo

Pedido de la autora sobre la portada pública (`frontend/src/paginas/PaginaPortada.jsx` y `frontend/src/estilos/portada.css`):

- **Se quitaron:** los tres beneficios del encabezado (informe sellado, verificable, confidencial), los tres globos sobre la captura («Análisis listo», «Moderados en el lateral», «Sellado y verificable»), la sección «para abogados y aseguradoras» y su enlace «Para quién» del menú, el sello «Encontrás todo con Ctrl K» y las letras gigantes de la sección de pasos, y el ojo del cierre (también su imagen, `public/portada/ojo.jpg`, que ya no se usaba).
- **Cuatro miradas:** el título y la bajada a la izquierda (fijos al desplazarse en escritorio) y las cuatro cajas en filas, una abajo de otra, con el ícono a la izquierda del texto. En tableta y celular el título pasa arriba.
- **Planes:** las tres tarjetas quedan a la misma altura (el plan destacado ya no se desplaza hacia arriba), con los botones alineados abajo.
- **Pie:** los enlaces (Términos, Privacidad y seguridad, Verificar un informe, Estado del sistema) a la derecha; en el celular quedan debajo del descargo, alineados a la izquierda.
- Se borraron los estilos y las animaciones de todo lo quitado.
- Lo demás se mantiene: encabezado, captura del sistema, pasos con la captura del buscador, planes con el selector y cierre.

## Decisiones

- De la sección «para quién» se eligió la opción de quitarla, que la autora dio como alternativa: el encabezado ya dice «Para abogados y aseguradoras» y los planes tienen el selector por tipo de organización.

## Verificación

- ESLint sin errores y 261 pruebas de Vitest en verde. La prueba de la portada ahora verifica que lo quitado no aparece.
- Capturas a 1440 px y a 390 px sin desbordes horizontales (`docs/funcionalidades/034-pulido-ux/capturas/quinta-tanda-*.jpg`).

## Pendiente

- Que la autora la revise y abra el Pull Request de `funcionalidad/034-quinta-tanda` hacia `desarrollo`.
