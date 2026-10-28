/**
 * Pruebas de la copia de datos y de la eliminación de la cuenta en "Mi perfil"
 * (funcionalidad 019).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const seccion = (titulo) => screen.getByRole('region', { name: titulo })

const SIN_PENDIENTES = { casos: [], referente_de: [], a_eliminar: [], puede_eliminar: true }

describe('copia de datos personales', () => {
  it('genera la copia y ofrece los enlaces de descarga (CA1)', async () => {
    simularApi({
      ...CON_SESION,
      'POST /api/perfil/copia': {
        cuerpo: {
          enlaces: { json: '/api/perfil/copia/json?token=abc', pdf: '/api/perfil/copia/pdf?token=abc' },
          vence_en: '2026-10-19T15:15:00',
          mensaje: 'Tu copia está lista. Los enlaces vencen en 15 minutos.',
        },
      },
    })
    const { usuario } = renderizarEn('/perfil?seccion=privacidad')

    await usuario.click(await screen.findByRole('button', { name: 'Generar mi copia' }))

    const copia = seccion('Copia de tus datos')
    expect(await within(copia).findByText(/Tu copia está lista/)).toBeInTheDocument()
    expect(within(copia).getByRole('link', { name: 'Descargar en PDF' })).toHaveAttribute(
      'href',
      '/api/perfil/copia/pdf?token=abc',
    )
    expect(within(copia).getByRole('link', { name: 'Descargar en JSON' })).toHaveAttribute(
      'href',
      '/api/perfil/copia/json?token=abc',
    )
  })

  it('muestra el error si no se puede generar', async () => {
    simularApi({
      ...CON_SESION,
      'POST /api/perfil/copia': { estado: 500, cuerpo: { mensaje: 'Ocurrió un error inesperado.' } },
    })
    const { usuario } = renderizarEn('/perfil?seccion=privacidad')

    await usuario.click(await screen.findByRole('button', { name: 'Generar mi copia' }))

    expect(await within(seccion('Copia de tus datos')).findByText('Ocurrió un error inesperado.')).toBeInTheDocument()
  })
})

describe('eliminación de la cuenta', () => {
  it('lista lo que falta resolver y no pide la contraseña (CA5, CA6, CA7)', async () => {
    let situacion = {
      casos: [{ id: 7, numero: 'CASO-2026-000007', estado_nombre: 'Borrador', espacio: 'Personal' }],
      referente_de: [{ id: 3, nombre: 'Estudio Pérez' }],
      a_eliminar: [{ id: 4, nombre: 'Estudio Sola', cantidad_casos: 2 }],
      puede_eliminar: false,
    }
    simularApi({ ...CON_SESION, 'GET /api/perfil/baja': () => ({ cuerpo: situacion }) })
    const { usuario } = renderizarEn('/perfil?seccion=privacidad')

    await usuario.click(await screen.findByRole('button', { name: 'Quiero eliminar mi cuenta' }))

    const zona = seccion('Eliminar mi cuenta')
    expect(await within(zona).findByRole('link', { name: 'CASO-2026-000007' })).toHaveAttribute('href', '/casos/7')
    expect(within(zona).getByRole('link', { name: 'Estudio Pérez' })).toHaveAttribute('href', '/organizaciones/3')
    expect(within(zona).getByText(/Estudio Sola \(2 casos\)/)).toBeInTheDocument()
    expect(within(zona).queryByLabelText('Contraseña')).not.toBeInTheDocument()

    situacion = { ...SIN_PENDIENTES, a_eliminar: situacion.a_eliminar }
    await usuario.click(within(zona).getByRole('button', { name: 'Volver a revisar' }))

    expect(await within(zona).findByLabelText('Contraseña')).toBeInTheDocument()
    expect(within(zona).queryByRole('link', { name: 'CASO-2026-000007' })).not.toBeInTheDocument()
  })

  it('con la contraseña correcta elimina la cuenta y vuelve al inicio de sesión (CA9)', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION,
      'GET /api/perfil/baja': { cuerpo: SIN_PENDIENTES },
      'DELETE /api/perfil': { cuerpo: { mensaje: 'Tu cuenta fue eliminada.' } },
    })
    const { usuario } = renderizarEn('/perfil?seccion=privacidad')

    await usuario.click(await screen.findByRole('button', { name: 'Quiero eliminar mi cuenta' }))
    const zona = seccion('Eliminar mi cuenta')
    const boton = await within(zona).findByRole('button', { name: 'Eliminar mi cuenta definitivamente' })
    expect(boton).toBeDisabled()
    await usuario.type(within(zona).getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(boton)

    expect(await screen.findByText(/Tu cuenta fue eliminada. Te enviamos una confirmación/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'DELETE').cuerpo).toEqual({ contrasenia: 'Segura12345' })
  })

  it('con la contraseña incorrecta muestra el error (CA8)', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/perfil/baja': { cuerpo: SIN_PENDIENTES },
      'DELETE /api/perfil': {
        estado: 400,
        cuerpo: { mensaje: 'La contraseña no es correcta.', errores: { contrasenia: 'La contraseña no es correcta.' } },
      },
    })
    const { usuario } = renderizarEn('/perfil?seccion=privacidad')

    await usuario.click(await screen.findByRole('button', { name: 'Quiero eliminar mi cuenta' }))
    const zona = seccion('Eliminar mi cuenta')
    await usuario.type(await within(zona).findByLabelText('Contraseña'), 'Otra')
    await usuario.click(within(zona).getByRole('button', { name: 'Eliminar mi cuenta definitivamente' }))

    expect((await within(zona).findAllByText('La contraseña no es correcta.')).length).toBeGreaterThan(0)
    expect(screen.getByRole('heading', { name: 'Mi perfil' })).toBeInTheDocument()
  })

  it('muestra el error si no puede revisar la situación', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/perfil/baja': { estado: 500, cuerpo: { mensaje: 'Ocurrió un error inesperado.' } },
    })
    const { usuario } = renderizarEn('/perfil?seccion=privacidad')

    await usuario.click(await screen.findByRole('button', { name: 'Quiero eliminar mi cuenta' }))

    expect(await within(seccion('Eliminar mi cuenta')).findByText('Ocurrió un error inesperado.')).toBeInTheDocument()
  })
})
