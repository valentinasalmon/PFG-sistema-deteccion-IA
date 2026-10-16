/**
 * Pruebas de las pantallas de acceso: inicio de sesión, registro y rutas
 * protegidas (CA1 a CA5, CA7 a CA9, CA11, CA12 y CA22 de la funcionalidad 002, y
 * CA1 a CA8 de la funcionalidad 020, registro por pasos).
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

describe('registro por pasos', () => {
  const RESPUESTA_REGISTRO = {
    'POST /api/cuentas/registro': { estado: 201, cuerpo: { mensaje: 'Te enviamos un correo para verificar tu cuenta.' } },
  }

  async function siguiente(usuario) {
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
  }

  /** Completa los pasos 1 a 3 y deja el formulario en el paso 4. */
  async function llegarAlPaso4(usuario, { perfil = 'Abogado o abogada', institucion } = {}) {
    await usuario.click(await screen.findByLabelText(new RegExp(perfil)))
    await siguiente(usuario)
    await usuario.type(screen.getByLabelText('Nombre'), 'Ana')
    await usuario.type(screen.getByLabelText('Apellido'), 'López')
    await siguiente(usuario)
    if (institucion) await usuario.type(screen.getByLabelText(institucion.etiqueta, { exact: false }), institucion.valor)
    await siguiente(usuario)
  }

  async function completarCuenta(usuario) {
    await usuario.type(screen.getByLabelText('Correo electrónico'), 'ana@ejemplo.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(screen.getByRole('checkbox'))
  }

  it('empieza en el paso 1 de 4 con la elección del perfil y su aclaración (CA1)', async () => {
    simularApi()
    renderizarEn('/registro')
    expect(await screen.findByText('Paso 1 de 4')).toBeInTheDocument()
    const grupo = screen.getByRole('group', { name: '¿Cómo vas a usar la plataforma?' })
    expect(grupo).toHaveAccessibleDescription(/no puede cambiarse/)
    expect(screen.getByRole('radio', { name: /Abogado o abogada/ })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: /Aseguradora/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Atrás' })).not.toBeInTheDocument()
  })

  it('no avanza sin elegir un perfil (CA2)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await screen.findByText('Paso 1 de 4')
    await siguiente(usuario)
    expect(screen.getByText('Paso 1 de 4')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent('Revisá los datos marcados.')
    expect(screen.getByRole('group')).toHaveAccessibleDescription(/Elegí cómo vas a usar la plataforma/)
  })

  it('marca la opción elegida', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.click(await screen.findByLabelText(/Aseguradora/))
    expect(screen.getByLabelText(/Aseguradora/).closest('label')).toHaveClass('opcion-tarjeta--elegida')
    expect(screen.getByLabelText(/Abogado o abogada/).closest('label')).not.toHaveClass('opcion-tarjeta--elegida')
  })

  it('no avanza sin nombre ni apellido y marca cada campo vacío (CA3)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.click(await screen.findByLabelText(/Abogado o abogada/))
    await siguiente(usuario)
    await siguiente(usuario)
    expect(screen.getByText('Paso 2 de 4')).toBeInTheDocument()
    expect(screen.getByLabelText('Nombre')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText('Apellido')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText('Ingresá tu nombre.')).toBeInTheDocument()
    expect(screen.getByText('Ingresá tu apellido.')).toBeInTheDocument()

    await usuario.type(screen.getByLabelText('Nombre'), 'Ana')
    await siguiente(usuario)
    expect(screen.getByLabelText('Nombre')).not.toHaveAttribute('aria-invalid')
    expect(screen.getByLabelText('Apellido')).toHaveAttribute('aria-invalid', 'true')
  })

  it('pide el colegio a los abogados y permite avanzar sin completarlo (CA4)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.click(await screen.findByLabelText(/Abogado o abogada/))
    await siguiente(usuario)
    await usuario.type(screen.getByLabelText('Nombre'), 'Ana')
    await usuario.type(screen.getByLabelText('Apellido'), 'López')
    await siguiente(usuario)
    expect(screen.getByRole('heading', { name: 'Tu colegio de abogados' })).toBeInTheDocument()
    expect(screen.getByLabelText(/Colegio de abogados/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Empresa/)).not.toBeInTheDocument()
    await siguiente(usuario)
    expect(screen.getByText('Paso 4 de 4')).toBeInTheDocument()
  })

  it('pide la empresa a las aseguradoras (CA4)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.click(await screen.findByLabelText(/Aseguradora/))
    await siguiente(usuario)
    await usuario.type(screen.getByLabelText('Nombre'), 'Ana')
    await usuario.type(screen.getByLabelText('Apellido'), 'López')
    await siguiente(usuario)
    expect(screen.getByRole('heading', { name: 'Tu empresa' })).toBeInTheDocument()
    expect(screen.queryByLabelText(/Colegio/)).not.toBeInTheDocument()
  })

  it('al volver atrás conserva los datos cargados (CA5)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await llegarAlPaso4(usuario, { institucion: { etiqueta: 'Colegio', valor: 'CPACF' } })
    await usuario.type(screen.getByLabelText('Correo electrónico'), 'ana@ejemplo.com')

    await usuario.click(screen.getByRole('button', { name: 'Atrás' }))
    expect(screen.getByLabelText(/Colegio de abogados/)).toHaveValue('CPACF')
    await usuario.click(screen.getByRole('button', { name: 'Atrás' }))
    expect(screen.getByLabelText('Nombre')).toHaveValue('Ana')
    expect(screen.getByLabelText('Apellido')).toHaveValue('López')
    await usuario.click(screen.getByRole('button', { name: 'Atrás' }))
    expect(screen.getByLabelText(/Abogado o abogada/)).toBeChecked()

    await siguiente(usuario)
    await siguiente(usuario)
    await siguiente(usuario)
    expect(screen.getByLabelText('Correo electrónico')).toHaveValue('ana@ejemplo.com')
  })

  it('crea la cuenta enviando solo el dato del perfil elegido (CA6)', async () => {
    const { solicitudes } = simularApi(RESPUESTA_REGISTRO)
    const { usuario } = renderizarEn('/registro')
    await llegarAlPaso4(usuario, {
      perfil: 'Aseguradora',
      institucion: { etiqueta: 'Empresa', valor: 'Seguros del Sur' },
    })
    await completarCuenta(usuario)
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

  it('no envía el colegio si el perfil cambió a Aseguradora (CA6)', async () => {
    const { solicitudes } = simularApi(RESPUESTA_REGISTRO)
    const { usuario } = renderizarEn('/registro')
    await llegarAlPaso4(usuario, { institucion: { etiqueta: 'Colegio', valor: 'CPACF' } })
    for (let i = 0; i < 3; i += 1) await usuario.click(screen.getByRole('button', { name: 'Atrás' }))
    await usuario.click(screen.getByLabelText(/Aseguradora/))
    for (let i = 0; i < 3; i += 1) await siguiente(usuario)
    await completarCuenta(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    await screen.findByRole('heading', { name: 'Revisá tu correo' })
    const enviado = solicitudes.find((s) => s.ruta === '/api/cuentas/registro').cuerpo
    expect(enviado.perfil).toBe('aseguradora')
    expect(enviado).not.toHaveProperty('colegio')
    expect(enviado).not.toHaveProperty('empresa')
  })

  it('muestra junto a cada campo del paso 4 los errores del backend (CA6, RF01 CA2 y CA4)', async () => {
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
    await llegarAlPaso4(usuario)
    await usuario.type(screen.getByLabelText('Correo electrónico'), 'ana@ejemplo.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'Password123')
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Revisá los datos marcados.')
    expect(screen.getByText('Paso 4 de 4')).toBeInTheDocument()
    expect(screen.getByText(/demasiado común/)).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByRole('checkbox')).toHaveAttribute('aria-invalid', 'true')
  })

  it('si el backend rechaza un dato de un paso anterior, vuelve a ese paso (CA7)', async () => {
    simularApi({
      'POST /api/cuentas/registro': {
        estado: 400,
        cuerpo: {
          codigo: 'datos_invalidos',
          mensaje: 'Revisá los datos marcados.',
          errores: { apellido: 'El apellido es demasiado largo.', correo: 'Ingresá un correo válido.' },
        },
      },
    })
    const { usuario } = renderizarEn('/registro')
    await llegarAlPaso4(usuario)
    await completarCuenta(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    expect(await screen.findByText('Paso 2 de 4')).toBeInTheDocument()
    expect(screen.getByLabelText('Apellido')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText('El apellido es demasiado largo.')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent('Revisá los datos marcados.')
  })

  it('un error general del backend deja el formulario en el paso 4', async () => {
    simularApi({
      'POST /api/cuentas/registro': { estado: 500, cuerpo: { codigo: 'error_interno', mensaje: 'Ocurrió un error.' } },
    })
    const { usuario } = renderizarEn('/registro')
    await llegarAlPaso4(usuario)
    await completarCuenta(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Ocurrió un error.')
    expect(screen.getByText('Paso 4 de 4')).toBeInTheDocument()
  })

  it('al cambiar de paso, el foco pasa al título del paso nuevo (CA8)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.click(await screen.findByLabelText(/Abogado o abogada/))
    await siguiente(usuario)
    expect(screen.getByRole('heading', { name: 'Tus datos' })).toHaveFocus()
    await usuario.click(screen.getByRole('button', { name: 'Atrás' }))
    expect(screen.getByRole('heading', { name: '¿Cómo vas a usar la plataforma?' })).toHaveFocus()
  })

  it('con Enter en un campo avanza al paso siguiente', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await usuario.click(await screen.findByLabelText(/Abogado o abogada/))
    await siguiente(usuario)
    await usuario.type(screen.getByLabelText('Nombre'), 'Ana')
    await usuario.type(screen.getByLabelText('Apellido'), 'López{Enter}')
    expect(screen.getByText('Paso 3 de 4')).toBeInTheDocument()
  })

  it('marca las reglas de la contraseña a medida que se cumplen (RF01 CA4)', async () => {
    simularApi()
    const { usuario } = renderizarEn('/registro')
    await llegarAlPaso4(usuario)
    await usuario.type(screen.getByLabelText('Contraseña'), 'abc')
    expect(screen.getByText(/Al menos una letra/).closest('li')).toHaveClass('reglas__item--cumplida')
    expect(screen.getByText(/Al menos un número/).closest('li')).not.toHaveClass('reglas__item--cumplida')
  })
})
