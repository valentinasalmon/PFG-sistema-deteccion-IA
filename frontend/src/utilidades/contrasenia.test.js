/** Pruebas de las reglas de contraseña que se muestran al escribir (CA4). */
import { describe, expect, it } from 'vitest'
import { evaluarContrasenia } from './contrasenia.js'

const cumplidas = (contrasenia) =>
  evaluarContrasenia(contrasenia)
    .filter((regla) => regla.cumplida)
    .map((regla) => regla.id)

describe('evaluarContrasenia', () => {
  it('una contraseña vacía no cumple ninguna regla', () => {
    expect(cumplidas('')).toEqual([])
  })

  it('reconoce longitud, letras (con tilde) y números', () => {
    expect(cumplidas('ñandú12345')).toEqual(['longitud', 'letra', 'numero', 'maximo'])
    expect(cumplidas('1234567890')).toEqual(['longitud', 'numero', 'maximo'])
  })

  it('cuenta bytes para el máximo: las letras con tilde ocupan dos', () => {
    expect(cumplidas('a1'.repeat(36))).toContain('maximo')
    expect(cumplidas('á1'.repeat(36))).not.toContain('maximo')
  })
})
