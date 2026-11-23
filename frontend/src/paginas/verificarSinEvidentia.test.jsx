import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import PaginaVerificarSinEvidentia from './PaginaVerificarSinEvidentia.jsx'
import { obtenerRedPublica } from '../api/informes.js'

vi.mock('../api/informes.js', () => ({ obtenerRedPublica: vi.fn() }))

function mostrar() {
  return render(
    <MemoryRouter>
      <PaginaVerificarSinEvidentia />
    </MemoryRouter>,
  )
}

describe('Verificar sin evidentIA (048)', () => {
  it('explica cómo calcular la huella en cada sistema', async () => {
    obtenerRedPublica.mockResolvedValue(null)
    mostrar()
    expect(screen.getByText('certutil -hashfile informe.pdf SHA256')).toBeInTheDocument()
    expect(screen.getByText('shasum -a 256 informe.pdf')).toBeInTheDocument()
    expect(screen.getByText('sha256sum informe.pdf')).toBeInTheDocument()
    expect(await screen.findByText(/recuadro «Verificar sin evidentIA»/)).toBeInTheDocument()
  })

  it('enlaza el tema público de Hedera cuando hay sello real', async () => {
    obtenerRedPublica.mockResolvedValue({
      red: 'testnet', tema: '0.0.123', enlace_tema: 'https://hashscan.io/testnet/topic/0.0.123',
    })
    mostrar()
    const enlace = await screen.findByRole('link', { name: 'Abrir el tema en HashScan' })
    expect(enlace).toHaveAttribute('href', 'https://hashscan.io/testnet/topic/0.0.123')
    expect(screen.getByText('0.0.123')).toBeInTheDocument()
  })
})
