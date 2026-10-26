/**
 * Pruebas de la página pública "Verificar un informe" (funcionalidad 026).
 */
import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { simularApi } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'
import { huellaDeArchivo } from '../utilidades/verificacion.js'

const CONTENIDO = new TextEncoder().encode('%PDF-1.7 informe de prueba')

function pdf(contenido = CONTENIDO) {
  return new File([contenido], 'informe.pdf', { type: 'application/pdf' })
}

async function informeCon(huella) {
  return {
    generado_en: '2026-10-26T18:00:00',
    huella,
    sello: {
      estado: 'sellado',
      referencia: 'Hedera testnet · tema 0.0.2002 · mensaje 9',
      fecha: '2026-10-26T18:00:05',
      simulado: false,
      enlace: 'https://hashscan.io/testnet/topic/0.0.2002/message/9',
    },
    version: {
      numero: '0.3.0',
      commit: 'abc1234',
      huella: 'b'.repeat(64),
      sello: {
        estado: 'sellado',
        simulado: false,
        enlace: 'https://hashscan.io/testnet/topic/0.0.2002/message/3',
      },
    },
  }
}

describe('verificar un informe (RF55 CA3)', () => {
  it('con el código del QR, el PDF original coincide y uno modificado no', async () => {
    const huella = await huellaDeArchivo(pdf())
    simularApi({
      'GET /api/verificacion?codigo=ABCDEFGHJKMN': { cuerpo: { informe: await informeCon(huella) } },
    })
    const { usuario } = renderizarEn('/verificar/ABCDEFGHJKMN')

    expect(await screen.findByText(huella)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Verificar en HashScan' })).toHaveAttribute(
      'href',
      'https://hashscan.io/testnet/topic/0.0.2002/message/9',
    )
    expect(screen.getByText(/Analizado con evidentIA 0.3.0 \(código abc1234\)/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Ver la versión en HashScan' })).toBeInTheDocument()
    const campo = screen.getByLabelText('Elegir el PDF para comprobarlo')
    await usuario.upload(campo, pdf())
    expect(await screen.findByText('El PDF coincide con el registrado.')).toBeInTheDocument()

    await usuario.upload(campo, pdf(new TextEncoder().encode('%PDF-1.7 informe cambiado')))
    expect(await screen.findByText('El PDF no coincide.')).toBeInTheDocument()
  })

  it('sin código, busca el informe por la huella del archivo', async () => {
    const huella = await huellaDeArchivo(pdf())
    const { solicitudes } = simularApi({
      [`GET /api/verificacion?huella=${huella}`]: { cuerpo: { informe: await informeCon(huella) } },
    })
    const { usuario } = renderizarEn('/verificar')

    await usuario.upload(await screen.findByLabelText('Elegir el PDF para comprobarlo'), pdf())

    expect(await screen.findByText('El PDF coincide con el registrado.')).toBeInTheDocument()
    expect(solicitudes.some((s) => s.ruta.includes(huella))).toBe(true)
  })

  it('avisa si el PDF no es de la plataforma', async () => {
    const huella = await huellaDeArchivo(pdf())
    simularApi({
      [`GET /api/verificacion?huella=${huella}`]: {
        estado: 404,
        cuerpo: { codigo: 'informe_no_encontrado', mensaje: 'No hay ningún informe.' },
      },
    })
    const { usuario } = renderizarEn('/verificar')

    await usuario.upload(await screen.findByLabelText('Elegir el PDF para comprobarlo'), pdf())

    expect(await screen.findByText('No encontramos este PDF.')).toBeInTheDocument()
  })
})
