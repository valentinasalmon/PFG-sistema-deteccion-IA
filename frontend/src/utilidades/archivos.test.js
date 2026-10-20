/**
 * Pruebas del tamaño legible y de la descarga de archivos (funcionalidad 006).
 */
import { describe, expect, it, vi } from 'vitest'
import { abrirDescarga, formatearTamanio } from './archivos.js'

describe('formatearTamanio', () => {
  it('usa B, KB o MB con coma decimal', () => {
    expect(formatearTamanio(512)).toBe('512 B')
    expect(formatearTamanio(1536)).toBe('1,5 KB')
    expect(formatearTamanio(20 * 1024 * 1024)).toBe('20 MB')
  })
})

describe('abrirDescarga', () => {
  it('abre el enlace con un vínculo temporal que después se quita', () => {
    const clic = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    abrirDescarga('/api/archivos/token')
    expect(clic).toHaveBeenCalledTimes(1)
    expect(clic.mock.instances[0].getAttribute('href')).toBe('/api/archivos/token')
    expect(document.querySelector('a[href="/api/archivos/token"]')).toBeNull()
    clic.mockRestore()
  })
})
