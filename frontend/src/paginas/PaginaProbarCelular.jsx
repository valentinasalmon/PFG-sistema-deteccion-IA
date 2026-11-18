/**
 * Página pública «Probar mi celular» (funcionalidad 047).
 *
 * Según el camino que se use para elegir una foto (la galería, la cámara o la
 * app Archivos del iPhone, o la galería de Android), el celular puede
 * entregarla convertida y sin metadatos. Esta página mide qué llega: se elige
 * una foto por cada camino y se ve el formato, la cámara, la fecha y si trae
 * ubicación. La foto no se guarda.
 *
 * Realiza: CA1 y CA2 de la funcionalidad 047.
 */
import { useState } from 'react'
import { diagnosticarFoto } from '../api/diagnostico.js'
import Aviso from '../componentes/Aviso.jsx'

const CAMINOS = [
  { id: 'galeria', titulo: 'Desde la galería', ayuda: 'Elegí una foto de Fotos o de la galería.', accept: 'image/*' },
  { id: 'camara', titulo: 'Sacando una foto', ayuda: 'Abre la cámara y saca una foto nueva.', accept: 'image/*', capture: 'environment' },
  {
    id: 'archivos',
    titulo: 'Desde Archivos',
    ayuda: 'En el iPhone, tocá «Elegir archivo» y buscá la foto en la app Archivos.',
    accept: '.jpg,.jpeg,.png,.heic,.heif',
  },
]

function Resultado({ camino, datos }) {
  const si = (valor) => (valor ? 'Sí' : 'No')
  return (
    <section className="seccion" aria-label={`Resultado: ${camino}`}>
      <h2 className="probar-celular__titulo">{camino}</h2>
      <dl className="datos-verificacion">
        <dt>Formato recibido</dt>
        <dd>{datos.formato}</dd>
        <dt>Datos de la cámara (EXIF)</dt>
        <dd>{datos.metadatos_leidos ? `${datos.campos_exif} campos` : 'No se pudieron leer'}</dd>
        <dt>Cámara</dt>
        <dd>{[datos.marca, datos.modelo].filter(Boolean).join(' ') || 'Sin datos'}</dd>
        <dt>Fecha de la foto</dt>
        <dd>{datos.fecha_captura ?? 'Sin datos'}</dd>
        <dt>Ubicación</dt>
        <dd>{si(datos.tiene_ubicacion)}</dd>
        <dt>Desde</dt>
        <dd>
          {datos.dispositivo.sistema} · {datos.dispositivo.navegador}
        </dd>
      </dl>
    </section>
  )
}

export default function PaginaProbarCelular() {
  const [resultados, setResultados] = useState([])
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(null)

  async function alElegir(camino, evento) {
    const archivo = evento.target.files?.[0]
    evento.target.value = ''
    if (!archivo) return
    setError(null)
    setCargando(camino.id)
    try {
      const datos = await diagnosticarFoto(archivo)
      setResultados((anteriores) => [{ camino: camino.titulo, datos }, ...anteriores])
    } catch (falla) {
      setError(falla.mensaje ?? 'No se pudo leer la foto. Probá de nuevo.')
    } finally {
      setCargando(null)
    }
  }

  return (
    <>
      <h1>Probar mi celular</h1>
      <p className="subtitulo probar-celular__intro">
        Elegí la misma foto por cada camino y mirá qué datos llegan. La foto no se guarda: solo se lee y se muestra el
        resultado.
      </p>
      <ul className="probar-celular__caminos">
        {CAMINOS.map((camino) => (
          <li key={camino.id}>
            <label className="boton boton--secundario">
              {cargando === camino.id ? 'Leyendo…' : camino.titulo}
              <input
                type="file"
                className="solo-lectores"
                accept={camino.accept}
                capture={camino.capture}
                onChange={(evento) => alElegir(camino, evento)}
                disabled={cargando !== null}
              />
            </label>
            <small className="nota">{camino.ayuda}</small>
          </li>
        ))}
      </ul>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {resultados.map((resultado, indice) => (
        <Resultado key={`${resultado.camino}-${resultados.length - indice}`} {...resultado} />
      ))}
    </>
  )
}
