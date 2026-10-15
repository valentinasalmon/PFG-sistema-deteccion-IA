/**
 * Renderiza la aplicación completa (rutas y proveedor de sesión) en una
 * dirección dada, como si se la abriera en el navegador.
 */
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import App from '../App.jsx'
import ProveedorSesion from '../contextos/ProveedorSesion.jsx'

export function renderizarEn(ruta) {
  const usuario = userEvent.setup()
  const resultado = render(
    <MemoryRouter initialEntries={[ruta]}>
      <ProveedorSesion>
        <App />
      </ProveedorSesion>
    </MemoryRouter>,
  )
  return { usuario, ...resultado }
}
