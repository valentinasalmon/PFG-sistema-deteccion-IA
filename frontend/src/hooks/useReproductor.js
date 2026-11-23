/**
 * Reproductor de escenas de la portada (funcionalidad 050, «Qué miramos»).
 *
 * Avanza las escenas como un video: cada una dura lo que dice ``duraciones``
 * y, al terminar la última, vuelve a empezar. Solo corre mientras el elemento
 * está a la vista y la persona no lo pausó; con «reducir movimiento» no
 * arranca solo (WCAG 2.2.2: todo movimiento de más de 5 segundos se puede
 * pausar).
 *
 * Realiza: RF19 (portada); RNF10 (rendimiento y accesibilidad).
 */
import { useEffect, useRef, useState } from 'react'

/** ¿La persona pidió reducir el movimiento? */
export function reducirMovimiento() {
  return typeof window !== 'undefined' && Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)
}

/**
 * Devuelve ``{ escena, ir, reproduciendo, alternar, quieta }``.
 *
 * @param {React.RefObject} refElemento elemento que tiene que estar a la vista.
 * @param {number[]} duraciones milisegundos de cada escena.
 */
export function useReproductor(refElemento, duraciones) {
  const quieta = reducirMovimiento()
  const [escena, setEscena] = useState(quieta ? duraciones.length - 1 : 0)
  const [visible, setVisible] = useState(false)
  const [reproduciendo, setReproduciendo] = useState(!quieta)

  useEffect(() => {
    const elemento = refElemento.current
    if (!elemento || typeof IntersectionObserver === 'undefined') return undefined
    const observador = new IntersectionObserver(([entrada]) => setVisible(entrada.isIntersecting), {
      threshold: 0.35,
    })
    observador.observe(elemento)
    return () => observador.disconnect()
  }, [refElemento])

  // Lo que le falta a la escena actual: al pausar se descuenta lo ya visto, así la
  // barra de avance (que el CSS pausa) y el cambio de escena siguen juntos.
  const restante = useRef(duraciones[escena])
  useEffect(() => {
    restante.current = duraciones[escena]
  }, [escena, duraciones])

  const corriendo = reproduciendo && visible
  useEffect(() => {
    if (!corriendo) return undefined
    const inicio = Date.now()
    const reloj = setTimeout(
      () => setEscena((actual) => (actual + 1) % duraciones.length),
      restante.current,
    )
    return () => {
      clearTimeout(reloj)
      restante.current = Math.max(0, restante.current - (Date.now() - inicio))
    }
  }, [corriendo, escena, duraciones])

  /** Ir a una escena (los capítulos de la lista). Sigue reproduciendo desde ahí. */
  function ir(indice) {
    setEscena(indice)
  }

  function alternar() {
    setReproduciendo((actual) => !actual)
  }

  return { escena, ir, reproduciendo: corriendo, pausado: !reproduciendo, alternar, quieta }
}
