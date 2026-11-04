/**
 * Pruebas de la verificación de identidad del Referente de una aseguradora
 * (funcionalidad 035): sección en la organización, página pública simulada y
 * aprobación bloqueada en Administración (RN41).
 */
import { screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { simularApi, USUARIO } from '../pruebas/api.js'
import { renderizarEn } from '../pruebas/renderizar.jsx'
import { navegador } from '../utilidades/identidad.js'

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
const SESION = {
  'GET /api/sesion': { cuerpo: { usuario: { ...USUARIO, perfil: 'aseguradora', empresa: 'SEGUROS GALICIA S.A.' } } },
}
const SESION_ADMINISTRADOR = {
  'GET /api/sesion': { cuerpo: { usuario: { ...USUARIO, rol: 'administrador' } } },
  'GET /api/administracion/tablero?': {
    cuerpo: {
      tablero: {
        usuarios_por_perfil: {},
        organizaciones_por_tipo: {},
        organizaciones_por_plan: {},
        casos_por_estado: {},
        casos_por_tipo: {},
        analisis_por_mes: {},
        altas_por_mes: {},
      },
    },
  },
  'GET /api/administracion/usuarios?pagina=1': { cuerpo: { usuarios: [], total: 0, pagina: 1, paginas: 1 } },
}
const PENDIENTE = {
  id: 7,
  nombre: 'SEGUROS GALICIA S.A.',
  cuit: '30500000127',
  creada_en: '2026-10-16T12:00:00',
  plan: 'basico',
  referente: { nombre: 'Rita López', correo: 'rita@galicia.com', verificado: true },
}

function identidad(estado, cambios = {}) {
  return { activa: true, corresponde: true, estado, creada_en: null, resuelta_en: null, motivo: null, ...cambios }
}

function apiDeOrganizacion(estadoIdentidad, extra = {}, organizacion = ASEGURADORA) {
  return simularApi({
    ...SESION,
    'GET /api/organizaciones/7': { cuerpo: { organizacion } },
    'GET /api/organizaciones/7/miembros': { cuerpo: { miembros: [RITA] } },
    'GET /api/organizaciones/7/invitaciones': { cuerpo: { invitaciones: [] } },
    'GET /api/organizaciones/7/identidad': { cuerpo: { identidad: estadoIdentidad } },
    ...extra,
  })
}

afterEach(() => vi.restoreAllMocks())

describe('sección de identidad en la organización', () => {
  it('el Referente inicia la verificación y va al enlace (CA1)', async () => {
    const ir = vi.spyOn(navegador, 'ir').mockImplementation(() => {})
    const { solicitudes } = apiDeOrganizacion(identidad('sin_verificar'), {
      'POST /api/organizaciones/7/identidad': {
        estado: 201,
        cuerpo: { url: 'http://localhost/identidad/tok', mensaje: 'Abrí el enlace.' },
      },
    })
    const { usuario } = renderizarEn('/organizaciones/7')
    expect(await screen.findByText('Identidad sin verificar')).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Verificar mi identidad' }))
    expect(solicitudes.some((s) => s.metodo === 'POST' && s.ruta.endsWith('/identidad'))).toBe(true)
    expect(ir).toHaveBeenCalledWith('http://localhost/identidad/tok')
  })

  it('un error al iniciar se muestra', async () => {
    apiDeOrganizacion(identidad('sin_verificar'), {
      'POST /api/organizaciones/7/identidad': { estado: 400, cuerpo: { mensaje: 'La verificación de identidad no está activa.' } },
    })
    const { usuario } = renderizarEn('/organizaciones/7')
    await usuario.click(await screen.findByRole('button', { name: 'Verificar mi identidad' }))
    expect(await screen.findByText('La verificación de identidad no está activa.')).toBeInTheDocument()
  })

  it('aprobada no ofrece verificar otra vez; rechazada muestra el motivo (CA7)', async () => {
    apiDeOrganizacion(identidad('aprobada'))
    renderizarEn('/organizaciones/7')
    expect(await screen.findByText('Identidad verificada')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Verificar mi identidad' })).not.toBeInTheDocument()
  })

  it('después de un rechazo se puede intentar de nuevo (CA7)', async () => {
    apiDeOrganizacion(identidad('rechazada', { motivo: 'Rechazada en la simulación.' }))
    renderizarEn('/organizaciones/7')
    expect(await screen.findByText('Motivo: Rechazada en la simulación.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Verificar mi identidad' })).toBeInTheDocument()
  })

  it('un miembro ve el estado pero no inicia (CA2)', async () => {
    apiDeOrganizacion(identidad('pendiente'), {}, { ...ASEGURADORA, mi_rol: 'miembro' })
    renderizarEn('/organizaciones/7')
    expect(await screen.findByText('Verificación en curso')).toBeInTheDocument()
    expect(screen.getByText('La verificación la hace el Referente de la aseguradora.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Verificar mi identidad' })).not.toBeInTheDocument()
  })

  it('con la verificación desactivada no se muestra', async () => {
    apiDeOrganizacion(identidad('sin_verificar', { activa: false }))
    renderizarEn('/organizaciones/7')
    expect(await screen.findByText(/pendiente de aprobación/)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /Verificación de identidad/ })).not.toBeInTheDocument()
  })
})

