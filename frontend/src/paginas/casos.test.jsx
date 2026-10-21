/**
 * Pruebas de las pantallas de casos (funcionalidad 005).
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CON_SESION, simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'

const TODAS = {
  editar: true,
  cerrar: true,
  archivar: false,
  desarchivar: false,
  reabrir: false,
  compartir: true,
  transferir: true,
  eliminar: true,
}
const NINGUNA = Object.fromEntries(Object.keys(TODAS).map((accion) => [accion, false]))

const CASO = {
  id: 7,
  numero: 'CASO-2026-000007',
  tipo: 'automovilistico',
  tipo_nombre: 'Automovilístico',
  fecha_hecho: '2026-10-01',
  lugar: 'Av. Corrientes 1234',
  expediente: 'EXP-55/2026',
  descripcion: 'Choque en la esquina.',
  estado: 'borrador',
  estado_nombre: 'Borrador',
  espacio: { tipo: 'organizacion', id: 3, nombre: 'Estudio Pérez' },
  responsable: { id: USUARIO.id, nombre: 'Ana López', correo: 'ana@ejemplo.com' },
  mi_permiso: 'responsable',
  mi_permiso_nombre: 'Responsable',
  creado_en: '2026-10-16T12:00:00',
  actualizado_en: '2026-10-16T12:00:00',
  retencion_desde: null,
  retencion_vence: null,
  acciones: TODAS,
  transferencia_pendiente: null,
}
const ORGANIZACION = { id: 3, nombre: 'Estudio Pérez', estado: 'activa', mi_rol: 'referente' }
const MIEMBROS = [
  { id_usuario: USUARIO.id, nombre: 'Ana', apellido: 'López' },
  { id_usuario: 2, nombre: 'Beto', apellido: 'Paz' },
]
const ACCESO = {
  id: 11,
  toda_organizacion: false,
  usuario: { id: 2, nombre: 'Beto Paz', correo: 'beto@ejemplo.com' },
  nivel: 'lectura',
  nivel_nombre: 'Lectura',
  otorgado_en: '2026-10-16T13:00:00',
}

function apiDeListado({ casos = [CASO], total = casos.length, paginas = 1, transferencias = [], extra = {} } = {}) {
  const listado = { cuerpo: { casos, total, pagina: 1, paginas } }
  return simularApi({
    ...CON_SESION,
    'GET /api/casos': listado,
    'GET /api/casos/transferencias': { cuerpo: { transferencias } },
    'GET /api/organizaciones': { cuerpo: { organizaciones: [ORGANIZACION] } },
    ...extra,
  })
}

const SIN_IMAGENES = { imagenes: [], limite: 50, tamanio_maximo: 20971520, puede_modificar: true }

function apiDeCaso({ caso = CASO, accesos = [ACCESO], extra = {} } = {}) {
  return simularApi({
    ...CON_SESION,
    'GET /api/casos/7': { cuerpo: { caso, accesos } },
    'GET /api/organizaciones/3/miembros': { cuerpo: { miembros: MIEMBROS } },
    'GET /api/casos/7/imagenes': { cuerpo: SIN_IMAGENES },
    'GET /api/casos/7/analisis': { cuerpo: { analisis: [] } },
    'GET /api/casos/7/informes': { cuerpo: { informes: [] } },
    ...extra,
  })
}

describe('listado de casos', () => {
  it('lista los casos accesibles con su estado y permiso (CA5)', async () => {
    apiDeListado()
    renderizarEn('/casos')

    const enlace = await screen.findByRole('link', { name: 'CASO-2026-000007' })
    expect(enlace).toHaveAttribute('href', '/casos/7')
    const tarjeta = enlace.closest('li')
    expect(within(tarjeta).getByText('Borrador')).toBeInTheDocument()
    expect(within(tarjeta).getByText('Responsable')).toBeInTheDocument()
    expect(within(tarjeta).getByText(/Estudio Pérez · Hecho del 01\/10\/2026 · EXP-55\/2026/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '1 caso' })).toBeInTheDocument()
  })

  it('busca con los filtros y los guarda en la dirección (CA6)', async () => {
    const { solicitudes } = apiDeListado({
      extra: {
        'GET /api/casos?expediente=exp-55&estado=archivado': { cuerpo: { casos: [], total: 0, pagina: 1, paginas: 1 } },
      },
    })
    const { usuario } = renderizarEn('/casos')
    await screen.findByRole('link', { name: 'CASO-2026-000007' })

    await usuario.type(screen.getByLabelText('Expediente'), 'exp-55')
    await usuario.selectOptions(screen.getByLabelText('Estado'), 'archivado')
    await usuario.click(screen.getByRole('button', { name: 'Buscar' }))

    expect(await screen.findByText('No hay casos con esos filtros.')).toBeInTheDocument()
    expect(solicitudes.map((s) => s.ruta)).toContain('/api/casos?expediente=exp-55&estado=archivado')

    await usuario.click(screen.getByRole('button', { name: 'Limpiar los filtros' }))
    expect(await screen.findByRole('link', { name: 'CASO-2026-000007' })).toBeInTheDocument()
  })

  it('ofrece el espacio personal solo a quienes tienen perfil Abogado', async () => {
    apiDeListado()
    renderizarEn('/casos')
    await screen.findByRole('link', { name: 'CASO-2026-000007' })

    const espacio = screen.getByLabelText('Espacio')
    expect(within(espacio).getByRole('option', { name: 'Personal' })).toBeInTheDocument()
    expect(within(espacio).getByRole('option', { name: 'Estudio Pérez' })).toBeInTheDocument()
  })

  it('pagina los resultados', async () => {
    apiDeListado({
      total: 25,
      paginas: 2,
      extra: {
        'GET /api/casos?pagina=2': {
          cuerpo: { casos: [{ ...CASO, id: 8, numero: 'CASO-2026-000008' }], total: 25, pagina: 2, paginas: 2 },
        },
      },
    })
    const { usuario } = renderizarEn('/casos')
    await screen.findByText('Página 1 de 2')
    expect(screen.getByRole('button', { name: 'Anterior' })).toBeDisabled()

    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }))

    expect(await screen.findByRole('link', { name: 'CASO-2026-000008' })).toBeInTheDocument()
    expect(screen.getByText('Página 2 de 2')).toBeInTheDocument()
  })

  it('invita a crear el primer caso cuando no hay ninguno', async () => {
    apiDeListado({ casos: [] })
    renderizarEn('/casos')

    expect(await screen.findByText('Todavía no tenés casos. Creá el primero.')).toBeInTheDocument()
  })
})

describe('transferencias de casos personales (CA18)', () => {
  const TRANSFERENCIA = {
    id: 9,
    numero: 'CASO-2026-000009',
    tipo_nombre: 'Laboral',
    solicitante: { id: 5, nombre: 'Carla Ruiz', correo: 'carla@ejemplo.com' },
    solicitada_en: '2026-10-16T10:00:00',
  }

  it('acepta un caso y lleva a su pantalla', async () => {
    apiDeListado({
      transferencias: [TRANSFERENCIA],
      extra: {
        'POST /api/casos/9/transferencia/aceptacion': {
          cuerpo: { mensaje: 'Ahora sos Responsable del caso CASO-2026-000009.', id_caso: 9 },
        },
        'GET /api/casos/9/imagenes': { cuerpo: SIN_IMAGENES },
        'GET /api/casos/9/analisis': { cuerpo: { analisis: [] } },
        'GET /api/casos/9/informes': { cuerpo: { informes: [] } },
        'GET /api/casos/9': {
          cuerpo: {
            caso: { ...CASO, id: 9, numero: 'CASO-2026-000009', espacio: { tipo: 'personal', id: null, nombre: 'Personal' } },
            accesos: [],
          },
        },
      },
    })
    const { usuario } = renderizarEn('/casos')

    expect(await screen.findByText(/De Carla Ruiz/)).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Aceptar el caso CASO-2026-000009' }))

    expect(await screen.findByRole('heading', { name: 'CASO-2026-000009' })).toBeInTheDocument()
    expect(screen.getByText('Ahora sos Responsable del caso CASO-2026-000009.')).toBeInTheDocument()
  })

  it('rechaza un caso y vuelve a cargar el listado', async () => {
    let pendientes = [TRANSFERENCIA]
    const { solicitudes } = apiDeListado({
      extra: {
        'GET /api/casos/transferencias': () => ({ cuerpo: { transferencias: pendientes } }),
        'POST /api/casos/9/transferencia/rechazo': () => {
          pendientes = []
          return { cuerpo: { mensaje: 'Rechazaste el caso CASO-2026-000009.' } }
        },
      },
    })
    const { usuario } = renderizarEn('/casos')

    await usuario.click(await screen.findByRole('button', { name: 'Rechazar el caso CASO-2026-000009' }))

    await screen.findByRole('link', { name: 'CASO-2026-000007' })
    expect(screen.queryByText('Casos que te quieren transferir')).not.toBeInTheDocument()
    expect(solicitudes.some((s) => s.ruta === '/api/casos/9/transferencia/rechazo')).toBe(true)
  })
})

describe('nuevo caso', () => {
  it('crea un caso en el espacio elegido y lleva a su pantalla (CA1)', async () => {
    const { solicitudes } = simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': {
        cuerpo: { organizaciones: [ORGANIZACION, { ...ORGANIZACION, id: 4, nombre: 'Pendiente SA', estado: 'pendiente' }] },
      },
      'POST /api/casos': { estado: 201, cuerpo: { caso: CASO, accesos: [], mensaje: 'Se creó el caso.' } },
      'GET /api/casos/7': { cuerpo: { caso: CASO, accesos: [] } },
      'GET /api/casos/7/imagenes': { cuerpo: SIN_IMAGENES },
      'GET /api/casos/7/analisis': { cuerpo: { analisis: [] } },
      'GET /api/casos/7/informes': { cuerpo: { informes: [] } },
      'GET /api/organizaciones/3/miembros': { cuerpo: { miembros: MIEMBROS } },
    })
    const { usuario } = renderizarEn('/casos/nuevo')

    const espacio = await screen.findByLabelText('Espacio de trabajo')
    expect(within(espacio).queryByRole('option', { name: 'Pendiente SA' })).not.toBeInTheDocument()
    await usuario.selectOptions(espacio, '3')
    await usuario.click(screen.getByRole('radio', { name: /Automovilístico/ }))
    await usuario.type(screen.getByLabelText('Fecha del hecho'), '2026-10-01')
    await usuario.type(screen.getByLabelText('Lugar del hecho'), 'Av. Corrientes 1234')
    await usuario.click(screen.getByRole('button', { name: 'Crear caso' }))

    expect(await screen.findByText('Se creó el caso CASO-2026-000007.')).toBeInTheDocument()
    const envio = solicitudes.find((s) => s.metodo === 'POST' && s.ruta === '/api/casos')
    expect(envio.cuerpo).toMatchObject({
      espacio: '3',
      tipo: 'automovilistico',
      fecha_hecho: '2026-10-01',
      lugar: 'Av. Corrientes 1234',
    })
  })

  it('marca los datos obligatorios sin llamar a la API (CA2)', async () => {
    const { solicitudes } = simularApi({ ...CON_SESION, 'GET /api/organizaciones': { cuerpo: { organizaciones: [] } } })
    const { usuario } = renderizarEn('/casos/nuevo')

    await usuario.click(await screen.findByRole('button', { name: 'Crear caso' }))

    expect(screen.getByText('Elegí el tipo de caso.')).toBeInTheDocument()
    expect(screen.getByText('Indicá la fecha del hecho.')).toBeInTheDocument()
    expect(screen.getByText('Indicá el lugar del hecho.')).toBeInTheDocument()
    expect(screen.getByText('Personal')).toBeInTheDocument()
    expect(solicitudes.some((s) => s.metodo === 'POST')).toBe(false)
  })

  it('muestra los errores que devuelve la API', async () => {
    simularApi({
      ...CON_SESION,
      'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
      'POST /api/casos': {
        estado: 422,
        cuerpo: { mensaje: 'Revisá los datos.', errores: { fecha_hecho: 'La fecha del hecho no puede ser futura.' } },
      },
    })
    const { usuario } = renderizarEn('/casos/nuevo')

    await usuario.click(await screen.findByRole('radio', { name: /Laboral/ }))
    await usuario.type(screen.getByLabelText('Fecha del hecho'), '2026-10-01')
    await usuario.type(screen.getByLabelText('Lugar del hecho'), 'Fábrica')
    await usuario.click(screen.getByRole('button', { name: 'Crear caso' }))

    expect(await screen.findByText('La fecha del hecho no puede ser futura.')).toBeInTheDocument()
  })

  it('explica que hace falta una aseguradora aprobada a quien no tiene espacios (CA3)', async () => {
    simularApi({
      'GET /api/sesion': { cuerpo: { usuario: { ...USUARIO, perfil: 'aseguradora', colegio: null } } },
      'GET /api/organizaciones': {
        cuerpo: { organizaciones: [{ ...ORGANIZACION, nombre: 'Seguros Sur', estado: 'pendiente' }] },
      },
    })
    renderizarEn('/casos/nuevo')

    expect(await screen.findByText(/aseguradora aprobada por el Administrador/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Crear caso' })).not.toBeInTheDocument()
  })
})

describe('pantalla del caso', () => {
  it('edita los datos del caso (CA7)', async () => {
    const { solicitudes } = apiDeCaso({
      extra: {
        'PATCH /api/casos/7': {
          cuerpo: { caso: { ...CASO, lugar: 'Av. Santa Fe 100' }, accesos: [ACCESO], mensaje: 'Se guardaron los cambios.' },
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Editar los datos' }))
    const lugar = await screen.findByLabelText('Lugar del hecho')
    await usuario.clear(lugar)
    await usuario.type(lugar, 'Av. Santa Fe 100')
    await usuario.click(screen.getByRole('button', { name: 'Guardar los datos' }))

    expect(await screen.findByText('Se guardaron los cambios.')).toBeInTheDocument()
    const envio = solicitudes.find((s) => s.metodo === 'PATCH')
    expect(envio.cuerpo.lugar).toBe('Av. Santa Fe 100')
  })

  it('con permiso de Lectura muestra los datos sin acciones (CA4)', async () => {
    apiDeCaso({
      caso: {
        ...CASO,
        responsable: { id: 2, nombre: 'Beto Paz', correo: 'beto@ejemplo.com' },
        mi_permiso: 'lectura',
        mi_permiso_nombre: 'Lectura',
        acciones: NINGUNA,
        transferencia_pendiente: undefined,
      },
      accesos: [{ ...ACCESO, usuario: { id: USUARIO.id, nombre: 'Ana López', correo: 'ana@ejemplo.com' } }],
    })
    renderizarEn('/casos/7')

    expect(await screen.findByText('Av. Corrientes 1234')).toBeInTheDocument()
    expect(screen.getByText('Beto Paz')).toBeInTheDocument()
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Guardar los datos' })).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Estado' })).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Transferir' })).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Eliminar el caso' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Compartir el caso' })).not.toBeInTheDocument()
  })

  it('cierra el caso con confirmación y muestra el plazo de retención (CA8, CA9)', async () => {
    let caso = CASO
    const { solicitudes } = apiDeCaso({
      extra: {
        'GET /api/casos/7': () => ({ cuerpo: { caso, accesos: [] } }),
        'POST /api/casos/7/estado': () => {
          caso = {
            ...CASO,
            estado: 'cerrado',
            estado_nombre: 'Cerrado',
            retencion_vence: '2031-10-16T12:00:00',
            acciones: { ...TODAS, editar: false, cerrar: false, archivar: true, reabrir: true },
          }
          return { cuerpo: { caso, accesos: [], mensaje: 'El caso quedó cerrado.' } }
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Cerrar el caso' }))
    await usuario.click(screen.getByRole('button', { name: 'Cerrar' }))

    expect(await screen.findByText('El caso quedó cerrado.')).toBeInTheDocument()
    expect(await screen.findByText(/Los datos se conservan hasta el 16\/10\/2031/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Archivar' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Reabrir' })).toBeInTheDocument()
    expect(screen.getByText(/es de solo lectura/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta === '/api/casos/7/estado').cuerpo).toEqual({ operacion: 'cerrar' })
  })

  it('comparte el caso con un miembro y cambia o revoca accesos (CA12, CA13)', async () => {
    const { solicitudes } = apiDeCaso({
      extra: {
        'POST /api/casos/7/accesos': { cuerpo: { caso: CASO, accesos: [ACCESO], mensaje: 'Compartiste el caso.' } },
        'PATCH /api/casos/7/accesos/11': { cuerpo: { caso: CASO, accesos: [ACCESO], mensaje: 'Se cambió el permiso.' } },
        'DELETE /api/casos/7/accesos/11': { cuerpo: { caso: CASO, accesos: [], mensaje: 'Se revocó el acceso.' } },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    const conQuien = await screen.findByLabelText('Con quién')
    expect(within(conQuien).queryByRole('option', { name: 'Ana López' })).not.toBeInTheDocument()
    await usuario.selectOptions(conQuien, '2')
    await usuario.selectOptions(screen.getByLabelText('Permiso'), 'colaboracion')
    await usuario.click(screen.getByRole('button', { name: 'Compartir el caso' }))
    expect(await screen.findByText('Compartiste el caso.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo).toEqual({ nivel: 'colaboracion', id_usuario: 2 })

    await usuario.selectOptions(screen.getByLabelText('Permiso de Beto Paz'), 'colaboracion')
    expect(await screen.findByText('Se cambió el permiso.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'PATCH').cuerpo).toEqual({ nivel: 'colaboracion' })

    await usuario.click(screen.getByRole('button', { name: 'Revocar' }))
    await usuario.click(screen.getByRole('button', { name: 'Revocar' }))
    expect(await screen.findByText('Se revocó el acceso.')).toBeInTheDocument()
  })

  it('comparte con toda la organización por defecto', async () => {
    const { solicitudes } = apiDeCaso({
      accesos: [],
      extra: { 'POST /api/casos/7/accesos': { cuerpo: { caso: CASO, accesos: [], mensaje: 'Compartiste el caso.' } } },
    })
    const { usuario } = renderizarEn('/casos/7')

    expect(await screen.findByText('Solo el Responsable tiene acceso a este caso.')).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Compartir el caso' }))

    await screen.findByText('Compartiste el caso.')
    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo).toEqual({ nivel: 'lectura', id_usuario: null })
  })

  it('transfiere un caso de organización a otro miembro (CA15)', async () => {
    const { solicitudes } = apiDeCaso({
      extra: { 'POST /api/casos/7/transferencia': { cuerpo: { caso: CASO, accesos: [], mensaje: 'Transferiste el caso.' } } },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.selectOptions(await screen.findByLabelText('Nuevo Responsable'), '2')
    await usuario.click(screen.getByRole('checkbox', { name: 'Conservar el permiso de Colaboración' }))
    await usuario.click(screen.getByRole('button', { name: 'Transferir el caso' }))

    expect(await screen.findByText('Transferiste el caso.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo).toEqual({ destino: '2', conservar_colaboracion: false })
  })

  it('pide la transferencia de un caso personal por correo y permite cancelarla (CA17)', async () => {
    const personal = { ...CASO, espacio: { tipo: 'personal', id: null, nombre: 'Personal' }, acciones: { ...TODAS, compartir: false } }
    let caso = personal
    const { solicitudes } = apiDeCaso({
      extra: {
        'GET /api/casos/7': () => ({ cuerpo: { caso, accesos: [] } }),
        'POST /api/casos/7/transferencia': () => {
          caso = { ...personal, transferencia_pendiente: { id: 5, nombre: 'Carla Ruiz', correo: 'carla@ejemplo.com' } }
          return { cuerpo: { caso, accesos: [], mensaje: 'Le pedimos a Carla Ruiz que acepte el caso.' } }
        },
        'DELETE /api/casos/7/transferencia': () => {
          caso = personal
          return { cuerpo: { caso, accesos: [], mensaje: 'Cancelaste la transferencia.' } }
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    expect(await screen.findByRole('heading', { name: 'Transferir' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Accesos' })).not.toBeInTheDocument()
    await usuario.type(screen.getByLabelText('Correo de la persona'), 'carla@ejemplo.com')
    await usuario.click(screen.getByRole('button', { name: 'Transferir el caso' }))

    expect(await screen.findByText(/Seguís siendo Responsable hasta que lo acepte/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'POST').cuerpo.destino).toBe('carla@ejemplo.com')
    expect(solicitudes.some((s) => s.ruta === '/api/organizaciones/3/miembros')).toBe(false)

    await usuario.click(screen.getByRole('button', { name: 'Cancelar la transferencia' }))
    expect(await screen.findByText('Cancelaste la transferencia.')).toBeInTheDocument()
    expect(screen.getByLabelText('Correo de la persona')).toBeInTheDocument()
  })

  it('elimina el caso solo al escribir su número (CA19)', async () => {
    const { solicitudes } = apiDeCaso({
      extra: {
        'DELETE /api/casos/7': { cuerpo: { mensaje: 'El caso fue eliminado.' } },
        'GET /api/casos': { cuerpo: { casos: [], total: 0, pagina: 1, paginas: 1 } },
        'GET /api/casos/transferencias': { cuerpo: { transferencias: [] } },
        'GET /api/organizaciones': { cuerpo: { organizaciones: [] } },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    const boton = await screen.findByRole('button', { name: 'Eliminar el caso' })
    expect(boton).toBeDisabled()
    await usuario.type(screen.getByLabelText(/escribí el número/), 'caso-2026-000007')
    expect(boton).toBeEnabled()
    await usuario.click(boton)

    expect(await screen.findByText('El caso fue eliminado.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Casos' })).toBeInTheDocument()
    expect(solicitudes.find((s) => s.metodo === 'DELETE').cuerpo).toEqual({ confirmacion: 'caso-2026-000007' })
  })

  it('muestra el error de la API al eliminar', async () => {
    apiDeCaso({
      extra: { 'DELETE /api/casos/7': { estado: 409, cuerpo: { mensaje: 'El caso está en análisis.' } } },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.type(await screen.findByLabelText(/escribí el número/), 'CASO-2026-000007')
    await usuario.click(screen.getByRole('button', { name: 'Eliminar el caso' }))

    expect(await screen.findByText('El caso está en análisis.')).toBeInTheDocument()
  })

  it('muestra un caso inexistente o sin permiso como no encontrado (RNF05)', async () => {
    simularApi({ ...CON_SESION, 'GET /api/casos/99': { estado: 404, cuerpo: { mensaje: 'No encontramos el caso.' } } })
    renderizarEn('/casos/99')

    expect(await screen.findByText('No encontramos el caso.')).toBeInTheDocument()
  })

  it('muestra el error de una acción sin perder la pantalla', async () => {
    apiDeCaso({
      extra: { 'POST /api/casos/7/estado': { estado: 409, cuerpo: { mensaje: 'No se puede cerrar en este estado.' } } },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Cerrar el caso' }))
    await usuario.click(screen.getByRole('button', { name: 'Cerrar' }))

    expect(await screen.findByText('No se puede cerrar en este estado.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'CASO-2026-000007' })).toBeInTheDocument()
  })
})

describe('retención (funcionalidad 015)', () => {
  const CERRADO = {
    ...CASO, estado: 'cerrado', estado_nombre: 'Cerrado',
    retencion_desde: '2021-11-01T12:00:00', retencion_vence: '2026-11-01T12:00:00',
    acciones: { ...TODAS, editar: false, cerrar: false, archivar: true, reabrir: true, prorrogar: true },
  }

  it('muestra cuándo se elimina y prorroga con motivo obligatorio (RF51)', async () => {
    const { solicitudes } = apiDeCaso({
      caso: CERRADO,
      extra: {
        'POST /api/casos/7/prorroga': {
          cuerpo: { caso: { ...CERRADO, retencion_vence: '2027-11-01T12:00:00' }, accesos: [ACCESO], mensaje: 'Listo: el caso se conserva hasta el 01/11/2027.' },
        },
      },
    })
    const { usuario } = renderizarEn('/casos/7')

    await usuario.click(await screen.findByRole('button', { name: 'Prorrogar 1 año' }))
    await usuario.click(screen.getByRole('button', { name: 'Prorrogar' }))
    expect(screen.getByText(/Indicá el motivo de la prórroga/)).toBeInTheDocument()

    await usuario.type(screen.getByLabelText('Motivo de la prórroga'), 'Juicio en trámite')
    await usuario.click(screen.getByRole('button', { name: 'Prorrogar' }))

    expect(await screen.findByText('Listo: el caso se conserva hasta el 01/11/2027.')).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta === '/api/casos/7/prorroga').cuerpo).toEqual({ motivo: 'Juicio en trámite' })
  })
})
