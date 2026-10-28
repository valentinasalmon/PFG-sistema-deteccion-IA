# Plan técnico: 028 — Mejoras de usabilidad e interfaz (primera tanda)

| Parte | Archivos | Detalle |
|---|---|---|
| Componentes comunes | `componentes/FilaCaso.jsx`, `componentes/EtiquetaEstado.jsx` | Fila de caso completa (lista) o compacta (inicio); estado con color propio |
| Inicio | `paginas/PaginaInicio.jsx`; backend `servicio_panel.py`, `esquemas/panel.py` | `redactar_actividad(…, id_lector)` en segunda persona; la actividad incluye `accion` y los recientes, `lugar` |
| Lista de casos | `paginas/PaginaCasos.jsx`; backend `esquemas/casos.py`, `servicio_casos.py`, `repositorio_casos.py` | Filtro `busqueda` (número, expediente normalizado o lugar) |
| Perfil | `paginas/PaginaPerfil.jsx` | Pestañas con `role="tablist"`, flechas del teclado y `?seccion=` |
| Organización | `paginas/PaginaOrganizacion.jsx` | Invitaciones dentro de Miembros; zona de riesgo en filas |
| Administración | `paginas/PaginaAdministracion.jsx`, `utilidades/periodos.js` | Períodos rápidos y pestañas |
| Estilos | `estilos/global.css` | `.fila-caso`, `.estado-caso--*`, `.contadores`, `.actividad`, `.pestanias`, `.zona-riesgo-filas`, `.invitar`, `.periodos` |

Pruebas nuevas o actualizadas:
- backend: actividad en segunda persona y buscador único;
- frontend: panel, casos, perfil (pestañas), organización (eliminar), administración (período) y `periodos.test.js`.

Capturas antes y después en `capturas/`, con datos de ejemplo, nunca de casos reales.
