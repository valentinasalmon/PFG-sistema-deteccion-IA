/**
 * Pruebas del menú según quién entra (funcionalidad 028).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const PANEL_VACIO = {
  por_estado: {},
  recientes: [],
  analisis_en_curso: [],
  compartidos: [],
  invitaciones: [],
  transferencias: [],
  proximos_a_destruir: [],
  actividad: [],
}

function conUsuario(datos) {
  return {
    'GET /api/sesion': { cuerpo: { usuario: { ...USUARIO, ...datos } } },
    'GET /api/panel': { cuerpo: { panel: PANEL_VACIO } },
  }
}

function enlacesDelMenu() {
  const menu = screen.getByRole('navigation', { name: 'Principal' })
  return within(menu)
    .getAllByRole('link')
    .map((enlace) => enlace.textContent)
}

describe('menú según el rol', () => {
  it('sin organización no muestra «Organizaciones»', async () => {
    simularApi(conUsuario({ en_organizacion: false }))
    renderizarEn('/')
    await screen.findByRole('heading', { name: /Hola, Ana/ })
    expect(enlacesDelMenu()).toEqual(['Inicio', 'Casos', 'Mi perfil'])
    expect(screen.getByRole('link', { name: /Nuevo caso/ })).toBeInTheDocument()
  })

  it('con organización muestra «Organizaciones»', async () => {
    simularApi(conUsuario({ en_organizacion: true }))
    renderizarEn('/')
    await screen.findByRole('heading', { name: /Hola, Ana/ })
    expect(enlacesDelMenu()).toEqual(['Inicio', 'Casos', 'Organizaciones', 'Mi perfil'])
  })

  it('el abogado sin organización encuentra en Mi perfil cómo crear un estudio', async () => {
    simularApi(conUsuario({ en_organizacion: false }))
    renderizarEn('/perfil')
    expect(await screen.findByRole('heading', { name: 'Trabajo en equipo' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Crear un estudio jurídico/ })).toHaveAttribute(
      'href',
      '/organizaciones/nueva',
    )
  })

  it('con organización, Mi perfil no repite el trabajo en equipo', async () => {
    simularApi(conUsuario({ en_organizacion: true }))
    renderizarEn('/perfil')
    await screen.findByRole('heading', { name: 'Mi perfil' })
    expect(screen.queryByRole('heading', { name: 'Trabajo en equipo' })).not.toBeInTheDocument()
  })
})
