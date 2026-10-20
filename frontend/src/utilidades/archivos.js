/**
 * Utilidades para archivos: tamaño legible y descarga desde un enlace.
 */

/** Tamaño en B, KB o MB con una cifra decimal, al estilo argentino (1,5 MB). */
export function formatearTamanio(bytes) {
  if (bytes < 1024) return `${bytes} B`
  const kilos = bytes / 1024
  if (kilos < 1024) return `${kilos.toLocaleString('es-AR', { maximumFractionDigits: 1 })} KB`
  return `${(kilos / 1024).toLocaleString('es-AR', { maximumFractionDigits: 1 })} MB`
}

/** Abre un enlace de descarga (el servidor responde con el archivo adjunto). */
export function abrirDescarga(url) {
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.rel = 'noopener'
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
}
