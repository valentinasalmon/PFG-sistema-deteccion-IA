/**
 * Punto de entrada del frontend: monta la aplicación React en el elemento #raiz
 * con el enrutador y el proveedor de la sesión.
 *
 * Si la compilación trae el identificador de Microsoft Clarity, lo carga con
 * todo el contenido enmascarado (034, CA8).
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import App from './App.jsx'
import ProveedorSesion from './contextos/ProveedorSesion.jsx'
import '@fontsource-variable/sora'
import '@fontsource-variable/figtree'
import './estilos/global.css'
import { iniciarClarity } from './utilidades/clarity.js'

iniciarClarity()

createRoot(document.getElementById('raiz')).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorSesion>
        <App />
      </ProveedorSesion>
    </BrowserRouter>
  </StrictMode>,
)
