/**
 * Pruebas del cliente HTTP: JSON, CSRF y traducción de errores
 * (CA21 y CA22 de la funcionalidad 002).
 */
import { describe, expect, it, vi } from 'vitest'
import { simularApi } from '../pruebas/api.js'
import { configurarAlExpirarSesion, definirTokenCsrf, ErrorApi, solicitar } from './cliente.js'

describe('solicitar', () => {
  it('devuelve el cuerpo JSON de una respuesta exitosa', async () => {
    simularApi({ 'GET /api/perfil': { cuerpo: { usuario: { nombre: 'Ana' } } } })
    await expect(solicitar('GET', '/api/perfil')).resolves.toEqual({ usuario: { nombre: 'Ana' } })
  })

  it('no pide token CSRF para las consultas', async () => {
    const { solicitudes } = simularApi({ 'GET /api/perfil': { cuerpo: {} } })
    await solicitar('GET', '/api/perfil')
    expect(solicitudes.map((s) => s.ruta)).toEqual(['/api/perfil'])
  })

  it('pide el token CSRF una vez y lo envía en las solicitudes que modifican datos (CA21)', async () => {
    const { solicitudes } = simularApi({ 'PATCH /api/perfil': { cuerpo: {} } })
    await solicitar('PATCH', '/api/perfil', { nombre: 'Ana' })
    await solicitar('PATCH', '/api/perfil', { nombre: 'Ana' })
    const pedidosCsrf = solicitudes.filter((s) => s.ruta === '/api/sesion/csrf')
    expect(pedidosCsrf).toHaveLength(1)
    expect(solicitudes.at(-1).cabeceras['X-CSRFToken']).toBe('token-csrf')
    expect(solicitudes.at(-1).cuerpo).toEqual({ nombre: 'Ana' })
  })

  it('usa el token CSRF definido al iniciar sesión', async () => {
    const { solicitudes } = simularApi({ 'DELETE /api/sesion': { cuerpo: {} } })
    definirTokenCsrf('token-de-la-sesion')
    await solicitar('DELETE', '/api/sesion')
    expect(solicitudes).toHaveLength(1)
    expect(solicitudes[0].cabeceras['X-CSRFToken']).toBe('token-de-la-sesion')
  })

  it('renueva el token y reintenta una vez si el backend lo rechaza', async () => {
    let intentos = 0
    const { solicitudes } = simularApi({
      'POST /api/cuentas/recuperacion': () => {
        intentos += 1
        return intentos === 1
          ? { estado: 400, cuerpo: { codigo: 'csrf_invalido', mensaje: 'Expiró.' } }
          : { estado: 200, cuerpo: { mensaje: 'Listo' } }
      },
    })
    definirTokenCsrf('token-vencido')
    await expect(solicitar('POST', '/api/cuentas/recuperacion', {})).resolves.toEqual({
      mensaje: 'Listo',
    })
    expect(solicitudes.filter((s) => s.ruta === '/api/sesion/csrf')).toHaveLength(1)
  })

  it('convierte los errores en ErrorApi con el mensaje y los errores por campo', async () => {
    simularApi({
      'POST /api/cuentas/registro': {
        estado: 400,
        cuerpo: { codigo: 'datos_invalidos', mensaje: 'Revisá los datos marcados.', errores: { correo: 'No es válido.' } },
      },
    })
    const error = await solicitar('POST', '/api/cuentas/registro', {}).catch((e) => e)
    expect(error).toBeInstanceOf(ErrorApi)
    expect(error.estado).toBe(400)
    expect(error.codigo).toBe('datos_invalidos')
    expect(error.message).toBe('Revisá los datos marcados.')
    expect(error.errores).toEqual({ correo: 'No es válido.' })
  })

  it('usa un mensaje genérico si la respuesta de error no trae cuerpo JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 502, json: async () => { throw new SyntaxError() } }),
    )
    const error = await solicitar('GET', '/api/perfil').catch((e) => e)
    expect(error.estado).toBe(502)
    expect(error.message).toMatch(/error inesperado/)
  })

  it('informa la falta de conexión', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const error = await solicitar('GET', '/api/perfil').catch((e) => e)
    expect(error.codigo).toBe('sin_conexion')
  })

  it('avisa cuando la sesión venció (CA12, CA22)', async () => {
    simularApi({
      'GET /api/perfil': { estado: 401, cuerpo: { codigo: 'sesion_requerida', mensaje: 'Iniciá sesión.' } },
    })
    const alExpirar = vi.fn()
    configurarAlExpirarSesion(alExpirar)
    await expect(solicitar('GET', '/api/perfil')).rejects.toBeInstanceOf(ErrorApi)
    expect(alExpirar).toHaveBeenCalledOnce()
  })
})
