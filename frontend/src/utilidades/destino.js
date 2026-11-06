/**
 * Pantalla a la que volver después de iniciar sesión con Google (038).
 *
 * Con correo y contraseña, la pantalla pedida viaja en el estado de la
 * navegación. Google sale del sistema y vuelve al inicio, así que se guarda
 * en el navegador antes de salir y se retoma al volver (por ejemplo, el QR del
 * análisis detallado del PDF). Si el almacenamiento no está disponible, se
 * vuelve al inicio como antes.
 */
const CLAVE = 'evidentia.destino'

/** Guarda la pantalla de destino; solo direcciones internas. */
export function guardarDestino(destino) {
  try {
    if (destino && destino.startsWith('/') && !destino.startsWith('//')) {
      sessionStorage.setItem(CLAVE, destino)
    } else {
      sessionStorage.removeItem(CLAVE)
    }
  } catch {
    // Sin almacenamiento disponible: se vuelve al inicio.
  }
}

/** Devuelve la pantalla guardada, o null. */
export function leerDestino() {
  try {
    return sessionStorage.getItem(CLAVE)
  } catch {
    return null
  }
}

/** Borra la pantalla guardada, para usarla una sola vez. */
export function olvidarDestino() {
  try {
    sessionStorage.removeItem(CLAVE)
  } catch {
    // Sin almacenamiento disponible: no hay nada que borrar.
  }
}
