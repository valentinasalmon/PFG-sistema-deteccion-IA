/**
 * Pruebas de las páginas de Términos de Uso, Política de Privacidad y página
 * no encontrada (RF01 CA2 y RNF08 de la funcionalidad 002).
 */
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it } from 'vitest'
import PaginaNoEncontrada from './PaginaNoEncontrada.jsx'
import PaginaPrivacidad from './PaginaPrivacidad.jsx'
import PaginaTerminos from './PaginaTerminos.jsx'

afterEach(() => {
  cleanup()
})

describe('textos legales', () => {
  it('los Términos de Uso muestran la versión y aclaran que no hay veredictos (RN27)', () => {
    render(<PaginaTerminos />)
    expect(screen.getByRole('heading', { level: 1, name: 'Términos de Uso' })).toBeInTheDocument()
    expect(screen.getByText(/Versión 1.0/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /no veredictos/ })).toBeInTheDocument()
  })

  it('la Política de Privacidad informa la retención y la Ley 25.326', () => {
    render(<PaginaPrivacidad />)
    expect(screen.getByRole('heading', { level: 1, name: 'Política de Privacidad' })).toBeInTheDocument()
    expect(screen.getByText(/dos años/)).toBeInTheDocument()
    expect(screen.getByText(/25.326/)).toBeInTheDocument()
  })
})

describe('PaginaNoEncontrada', () => {
  it('ofrece volver al inicio', () => {
    render(
      <MemoryRouter>
        <PaginaNoEncontrada />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Página no encontrada' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Ir al inicio' })).toHaveAttribute('href', '/')
  })
})
