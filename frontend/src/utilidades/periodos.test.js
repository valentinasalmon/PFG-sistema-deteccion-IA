/**
 * Pruebas de los períodos rápidos del tablero (funcionalidad 028).
 */
import { describe, expect, it } from 'vitest'
import { rangoDelPeriodo } from './periodos.js'

const HOY = new Date(2026, 9, 28)

describe('rangoDelPeriodo', () => {
  it.each([
    ['mes', { desde: '2026-10-01', hasta: '2026-10-28' }],
    ['trimestre', { desde: '2026-08-01', hasta: '2026-10-28' }],
    ['anio', { desde: '2026-01-01', hasta: '2026-10-28' }],
    ['inicio', { desde: '', hasta: '' }],
  ])('%s', (periodo, esperado) => {
    expect(rangoDelPeriodo(periodo, HOY)).toEqual(esperado)
  })

  it('el trimestre cruza el cambio de año', () => {
    expect(rangoDelPeriodo('trimestre', new Date(2026, 0, 15)).desde).toBe('2025-11-01')
  })
})
