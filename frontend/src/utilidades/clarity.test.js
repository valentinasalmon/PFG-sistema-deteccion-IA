/**
 * Pruebas de la carga condicional de Microsoft Clarity (034, CA8).
 */
import { afterEach, describe, expect, it } from 'vitest'
import { iniciarClarity } from './clarity.js'

function scriptsDeClarity() {
  return document.querySelectorAll('script[src^="https://www.clarity.ms/tag/"]')
}

afterEach(() => {
  scriptsDeClarity().forEach((script) => script.remove())
  document.body.removeAttribute('data-clarity-mask')
  delete window.clarity
})

describe('Clarity', () => {
  it('no carga nada sin identificador', () => {
    expect(iniciarClarity(undefined)).toBe(false)
    expect(iniciarClarity('')).toBe(false)
    expect(scriptsDeClarity()).toHaveLength(0)
    expect(document.body).not.toHaveAttribute('data-clarity-mask')
  })

  it('rechaza un identificador con formato inválido', () => {
    expect(iniciarClarity('abc"><script>')).toBe(false)
    expect(scriptsDeClarity()).toHaveLength(0)
  })

  it('con identificador carga el script una sola vez y enmascara toda la página', () => {
    expect(iniciarClarity('ab12cd34ef')).toBe(true)
    expect(iniciarClarity('ab12cd34ef')).toBe(true)
    expect(scriptsDeClarity()).toHaveLength(1)
    expect(scriptsDeClarity()[0].src).toBe('https://www.clarity.ms/tag/ab12cd34ef')
    expect(document.body).toHaveAttribute('data-clarity-mask', 'true')
    window.clarity('set', 'prueba', '1')
    expect(window.clarity.q).toEqual([['set', 'prueba', '1']])
  })
})
