/**
 * Acceso al endpoint de salud del backend.
 *
 * La carpeta src/api es el único lugar del frontend que conoce las URL de la API.
 *
 * Realiza: CA4 y CA5 de la funcionalidad 001.
 */

/**
 * Consulta GET /api/salud.
 *
 * El backend responde 200 si todo funciona y 503 si algún componente falla;
 * en ambos casos el cuerpo trae el detalle, por eso no se descarta el 503.
 *
 * @returns {Promise<{estado: string, componentes: Object<string, string>, entorno: string, version: string}>}
 * @throws {Error} si la API no responde o devuelve una respuesta inesperada.
 */
export async function obtenerSalud() {
  const respuesta = await fetch('/api/salud')
  if (respuesta.status !== 200 && respuesta.status !== 503) {
    throw new Error(`Respuesta inesperada de la API: ${respuesta.status}`)
  }
  return respuesta.json()
}
