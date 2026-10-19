/**
 * Configuración común de las pruebas con Vitest.
 *
 * - Agrega comparadores como toBeInTheDocument() (Testing Library).
 * - Después de cada prueba desmonta lo renderizado, restaura fetch y olvida
 *   el token CSRF guardado, para que ninguna prueba dependa de otra.
 */
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'
import { configurarAlExpirarSesion, definirTokenCsrf } from '../api/cliente.js'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  definirTokenCsrf(null)
  configurarAlExpirarSesion(null)
})
