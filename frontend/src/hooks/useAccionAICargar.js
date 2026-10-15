/**
 * Ejecuta una acción una sola vez al mostrar la pantalla, por ejemplo,
 * confirmar el token de un enlace recibido por correo.
 *
 * Los enlaces son de un solo uso: si la acción se ejecutara dos veces (como
 * ocurre en desarrollo con StrictMode, que monta los componentes dos veces),
 * la segunda fallaría con "enlace ya utilizado". La referencia lo evita.
 *
 * @param {() => Promise<any>} accion
 * @param {boolean} [lista=true] false para esperar (por ejemplo, a que se
 *   conozca la sesión) antes de ejecutar.
 * @returns {{estado: 'cargando' | 'exito' | 'error', error: import('../api/cliente.js').ErrorApi | null}}
 */
import { useEffect, useRef, useState } from 'react'

export function useAccionAlCargar(accion, lista = true) {
  const [resultado, setResultado] = useState({ estado: 'cargando', error: null })
  const ejecutada = useRef(false)

  useEffect(() => {
    if (!lista || ejecutada.current) return
    ejecutada.current = true
    accion()
      .then(() => setResultado({ estado: 'exito', error: null }))
      .catch((error) => setResultado({ estado: 'error', error }))
  }, [accion, lista])

  return resultado
}
