/**
 * Pruebas de la página inicial (CA4 y CA5 de la funcionalidad 001).
 * La API se simula reemplazando la función global fetch.
 */
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import PaginaInicio from './PaginaInicio.jsx'

/** Simula una respuesta de fetch con el estado y el cuerpo indicados. */
function simularRespuesta(status, cuerpo) {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ status, json: async () => cuerpo }))
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('PaginaInicio', () => {
  it('muestra que la API está conectada cuando todo funciona (CA4)', async () => {
    simularRespuesta(200, {
      estado: 'ok',
      componentes: { api: 'ok', base_de_datos: 'ok', redis: 'ok' },
      entorno: 'desarrollo',
      version: '0.1.0',
    })
    render(<PaginaInicio />)
    expect(await screen.findByText(/API conectada: todos los servicios funcionan/)).toBeInTheDocument()
    expect(screen.getByText('Base de datos')).toBeInTheDocument()
  })

  it('indica qué servicio no responde (CA4)', async () => {
    simularRespuesta(503, {
      estado: 'degradado',
      componentes: { api: 'ok', base_de_datos: 'error', redis: 'ok' },
      entorno: 'desarrollo',
      version: '0.1.0',
    })
    render(<PaginaInicio />)
    expect(await screen.findByText(/hay servicios que no responden/)).toBeInTheDocument()
    expect(screen.getByText('No responde')).toBeInTheDocument()
  })

  it('muestra un mensaje claro si la API no responde (CA5)', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    render(<PaginaInicio />)
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con la API.')
  })

  it('trata como error una respuesta inesperada de la API', async () => {
    simularRespuesta(500, {})
    render(<PaginaInicio />)
    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})
