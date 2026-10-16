/**
 * Carga datos de la API al mostrar una pantalla y permite volver a pedirlos.
 *
 * @param {() => Promise<any>} cargar función que trae los datos; si cambia
 *   (por ejemplo, porque depende del identificador de la ruta), se vuelve a
 *   ejecutar. Conviene envolverla en useCallback.
 * @returns {{datos: any, error: import('../api/cliente.js').ErrorApi | null,
 *   cargando: boolean, recargar: () => Promise<void>}}
 */
import { useCallback, useEffect, useState } from 'react'

export function useDatos(cargar) {
  const [estado, setEstado] = useState({ datos: null, error: null, cargando: true })

  const recargar = useCallback(async () => {
    try {
      const datos = await cargar()
      setEstado({ datos, error: null, cargando: false })
    } catch (error) {
      setEstado({ datos: null, error, cargando: false })
    }
  }, [cargar])

  useEffect(() => {
    let vigente = true
    cargar()
      .then((datos) => vigente && setEstado({ datos, error: null, cargando: false }))
      .catch((error) => vigente && setEstado({ datos: null, error, cargando: false }))
    return () => {
      vigente = false
    }
  }, [cargar])

  return { ...estado, recargar }
}
