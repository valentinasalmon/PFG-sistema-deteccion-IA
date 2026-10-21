/**
 * Pruebas de las pantallas de la funcionalidad 021: registro de empleados con
 * la invitación de una aseguradora, aseguradoras pendientes, administración y
 * cuentas desactivadas.
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const ASEGURADORA = {
  id: 7,
  nombre: 'SEGUROS GALICIA S.A.',
  tipo: 'aseguradora',
  tipo_nombre: 'Aseguradora',
  correo_contacto: null,
  telefono: null,
  mi_rol: 'referente',
  estado: 'pendiente',
  cuit: '30500000127',
  plan: { codigo: 'basico', nombre: 'Organización Básico', limite_miembros: 5 },
}
const RITA = {
  id_usuario: USUARIO.id,
  nombre: 'Rita',
  apellido: 'López',
  correo: 'rita@galicia.com',
  perfil: 'aseguradora',
  cargo: null,
  rol: 'referente',
  incorporado_en: '2026-10-16T12:00:00',
}
const INVITACION = {
  id: 9,
  correo: 'eva@galicia.com',
  cargo: 'Liquidadora',
  estado: 'pendiente',
  vigente: true,
  vence_en: '2026-10-23T12:00:00',
  organizacion: { id: 7, nombre: 'SEGUROS GALICIA S.A.', tipo: 'aseguradora', tipo_nombre: 'Aseguradora' },
  invitante: 'Rita López',
  sesion_con_el_correo: false,
}
const CON_SESION_ASEGURADORA = {
  'GET /api/sesion': { cuerpo: { usuario: { ...USUARIO, perfil: 'aseguradora', empresa: 'SEGUROS GALICIA S.A.' } } },
}
const CON_SESION_ADMINISTRADOR = {
  'GET /api/sesion': { cuerpo: { usuario: { ...USUARIO, rol: 'administrador' } } },
}
const PENDIENTE = {
  id: 7,
  nombre: 'SEGUROS GALICIA S.A.',
  cuit: '30500000127',
  creada_en: '2026-10-16T12:00:00',
  referente: { nombre: 'Rita López', correo: 'rita@galicia.com', verificado: true },
}

function apiDeAseguradora(organizacion = ASEGURADORA, extra = {}) {
  return simularApi({
    ...CON_SESION_ASEGURADORA,
    'GET /api/organizaciones/7': { cuerpo: { organizacion } },
    'GET /api/organizaciones/7/miembros': { cuerpo: { miembros: [RITA] } },
    'GET /api/organizaciones/7/invitaciones': { cuerpo: { invitaciones: [] } },
    ...extra,
  })
}

describe('registro con la invitación de una aseguradora', () => {
  it('fija el correo y el perfil y solo pide datos y cuenta (CA10)', async () => {
    const { solicitudes } = simularApi({
      'POST /api/invitaciones/consulta': { cuerpo: { invitacion: INVITACION } },
      'POST /api/cuentas/registro': { estado: 201, cuerpo: { mensaje: 'Te enviamos un correo para verificar tu cuenta.' } },
    })
    const { usuario } = renderizarEn('/registro?invitacion=tok')
    expect(await screen.findByText(/Te sumás a SEGUROS GALICIA S.A. con la invitación de Rita López/)).toBeInTheDocument()
    expect(screen.getByText('Paso 1 de 2')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Tus datos' })).toBeInTheDocument()
    await usuario.type(screen.getByLabelText('Nombre'), 'Eva')
    await usuario.type(screen.getByLabelText('Apellido'), 'Paz')
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(screen.getByLabelText('Correo electrónico')).toHaveValue('eva@galicia.com')
    expect(screen.getByLabelText('Correo electrónico')).toHaveAttribute('readonly')
    await usuario.type(screen.getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))

    expect(await screen.findByText(/vas a quedar dentro de SEGUROS GALICIA S.A./)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta === '/api/cuentas/registro').cuerpo).toEqual({
      nombre: 'Eva',
      apellido: 'Paz',
      correo: 'eva@galicia.com',
      contrasenia: 'Segura12345',
      perfil: 'aseguradora',
      acepta_terminos: true,
      token_invitacion: 'tok',
    })
  })

  it('una invitación que ya no está vigente no permite registrarse', async () => {
    simularApi({ 'POST /api/invitaciones/consulta': { cuerpo: { invitacion: { ...INVITACION, vigente: false } } } })
    renderizarEn('/registro?invitacion=tok')
    expect(await screen.findByRole('alert')).toHaveTextContent('La invitación ya no está vigente')
    expect(screen.getByRole('link', { name: 'Crear una cuenta sin invitación' })).toHaveAttribute('href', '/registro')
  })

  it('un enlace alterado se informa', async () => {
    simularApi({
      'POST /api/invitaciones/consulta': { estado: 400, cuerpo: { codigo: 'enlace_invalido', mensaje: 'El enlace no es válido. Solicitá uno nuevo.' } },
    })
    renderizarEn('/registro?invitacion=x')
    expect(await screen.findByRole('alert')).toHaveTextContent('El enlace no es válido')
  })

  it('el enlace de la invitación de una aseguradora explica que se queda adentro al verificar', async () => {
    simularApi({ 'POST /api/invitaciones/consulta': { cuerpo: { invitacion: INVITACION } } })
    renderizarEn('/invitaciones/responder?token=tok')
    expect(await screen.findByText(/al verificar tu correo vas a quedar dentro de la aseguradora/)).toBeInTheDocument()
  })
})

describe('aseguradora pendiente de aprobación', () => {
  it('lo indica y no ofrece invitar (CA6)', async () => {
    apiDeAseguradora()
    renderizarEn('/organizaciones/7')
    expect(await screen.findByText(/pendiente de aprobación/)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Invitar miembros' })).not.toBeInTheDocument()
    expect(screen.getByText('CUIT 30500000127')).toBeInTheDocument()
  })

  it('el nombre de una aseguradora no se edita (CA18)', async () => {
    apiDeAseguradora({ ...ASEGURADORA, estado: 'activa' })
    const { usuario } = renderizarEn('/organizaciones/7')
    const seccion = (await screen.findByRole('heading', { name: 'Datos de la organización' })).closest('section')
    await usuario.click(within(seccion).getByRole('button', { name: 'Editar los datos de la organización' }))
    expect(within(seccion).getByLabelText('Nombre')).toHaveAttribute('readonly')
    expect(screen.getByRole('heading', { name: 'Invitar miembros' })).toBeInTheDocument()
  })

  it('en la lista se marca como pendiente y una aseguradora no crea organizaciones (CA17)', async () => {
    simularApi({
      ...CON_SESION_ASEGURADORA,
      'GET /api/organizaciones': { cuerpo: { organizaciones: [ASEGURADORA] } },
      'GET /api/invitaciones': { cuerpo: { invitaciones: [] } },
    })
    renderizarEn('/organizaciones')
    expect(await screen.findByText('Pendiente de aprobación')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Crear estudio jurídico' })).not.toBeInTheDocument()
  })

  it('sin organizaciones, una aseguradora no ve la invitación a crear una', async () => {
    simularApi({
      ...CON_SESION_ASEGURADORA,
      'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
      'GET /api/invitaciones': { cuerpo: { invitaciones: [] } },
    })
    renderizarEn('/organizaciones')
    expect(await screen.findByText('Todavía no pertenecés a ninguna organización.')).toBeInTheDocument()
  })
})

describe('cuenta desactivada', () => {
  it('al abandonar la última aseguradora vuelve al inicio de sesión con el aviso (CA13)', async () => {
    apiDeAseguradora(
      { ...ASEGURADORA, estado: 'activa', mi_rol: 'miembro' },
      {
        'GET /api/organizaciones/7/miembros': { cuerpo: { miembros: [{ ...RITA, rol: 'miembro' }, { ...RITA, id_usuario: 99, rol: 'referente' }] } },
        'POST /api/organizaciones/7/abandono': {
          cuerpo: { mensaje: 'Abandonaste la organización.', organizacion_eliminada: false, cuenta_desactivada: true },
        },
      },
    )
    const { usuario } = renderizarEn('/organizaciones/7')
    await usuario.click(await screen.findByRole('button', { name: 'Abandonar la organización' }))
    await usuario.click(screen.getByRole('button', { name: 'Abandonar' }))
    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.getByText(/Tu cuenta quedó desactivada/)).toBeInTheDocument()
  })

  it('al iniciar sesión se informa que está desactivada (CA14)', async () => {
    simularApi({
      'POST /api/sesion': {
        estado: 403,
        cuerpo: { codigo: 'cuenta_desactivada', mensaje: 'Tu cuenta está desactivada porque ya no pertenecés a ninguna aseguradora.' },
      },
    })
    const { usuario } = renderizarEn('/iniciar-sesion')
    await usuario.type(await screen.findByLabelText('Correo electrónico'), 'eva@galicia.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(screen.getByRole('button', { name: 'Ingresar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Tu cuenta está desactivada')
  })
})

describe('administración', () => {
  it('quien no es Administrador no ve la pantalla ni el enlace (CA7)', async () => {
    simularApi(CON_SESION)
    renderizarEn('/administracion')
    expect(await screen.findByText(/Solo el Administrador/)).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Administración' })).not.toBeInTheDocument()
  })

  it('lista las pendientes con su CUIT y quién las registró (CA7)', async () => {
    simularApi({
      ...CON_SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': {
        cuerpo: { aseguradoras: [PENDIENTE, { ...PENDIENTE, id: 8, referente: { ...PENDIENTE.referente, verificado: false } }] },
      },
    })
    renderizarEn('/administracion')
    expect(await screen.findAllByText('SEGUROS GALICIA S.A.')).toHaveLength(2)
    expect(screen.getAllByText(/CUIT 30500000127 · Registrada el 16\/10\/2026/)).toHaveLength(2)
    expect(screen.getByText(/correo sin verificar/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Administración' })).toBeInTheDocument()
  })

  it('sin pendientes lo indica', async () => {
    simularApi({ ...CON_SESION_ADMINISTRADOR, 'GET /api/administracion/aseguradoras-pendientes': { cuerpo: { aseguradoras: [] } } })
    renderizarEn('/administracion')
    expect(await screen.findByText('No hay aseguradoras pendientes.')).toBeInTheDocument()
  })

  it('si la lista no carga, muestra el error', async () => {
    simularApi({
      ...CON_SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': { estado: 500, cuerpo: { mensaje: 'Ocurrió un error inesperado.' } },
    })
    renderizarEn('/administracion')
    expect(await screen.findByRole('alert')).toHaveTextContent('Ocurrió un error inesperado.')
  })

  it('aprueba con confirmación (CA8)', async () => {
    let pendientes = [PENDIENTE]
    const { solicitudes } = simularApi({
      ...CON_SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': () => ({ cuerpo: { aseguradoras: pendientes } }),
      'POST /api/administracion/organizaciones/7/aprobacion': () => {
        pendientes = []
        return { cuerpo: { mensaje: 'SEGUROS GALICIA S.A. fue aprobada.' } }
      },
    })
    const { usuario } = renderizarEn('/administracion')
    await usuario.click(await screen.findByRole('button', { name: 'Aprobar' }))
    await usuario.click(within(screen.getByRole('group', { name: /¿Aprobar/ })).getByRole('button', { name: 'Aprobar' }))
    expect(await screen.findByText('SEGUROS GALICIA S.A. fue aprobada.')).toBeInTheDocument()
    expect(screen.getByText('No hay aseguradoras pendientes.')).toBeInTheDocument()
    expect(solicitudes.some((s) => s.ruta.endsWith('/aprobacion'))).toBe(true)
  })

  it('un error al aprobar se muestra', async () => {
    simularApi({
      ...CON_SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': { cuerpo: { aseguradoras: [PENDIENTE] } },
      'POST /api/administracion/organizaciones/7/aprobacion': { estado: 404, cuerpo: { mensaje: 'La aseguradora no existe o ya fue revisada.' } },
    })
    const { usuario } = renderizarEn('/administracion')
    await usuario.click(await screen.findByRole('button', { name: 'Aprobar' }))
    await usuario.click(within(screen.getByRole('group', { name: /¿Aprobar/ })).getByRole('button', { name: 'Aprobar' }))
    expect(await screen.findByText('La aseguradora no existe o ya fue revisada.')).toBeInTheDocument()
  })

  it('rechaza con un motivo obligatorio (CA9)', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': { cuerpo: { aseguradoras: [PENDIENTE] } },
      'POST /api/administracion/organizaciones/7/rechazo': { cuerpo: { mensaje: 'La aseguradora fue rechazada y se avisó a quien la registró.' } },
    })
    const { usuario } = renderizarEn('/administracion')
    await usuario.click(await screen.findByRole('button', { name: 'Rechazar SEGUROS GALICIA S.A.' }))
    await usuario.click(screen.getByRole('button', { name: 'Rechazar la aseguradora' }))
    expect(screen.getByText(/Indicá el motivo/)).toBeInTheDocument()
    await usuario.type(screen.getByLabelText(/Motivo del rechazo/), 'No trabaja en la empresa.')
    await usuario.click(screen.getByRole('button', { name: 'Rechazar la aseguradora' }))
    expect(await screen.findByText(/fue rechazada/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta.endsWith('/rechazo')).cuerpo).toEqual({ motivo: 'No trabaja en la empresa.' })
  })

  it('cancelar el rechazo no envía nada y un error al rechazar se muestra', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': { cuerpo: { aseguradoras: [PENDIENTE] } },
      'POST /api/administracion/organizaciones/7/rechazo': { estado: 404, cuerpo: { mensaje: 'La aseguradora no existe o ya fue revisada.' } },
    })
    const { usuario } = renderizarEn('/administracion')
    await usuario.click(await screen.findByRole('button', { name: 'Rechazar SEGUROS GALICIA S.A.' }))
    await usuario.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(solicitudes.some((s) => s.ruta.endsWith('/rechazo'))).toBe(false)
    await usuario.click(screen.getByRole('button', { name: 'Rechazar SEGUROS GALICIA S.A.' }))
    await usuario.type(screen.getByLabelText(/Motivo del rechazo/), 'x')
    await usuario.click(screen.getByRole('button', { name: 'Rechazar la aseguradora' }))
    expect(await screen.findByText('La aseguradora no existe o ya fue revisada.')).toBeInTheDocument()
  })
})
