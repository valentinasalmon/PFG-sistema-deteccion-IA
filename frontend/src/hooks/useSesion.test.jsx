/** Pruebas del hook useSesion. */
import { renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { useSesion } from './useSesion.js'

describe('useSesion', () => {
  it('avisa con claridad si se usa fuera del proveedor de sesión', () => {
    expect(() => renderHook(() => useSesion())).toThrow('dentro de <ProveedorSesion>')
  })
})
