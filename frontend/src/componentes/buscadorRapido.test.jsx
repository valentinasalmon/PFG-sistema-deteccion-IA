/**
 * Pruebas del buscador «Buscar o ir a…» con Ctrl K (funcionalidad 034, CA7).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const PANEL = {
  por_estado: { borrador: 1 },
  recientes: [],
  analisis_en_curso: [],
  compartidos: [],
  invitaciones: [],
  transferencias: [],
  proximos_a_destruir: [],
  actividad: [],
}

const CASO = { id: 7, numero: 'CASO-2026-000007', lugar: 'Av. Corrientes 1234', estado_nombre: 'Borrador' }

function api() {
  return simularApi({
    ...CON_SESION,
    'GET /api/panel': { cuerpo: { panel: PANEL } },
    'GET /api/casos?busqueda=cas': { cuerpo: { casos: [CASO], total: 1, pagina: 1, paginas: 1 } },
    'GET /api/casos': { cuerpo: { casos: [CASO], total: 1, pagina: 1, paginas: 1 } },
    'GET /api/casos/transferencias': { cuerpo: { transferencias: [] } },
    'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
  })
}

describe('buscador rápido', () => {
  it('se abre con Ctrl K, muestra los atajos y se cierra con Esc', async () => {
    api()
    const { usuario } = renderizarEn('/')
    await screen.findByRole('heading', { name: /Hola/ })

    await usuario.keyboard('{Control>}k{/Control}')
    const dialogo = screen.getByRole('dialog', { name: 'Buscar o ir a…' })
    expect(within(dialogo).getByRole('combobox')).toHaveFocus()
    const opciones = within(dialogo).getAllByRole('option').map((o) => o.textContent)
    expect(opciones.join('|')).toMatch(/Nuevo caso.*Inicio.*Casos.*Mi perfil/)

    await usuario.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('filtra los atajos y abre el elegido con Enter', async () => {
    api()
    const { usuario } = renderizarEn('/')
    await screen.findByRole('heading', { name: /Hola/ })

    await usuario.click(screen.getByRole('button', { name: /Buscar o ir a/ }))
    await usuario.type(screen.getByRole('combobox'), 'perf')
    const opciones = screen.getAllByRole('option')
    expect(opciones).toHaveLength(1)
    expect(opciones[0]).toHaveAttribute('aria-selected', 'true')
    await usuario.keyboard('{Enter}')

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: 'Mi perfil', level: 1 })).toBeInTheDocument()
  })

  it('busca entre los casos y se mueve con las flechas', async () => {
    const { solicitudes } = api()
    const { usuario } = renderizarEn('/')
    await screen.findByRole('heading', { name: /Hola/ })

    await usuario.keyboard('{Control>}k{/Control}')
    // «cas» encuentra el caso y también el atajo «Casos».
    await usuario.type(screen.getByRole('combobox'), 'cas')
    const caso = await screen.findByRole('option', { name: /CASO-2026-000007/ })
    expect(caso).toHaveTextContent('Av. Corrientes 1234 · Borrador')
    expect(solicitudes.map((s) => s.ruta)).toContain('/api/casos?busqueda=cas')

    expect(caso).toHaveAttribute('aria-selected', 'true')
    await usuario.keyboard('{ArrowUp}')
    expect(caso).toHaveAttribute('aria-selected', 'false')
    await usuario.keyboard('{ArrowDown}')
    expect(caso).toHaveAttribute('aria-selected', 'true')
  })

  it('avisa cuando nada coincide', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/panel': { cuerpo: { panel: PANEL } },
      'GET /api/casos?busqueda=zzz': { cuerpo: { casos: [], total: 0, pagina: 1, paginas: 1 } },
    })
    const { usuario } = renderizarEn('/')
    await screen.findByRole('heading', { name: /Hola/ })

    await usuario.keyboard('{Control>}k{/Control}')
    await usuario.type(screen.getByRole('combobox'), 'zzz')
    expect(await screen.findByText('Nada coincide con «zzz».')).toBeInTheDocument()
  })
})
