/**
 * Pruebas de las pantallas de acceso: inicio de sesión, registro y rutas
 * protegidas (CA1 a CA5, CA7 a CA9, CA11, CA12 y CA22 de la funcionalidad 002).
 * Los textos legales se prueban en legales.test.jsx.
 */
import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const ERROR_CREDENCIALES = {
  estado: 401,
  cuerpo: { codigo: 'credenciales_invalidas', mensaje: 'El correo o la contraseña no son correctos.' },
}

async function completarInicioDeSesion(usuario) {
  await usuario.type(await screen.findByLabelText('Correo electrónico'), 'ana@ejemplo.com')
  await usuario.type(screen.getByLabelText('Contraseña'), 'Segura12345')
  await usuario.click(screen.getByRole('button', { name: 'Ingresar' }))
}

describe('rutas protegidas', () => {
  it('sin sesión, una pantalla interna lleva al inicio de sesión (CA22)', async () => {
    simularApi()
    renderizarEn('/perfil')
    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('con sesión, las pantallas de acceso llevan al inicio', async () => {
    simularApi(CON_SESION)
    renderizarEn('/iniciar-sesion')
    expect(await screen.findByRole('heading', { name: 'Hola, Ana' })).toBeInTheDocument()
  })

  it('si la sesión vence, vuelve al inicio de sesión con un aviso (CA12)', async () => {
    simularApi({
      ...CON_SESION,
      'PATCH /api/perfil': { estado: 401, cuerpo: { codigo: 'sesion_requerida', mensaje: 'Iniciá sesión.' } },
    })
    const { usuario } = renderizarEn('/perfil')
    await usuario.click(await screen.findByRole('button', { name: 'Guardar los datos' }))
    expect(await screen.findByText(/Tu sesión venció/)).toBeInTheDocument()
  })
})

describe('inicio de sesión', () => {
  it('con credenciales válidas entra y muestra el nombre (CA7)', async () => {
    const { solicitudes } = simularApi({
      'POST /api/sesion': { cuerpo: { usuario: USUARIO, csrf: 'token-sesion' } },
    })
    const { usuario } = renderizarEn('/iniciar-sesion')
    await completarInicioDeSesion(usuario)
    expect(await screen.findByRole('heading', { name: 'Hola, Ana' })).toBeInTheDocument()
    expect(screen.getByText('Ana López')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta === '/api/sesion' && s.metodo === 'POST').cuerpo).toEqual({
      correo: 'ana@ejemplo.com',
      contrasenia: 'Segura12345',
    })
  })

  it('vuelve a la pantalla que se quería abrir', async () => {
    simularApi({ 'POST /api/sesion': { cuerpo: { usuario: USUARIO, csrf: 't' } } })
    const { usuario } = renderizarEn('/perfil')
    await completarInicioDeSesion(usuario)
    expect(await screen.findByRole('heading', { name: 'Mi perfil' })).toBeInTheDocument()
  })

  it('con credenciales inválidas muestra el mensaje genérico (CA8)', async () => {
    simularApi({ 'POST /api/sesion': ERROR_CREDENCIALES })
    const { usuario } = renderizarEn('/iniciar-sesion')
    await completarInicioDeSesion(usuario)
    expect(await screen.findByRole('alert')).toHaveTextContent('El correo o la contraseña no son correctos.')
  })

  it('con la cuenta sin verificar ofrece reenviar el correo (CA9)', async () => {
    simularApi({
      'POST /api/sesion': {
        estado: 403,
        cuerpo: { codigo: 'cuenta_no_verificada', mensaje: 'Tenés que verificar tu correo.' },
      },
      'POST /api/cuentas/verificacion/reenvio': { cuerpo: { mensaje: 'Si el correo corresponde, te enviamos un mensaje.' } },
    })
    const { usuario } = renderizarEn('/iniciar-sesion')
    await completarInicioDeSesion(usuario)
    await usuario.click(await screen.findByRole('button', { name: 'Reenviar el correo de verificación' }))
    expect(await screen.findByText(/te enviamos un mensaje/)).toBeInTheDocument()
  })

  it('al cerrar sesión vuelve al inicio de sesión con un aviso (CA11)', async () => {
    const { solicitudes } = simularApi({ ...CON_SESION, 'DELETE /api/sesion': { cuerpo: {} } })
    const { usuario } = renderizarEn('/')
    await usuario.click(await screen.findByRole('button', { name: 'Cerrar sesión' }))
    expect(await screen.findByText('Cerraste la sesión.')).toBeInTheDocument()
    expect(solicitudes.some((s) => s.metodo === 'DELETE' && s.ruta === '/api/sesion')).toBe(true)
  })
})

describe('registro', () => {
  async function completarRegistro(usuario, { perfil = 'Abogado o abogada', institucion } = {}) {
    await usuario.type(await screen.findByLabelText('Nombre'), 'Ana')
    await usuario.type(screen.getByLabelText('Apellido'), 'López')
    await usuario.type(screen.getByLabelText('Correo electrónico'), 'ana@ejemplo.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(screen.getByLabelText(perfil))
    if (institucion) await usuario.type(screen.getByLabelText(institucion.etiqueta, { exact: false }), institucion.valor)
  }

  it('envía solo el dato del perfil elegido y muestra el aviso de verificación (CA1)', async () => {
    const { solicitudes } = simularApi({
      'POST /api/cuentas/registro': { estado: 201, cuerpo: { mensaje: 'Te enviamos un correo para verificar tu cuenta.' } },
    })
    const { usuario } = renderizarEn('/registro')
    await completarRegistro(usuario, {
      perfil: 'Aseguradora',
      institucion: { etiqueta: 'Empresa', valor: 'Seguros del Sur' },
    })
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    expect(await screen.findByRole('heading', { name: 'Revisá tu correo' })).toBeInTheDocument()
    const enviado = solicitudes.find((s) => s.ruta === '/api/cuentas/registro').cuerpo
    expect(enviado).toEqual({
      nombre: 'Ana',
      apellido: 'López',
      correo: 'ana@ejemplo.com',
      contrasenia: 'Segura12345',
      perfil: 'aseguradora',
      empresa: 'Seguros del Sur',
      acepta_terminos: true,
    })
  })

  it('muestra el campo según el perfil: colegio para abogados', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await completarRegistro(usuario)
    expect(screen.getByLabelText(/Colegio de abogados/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Empresa/)).not.toBeInTheDocument()
  })

  it('muestra junto a cada campo los errores que informa el backend (CA2, CA4)', async () => {
    simularApi({
      'POST /api/cuentas/registro': {
        estado: 400,
        cuerpo: {
          codigo: 'datos_invalidos',
          mensaje: 'Revisá los datos marcados.',
          errores: {
            contrasenia: 'Esa contraseña es demasiado común. Elegí otra.',
            acepta_terminos: 'Tenés que aceptar los Términos de Uso y la Política de Privacidad.',
          },
        },
      },
    })
    const { usuario } = renderizarEn('/registro')
    await completarRegistro(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Revisá los datos marcados.')
    expect(screen.getByText(/demasiado común/)).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByRole('checkbox')).toHaveAttribute('aria-invalid', 'true')
  })

  it('marca las reglas de la contraseña a medida que se cumplen (CA4)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.type(await screen.findByLabelText('Contraseña'), 'abc')
    expect(screen.getByText(/Al menos una letra/).closest('li')).toHaveClass('reglas__item--cumplida')
    expect(screen.getByText(/Al menos un número/).closest('li')).not.toHaveClass('reglas__item--cumplida')
  })
})
