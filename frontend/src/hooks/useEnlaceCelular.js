/**
 * Estado del enlace de carga desde el celular (funcionalidades 024 y 028):
 * lo crea y lo cancela, cuenta el tiempo que le queda y, mientras está
 * abierto, actualiza las imágenes del caso cada pocos segundos para que las
 * fotos aparezcan a medida que se suben. Desde la 038 el QR es de un solo
 * uso: cuando el celular toca «Terminar», el panel se cierra solo y avisa
 * cuántas fotos llegaron.
 *
 * Realiza: RF53 (CA2).
 */
import { useCallback, useEffect, useState } from 'react'
import { cancelarEnlaceCarga, crearEnlaceCarga, estadoEnlaceCarga } from '../api/cargaCelular.js'

const INTERVALO_ACTUALIZACION = 4000 // milisegundos

function segundosRestantes(venceEn, ahora) {
  return Math.max(0, Math.round((new Date(`${venceEn}Z`).getTime() - ahora) / 1000))
}

/** Crea y cancela el enlace del celular, y actualiza las imágenes mientras está abierto. */
export function useEnlaceCelular(idCaso, alActualizar) {
  const [enlace, setEnlace] = useState(null)
  const [error, setError] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [ahora, setAhora] = useState(() => Date.now())

  const abrir = useCallback(async () => {
    setError(null)
    setAviso(null)
    try {
      setEnlace(await crearEnlaceCarga(idCaso))
      setAhora(Date.now())
    } catch (errorApi) {
      setError(errorApi.message)
    }
  }, [idCaso])

  const cerrar = useCallback(async () => {
    setEnlace(null)
    await cancelarEnlaceCarga(idCaso).catch(() => {})
  }, [idCaso])

  useEffect(() => {
    if (!enlace) return undefined
    const reloj = setInterval(() => setAhora(Date.now()), 1000)
    const actualizacion = setInterval(async () => {
      await alActualizar()
      const estado = await estadoEnlaceCarga(idCaso).catch(() => null)
      if (estado?.terminado) {
        setEnlace(null)
        const fotos = estado.cargas === 1 ? 'llegó 1 foto' : `llegaron ${estado.cargas} fotos`
        setAviso(`El celular terminó: ${fotos}. Para subir más, mostrá un QR nuevo.`)
      }
    }, INTERVALO_ACTUALIZACION)
    return () => {
      clearInterval(reloj)
      clearInterval(actualizacion)
    }
  }, [enlace, alActualizar, idCaso])

  return {
    enlace,
    error,
    aviso,
    restante: enlace ? segundosRestantes(enlace.vence_en, ahora) : 0,
    abrir,
    cerrar,
  }
}
