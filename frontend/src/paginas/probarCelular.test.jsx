import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import PaginaProbarCelular from './PaginaProbarCelular.jsx'
import { diagnosticarFoto } from '../api/diagnostico.js'

vi.mock('../api/diagnostico.js', () => ({ diagnosticarFoto: vi.fn() }))

describe('Probar mi celular (047)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('ofrece los tres caminos para elegir una foto', () => {
    render(<PaginaProbarCelular />)
    expect(screen.getByText('Desde la galería')).toBeInTheDocument()
    expect(screen.getByText('Sacando una foto')).toBeInTheDocument()
    expect(screen.getByText('Desde Archivos')).toBeInTheDocument()
  })

  it('muestra qué llegó al servidor', async () => {
    diagnosticarFoto.mockResolvedValue({
      formato: 'JPEG', metadatos_leidos: true, campos_exif: 0, marca: null, modelo: null,
      fecha_captura: null, tiene_ubicacion: false,
      dispositivo: { sistema: 'iPhone o iPad (iOS 18.1)', navegador: 'Safari' },
    })
    render(<PaginaProbarCelular />)
    const archivo = new File(['x'], 'foto.jpg', { type: 'image/jpeg' })
    await userEvent.upload(screen.getByLabelText('Desde la galería'), archivo)
    await waitFor(() => expect(screen.getByLabelText('Resultado: Desde la galería')).toBeInTheDocument())
    expect(screen.getByText('0 campos')).toBeInTheDocument()
    expect(screen.getByText(/iOS 18\.1/)).toBeInTheDocument()
  })

  it('muestra el error si la foto no se pudo leer', async () => {
    diagnosticarFoto.mockRejectedValue({ mensaje: 'El archivo no es una imagen JPEG, PNG o HEIC.' })
    render(<PaginaProbarCelular />)
    await userEvent.upload(screen.getByLabelText('Desde Archivos'), new File(['x'], 'a.jpg', { type: 'image/jpeg' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('no es una imagen')
  })
})
