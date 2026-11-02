/**
 * Pruebas de la portada pública (funcionalidades 033 y 034).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const BASE = { analisis_mes: 100, imagenes_por_caso: 50, precio: null }
const PLANES = {
  'GET /api/catalogos/planes': {
    cuerpo: {
      planes: [
        { codigo: 'basico', nombre: 'Organización Básico', miembros: 5, almacenamiento_gb: 20, ...BASE },
        {
          codigo: 'profesional',
          nombre: 'Organización Profesional',
          miembros: 25,
          almacenamiento_gb: 100,
          ...BASE,
        },
      ],
      personal: { nombre: 'Personal', analisis_mes: 10, imagenes_por_caso: 20 },
    },
  },
}

describe('portada pública', () => {
  it('sin sesión, la raíz muestra la portada con sus secciones (CA1, CA4)', async () => {
    simularApi(PLANES)
    renderizarEn('/')
    expect(
      await screen.findByRole('heading', { level: 1, name: /Esa foto es real\? Sabelo en minutos/ }),
    ).toBeInTheDocument()
    for (const titulo of [
      /Cuatro miradas sobre cada foto/,
      /Para abogados y estudios/,
      /Para aseguradoras/,
      /Empezá en tres pasos/,
      /Empezá gratis y sumá a tu equipo/,
    ]) {
      expect(screen.getByRole('heading', { level: 2, name: titulo })).toBeInTheDocument()
    }
    expect(screen.getByText(/no emite veredictos/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Iniciar sesión' })).toHaveAttribute('href', '/iniciar-sesion')
    // La portada habla de beneficios: no nombra proveedores ni la infraestructura.
    expect(document.body.textContent).not.toMatch(/AWS|Hedera|SHA-256|Irlanda/)
    expect(screen.getByRole('link', { name: /Registrar mi aseguradora/ })).toHaveAttribute(
      'href',
      '/registro?tipo=aseguradora',
    )
  })

  it('con sesión, la raíz sigue siendo el Inicio (CA1)', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/panel': { cuerpo: { contadores: {}, actividad: [], casos: [] } },
    })
    renderizarEn('/')
    expect(await screen.findByRole('heading', { name: 'Hola, Ana' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /Empezá gratis y sumá/ })).not.toBeInTheDocument()
  })

  it('los planes llevan al registro con el camino y el plan elegidos (CA2, CA3)', async () => {
    simularApi({ ...CON_SESION, ...PLANES })
    const { usuario } = renderizarEn('/presentacion')
    const planes = (await screen.findByRole('heading', { name: /Empezá gratis y sumá/ })).closest('section')

    expect(await within(planes).findByText('Hasta 25 miembros')).toBeInTheDocument()
    expect(within(planes).getAllByText('A confirmar')).toHaveLength(2)
    expect(within(planes).getByRole('link', { name: 'Crear cuenta gratis' })).toHaveAttribute(
      'href',
      '/registro?tipo=independiente',
    )
    expect(within(planes).getByRole('link', { name: /Elegir Profesional/ })).toHaveAttribute(
      'href',
      '/registro?tipo=estudio&plan=profesional',
    )

    await usuario.click(within(planes).getByRole('radio', { name: 'Aseguradora' }))
    expect(within(planes).getByRole('link', { name: /Elegir Básico/ })).toHaveAttribute(
      'href',
      '/registro?tipo=aseguradora&plan=basico',
    )
    // Con sesión, la presentación ofrece volver a la cuenta.
    expect(screen.getByRole('link', { name: 'Ir a mi cuenta' })).toHaveAttribute('href', '/')
  })

  it('si los planes no cargan, igual se pueden elegir', async () => {
    simularApi({ 'GET /api/catalogos/planes': { estado: 500, cuerpo: { mensaje: 'Error.' } } })
    renderizarEn('/')
    expect(await screen.findByRole('link', { name: /Elegir Profesional/ })).toHaveAttribute(
      'href',
      '/registro?tipo=estudio&plan=profesional',
    )
  })
})
