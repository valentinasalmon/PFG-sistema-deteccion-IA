import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { simularApi } from '../pruebas/api.js'
import { cabecerasRecaptcha, reiniciarRecaptcha } from './recaptcha.js'

describe('reCAPTCHA en los formularios públicos (051)', () => {
  beforeEach(() => reiniciarRecaptcha())
  afterEach(() => {
    delete window.grecaptcha
    document.head.querySelectorAll('script[src*="recaptcha"]').forEach((s) => s.remove())
  })

  it('desactivado: no carga el script ni manda cabecera', async () => {
    simularApi({ 'GET /api/recaptcha/configuracion': { cuerpo: { habilitado: false, clave_sitio: null } } })
    expect(await cabecerasRecaptcha('registro')).toEqual({})
    expect(document.head.querySelector('script[src*="recaptcha"]')).toBeNull()
  })

  it('activo: carga el script con la clave del backend y manda el token de la acción', async () => {
    simularApi({ 'GET /api/recaptcha/configuracion': { cuerpo: { habilitado: true, clave_sitio: 'clave-123' } } })
    const ejecutar = vi.fn().mockResolvedValue('token-xyz')
    const pedido = cabecerasRecaptcha('inicio_sesion')
    await vi.waitFor(() => expect(document.head.querySelector('script[src*="recaptcha"]')).not.toBeNull())
    const etiqueta = document.head.querySelector('script[src*="recaptcha"]')
    expect(etiqueta.src).toBe('https://www.google.com/recaptcha/enterprise.js?render=clave-123')
    window.grecaptcha = { enterprise: { ready: (listo) => listo(), execute: ejecutar } }
    etiqueta.onload()
    expect(await pedido).toEqual({ 'X-Recaptcha': 'token-xyz' })
    expect(ejecutar).toHaveBeenCalledWith('clave-123', { action: 'inicio_sesion' })
  })

  it('si el script no carga, sigue sin cabecera (el backend explica el rechazo)', async () => {
    simularApi({ 'GET /api/recaptcha/configuracion': { cuerpo: { habilitado: true, clave_sitio: 'clave-123' } } })
    const pedido = cabecerasRecaptcha('registro')
    await vi.waitFor(() => expect(document.head.querySelector('script[src*="recaptcha"]')).not.toBeNull())
    document.head.querySelector('script[src*="recaptcha"]').onerror()
    expect(await pedido).toEqual({})
  })
})
