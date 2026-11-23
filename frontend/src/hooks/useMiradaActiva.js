/**
 * Mirada activa de la animación de «Qué miramos» (050).
 *
 * Avanza sola cada ``DURACION_MIRADA`` mientras la sección está a la vista y
 * la persona no pidió «reducir movimiento»; al pasar por una mirada de la
 * lista, muestra esa y se pausa.
 *
 * Realiza: RF19 (portada); RNF10.
 */
import { useEffect, useState } from 'react'

export const DURACION_MIRADA = 2800

/** ¿La persona pidió reducir el movimiento? */
function reducirMovimiento() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
}

/**
 * Hace avanzar la mirada activa cada ``DURACION_MIRADA`` mientras el elemento
 * está en pantalla. Devuelve ``[activa, elegir, quieta]``.
 */
export function useMiradaActiva(refElemento, cantidad) {
  const [activa, setActiva] = useState(0)
  const [visible, setVisible] = useState(false)
  const [pausada, setPausada] = useState(false)
  const quieta = reducirMovimiento()

  useEffect(() => {
    const elemento = refElemento.current
    if (!elemento || typeof IntersectionObserver === 'undefined') return undefined
    const observador = new IntersectionObserver(([entrada]) => setVisible(entrada.isIntersecting), {
      threshold: 0.3,
    })
    observador.observe(elemento)
    return () => observador.disconnect()
  }, [refElemento])

  useEffect(() => {
    if (quieta || !visible || pausada) return undefined
    const reloj = setInterval(() => setActiva((actual) => (actual + 1) % cantidad), DURACION_MIRADA)
    return () => clearInterval(reloj)
  }, [quieta, visible, pausada, cantidad])

  /** Al pasar o enfocar una mirada de la lista, se muestra esa y se pausa el avance. */
  function elegir(indice) {
    setPausada(indice !== null)
    if (indice !== null) setActiva(indice)
  }

  return [activa, elegir, quieta]
}

