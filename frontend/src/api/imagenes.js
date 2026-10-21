/**
 * Operaciones sobre las imágenes de un caso (funcionalidad 006).
 *
 * Realiza: RF34 a RF36.
 */
import { solicitar } from './cliente.js'

const base = (idCaso) => `/api/casos/${idCaso}/imagenes`

/** Imágenes del caso con su vista previa, el límite del plan y si se pueden modificar (RF35). */
export function listarImagenes(idCaso) {
  return solicitar('GET', base(idCaso))
}

/** Carga un archivo; cada archivo va en su propia solicitud (RF34 CA5). */
export function cargarImagen(idCaso, archivo) {
  const formulario = new FormData()
  formulario.append('archivo', archivo)
  return solicitar('POST', base(idCaso), formulario)
}

/** Enlace firmado de corta duración para descargar el original (RF35 CA2). */
export async function enlaceDeDescarga(idCaso, idImagen) {
  const { url } = await solicitar('GET', `${base(idCaso)}/${idImagen}/descarga`)
  return url
}

/** Elimina la imagen y sus archivos (RF36). */
export function eliminarImagen(idCaso, idImagen) {
  return solicitar('DELETE', `${base(idCaso)}/${idImagen}`)
}

/** Guarda en el servidor un recibo de BFA obtenido por el navegador (RF37, funcionalidad 016). */
export function registrarSello(idCaso, idImagen, datos) {
  return solicitar('POST', `${base(idCaso)}/${idImagen}/sello`, datos)
}
