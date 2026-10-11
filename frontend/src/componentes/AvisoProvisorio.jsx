/**
 * Aclaración que acompaña a los textos legales hasta su validación definitiva.
 */
import { VERSION_DOCUMENTOS_LEGALES } from '../utilidades/legales.js'

export default function AvisoProvisorio() {
  return (
    <p className="nota">
      Versión {VERSION_DOCUMENTOS_LEGALES} · Texto provisorio, pendiente de revisión legal.
    </p>
  )
}
