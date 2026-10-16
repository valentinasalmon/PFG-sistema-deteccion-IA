/**
 * Indicador de carga con texto, para que también lo perciban los lectores de pantalla.
 */
export default function Cargando({ texto = 'Cargando…' }) {
  return (
    <p className="cargando" role="status">
      {texto}
    </p>
  )
}
