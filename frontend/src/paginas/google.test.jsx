/**
 * Pruebas del inicio de sesión y del registro con Google (funcionalidad 027).
 *
 * Realiza: verificación de RF52 (CA1) en la interfaz.
 */
import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const HABILITADO = { 'GET /api/google/estado': { cuerpo: { habilitado: true } } }
const PENDIENTE = {
  'GET /api/google/registro': {
    cuerpo: { nombre: 'Ana', apellido: 'López', correo: 'ana@ejemplo.com', invitacion: null },
  },
}

/** Simula la API con el registro pendiente; GET /api/sesion responde según si ya se creó la cuenta. */
function simularRegistro(respuestaRegistro) {
  let registrado = false
  return simularApi({
    ...PENDIENTE,
    'POST /api/google/registro': (cuerpo) => {
      const respuesta = respuestaRegistro?.(cuerpo) ?? {
        estado: 201,
        cuerpo: { usuario: USUARIO, csrf: 'token-nuevo' },
      }
      registrado = respuesta.estado === 201
      return respuesta
    },
    'GET /api/sesion': () =>
      registrado
        ? { cuerpo: { usuario: USUARIO } }
        : { estado: 401, cuerpo: { codigo: 'sesion_requerida', mensaje: 'Iniciá sesión.' } },
  })
}

describe('botón "Continuar con Google"', () => {
  it('no aparece si Google no está configurado', async () => {
    simularApi()
    renderizarEn('/iniciar-sesion')
    await screen.findByRole('heading', { name: 'Iniciar sesión' })
    expect(screen.queryByRole('link', { name: 'Continuar con Google' })).not.toBeInTheDocument()
  })

  it('aparece en el inicio de sesión y lleva al inicio del flujo', async () => {
    simularApi(HABILITADO)
    renderizarEn('/iniciar-sesion')
    const enlace = await screen.findByRole('link', { name: 'Continuar con Google' })
    expect(enlace).toHaveAttribute('href', '/api/google/inicio')
  })

  it('en el registro con invitación conserva el token', async () => {
    simularApi({
      ...HABILITADO,
      'POST /api/invitaciones/consulta': {
        cuerpo: {
          invitacion: {
            correo: 'ana@ejemplo.com',
            vigente: true,
            invitante: 'Rita',
            organizacion: { nombre: 'Estudio Pérez', tipo: 'estudio' },
          },
        },
      },
    })
    renderizarEn('/registro?invitacion=abc')
    const enlace = await screen.findByRole('link', { name: 'Continuar con Google' })
    expect(enlace).toHaveAttribute('href', '/api/google/inicio?invitacion=abc')
  })

  it.each([
    ['google_cancelado', /Cancelaste el ingreso con Google/],
    ['google_no_verificado', /Google no confirmó tu correo/],
    ['cuenta_desactivada', /Tu cuenta está desactivada/],
    ['otro', /No pudimos ingresar con Google/],
  ])('muestra el motivo cuando Google vuelve con %s', async (codigo, texto) => {
    simularApi()
    renderizarEn(`/iniciar-sesion?google=${codigo}`)
    expect(await screen.findByText(texto)).toBeInTheDocument()
  })
})

describe('completar el registro con Google', () => {
  it('pide el perfil antes de crear la cuenta y entra al terminar', async () => {
    const { solicitudes } = simularRegistro()
    const { usuario } = renderizarEn('/registro/google')
    expect(await screen.findByText(/Ingresaste con Google como/)).toBeInTheDocument()

    // El perfil es obligatorio.
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(await screen.findByText('Elegí cómo vas a usar la plataforma.')).toBeInTheDocument()
    await usuario.click(screen.getByLabelText(/Abogado o abogada/))
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))

    // Nombre y apellido vienen de Google.
    expect(screen.getByLabelText('Nombre')).toHaveValue('Ana')
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    await usuario.type(screen.getByLabelText(/Colegio de abogados/), 'CPACF')
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))

    // Los Términos también.
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))
    expect(await screen.findByText(/Tenés que aceptar los Términos/)).toBeInTheDocument()
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    expect(await screen.findByRole('heading', { name: 'Hola, Ana' })).toBeInTheDocument()
    const envio = solicitudes.find((s) => s.metodo === 'POST' && s.ruta === '/api/google/registro')
    expect(envio.cuerpo).toEqual({
      nombre: 'Ana',
      apellido: 'López',
      perfil: 'abogado',
      colegio: 'CPACF',
      acepta_terminos: true,
    })
  })

  it('si el backend rechaza un dato, vuelve al paso de ese dato', async () => {
    simularRegistro(() => ({
      estado: 400,
      cuerpo: { codigo: 'datos_invalidos', mensaje: 'Revisá los datos.', errores: { nombre: 'Muy largo.' } },
    }))
    const { usuario } = renderizarEn('/registro/google')
    await usuario.click(await screen.findByLabelText(/Abogado o abogada/))
    for (let paso = 0; paso < 3; paso += 1) {
      await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    }
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))
    expect(await screen.findByText('Muy largo.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Tus datos' })).toBeInTheDocument()
  })

  it('sin un registro pendiente, explica que hay que volver a empezar', async () => {
    simularApi({
      'GET /api/google/registro': {
        estado: 404,
        cuerpo: { codigo: 'registro_google_vencido', mensaje: 'No hay un registro con Google en curso.' },
      },
    })
    renderizarEn('/registro/google')
    expect(await screen.findByText('No hay un registro con Google en curso.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Volver a iniciar sesión' })).toBeInTheDocument()
  })
})
