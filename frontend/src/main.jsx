/**
 * Punto de entrada del frontend: monta la aplicación React en el elemento #raiz
 * con el enrutador y el proveedor de la sesión.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import App from './App.jsx'
import ProveedorSesion from './contextos/ProveedorSesion.jsx'
import './estilos/global.css'

createRoot(document.getElementById('raiz')).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorSesion>
        <App />
      </ProveedorSesion>
    </BrowserRouter>
  </StrictMode>,
)
