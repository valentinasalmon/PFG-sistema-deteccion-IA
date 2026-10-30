/**
 * Pantalla para direcciones que no existen.
 *
 * Desde la funcionalidad 034 lleva una ilustración y dos salidas: volver a la
 * pantalla anterior o ir al inicio.
 */
import { Link, useNavigate } from 'react-router'
import EstadoVacio from '../componentes/EstadoVacio.jsx'
import { IlustracionRoto } from '../componentes/Ilustraciones.jsx'

export default function PaginaNoEncontrada() {
  const navegar = useNavigate()
  return (
    <EstadoVacio
      Ilustracion={IlustracionRoto}
      titulo="Página no encontrada"
      texto="La dirección que abriste no existe o cambió."
      encabezado
    >
      <button type="button" className="boton boton--secundario" onClick={() => navegar(-1)}>
        Volver
      </button>
      <Link to="/" className="boton">
        Ir al inicio
      </Link>
    </EstadoVacio>
  )
}
