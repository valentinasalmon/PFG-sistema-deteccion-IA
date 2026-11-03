/**
 * Pruebas de la página de estado del sistema (CA4 y CA5 de la funcionalidad 001).
 * La API se simula reemplazando la función global fetch.
 */
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import PaginaEstado from './PaginaEstado.jsx'

/** Simula una respuesta de fetch con el estado y el cuerpo indicados. */
function simularRespuesta(status, cuerpo) {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ status, json: async () => cuerpo }))
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('PaginaEstado', () => {
  it('muestra que la API está conectada cuando todo funciona (CA4)', async () => {
    simularRespuesta(200, {
      estado: 'ok',
      componentes: { api: 'ok', base_de_datos: 'ok', redis: 'ok' },
      entorno: 'desarrollo',
      version: '0.1.0',
    })
    render(<PaginaEstado />)
    expect(await screen.findByText(/API conectada: todos los servicios funcionan/)).toBeInTheDocument()
    expect(screen.getByText('Base de datos')).toBeInTheDocument()
  })

  it('muestra el estado del sello en Hedera y el último confirmado', async () => {
    simularRespuesta(200, {
      estado: 'ok',
      componentes: { api: 'ok' },
      entorno: 'produccion',
      version: '1.0.0',
      sello: { modo: 'hedera', red: 'testnet', estado: 'ok', ultimo: '2026-10-30T12:00:00' },
    })
    render(<PaginaEstado />)
    expect(await screen.findByText('Sello de tiempo · Hedera (testnet)')).toBeInTheDocument()
    expect(screen.getByText(/Último confirmado el/)).toBeInTheDocument()
  })

  it('avisa si hay sellos que no se pudieron registrar', async () => {
    simularRespuesta(200, {
      estado: 'ok',
      componentes: { api: 'ok' },
      entorno: 'produccion',
      version: '1.0.0',
      sello: { modo: 'hedera', red: 'mainnet', estado: 'con_fallas', ultimo: null },
    })
    render(<PaginaEstado />)
    expect(await screen.findByText(/Con fallas/)).toBeInTheDocument()
  })

  it('indica qué servicio no responde (CA4)', async () => {
    simularRespuesta(503, {
      estado: 'degradado',
      componentes: { api: 'ok', base_de_datos: 'error', redis: 'ok' },
      entorno: 'desarrollo',
      version: '0.1.0',
    })
    render(<PaginaEstado />)
    expect(await screen.findByText(/hay servicios que no responden/)).toBeInTheDocument()
    expect(screen.getByText('No responde')).toBeInTheDocument()
  })

  it('muestra un mensaje claro si la API no responde (CA5)', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    render(<PaginaEstado />)
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con la API.')
  })

  it('trata como error una respuesta inesperada de la API', async () => {
    simularRespuesta(500, {})
    render(<PaginaEstado />)
    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})