describe('página pública de la verificación', () => {
  const VERIFICACION = { aseguradora: 'SEGUROS GALICIA S.A.', simulada: true, ...identidad('pendiente') }

  it('aclara que es simulada y registra el resultado aprobado (CA6)', async () => {
    const { solicitudes } = simularApi({
      'GET /api/sesion': { estado: 401, cuerpo: { mensaje: 'Iniciá sesión.' } },
      'GET /api/identidad/tok': { cuerpo: { verificacion: VERIFICACION } },
      'POST /api/identidad/tok/simulacion': {
        cuerpo: { verificacion: identidad('aprobada'), mensaje: 'Se registró el resultado (simulado).' },
      },
    })
    const { usuario } = renderizarEn('/identidad/tok')
    expect(await screen.findByText(/Esta verificación es una simulación/)).toBeInTheDocument()
    expect(screen.getByText('SEGUROS GALICIA S.A.')).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Simular verificación aprobada' }))
    expect(await screen.findByText(/Tu identidad quedó verificada/)).toBeInTheDocument()
    expect(solicitudes.find((s) => s.ruta.endsWith('/simulacion')).cuerpo).toEqual({ resultado: 'aprobada' })
  })

  it('el rechazo simulado indica cómo reintentar', async () => {
    simularApi({
      'GET /api/sesion': { estado: 401, cuerpo: { mensaje: 'Iniciá sesión.' } },
      'GET /api/identidad/tok': { cuerpo: { verificacion: VERIFICACION } },
      'POST /api/identidad/tok/simulacion': { cuerpo: { verificacion: identidad('rechazada') } },
    })
    const { usuario } = renderizarEn('/identidad/tok')
    await usuario.click(await screen.findByRole('button', { name: 'Simular rechazo' }))
    expect(await screen.findByText(/La verificación fue rechazada/)).toBeInTheDocument()
  })

  it('un enlace inválido muestra el error', async () => {
    simularApi({
      'GET /api/sesion': { estado: 401, cuerpo: { mensaje: 'Iniciá sesión.' } },
      'GET /api/identidad/malo': {
        estado: 404,
        cuerpo: { mensaje: 'El enlace de verificación no existe o ya no es válido.', codigo: 'verificacion_invalida' },
      },
    })
    renderizarEn('/identidad/malo')
    expect(await screen.findByText('El enlace de verificación no existe o ya no es válido.')).toBeInTheDocument()
  })

  it('con el proveedor real no ofrece simular', async () => {
    simularApi({
      'GET /api/sesion': { estado: 401, cuerpo: { mensaje: 'Iniciá sesión.' } },
      'GET /api/identidad/tok': { cuerpo: { verificacion: { ...VERIFICACION, simulada: false } } },
    })
    renderizarEn('/identidad/tok')
    expect(await screen.findByText(/Completá la verificación en la página del proveedor/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Simular rechazo' })).not.toBeInTheDocument()
  })
})

describe('aprobación en Administración (RN41)', () => {
  it('sin la identidad aprobada, «Aprobar» queda deshabilitado (CA4, CA5)', async () => {
    simularApi({
      ...SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': {
        cuerpo: { verificacion_identidad: true, aseguradoras: [{ ...PENDIENTE, identidad: identidad('pendiente') }] },
      },
    })
    renderizarEn('/administracion')
    expect(await screen.findByText('Verificación en curso')).toBeInTheDocument()
    expect(screen.getByText(/cuando el Referente verifique su identidad/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Aprobar' })).toBeDisabled()
  })

  it('con la identidad aprobada se puede aprobar', async () => {
    simularApi({
      ...SESION_ADMINISTRADOR,
      'GET /api/administracion/aseguradoras-pendientes': {
        cuerpo: { verificacion_identidad: true, aseguradoras: [{ ...PENDIENTE, identidad: identidad('aprobada') }] },
      },
    })
    renderizarEn('/administracion')
    const tarjeta = (await screen.findByText('Identidad verificada')).closest('li')
    expect(within(tarjeta).getByRole('button', { name: 'Aprobar' })).toBeEnabled()
  })
})
