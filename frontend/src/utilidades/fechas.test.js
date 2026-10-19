/**
 * Pruebas del formato de fechas: las fechas del backend llegan en UTC y se
 * muestran en la hora de Argentina.
 */
import { describe, expect, it } from 'vitest'
import { formatearFecha } from './fechas.js'

describe('formatearFecha', () => {
  it('interpreta la fecha sin zona como UTC y la muestra en hora argentina', () => {
    // 02:00 UTC del 17 es todavía el 16 en Argentina (UTC-3).
    expect(formatearFecha('2026-10-17T02:00:00')).toBe('16/10/2026')
  })

  it('respeta la zona si viene indicada', () => {
    expect(formatearFecha('2026-10-17T02:00:00Z')).toBe('16/10/2026')
    expect(formatearFecha('2026-10-17T02:00:00+00:00')).toBe('16/10/2026')
  })

  it('sin fecha muestra un guion', () => {
    expect(formatearFecha(null)).toBe('—')
  })
})
