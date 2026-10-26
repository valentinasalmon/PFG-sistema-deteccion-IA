/**
 * "Cargar desde el celular": muestra un código QR de un solo uso para subir
 * fotos desde la galería o la cámara del celular a este caso (funcionalidad 024).
 *
 * Mientras el código está abierto, la lista de imágenes se actualiza sola
 * cada pocos segundos, así las fotos aparecen en la computadora a medida que
 * se suben. Al cerrarlo, el enlace se cancela.
 *
 * Realiza: RF53 (CA2).
 */
import { useEffect, useState } from 'react'
import { cancelarEnlaceCarga, crearEnlaceCarga } from '../api/cargaCelular.js'
import Aviso from './Aviso.jsx'
import Icono from './Icono.jsx'

const INTERVALO_ACTUALIZACION = 4000 // milisegundos

function segundosRestantes(venceEn, ahora) {
  return Math.max(0, Math.round((new Date(`${venceEn}Z`).getTime() - ahora) / 1000))
}

function formatearRestante(segundos) {
  const minutos = Math.floor(segundos / 60)
  return `${minutos}:${String(segundos % 60).padStart(2, '0')}`
}

export default function CargaDesdeCelular({ idCaso, alActualizar }) {
  const [enlace, setEnlace] = useState(null)
  const [error, setError] = useState(null)
  const [ahora, setAhora] = useState(() => Date.now())
  const restante = enlace ? segundosRestantes(enlace.vence_en, ahora) : 0

  async function abrir() {
    setError(null)
    try {
      setEnlace(await crearEnlaceCarga(idCaso))
      setAhora(Date.now())
    } catch (errorApi) {
      setError(errorApi.message)
    }
  }

  async function cerrar() {
    setEnlace(null)
    await cancelarEnlaceCarga(idCaso).catch(() => {})
  }

  useEffect(() => {
    if (!enlace) return undefined
    const reloj = setInterval(() => setAhora(Date.now()), 1000)
    const actualizacion = setInterval(() => alActualizar(), INTERVALO_ACTUALIZACION)
    return () => {
      clearInterval(reloj)
      clearInterval(actualizacion)
    }
  }, [enlace, alActualizar])

  if (!enlace) {
    return (
      <>
        <button type="button" className="boton boton--secundario" onClick={abrir}>
          <Icono nombre="camara" tamanio={18} />
          Cargar desde el celular
        </button>
        {error && <Aviso tipo="error">{error}</Aviso>}
      </>
    )
  }

  return (
    <section className="carga-celular" aria-labelledby="titulo-carga-celular">
      <h3 id="titulo-carga-celular">Cargar desde el celular</h3>
      {restante > 0 ? (
        <div className="carga-celular__contenido">
          <div className="visor carga-celular__qr">
            <img src={enlace.qr} alt="Código QR para cargar fotos desde el celular" />
          </div>
          <ol className="carga-celular__pasos">
            <li>Abrí la cámara del celular y apuntá al código.</li>
            <li>Tocá el enlace que aparece.</li>
            <li>Elegí las fotos de la galería o sacá una en el momento.</li>
          </ol>
          <p className="nota">
            Las fotos aparecen acá a medida que se suben. El código vence en{' '}
            <strong aria-live="off">{formatearRestante(restante)}</strong> y solo sirve para este caso. Podés
            subir todas las fotos que quieras, dentro del límite de tu plan.
          </p>
        </div>
      ) : (
        <Aviso tipo="info">El código venció. Generá uno nuevo para seguir cargando fotos.</Aviso>
      )}
      <div className="acciones-en-linea">
        {restante === 0 && (
          <button type="button" className="boton" onClick={abrir}>
            Generar otro código
          </button>
        )}
        <button type="button" className="boton boton--fantasma" onClick={cerrar}>
          {restante > 0 ? 'Cancelar' : 'Cerrar'}
        </button>
      </div>
    </section>
  )
}
