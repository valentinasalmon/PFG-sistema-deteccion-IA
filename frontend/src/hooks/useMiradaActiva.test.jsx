import { act, render, screen } from '@testing-library/react'
import { useRef } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { DURACION_MIRADA, useMiradaActiva } from './useMiradaActiva.js'

let avisar

function Prueba() {
  const ref = useRef(null)
  const [activa, elegir, quieta] = useMiradaActiva(ref, 4)
  return (
    <div ref={ref}>
      <span data-testid="activa">{quieta ? 'quieta' : activa}</span>
      <button type="button" onClick={() => elegir(2)}>elegir</button>
    </div>
  )
}

describe('mirada activa de la portada (050)', () => {
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

  it('avanza solo mientras se ve y se pausa al elegir una', () => {
    render(<Prueba />)
    act(() => vi.advanceTimersByTime(DURACION_MIRADA * 2))
    expect(screen.getByTestId('activa')).toHaveTextContent('0')
    act(() => avisar([{ isIntersecting: true }]))
    act(() => vi.advanceTimersByTime(DURACION_MIRADA))
    expect(screen.getByTestId('activa')).toHaveTextContent('1')
    act(() => screen.getByRole('button').click())
    act(() => vi.advanceTimersByTime(DURACION_MIRADA * 3))
    expect(screen.getByTestId('activa')).toHaveTextContent('2')
  })

  it('con «reducir movimiento» queda quieta', () => {
    const original = window.matchMedia
    window.matchMedia = () => ({ matches: true })
    render(<Prueba />)
    expect(screen.getByTestId('activa')).toHaveTextContent('quieta')
    window.matchMedia = original
  })
})
