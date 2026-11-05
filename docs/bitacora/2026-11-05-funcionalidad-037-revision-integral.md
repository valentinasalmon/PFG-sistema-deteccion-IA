# 2026-11-05 — Funcionalidad 037: revisión integral de la portada al PDF

La autora pidió revisar todo el sistema y arreglar usabilidad, flujo, diseño y textos, dejar clara la diferencia entre abogado y aseguradora y mostrarle el antes y el después.

## Cómo se revisó

- Recorrido automático con capturas en computadora (1440 px) y celular (390 px) de todas las pantallas públicas, los tres caminos del registro, las pantallas internas como abogado y como aseguradora y la administración.
- Script que busca elementos fuera del ancho o cortados en el celular.
- Lectura del informe PDF generado con la plantilla actual.

## Qué se hizo

- **Acceso**: tarjetas de 34rem y 56rem (antes la del login se achicaba al contenido), campos de 56 px; en el celular, a todo el ancho.
- **Paleta de la portada por dentro** (opción A): menú verde bosque, acción lima, enlaces verdes, rubro en píldora blanca, sin buscador en la barra en computadora (Ctrl K sigue).
- **Caso**: pasos en horizontal con el contenido debajo; huella del PDF abreviada con «Copiar»; caso inexistente con salida.
- **Vocabulario por perfil**: la aseguradora ve «siniestro» en todo el sistema y en el informe; el abogado, «caso». Hook `useRubro`.
- **Celular**: contadores en grilla, pestañas en dos filas, informe sin márgenes anidados.
- **Informe PDF**: aviso de «no emite veredictos» en la primera página, escala sin cortes, colores de la marca, sin «Caso CASO-», 3 páginas.
- **Textos**: plurales («1 imagen»), coma decimal en el ELA, portada para casos y siniestros con capturas renovadas, privacidad y términos completados.

## Decisiones de la autora pendientes

1. Red neuronal en la portada y los términos mientras no esté la 012 (propuesta: «Próximamente»).
2. Textos del análisis en pantalla (propuesta: un descargo arriba y lo técnico plegado).
3. Tarjetas «para abogados / para aseguradoras» en la portada.
4. Numeración «SIN-» para siniestros (propuesta: dejar «CASO-»).
5. Aprobar los textos nuevos de privacidad (incluye «las imágenes no se usan para entrenar»).
6. Ícono del contador «Cerrado».

La presentación con el antes y el después y estas opciones se publicó como página para la autora.

## Pruebas

- Frontend: 275 pruebas, ESLint sin errores, compilación correcta.
- Backend: pruebas del informe y del ELA actualizadas; flake8 sin errores.

## Decisiones de la autora sobre la revisión (2026-11-05, tarde)

1. Red neuronal en la portada y los términos: **«Próximamente»** hasta integrar la 012. Aplicado.
2. Textos del análisis: **un solo descargo arriba y los datos técnicos plegados**. En curso.
3. Portada: **dos tarjetas por perfil** («Tus casos, con prueba revisada» y «Tus siniestros, verificados antes de liquidar»). Aplicado.
4. Numeración: **se mantiene «CASO-»** como identificador interno.
5. Textos nuevos de privacidad: **aprobados** (siguen provisorios hasta la revisión legal final).
6. Contador «Cerrado»: **ícono claro como el resto**. Aplicado.

### Pedidos nuevos de la autora

- «Siniestro» en todo lo que ve una aseguradora y «caso» para abogados, sin importar perder lo anterior. Aplicado en el caso (datos, estado, compartir, eliminar), la lista, el inicio, el alta, el perfil y el buscador.
- Login más lleno en computadora y con el inicio con Google; registro con las opciones más espaciadas.
- Pantalla del caso reorganizada: muchas tarjetas, se pierde la persona.
- Revisar el celular: cosas fuera de lugar o flotando.
- Informe: arriba solo una línea («no emite veredictos, es una herramienta de apoyo»).
- Propuesta del tutor: **PDF breve con un enlace a la versión detallada en línea**, para quien quiera ver el porqué de cada resultado.
- Seguir revisando el resto de las pantallas y mostrar todo con el antes y el después. Criterio pedido: profesional, limpio y fluido.

### Regla de trabajo

La autora pidió que la bitácora se actualice todos los días, con cada tanda de trabajo, y no solo al cerrar una etapa.

## Informe PDF breve (2026-11-05, noche)

- Arriba, una sola línea: «Herramienta de apoyo: muestra indicios técnicos y no emite veredictos».
- La escala de lectura pasa a una línea de etiquetas; cada técnica muestra solo su nivel y qué encontró.
- Sección nueva «Más detalle y verificación» con dos QR: el análisis detallado en la plataforma (con cuenta) y la verificación pública del PDF.
- Queda abierta la CP-43: si el detalle debería abrirse sin cuenta.
- Plan, tareas y capturas del antes y el después de la 037 quedan en `docs/funcionalidades/037-acceso-y-pantallas/`.
- Backend: 567 pruebas, cobertura 97,5 %, pylint 10/10.

## Corrección pedida por la autora: vocabulario sostenible

La primera versión del vocabulario por perfil agregaba una frase suelta por pantalla («Nuevo caso», «Casos recientes», «Buscar un caso»…) para cada rubro: una lista que crece sin control. Se reemplazó por una función, `vocabulario(singular, plural)`, que arma todas las frases desde una sola palabra por rubro. Cambiar «siniestro» por otra palabra, o sumar un rubro, es una línea. Pruebas en `utilidades/lenguaje.test.js`.

## Otros avances del día

- Pantalla del caso: «Datos y gestión» en su propia pestaña; el contenido del paso ocupa todo el ancho.
- Inicio de sesión en dos columnas con «Continuar con Google» (visible donde Google está configurado, como en producción); registro más espaciado.
- Administrador: menú grafito con la píldora «Admin».
- Recorridos de punta a punta de aseguradora y abogado (computadora y celular emulado), con evidencia en `docs/funcionalidades/037-acceso-y-pantallas/evidencia.md`.

## Espacios y elementos flotantes (pedido de la autora)

- La barra «0 de 2 elegidas · Analizar» flotaba sobre las fotos aunque no hubiera ninguna elegida: pasó a una fila fija arriba de la galería.
- «Invitar miembros» ocupa el ancho de su tarjeta (el máximo de los formularios lo dejaba suelto).
- Celular: la huella SHA-256 del análisis se salía del borde (ahora abreviada con «Copiar»); «Editar los datos» de la organización quedaba suelto a la derecha; con tres pestañas, la tercera quedaba sola en una fila. Corregido; capturas en `capturas/`.
- Cada capa del análisis se describe sola (título, explicación y tipo) y el frontend los toma de la API: sumar la red neuronal es una clase (documentado en `docs/red-neuronal/07`).

## Segunda presentación a la autora

Se republicó la página de la revisión (versión 2) con el antes y el después de esta tanda, los recorridos de punta a punta y dos decisiones nuevas: CP-43 (enlace al análisis detallado con o sin cuenta) y si el PDF de 4 páginas está bien o se reduce a una página de resumen con anexo. Lo que falta del proyecto quedó actualizado en `docs/guias/pendientes.md`.
