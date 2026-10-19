/**
 * Pantalla para direcciones que no existen.
 */
import { Link } from 'react-router'

export default function PaginaNoEncontrada() {
  return (
    <>
      <h1>Página no encontrada</h1>
      <p>La dirección que abriste no existe o cambió.</p>
      <Link to="/" className="boton">
        Ir al inicio
      </Link>
    </>
  )
}
