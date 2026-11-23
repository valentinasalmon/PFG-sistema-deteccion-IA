import { act, render, screen } from '@testing-library/react'
import { useRef } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useReproductor } from './useReproductor.js'

const DURACIONES = [1000, 1000, 1000]
let avisar

function Prueba() {
  const ref = useRef(null)
  const { escena, ir, alternar, pausado, quieta } = useReproductor(ref, DURACIONES)
  return (
    <div ref={ref}>
      <span data-testid="escena">{escena}</span>
      <span data-testid="estado">{quieta ? 'quieta' : pausado ? 'pausado' : 'andando'}</span>
      <button type="button" onClick={() => ir(2)}>ir</button>
      <button type="button" onClick={alternar}>pausa</button>
    </div>
  )
}

describe('reproductor del video de la portada (050)', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    globalThis.IntersectionObserver = class {
      constructor(llamada) {
        avisar = llamada
      }
      observe() {}
      disconnect() {}
    }
  })
  afterEach(() => {
    vi.useRealTimers()
    delete globalThis.IntersectionObserver
  })

  const escena = () => screen.getByTestId('escena').textContent

  it('avanza solo a la vista, vuelve a empezar y sigue desde el capítulo elegido', () => {
    render(<Prueba />)
    act(() => vi.advanceTimersByTime(5000))
    expect(escena()).toBe('0')
    act(() => avisar([{ isIntersecting: true }]))
    act(() => vi.advanceTimersByTime(1000))
    expect(escena()).toBe('1')
    act(() => screen.getByText('ir').click())
    expect(escena()).toBe('2')
    act(() => vi.advanceTimersByTime(1000))
    expect(escena()).toBe('0')
  })

  it('al pausar se detiene y al seguir completa solo lo que faltaba', () => {
    render(<Prueba />)
    act(() => avisar([{ isIntersecting: true }]))
    act(() => vi.advanceTimersByTime(600))
    act(() => screen.getByText('pausa').click())
    expect(screen.getByTestId('estado')).toHaveTextContent('pausado')
    act(() => vi.advanceTimersByTime(5000))
    expect(escena()).toBe('0')
    act(() => screen.getByText('pausa').click())
    act(() => vi.advanceTimersByTime(400))
    expect(escena()).toBe('1')
  })

  it('con «reducir movimiento» arranca quieta en el informe', () => {
    const original = window.matchMedia
    window.matchMedia = () => ({ matches: true })
    render(<Prueba />)
    expect(escena()).toBe('2')
    expect(screen.getByTestId('estado')).toHaveTextContent('quieta')
    window.matchMedia = original
  })
})
