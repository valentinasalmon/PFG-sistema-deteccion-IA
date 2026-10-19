# Plan técnico: 020 — Registro guiado por pasos

Referencia: [especificacion.md](especificacion.md).

## Resumen de la solución

Solo cambia el frontend. La pantalla `PaginaRegistro` pasa a mostrar un paso por vez con un estado `paso` (1 a 4). Todos los datos viven en un único `useFormulario`, de modo que volver atrás no borra nada (CA5) y al final se envía la misma solicitud que en la funcionalidad 002 (CA6).

Cada paso es un formulario: "Siguiente" (o Enter) valida en el navegador los datos obligatorios de ese paso (perfil, nombre y apellido) y avanza (CA2, CA3). El paso 4 envía la solicitud y el backend valida de forma definitiva. Si el backend rechaza un campo de un paso anterior, la pantalla vuelve al primer paso con error usando una tabla campo → paso (CA7).

Al cambiar de paso, el foco pasa al título del paso (`h2` con `tabIndex=-1`) para que el lector de pantalla lo anuncie, y un indicador muestra "Paso N de 4" con una barra decorativa (CA8). El perfil se elige con dos tarjetas grandes que son botones de opción nativos, accesibles con teclado (CA1).

## Capas afectadas

| Capa | Archivos nuevos o modificados | Responsabilidad |
|---|---|---|
| Frontend: pantalla | `src/paginas/PaginaRegistro.jsx` | Pasos, validación por paso, regreso al paso con error, foco |
| Frontend: hook | `src/hooks/useFormulario.js` | Nuevo `marcarErrores(objeto)` para marcar varios campos a la vez |
| Frontend: presentación | `src/componentes/IndicadorPasos.jsx`, `src/componentes/OpcionTarjeta.jsx` | Avance y opción en tarjeta |
| Frontend: estilos | `src/estilos/global.css` | Sección "Formularios por pasos" |
| Backend | Ninguno | La API y las reglas de RF01 no cambian |

## Patrones aplicados

- Componentes de presentación sin estado, reutilizables en otros formularios por pasos.
- Estado del formulario centralizado en el hook existente (sin estado duplicado por paso).

## Contratos

- `IndicadorPasos({ actual, total })`.
- `OpcionTarjeta({ nombre, valor, seleccionada, onChange, titulo, descripcion? })`.
- `useFormulario(...).marcarErrores(errores: Object<string, string>)`: reemplaza los errores por campo; con un objeto vacío los borra junto con el aviso general. `marcarError(campo, mensaje)` se mantiene y usa `marcarErrores`.
- Sin endpoints nuevos: `POST /api/cuentas/registro` como en la 002.

## Cambios en datos

Ninguno.

## Bibliotecas nuevas

Ninguna.

## Estrategia de pruebas

- Componentes: `presentacion.test.jsx` (texto y ancho del indicador, opción elegida y aviso de cambio).
- Pantalla: `acceso.test.jsx`, un caso por criterio (CA1 a CA8), más Enter para avanzar, cambio de perfil sin enviar el dato del perfil anterior y error general en el paso 4.
- Manual: recorrido en navegador real contra el backend, en escritorio y a 375 px, con teclado (flechas en las tarjetas) y comprobación del correo de verificación.

## Excepciones a la constitución

Ninguna.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| El usuario cambia de perfil después de completar el colegio o la empresa | Se envía solo el dato del perfil final (`armarSolicitud`), con prueba |
| El backend rechaza datos de varios pasos a la vez | Se vuelve al primero; los errores de pasos posteriores reaparecen al reenviar |
| El foco automático molesta al abrir la pantalla | Solo se mueve al cambiar de paso, no al cargar |
