# 2026-10-31 — Funcionalidad 034, cuarta tanda: organización, administración, verificar y estado

Rama `funcionalidad/034-cuarta-tanda`, creada desde `funcionalidad/034-portada-nueva` (la tercera tanda, todavía sin integrar), porque reutiliza sus estilos de acceso.

## Qué se hizo

- **Organización en pestañas** (Miembros, Plan, Ajustes). Antes era una página de dos columnas que en el celular medía más de 2000 px. La pestaña elegida queda en la dirección (`?seccion=plan`), así un enlace la abre directo.
  - Cuando los lugares del plan están ocupados, el aviso de Miembros enlaza a la pestaña Plan.
  - Nuevo componente `Pestanias` y hook `usePestaniaElegida`. Mi perfil los usa también, en lugar de su código propio.
- **Administración**:
  - las aseguradoras pendientes van primero, con su cantidad en el título y un borde lima;
  - sin pendientes queda una sola línea («No hay aseguradoras esperando aprobación.»);
  - en el celular, la tabla de cuentas y organizaciones se apila (cada fila una tarjeta, cada dato con su nombre) en lugar de cortar los correos.
- **Verificar un informe**: la acción principal es una zona para elegir o soltar el PDF; el código queda abajo, como opción secundaria, con su campo y su botón en una fila e indicando dónde está en el informe (sección «Verificación de este informe», junto al QR).
- **Estado del sistema**: la fecha del último sello confirmado va en su propia línea.
- **CA2 (390 px)**: se revisaron todas las pantallas de acceso y las internas (Inicio, Casos, Nuevo caso, Mi perfil y sus pestañas, Organizaciones, la organización y sus pestañas, Administración). Se corrigió un desborde de la página de verificar: la columna de la grilla crecía con el botón, que no corta su texto (`minmax(0, 1fr)` en todo el acceso).

## Pruebas

- 261 pruebas del frontend, lint sin errores y compilación correcta.
- Revisado en el navegador contra el backend real con una base local de demostración, a 1280 y a 390 px.

## Pendiente

- Integrar primero el PR de la tercera tanda y después el de esta.
- CA1, CA3, CA4, CA6 y CA9 de la 034 se revisan en el cierre con la autora, pantalla por pantalla.
