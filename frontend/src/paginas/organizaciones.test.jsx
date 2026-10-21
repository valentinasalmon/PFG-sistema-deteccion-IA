/**
 * Pruebas de las pantallas de organizaciones e invitaciones (funcionalidad 004).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const PLAN = { codigo: 'basico', nombre: 'Organización Básico', limite_miembros: 5 }
const ORGANIZACION = {
  id: 3,
  nombre: 'Estudio Pérez',
  tipo: 'estudio_juridico',
  tipo_nombre: 'Estudio Jurídico',
  correo_contacto: null,
  telefono: '11 5555-0000',
  mi_rol: 'referente',
  plan: PLAN,
}
const ANA = {
  id_usuario: USUARIO.id,
  nombre: 'Ana',
  apellido: 'López',
  correo: 'ana@ejemplo.com',
  perfil: 'abogado',
  cargo: null,
  rol: 'referente',
  incorporado_en: '2026-10-16T12:00:00',
}
const BETO = { ...ANA, id_usuario: 2, nombre: 'Beto', apellido: 'Paz', correo: 'beto@ejemplo.com', rol: 'miembro', cargo: 'Asociado' }
const INVITACION = {
  id: 9,
  correo: 'carla@ejemplo.com',
  cargo: null,
  estado: 'pendiente',
  vigente: true,
  vence_en: '2026-10-23T12:00:00',
  organizacion: { id: 3, nombre: 'Estudio Pérez', tipo_nombre: 'Estudio Jurídico' },
  invitante: 'Ana López',
}

function apiDeOrganizacion({ organizacion = ORGANIZACION, miembros = [ANA, BETO], invitaciones = [INVITACION], extra = {} } = {}) {
  return simularApi({
    ...CON_SESION,
    'GET /api/organizaciones/3': { cuerpo: { organizacion } },
    'GET /api/organizaciones/3/miembros': { cuerpo: { miembros } },
    'GET /api/organizaciones/3/invitaciones': { cuerpo: { invitaciones } },
    ...extra,
  })
}

describe('mis organizaciones', () => {
  it('lista las organizaciones con el rol y las invitaciones pendientes (CA2, CA13)', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': {
        cuerpo: { organizaciones: [ORGANIZACION, { ...ORGANIZACION, id: 4, nombre: 'Sur', mi_rol: 'miembro' }] },
      },
      'GET /api/invitaciones': { cuerpo: { invitaciones: [INVITACION] } },
    })
    renderizarEn('/organizaciones')
    const lista = await screen.findByRole('heading', { name: 'Tus organizaciones' })
    const seccion = lista.closest('section')
    expect(within(seccion).getByRole('link', { name: 'Estudio Pérez' })).toHaveAttribute('href', '/organizaciones/3')
    expect(within(seccion).getByText('Referente')).toBeInTheDocument()
    expect(within(seccion).getByText('Miembro')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Invitaciones pendientes' })).toBeInTheDocument()
    expect(screen.getByText(/Te invitó Ana López/)).toBeInTheDocument()
  })

  it('sin organizaciones ni invitaciones lo explica', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
      'GET /api/invitaciones': { cuerpo: { invitaciones: [] } },
    })
    renderizarEn('/organizaciones')
    expect(await screen.findByText(/no pertenecés a ninguna organización/)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Invitaciones pendientes' })).not.toBeInTheDocument()
  })

  it('aceptar una invitación lleva a la organización (CA10)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      extra: {
        'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
        'GET /api/invitaciones': { cuerpo: { invitaciones: [INVITACION] } },
        'POST /api/invitaciones/9/aceptacion': { cuerpo: { mensaje: 'Ya sos miembro.', id_organizacion: 3 } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones')
    await usuario.click(await screen.findByRole('button', { name: 'Aceptar la invitación de Estudio Pérez' }))
    expect(await screen.findByText('Ya sos miembro de Estudio Pérez.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1, name: 'Estudio Pérez' })).toBeInTheDocument()
    expect(solicitudes.some((s) => s.ruta === '/api/invitaciones/9/aceptacion')).toBe(true)
  })

  it('rechazar una invitación la quita de la lista (CA10)', async () => {
    let pendientes = [INVITACION]
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
      'GET /api/invitaciones': () => ({ cuerpo: { invitaciones: pendientes } }),
      'POST /api/invitaciones/9/rechazo': () => {
        pendientes = []
        return { cuerpo: { mensaje: 'Rechazaste la invitación.' } }
      },
    })
    const { usuario } = renderizarEn('/organizaciones')
    await usuario.click(await screen.findByRole('button', { name: 'Rechazar la invitación de Estudio Pérez' }))
    expect(await screen.findByText(/no pertenecés a ninguna organización/)).toBeInTheDocument()
    expect(screen.queryByText(/Te invitó/)).not.toBeInTheDocument()
  })

  it('un error al responder se muestra', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
      'GET /api/invitaciones': { cuerpo: { invitaciones: [INVITACION] } },
      'POST /api/invitaciones/9/aceptacion': {
        estado: 409,
        cuerpo: { codigo: 'invitacion_no_vigente', mensaje: 'La invitación ya no está vigente.' },
      },
    })
    const { usuario } = renderizarEn('/organizaciones')
    await usuario.click(await screen.findByRole('button', { name: /Aceptar la invitación/ }))
    expect(await screen.findByRole('alert')).toHaveTextContent('ya no está vigente')
  })

  it('si la lista no carga, muestra el error', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': { estado: 500, cuerpo: { mensaje: 'Ocurrió un error inesperado.' } },
      'GET /api/invitaciones': { cuerpo: { invitaciones: [] } },
    })
    renderizarEn('/organizaciones')
    expect(await screen.findByRole('alert')).toHaveTextContent('Ocurrió un error inesperado.')
  })
})

describe('crear organización', () => {
  it('crea un estudio jurídico (CA1; RN40)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      invitaciones: [],
      miembros: [ANA],
      extra: { 'POST /api/organizaciones': { estado: 201, cuerpo: { organizacion: ORGANIZACION } } },
    })
    const { usuario } = renderizarEn('/organizaciones/nueva')
    await usuario.type(await screen.findByLabelText('Nombre'), 'Estudio Pérez')
    await usuario.type(screen.getByLabelText(/Teléfono/), '11 5555-0000')
    await usuario.click(screen.getByRole('button', { name: 'Crear estudio jurídico' }))
    expect(await screen.findByText(/Ya podés invitar a tu equipo/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'POST' && s.ruta === '/api/organizaciones').cuerpo).toEqual({
      nombre: 'Estudio Pérez',
      tipo: 'estudio_juridico',
      correo_contacto: '',
      telefono: '11 5555-0000',
    })
  })

  it('muestra los errores del backend junto a cada campo', async () => {
    simularApi({
      ...CON_SESION,
      'POST /api/organizaciones': {
        estado: 400,
        cuerpo: { mensaje: 'Revisá los datos marcados.', errores: { correo_contacto: 'El correo electrónico no es válido.' } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/nueva')
    await usuario.type(await screen.findByLabelText('Nombre'), 'X')
    await usuario.type(screen.getByLabelText(/Correo de contacto/), 'mal')
    await usuario.click(screen.getByRole('button', { name: 'Crear estudio jurídico' }))
    expect(await screen.findByText('El correo electrónico no es válido.')).toBeInTheDocument()
    expect(screen.getByLabelText(/Correo de contacto/)).toHaveAttribute('aria-invalid', 'true')
  })
})

describe('pantalla de la organización como Referente', () => {
  it('muestra el plan, los miembros y las invitaciones (CA14)', async () => {
    apiDeOrganizacion()
    renderizarEn('/organizaciones/3')
    expect(await screen.findByRole('heading', { level: 1, name: 'Estudio Pérez' })).toBeInTheDocument()
    expect(screen.getByText('Sos Referente')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Miembros (2 de 5)' })).toBeInTheDocument()
    expect(screen.getByText(/Abogado o abogada · Asociado · Desde el 16\/10\/2026/)).toBeInTheDocument()
    expect(screen.getByText('carla@ejemplo.com')).toBeInTheDocument()
    expect(screen.getByText('Vence el 23/10/2026')).toBeInTheDocument()
  })

  it('invita a una persona y limpia el formulario (CA5)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      extra: {
        'POST /api/organizaciones/3/invitaciones': {
          estado: 201,
          cuerpo: { invitacion: INVITACION, mensaje: 'Enviamos la invitación a dani@ejemplo.com.' },
        },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    const seccion = (await screen.findByRole('heading', { name: 'Invitar miembros' })).closest('section')
    await usuario.type(within(seccion).getByLabelText('Correo electrónico'), 'dani@ejemplo.com')
    await usuario.type(within(seccion).getByLabelText(/Cargo/), 'Perito')
    await usuario.click(within(seccion).getByRole('button', { name: 'Enviar invitación' }))
    expect(await screen.findByText('Enviamos la invitación a dani@ejemplo.com.')).toBeInTheDocument()
    expect(within(seccion).getByLabelText('Correo electrónico')).toHaveValue('')
    expect(solicitudes.find((s) => s.ruta === '/api/organizaciones/3/invitaciones' && s.metodo === 'POST').cuerpo).toEqual({
      correo: 'dani@ejemplo.com',
      cargo: 'Perito',
    })
  })

  it('el límite del plan se informa junto al correo (CA6)', async () => {
    apiDeOrganizacion({
      extra: {
        'POST /api/organizaciones/3/invitaciones': {
          estado: 409,
          cuerpo: {
            codigo: 'limite_del_plan',
            mensaje: 'La organización alcanzó el límite de 5 miembros de su plan.',
            errores: { correo: 'La organización alcanzó el límite de 5 miembros de su plan.' },
          },
        },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    const seccion = (await screen.findByRole('heading', { name: 'Invitar miembros' })).closest('section')
    await usuario.type(within(seccion).getByLabelText('Correo electrónico'), 'x@ejemplo.com')
    await usuario.click(within(seccion).getByRole('button', { name: 'Enviar invitación' }))
    expect(await within(seccion).findByRole('alert')).toHaveTextContent('límite de 5 miembros')
    expect(within(seccion).getByLabelText('Correo electrónico')).toHaveAttribute('aria-invalid', 'true')
  })

  it('reenvía y cancela invitaciones con confirmación (CA8)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      extra: {
        'POST /api/organizaciones/3/invitaciones/9/reenvio': { cuerpo: { mensaje: 'Reenviamos la invitación a carla@ejemplo.com.' } },
        'DELETE /api/organizaciones/3/invitaciones/9': { cuerpo: { mensaje: 'La invitación fue cancelada.' } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    await usuario.click(await screen.findByRole('button', { name: 'Reenviar la invitación a carla@ejemplo.com' }))
    expect(await screen.findByText('Reenviamos la invitación a carla@ejemplo.com.')).toBeInTheDocument()

    await usuario.click(screen.getByRole('button', { name: 'Cancelar invitación' }))
    expect(screen.getByRole('button', { name: 'Cancelar' })).toHaveFocus()
    await usuario.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(solicitudes.some((s) => s.metodo === 'DELETE')).toBe(false)

    await usuario.click(screen.getByRole('button', { name: 'Cancelar invitación' }))
    await usuario.click(within(screen.getByRole('group', { name: /¿Cancelar la invitación/ })).getByRole('button', { name: 'Cancelar invitación' }))
    expect(await screen.findByText('La invitación fue cancelada.')).toBeInTheDocument()
  })

  it('marca las invitaciones vencidas', async () => {
    apiDeOrganizacion({ invitaciones: [{ ...INVITACION, vigente: false }] })
    renderizarEn('/organizaciones/3')
    expect(await screen.findAllByText('Vencida')).toHaveLength(2)
  })

  it('edita el cargo de un miembro (CA15)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      extra: {
        'PATCH /api/organizaciones/3/miembros/2': { cuerpo: { miembro: BETO, mensaje: 'El cargo fue actualizado.' } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    await usuario.click(await screen.findByRole('button', { name: 'Editar el cargo de Beto Paz' }))
    const campo = screen.getByLabelText(/Cargo de Beto Paz/)
    await usuario.clear(campo)
    await usuario.type(campo, 'Socio')
    await usuario.click(screen.getByRole('button', { name: 'Guardar el cargo' }))
    expect(await screen.findByText('El cargo fue actualizado.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'PATCH').cuerpo).toEqual({ cargo: 'Socio' })
  })

  it('cancelar la edición del cargo no envía nada', async () => {
    const { solicitudes } = apiDeOrganizacion()
    const { usuario } = renderizarEn('/organizaciones/3')
    await usuario.click(await screen.findByRole('button', { name: 'Editar el cargo de Ana López' }))
    await usuario.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(screen.queryByLabelText(/Cargo de Ana/)).not.toBeInTheDocument()
    expect(solicitudes.some((s) => s.metodo === 'PATCH')).toBe(false)
  })

  it('designa Referente y desvincula con confirmación (CA16, CA17)', async () => {
    let organizacion = ORGANIZACION
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones/3': () => ({ cuerpo: { organizacion } }),
      'GET /api/organizaciones/3/miembros': { cuerpo: { miembros: [ANA, BETO] } },
      'GET /api/organizaciones/3/invitaciones': { cuerpo: { invitaciones: [] } },
      'DELETE /api/organizaciones/3/miembros/2': { cuerpo: { mensaje: 'El miembro fue desvinculado de la organización.' } },
      'POST /api/organizaciones/3/referente': () => {
        organizacion = { ...ORGANIZACION, mi_rol: 'miembro' }
        return { cuerpo: { mensaje: 'Designaste un nuevo Referente. Ahora sos miembro.' } }
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    await usuario.click(await screen.findByRole('button', { name: 'Desvincular' }))
    await usuario.click(within(screen.getByRole('group', { name: '¿Desvincular a Beto Paz?' })).getByRole('button', { name: 'Desvincular' }))
    expect(await screen.findByText('El miembro fue desvinculado de la organización.')).toBeInTheDocument()

    await usuario.click(screen.getByRole('button', { name: 'Designar Referente' }))
    await usuario.click(screen.getByRole('button', { name: 'Designar' }))
    expect(await screen.findByText('Sos miembro')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Invitar miembros' })).not.toBeInTheDocument()
  })

  it('guarda los datos de la organización (CA3)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      extra: {
        'PATCH /api/organizaciones/3': { cuerpo: { organizacion: ORGANIZACION, mensaje: 'Los datos de la organización fueron actualizados.' } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    const seccion = (await screen.findByRole('heading', { name: 'Datos de la organización' })).closest('section')
    await usuario.click(within(seccion).getByRole('button', { name: 'Editar los datos de la organización' }))
    await usuario.clear(within(seccion).getByLabelText('Nombre'))
    await usuario.type(within(seccion).getByLabelText('Nombre'), 'Estudio Pérez y Asociados')
    await usuario.click(within(seccion).getByRole('button', { name: 'Guardar los datos' }))
    expect(await screen.findByText('Los datos de la organización fueron actualizados.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'PATCH').cuerpo).toEqual({
      nombre: 'Estudio Pérez y Asociados',
      correo_contacto: '',
      telefono: '11 5555-0000',
    })
  })

  it('el Referente con otros miembros no puede abandonar (CA19)', async () => {
    apiDeOrganizacion()
    renderizarEn('/organizaciones/3')
    expect(await screen.findByText(/primero designá a otro miembro como Referente/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abandonar la organización' })).toBeDisabled()
  })

  it('el único miembro abandona y la organización se elimina (CA19)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      miembros: [ANA],
      invitaciones: [],
      extra: {
        'POST /api/organizaciones/3/abandono': {
          cuerpo: { mensaje: 'Abandonaste la organización y, como eras su único miembro, se eliminó.' },
        },
        'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
        'GET /api/invitaciones': { cuerpo: { invitaciones: [] } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    expect(await screen.findByText(/Sos el único miembro/)).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Abandonar la organización' }))
    await usuario.click(screen.getByRole('button', { name: 'Abandonar' }))
    expect(await screen.findByText(/como eras su único miembro, se eliminó/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta === '/api/organizaciones/3/abandono').cuerpo).toEqual({ confirmar_eliminacion: true })
  })

  it('eliminar exige escribir el nombre exacto (CA20)', async () => {
    const { solicitudes } = apiDeOrganizacion({
      extra: {
        'DELETE /api/organizaciones/3': { cuerpo: { mensaje: 'La organización fue eliminada.' } },
        'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
        'GET /api/invitaciones': { cuerpo: { invitaciones: [] } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    const boton = await screen.findByRole('button', { name: 'Eliminar la organización' })
    const campo = screen.getByLabelText(/escribí el nombre: Estudio Pérez/)
    await usuario.type(campo, 'estudio pérez')
    expect(boton).toBeDisabled()
    await usuario.clear(campo)
    await usuario.type(campo, 'Estudio Pérez')
    await usuario.click(boton)
    expect(await screen.findByText('La organización fue eliminada.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'DELETE').cuerpo).toEqual({ confirmacion: 'Estudio Pérez' })
  })

  it('si una acción de salida falla, se informa', async () => {
    apiDeOrganizacion({
      miembros: [ANA],
      extra: {
        'POST /api/organizaciones/3/abandono': { estado: 500, cuerpo: { mensaje: 'Ocurrió un error inesperado.' } },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/3')
    await usuario.click(await screen.findByRole('button', { name: 'Abandonar la organización' }))
    await usuario.click(screen.getByRole('button', { name: 'Abandonar' }))
    expect(await screen.findByText('Ocurrió un error inesperado.')).toBeInTheDocument()
  })
})

describe('pantalla de la organización como Miembro', () => {
  it('ve los datos y los miembros, sin acciones de Referente (CA22)', async () => {
    apiDeOrganizacion({ organizacion: { ...ORGANIZACION, mi_rol: 'miembro' } })
    renderizarEn('/organizaciones/3')
    expect(await screen.findByText('Sos miembro')).toBeInTheDocument()
    expect(screen.getByText('11 5555-0000')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Invitar miembros' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Editar el cargo/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Eliminar la organización' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abandonar la organización' })).toBeEnabled()
  })

  it('si no pertenece, muestra que no existe (CA4)', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones/3': {
        estado: 404,
        cuerpo: { codigo: 'no_encontrado', mensaje: 'La organización no existe o no tenés acceso a ella.' },
      },
    })
    renderizarEn('/organizaciones/3')
    expect(await screen.findByRole('alert')).toHaveTextContent('no existe o no tenés acceso')
  })
})

describe('enlace de invitación', () => {
  const consulta = (invitacion) => ({
    'POST /api/invitaciones/consulta': { cuerpo: { invitacion: { ...INVITACION, sesion_con_el_correo: false, ...invitacion } } },
  })

  it('sin sesión muestra la invitación y ofrece ingresar o crear la cuenta (CA9)', async () => {
    simularApi(consulta())
    renderizarEn('/invitaciones/responder?token=abc')
    expect(await screen.findByRole('heading', { name: 'Te invitaron a Estudio Pérez' })).toBeInTheDocument()
    expect(screen.getByText('Ana López')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Crear una cuenta' })).toHaveAttribute('href', '/registro?invitacion=abc')
    expect(screen.getByRole('link', { name: 'Iniciar sesión' })).toHaveAttribute('href', '/iniciar-sesion')
  })

  it('crear la cuenta precarga el correo invitado, que no se puede cambiar', async () => {
    simularApi(consulta())
    const { usuario } = renderizarEn('/invitaciones/responder?token=abc')
    await usuario.click(await screen.findByRole('link', { name: 'Crear una cuenta' }))
    await usuario.click(await screen.findByLabelText(/Abogado o abogada/))
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    await usuario.type(screen.getByLabelText('Nombre'), 'Carla')
    await usuario.type(screen.getByLabelText('Apellido'), 'Gómez')
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(screen.getByLabelText('Correo electrónico')).toHaveValue('carla@ejemplo.com')
    expect(screen.getByLabelText('Correo electrónico')).toHaveAttribute('readonly')
    expect(screen.getByText('Paso 4 de 4')).toBeInTheDocument()
  })

  it('iniciar sesión vuelve a la invitación', async () => {
    simularApi({
      ...consulta(),
      'POST /api/sesion': { cuerpo: { usuario: { ...USUARIO, correo: 'carla@ejemplo.com' }, csrf: 't' } },
    })
    const { usuario } = renderizarEn('/invitaciones/responder?token=abc')
    await usuario.click(await screen.findByRole('link', { name: 'Iniciar sesión' }))
    await usuario.type(await screen.findByLabelText('Correo electrónico'), 'carla@ejemplo.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'Segura12345')
    await usuario.click(screen.getByRole('button', { name: 'Ingresar' }))
    expect(await screen.findByRole('heading', { name: 'Te invitaron a Estudio Pérez' })).toBeInTheDocument()
  })

  it('con la sesión del correo invitado acepta y va a la organización (CA10)', async () => {
    apiDeOrganizacion({
      organizacion: { ...ORGANIZACION, mi_rol: 'miembro' },
      extra: {
        ...consulta({ sesion_con_el_correo: true }),
        'POST /api/invitaciones/9/aceptacion': { cuerpo: { mensaje: 'Ya sos miembro de Estudio Pérez.', id_organizacion: 3 } },
      },
    })
    const { usuario } = renderizarEn('/invitaciones/responder?token=abc')
    await usuario.click(await screen.findByRole('button', { name: 'Aceptar la invitación' }))
    expect(await screen.findByText('Ya sos miembro de Estudio Pérez.')).toBeInTheDocument()
  })

  it('con la sesión del correo invitado puede rechazar (CA10)', async () => {
    simularApi({
      ...CON_SESION,
      ...consulta({ sesion_con_el_correo: true }),
      'POST /api/invitaciones/9/rechazo': { cuerpo: { mensaje: 'Rechazaste la invitación.' } },
    })
    const { usuario } = renderizarEn('/invitaciones/responder?token=abc')
    await usuario.click(await screen.findByRole('button', { name: 'Rechazar' }))
    expect(await screen.findByText('Rechazaste la invitación.')).toBeInTheDocument()
  })

  it('si responder falla, muestra el error', async () => {
    simularApi({
      ...CON_SESION,
      ...consulta({ sesion_con_el_correo: true }),
      'POST /api/invitaciones/9/aceptacion': { estado: 409, cuerpo: { mensaje: 'La invitación ya no está vigente.' } },
    })
    const { usuario } = renderizarEn('/invitaciones/responder?token=abc')
    await usuario.click(await screen.findByRole('button', { name: 'Aceptar la invitación' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('ya no está vigente')
  })

  it('con la sesión de otro correo indica con cuál ingresar (CA11)', async () => {
    simularApi({ ...CON_SESION, ...consulta() })
    renderizarEn('/invitaciones/responder?token=abc')
    expect(await screen.findByText(/Iniciaste sesión como ana@ejemplo.com, pero esta invitación es para carla@ejemplo.com/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Aceptar la invitación' })).not.toBeInTheDocument()
  })

  it('una invitación no vigente se informa (CA12)', async () => {
    simularApi(consulta({ vigente: false, cargo: 'Perito' }))
    renderizarEn('/invitaciones/responder?token=abc')
    expect(await screen.findByText(/ya no está vigente/)).toBeInTheDocument()
    expect(screen.getByText('Perito')).toBeInTheDocument()
  })

  it('un enlace alterado se informa (CA12)', async () => {
    simularApi({
      'POST /api/invitaciones/consulta': { estado: 400, cuerpo: { codigo: 'enlace_invalido', mensaje: 'El enlace no es válido. Solicitá uno nuevo.' } },
    })
    renderizarEn('/invitaciones/responder?token=x')
    expect(await screen.findByRole('alert')).toHaveTextContent('El enlace no es válido')
  })
})
