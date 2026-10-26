/**
 * Pruebas de las pantallas a las que llevan los enlaces enviados por correo y
 * de la recuperación de la contraseña (CA6, CA13 a CA15 y CA18 de la
 * funcionalidad 002).
 */
import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const ENLACE_USADO = {
  estado: 400,
  cuerpo: { codigo: 'enlace_invalido', mensaje: 'Este enlace ya fue utilizado o no es válido. Solicitá uno nuevo.' },
}

describe('verificación del correo', () => {
  it('envía el token una sola vez y confirma la cuenta (CA6)', async () => {
    const { solicitudes } = simularApi({ 'POST /api/cuentas/verificacion': { cuerpo: { mensaje: 'ok' } } })
    renderizarEn('/verificar-correo?token=abc')
    expect(await screen.findByText(/Tu correo fue verificado/)).toBeInTheDocument()
    const envios = solicitudes.filter((s) => s.ruta === '/api/cuentas/verificacion')
    expect(envios).toHaveLength(1)
    expect(envios[0].cuerpo).toEqual({ token: 'abc' })
  })

  it('si el enlace venció informa el motivo y ofrece reenviarlo (CA6)', async () => {
    simularApi({
      'POST /api/cuentas/verificacion': {
        estado: 400,
        cuerpo: { codigo: 'enlace_invalido', mensaje: 'El enlace venció. Solicitá uno nuevo.' },
      },
    })
    renderizarEn('/verificar-correo?token=viejo')
    expect(await screen.findByRole('alert')).toHaveTextContent('El enlace venció.')
    expect(screen.getByRole('button', { name: 'Reenviar el correo de verificación' })).toBeInTheDocument()
  })
})

describe('recuperación de la contraseña', () => {
  it('muestra el mensaje genérico del backend (CA13)', async () => {
    const { solicitudes } = simularApi({
      'POST /api/cuentas/recuperacion': {
        cuerpo: { mensaje: 'Si el correo corresponde a una cuenta, te enviamos un mensaje.' },
      },
    })
    const { usuario } = renderizarEn('/recuperar-contrasenia')
    await usuario.type(await screen.findByLabelText('Correo electrónico'), 'ana@ejemplo.com')
    await usuario.click(screen.getByRole('button', { name: 'Enviar el enlace' }))
    expect(await screen.findByText(/Si el correo corresponde/)).toBeInTheDocument()
    expect(screen.getByText(/vence en 1 hora/)).toBeInTheDocument()
    expect(solicitudes.at(-1).cuerpo).toEqual({ correo: 'ana@ejemplo.com' })
  })

  it('informa un correo con formato inválido', async () => {
    simularApi({
      'POST /api/cuentas/recuperacion': {
        estado: 400,
        cuerpo: { mensaje: 'Revisá los datos marcados.', errores: { correo: 'El correo electrónico no es válido.' } },
      },
    })
    const { usuario } = renderizarEn('/recuperar-contrasenia')
    await usuario.type(await screen.findByLabelText('Correo electrónico'), 'ana')
    await usuario.click(screen.getByRole('button', { name: 'Enviar el enlace' }))
    expect(await screen.findByText('El correo electrónico no es válido.')).toBeInTheDocument()
  })
})

describe('restablecimiento de la contraseña', () => {
  async function completar(usuario, nueva, confirmacion = nueva) {
    await usuario.type(await screen.findByLabelText('Contraseña nueva'), nueva)
    await usuario.type(screen.getByLabelText('Repetí la contraseña nueva'), confirmacion)
    await usuario.click(screen.getByRole('button', { name: 'Guardar la contraseña' }))
  }

  it('define la contraseña nueva con el token del enlace (CA14)', async () => {
    const { solicitudes } = simularApi({
      'POST /api/cuentas/recuperacion/restablecer': { cuerpo: { mensaje: 'Tu contraseña fue actualizada.' } },
    })
    const { usuario } = renderizarEn('/restablecer-contrasenia?token=xyz')
    await completar(usuario, 'OtraClave2026')
    expect(await screen.findByRole('heading', { name: 'Contraseña actualizada' })).toBeInTheDocument()
    expect(screen.getByText(/cerramos las sesiones/)).toBeInTheDocument()
    expect(solicitudes.at(-1).cuerpo).toEqual({ token: 'xyz', contrasenia: 'OtraClave2026' })
  })

  it('avisa si las contraseñas no coinciden, sin consultar al backend', async () => {
    const { solicitudes } = simularApi()
    const { usuario } = renderizarEn('/restablecer-contrasenia?token=xyz')
    await completar(usuario, 'OtraClave2026', 'OtraClave2027')
    expect(await screen.findByText('Las contraseñas no coinciden.')).toBeInTheDocument()
    expect(solicitudes.some((s) => s.ruta.includes('restablecer'))).toBe(false)
  })

  it('con un enlace usado o vencido ofrece pedir uno nuevo (CA15)', async () => {
    simularApi({ 'POST /api/cuentas/recuperacion/restablecer': ENLACE_USADO })
    const { usuario } = renderizarEn('/restablecer-contrasenia?token=usado')
    await completar(usuario, 'OtraClave2026')
    expect(await screen.findByRole('link', { name: 'Pedir un enlace nuevo' })).toHaveAttribute(
      'href',
      '/recuperar-contrasenia',
    )
  })
})

describe('confirmación del correo nuevo', () => {
  it('sin sesión confirma y ofrece iniciar sesión (CA18)', async () => {
    simularApi({ 'POST /api/perfil/correo/confirmacion': { cuerpo: { mensaje: 'ok' } } })
    renderizarEn('/confirmar-correo?token=t')
    expect(await screen.findByText(/Tu correo fue actualizado/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('con sesión actualiza los datos mostrados (CA18)', async () => {
    let confirmado = false
    simularApi({
      'GET /api/sesion': () => ({
        cuerpo: { usuario: confirmado ? { ...USUARIO, correo: 'nuevo@ejemplo.com' } : USUARIO },
      }),
      'POST /api/perfil/correo/confirmacion': () => {
        confirmado = true
        return { cuerpo: { mensaje: 'ok' } }
      },
    })
    const { usuario } = renderizarEn('/confirmar-correo?token=t')
    await usuario.click(await screen.findByRole('link', { name: 'Ir a mi perfil' }))
    expect((await screen.findAllByText('nuevo@ejemplo.com')).length).toBeGreaterThan(0)
  })

  it('informa si el enlace ya no es válido', async () => {
    simularApi({ ...CON_SESION, 'POST /api/perfil/correo/confirmacion': ENLACE_USADO })
    renderizarEn('/confirmar-correo?token=t')
    expect(await screen.findByRole('alert')).toHaveTextContent(/volvé a pedirlo desde tu perfil/)
  })
})
