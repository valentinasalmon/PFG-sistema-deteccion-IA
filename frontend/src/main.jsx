/**
 * Punto de entrada del frontend: monta la aplicación React en el elemento #raiz.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import PaginaInicio from './paginas/PaginaInicio.jsx'
import './estilos/global.css'

createRoot(document.getElementById('raiz')).render(
  <StrictMode>
    <PaginaInicio />
  </StrictMode>,
)
