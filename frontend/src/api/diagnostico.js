/**
 * Diagnóstico de qué llega al subir una foto (funcionalidad 047).
 */
import { solicitar } from './cliente.js'

/** Sube la foto a la página de prueba y devuelve lo que llegó al servidor. */
export async function diagnosticarFoto(archivo) {
  const formulario = new FormData()
  formulario.append('foto', archivo)
  const { diagnostico } = await solicitar('POST', '/api/diagnostico/foto', formulario)
  return diagnostico
}
