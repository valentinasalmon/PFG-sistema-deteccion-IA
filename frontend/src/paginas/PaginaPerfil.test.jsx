/**
 * Pruebas de la pantalla "Mi perfil" (CA16 a CA19 de la funcionalidad 002).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'


describe('PaginaPerfil', () => {
  it('muestra el perfil sin permitir modificarlo (CA19)', async () => {
    simularApi(CON_SESION)
    renderizarEn('/perfil')
    const datos = await screen.findByRole('region', { name: 'Datos personales' })
    expect(within(datos).getByText('Abogado o abogada')).toBeInTheDocument()
    expect(within(datos).getByText(/no puede modificarse/)).toBeInTheDocument()
    expect(within(datos).queryByRole('radio')).not.toBeInTheDocument()
  })

  it('guarda nombre, apellido y colegio y actualiza el encabezado (CA17)', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION,
      'PATCH /api/perfil': (cuerpo) => ({ cuerpo: { usuario: { ...USUARIO, ...cuerpo } } }),
    })
    const { usuario } = renderizarEn('/perfil')
    const nombre = await screen.findByLabelText('Nombre')
    await usuario.clear(nombre)
    await usuario.type(nombre, 'Ana María')
    await usuario.click(screen.getByRole('button', { name: 'Guardar los datos' }))

    expect(await screen.findByText('Tus datos fueron actualizados.')).toBeInTheDocument()
    expect(screen.getAllByText('Ana María López').length).toBeGreaterThan(0)
    expect(solicitudes.at(-1).cuerpo).toEqual({ nombre: 'Ana María', apellido: 'López', colegio: 'CPACF' })
  })

  it('para una aseguradora edita la empresa', async () => {
    simularApi({
      'GET /api/sesion': {
        cuerpo: { usuario: { ...USUARIO, perfil: 'aseguradora', colegio: undefined, empresa: 'Seguros SA' } },
      },
    })
    renderizarEn('/perfil')
    expect(await screen.findByLabelText(/Empresa/)).toHaveValue('Seguros SA')
    expect(screen.queryByLabelText(/Colegio/)).not.toBeInTheDocument()
  })

  it('cambia la contraseña y limpia el formulario (CA16)', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION,
      'POST /api/perfil/contrasenia': { cuerpo: { mensaje: 'Tu contraseña fue actualizada.' } },
    })
    const { usuario } = renderizarEn('/perfil')
    await usuario.type(await screen.findByLabelText('Contraseña actual'), 'Segura12345')
    await usuario.type(screen.getByLabelText('Contraseña nueva'), 'OtraClave2026')
    await usuario.type(screen.getByLabelText('Repetí la contraseña nueva'), 'OtraClave2026')
    await usuario.click(screen.getByRole('button', { name: 'Cambiar la contraseña' }))

    expect(await screen.findByText(/Cerramos las sesiones abiertas/)).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña actual')).toHaveValue('')
    expect(solicitudes.at(-1).cuerpo).toEqual({
      contrasenia_actual: 'Segura12345',
      contrasenia_nueva: 'OtraClave2026',
    })
  })

  it('con la contraseña actual incorrecta muestra el error en ese campo (CA16)', async () => {
    simularApi({
      ...CON_SESION,
      'POST /api/perfil/contrasenia': {
        estado: 400,
        cuerpo: {
          mensaje: 'La contraseña actual no es correcta.',
          errores: { contrasenia_actual: 'La contraseña actual no es correcta.' },
        },
      },
    })
    const { usuario } = renderizarEn('/perfil')
    await usuario.type(await screen.findByLabelText('Contraseña actual'), 'Incorrecta123')
    await usuario.type(screen.getByLabelText('Contraseña nueva'), 'OtraClave2026')
    await usuario.type(screen.getByLabelText('Repetí la contraseña nueva'), 'OtraClave2026')
    await usuario.click(screen.getByRole('button', { name: 'Cambiar la contraseña' }))
    expect(await screen.findByLabelText('Contraseña actual')).toHaveAttribute('aria-invalid', 'true')
  })

  it('avisa si la contraseña nueva y su repetición no coinciden', async () => {
    simularApi(CON_SESION)
    const { usuario } = renderizarEn('/perfil')
    await usuario.type(await screen.findByLabelText('Contraseña actual'), 'Segura12345')
    await usuario.type(screen.getByLabelText('Contraseña nueva'), 'OtraClave2026')
    await usuario.type(screen.getByLabelText('Repetí la contraseña nueva'), 'Distinta2026')
    await usuario.click(screen.getByRole('button', { name: 'Cambiar la contraseña' }))
    expect(await screen.findByText('Las contraseñas no coinciden.')).toBeInTheDocument()
  })

  it('pide el cambio de correo con la contraseña (CA18)', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION,
      'POST /api/perfil/correo': {
        cuerpo: { mensaje: 'Te enviamos un enlace al correo nuevo para confirmar el cambio.' },
      },
    })
    const { usuario } = renderizarEn('/perfil')
    const correo = await screen.findByRole('region', { name: 'Correo electrónico' })
    await usuario.type(within(correo).getByLabelText('Correo nuevo'), 'nuevo@ejemplo.com')
    await usuario.type(within(correo).getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(within(correo).getByRole('button', { name: 'Cambiar el correo' }))

    expect(await within(correo).findByText(/seguís ingresando con tu correo actual/)).toBeInTheDocument()
    expect(solicitudes.at(-1).cuerpo).toEqual({ correo_nuevo: 'nuevo@ejemplo.com', contrasenia: 'Segura12345' })
  })

  it('informa si el correo nuevo ya está en uso', async () => {
    simularApi({
      ...CON_SESION,
      'POST /api/perfil/correo': {
        estado: 409,
        cuerpo: { mensaje: 'Ese correo ya está en uso.', errores: { correo_nuevo: 'Ese correo ya está en uso.' } },
      },
    })
    const { usuario } = renderizarEn('/perfil')
    const correo = await screen.findByRole('region', { name: 'Correo electrónico' })
    await usuario.type(within(correo).getByLabelText('Correo nuevo'), 'beto@ejemplo.com')
    await usuario.type(within(correo).getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(within(correo).getByRole('button', { name: 'Cambiar el correo' }))
    expect(await within(correo).findByRole('alert')).toHaveTextContent('Ese correo ya está en uso.')
  })
})
