/**
 * Hace aparecer los elementos marcados con ``data-aparecer`` cuando entran
 * en pantalla (funcionalidad 033, portada).
 *
 * Agrega la clase ``aparecio``; el CSS define la animación y la apaga con
 * «reducir movimiento». Sin ``IntersectionObserver`` (navegadores viejos o
 * pruebas), todo se muestra de entrada.
 *
 * Realiza: RNF10.
 */
import { useEffect } from 'react'

export function useAparecer(refContenedor) {
  useEffect(() => {
    const contenedor = refContenedor.current
    if (!contenedor) return undefined
    const elementos = contenedor.querySelectorAll('[data-aparecer]')
    if (typeof IntersectionObserver === 'undefined') {
      elementos.forEach((elemento) => elemento.classList.add('aparecio'))
      return undefined
    }
    contenedor.classList.add('portada--animada')
    const observador = new IntersectionObserver(
      (entradas) => {
        entradas.forEach((entrada) => {
          if (entrada.isIntersecting) {
            entrada.target.classList.add('aparecio')
            observador.unobserve(entrada.target)
          }
        })
      },
      { threshold: 0.15 },
    )
    elementos.forEach((elemento) => observador.observe(elemento))
    return () => observador.disconnect()
  }, [refContenedor])
}
