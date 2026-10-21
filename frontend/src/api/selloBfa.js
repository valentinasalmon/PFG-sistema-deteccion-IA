/**
 * Pedidos al servicio de sello de tiempo de Blockchain Federal Argentina,
 * hechos desde el navegador (funcionalidad 016, modo "navegador").
 *
 * BFA solo acepta conexiones desde Argentina y el servidor de la plataforma
 * está en Irlanda: por eso el sello lo pide el navegador de quien usa la
 * plataforma. Solo viaja la huella SHA-256, nunca la imagen. El servidor
 * valida los recibos que se le pasan contra la huella de cada imagen.
 *
 * Realiza: RF37.
 */

export const URL_BFA = 'https://tsaapi.bfa.ar'

async function enviar(ruta, campos) {
  const respuesta = await fetch(`${URL_BFA}${ruta}`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    body: new URLSearchParams(campos),
  })
  if (!respuesta.ok) throw new Error(`BFA respondió ${respuesta.status}.`)
  return respuesta.json()
}

/** Pide el sello de la huella; devuelve el recibo temporal de BFA. */
export async function sellarEnBfa(huella) {
  const respuesta = await enviar('/api/tsa/stamp/', { file_hash: huella })
  if (respuesta.status !== 'success' || !respuesta.temporary_rd) {
    throw new Error('BFA no devolvió un recibo.')
  }
  return respuesta.temporary_rd
}

/**
 * Consulta si el sello ya está en un bloque.
 *
 * @returns {Promise<{recibo_definitivo: string, fecha: string} | null>} null si sigue pendiente.
 */
export async function verificarEnBfa(huella, recibo) {
  const respuesta = await enviar('/api/tsa/verify/', { file_hash: huella, rd: recibo })
  if (respuesta.status !== 'success' || !respuesta.permanent_rd) return null
  return { recibo_definitivo: respuesta.permanent_rd, fecha: respuesta.attestation_time }
}
