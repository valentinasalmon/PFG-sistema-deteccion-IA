/**
 * Pruebas del vocabulario por rubro (037): todas las frases salen de una palabra.
 */
import { describe, expect, it } from 'vitest'
import { textosDelRubro, vocabulario } from './lenguaje.js'

describe('vocabulario', () => {
  it('arma todas las frases a partir del singular y el plural', () => {
    expect(vocabulario('siniestro', 'siniestros')).toMatchObject({
      Casos: 'Siniestros',
      nuevo: 'Nuevo siniestro',
      recientes: 'Siniestros recientes',
      verTodos: 'Ver todos los siniestros',
      buscar: 'Buscar un siniestro',
      tipo: 'Tipo de siniestro',
    })
  })

  it('cada perfil usa su palabra y uno desconocido usa la de abogados', () => {
    expect(textosDelRubro('aseguradora').nuevo).toBe('Nuevo siniestro')
    expect(textosDelRubro('abogado').nuevo).toBe('Nuevo caso')
    expect(textosDelRubro(undefined).Casos).toBe('Casos')
  })
})
