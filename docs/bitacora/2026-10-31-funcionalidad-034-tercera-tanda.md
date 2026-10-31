# 2026-10-31 — Funcionalidad 034, tercera tanda: portada, acceso, registro, privacidad y estado de Hedera

## Qué se hizo

**Portada nueva** (`PaginaPortada.jsx`, `portada.css`), con la composición que eligió la autora entre las direcciones A y B:

1. encabezado verde bosque con grilla y la pregunta centrada «¿Esa foto es real? Sabelo en minutos.»;
2. la pantalla real del sistema debajo, con tarjetas flotantes;
3. «Cuatro miradas sobre cada foto» (metadatos, C2PA, ELA y red neuronal);
4. tarjetas lima y oscura para abogados y aseguradoras, que llevan al registro;
5. «Empezá en tres pasos», con la captura del buscador;
6. planes (Personal, Básico y Profesional destacado), con los límites del sistema y el selector estudio/aseguradora;
7. cierre con el ojo de la marca y pie.

- Habla de beneficios: no nombra proveedores ni la infraestructura (una prueba lo controla).
- Las capturas (`frontend/public/portada/`) se tomaron con la API simulada y datos de ejemplo («Laura Méndez»), sin datos reales.
- El movimiento (tarjetas que flotan, nodos, texto gigante que se desliza, barrido del ojo) se apaga con «reducir movimiento» y el contenido se ve en reposo.

**Registro más corto** (la autora: «el registro sigue muy mal»):
- «Tus datos» junta nombre, apellido, el colegio o la aseguradora y, para el estudio, su nombre.
- Lo que llega elegido desde la portada (camino y plan) no se vuelve a preguntar; un resumen arriba lo muestra con «Cambiar».
- Resultado: independiente desde la portada, 2 pasos (antes 4); estudio o aseguradora desde la portada, 3 pasos con el pago (antes 6). El registro con Google se simplificó igual.

**Acceso con la estética de la portada** (`acceso.css`): franja verde bosque con grilla y logo, tarjeta blanca montada encima, píldoras lima, campos de 52 px y nombre y apellido en fila en la computadora. Aplica a inicio de sesión, registro, pago, legales, verificación y estado.

**Política de Privacidad técnica:** cuatro pilares (confidencialidad, veracidad, seguridad y apoyo, no veredicto) y un detalle técnico de cada medida tomado de `docs/arquitectura/seguridad.md` (TLS, AES-256, bcrypt 12, sesión, enlaces firmados de 5 minutos, SHA-256 sellado en Hedera, auditoría, límites, OWASP, ubicación en la Unión Europea). No nombra al proveedor de nube.

**Estado del sello en Hedera** (pedido de la autora: «fijate lo de hedera»): desde este entorno no se puede consultar producción, así que `/api/salud` y la página `/estado` muestran ahora el modo del sello, la red, si hay sellos fallidos o demorados y la fecha del último confirmado. No expone la cuenta, el tema ni las huellas, y no cambia el código de respuesta (si Hedera falla, la plataforma sigue y reintenta).

## Decisiones

- **Cookies y Clarity (CP-37):** la política decía que no había cookies de seguimiento, pero Clarity ya está activo en producción. Se dejó un texto provisorio que lo explica; la autora tiene que aprobarlo.
- **Ubicación de los datos:** se informa «Unión Europea» en la política porque la Ley 25.326 pide informar la transferencia internacional; no se nombra al proveedor.
- Los spots publicitarios quedan como idea, sin construir (pedido de la autora).

## Pruebas

- Frontend: 261 pruebas, lint sin errores, compilación correcta. Revisado en el navegador a 1280 y 390 px, sin desborde horizontal.
- Backend: 546 pruebas, flake8, pylint 10/10 y cobertura por encima del 80 %.

## Pendiente

- La autora: aprobar el texto de Clarity (CP-37) y comprobar en `/estado` de producción que el sello de Hedera figura «Funciona» (tarea pendiente de la 023).
- 034: pestañas de la organización, perfil y administración (T06), y verificar informe y estado con el estilo nuevo (T07).
