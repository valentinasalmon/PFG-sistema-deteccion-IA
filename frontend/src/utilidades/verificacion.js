/**
 * Utilidades de la verificación pública de informes (funcionalidad 026).
 *
 * La huella SHA-256 del PDF se calcula en el navegador con Web Crypto: el
 * archivo nunca se sube al servidor.
 *
 * Realiza: RF55 (CA3).
 */

/** Código de verificación en grupos de cuatro, como se imprime en el PDF. */
export function codigoLegible(codigo) {
  return (codigo ?? '').match(/.{1,4}/g)?.join('-') ?? ''
}

function leerArchivo(archivo) {
  if (archivo.arrayBuffer) return archivo.arrayBuffer()
  return new Promise((resolver, rechazar) => {
    const lector = new FileReader()
    lector.onload = () => resolver(lector.result)
    lector.onerror = () => rechazar(lector.error)
    lector.readAsArrayBuffer(archivo)
  })
}

/** Huella SHA-256 de un archivo, en hexadecimal minúsculo. */
export async function huellaDeArchivo(archivo) {
  const resumen = await crypto.subtle.digest('SHA-256', await leerArchivo(archivo))
  return Array.from(new Uint8Array(resumen), (octeto) => octeto.toString(16).padStart(2, '0')).join('')
}
