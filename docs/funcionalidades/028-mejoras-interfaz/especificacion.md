# Especificación: 028 — Mejoras de usabilidad e interfaz

- **Rama**: `funcionalidad/028-mejoras-interfaz`
- **Estado**: En curso. Primera tanda implementada; la segunda espera la validación de la autora.
- **Requisitos que realiza**: RNF10, RF26, RF48 (interfaz), RF53 (enlace para la persona afectada, segunda tanda)
- **Reglas de negocio aplicadas**: RN01, RN12, RN27
- **Casos de uso**: transversal

## Problema

Una revisión de las 19 pantallas, en computadora y en celular, encontró:
- acciones duplicadas, como «Nuevo caso» en el menú y en la cabecera, o «Descargar el informe» tres veces en el caso;
- etiquetas de estado del mismo color;
- datos repetidos: el perfil aparece tres veces y el plan de la organización, tres;
- formularios mal armados, con dos campos de búsqueda separados y botones pegados a los títulos;
- listas apiladas: cinco contadores uno debajo del otro en el celular y números de caso cortados en tres líneas;
- una pantalla del caso de unos 8.800 px de alto.

Los frames de la propuesta están en el lienzo de diseño compartido con la autora (ronda 1 y ronda 2).

## Alcance

### Primera tanda (aprobada por la autora el 2026-10-28, implementada)
- **Inicio:**
  - contadores compactos que abren la lista filtrada;
  - casos recientes con la misma fila que la lista de casos;
  - actividad en dos columnas, en segunda persona («Cargaste…»), con el enlace solo en el número del caso y 5 eventos más «Ver toda la actividad».
- **Lista de casos:**
  - un solo buscador (número, expediente o lugar);
  - estado, tipo y espacio en la misma fila;
  - columnas fijas con encabezado;
  - el número no se corta y el rol solo aparece si el caso es compartido.
- **Mi perfil:** una tarjeta de identidad y pestañas Datos personales · Seguridad · Plan · Privacidad. Las reglas de la contraseña aparecen al escribirla.
- **Organización:**
  - cabecera sin datos repetidos y «Editar los datos» con texto;
  - miembros, invitaciones pendientes e invitar en una tarjeta;
  - plan y zona de riesgo a la derecha, en filas;
  - eliminar pide el nombre recién al elegir «Eliminar…».
- **Administración:**
  - período con botones (este mes, 3 meses, este año, desde el inicio) y fechas a pedido;
  - indicadores parejos con su detalle;
  - pestañas comunes.
- **Base:**
  - estados del caso de gris a azul y a verde (pedido de la autora);
  - un solo «Nuevo caso»;
  - lugar reservado para el mapa ELA.

### Segunda tanda (frames para validar)
- **Menú según el rol:**
  - la administradora solo ve Administración y Mi perfil;
  - quien no pertenece a ninguna organización no ve «Organizaciones».
- **Pantalla del caso por etapas** (Cargar imágenes · Análisis · Informe), y en cada etapa solo lo que le corresponde.
- **Enlace para que la persona afectada suba las fotos** sin cuenta:
  - vence en 7 días;
  - se puede anular;
  - no muestra datos del caso;
  - pide una declaración de que las fotos son suyas o tiene permiso.
- **Celular:** contadores que se deslizan, fotos de a dos y acciones fijas abajo.
- **Inicio de sesión y registro:**
  - panel de marca con ventajas reales;
  - Google arriba;
  - «Mostrar» contraseña;
  - pasos del registro con nombre.

### Excluido
- Cambios en la identidad visual (colores de marca, tipografías, esquinas de visor), que se mantienen.

## Criterios de aceptación (primera tanda)

- [x] **CA1**: Los contadores del inicio llevan a `/casos?estado=<estado>`.
- [x] **CA2**: La actividad propia se redacta en segunda persona. El enlace va solo en el número del caso. Se muestran 5 eventos y el resto a pedido.
- [x] **CA3**: El buscador de casos encuentra por número, por expediente (sin tildes ni mayúsculas) o por lugar.
- [x] **CA4**: La lista de casos muestra columnas fijas y el número en una línea. «Responsable» no se muestra como etiqueta.
- [x] **CA5**: El perfil se recorre en pestañas, también con las flechas del teclado, y la pestaña queda en la dirección.
- [x] **CA6**: En la organización, la eliminación pide el nombre recién después de elegir «Eliminar…».
- [x] **CA7**: El tablero de administración cambia de período con un botón.
- [x] **CA8**: Los estados del caso tienen un color propio, con el nombre siempre escrito.

## Preguntas abiertas

- Enlace para la persona afectada: implica tratar datos de un tercero (Ley 25.326). Ver CP-32.
- Cuentas de administración solo para administrar. Hoy la cuenta de prueba es abogada y administradora a la vez.
