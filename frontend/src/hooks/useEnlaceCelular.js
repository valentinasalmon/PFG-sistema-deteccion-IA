/**
 * Estado del enlace de carga desde el celular (funcionalidades 024 y 028):
 * lo crea y lo cancela, cuenta el tiempo que le queda y, mientras está
 * abierto, actualiza las imágenes del caso cada pocos segundos para que las
 * fotos aparezcan a medida que se suben.
 *
 * Realiza: RF53 (CA2).
 */
import { useCallback, useEffect, useState } from 'react'
import { cancelarEnlaceCarga, crearEnlaceCarga } from '../api/cargaCelular.js'

const INTERVALO_ACTUALIZACION = 4000 // milisegundos

function segundosRestantes(venceEn, ahora) {
  return Math.max(0, Math.round((new Date(`${venceEn}Z`).getTime() - ahora) / 1000))
}

/** Crea y cancela el enlace del celular, y actualiza las imágenes mientras está abierto. */
export function useEnlaceCelular(idCaso, alActualizar) {
  const [enlace, setEnlace] = useState(null)
  const [error, setError] = useState(null)
  const [ahora, setAhora] = useState(() => Date.now())

  const abrir = useCallback(async () => {
    setError(null)
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
    const actualizacion = setInterval(() => alActualizar(), INTERVALO_ACTUALIZACION)
    return () => {
      clearInterval(reloj)
      clearInterval(actualizacion)
    }
  }, [enlace, alActualizar])

  return { enlace, error, restante: enlace ? segundosRestantes(enlace.vence_en, ahora) : 0, abrir, cerrar }
}
