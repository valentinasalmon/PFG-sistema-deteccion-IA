/**
 * Pestaña elegida guardada en la dirección de la página (``?seccion=<id>``),
 * para que un enlace la abra directo y el botón Atrás la conserve. La primera
 * pestaña es la de entrada y no se escribe en la dirección.
 *
 * Realiza: RNF10.
 */
import { useSearchParams } from 'react-router'

/**
 * Devuelve la pestaña elegida según la dirección y la función para cambiarla.
 *
 * @param {{id: string}[]} pestanias Pestañas disponibles, la primera es la de entrada.
 */
export function usePestaniaElegida(pestanias) {
  const [parametros, setParametros] = useSearchParams()
  const pedida = parametros.get('seccion')
  const actual = pestanias.some((p) => p.id === pedida) ? pedida : pestanias[0].id

  function elegir(id) {
    setParametros(id === pestanias[0].id ? {} : { seccion: id }, { replace: true })
  }

  return [actual, elegir]
}

