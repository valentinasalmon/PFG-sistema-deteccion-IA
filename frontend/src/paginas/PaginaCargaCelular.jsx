/**
 * Página que abre el celular al escanear el código QR de un caso (funcionalidad 024).
 *
 * No requiere iniciar sesión: el enlace es la credencial y solo permite subir
 * fotos a ese caso. Ofrece elegir de la galería o sacar la foto en el momento,
 * y acepta HEIC para que el iPhone entregue el original sin convertirlo.
 *
 * Realiza: RF53 (CA2 a CA4).
 */
import { useCallback, useState } from 'react'
import { useParams } from 'react-router'
import { cargarConEnlace, consultarEnlaceCarga } from '../api/cargaCelular.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Icono from '../componentes/Icono.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { formatearTamanio } from '../utilidades/archivos.js'

const TIPOS_ACEPTADOS = 'image/jpeg,image/png,image/heic,image/heif,.jpg,.jpeg,.png,.heic,.heif'

function horaLocal(venceEn) {
  return new Date(`${venceEn}Z`).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
}

export default function PaginaCargaCelular() {
  const { token } = useParams()
  const consultar = useCallback(() => consultarEnlaceCarga(token), [token])
  const { datos, error, cargando, recargar } = useDatos(consultar)
  const [subiendo, setSubiendo] = useState(null)
  const [resultados, setResultados] = useState([])

  async function subir(evento) {
    const archivos = Array.from(evento.target.files ?? [])
    evento.target.value = ''
    const nuevos = []
    for (const [indice, archivo] of archivos.entries()) {
      setSubiendo({ actual: indice + 1, total: archivos.length })
      if (archivo.size > datos.tamanio_maximo) {
        const maximo = formatearTamanio(datos.tamanio_maximo)
        nuevos.push({ nombre: archivo.name, ok: false, mensaje: `Supera el máximo de ${maximo}.` })
        continue
      }
      try {
        await cargarConEnlace(token, archivo)
        nuevos.push({ nombre: archivo.name, ok: true, mensaje: 'Subida.' })
      } catch (errorApi) {
        nuevos.push({
          nombre: archivo.name,
          ok: false,
          mensaje: errorApi.errores?.archivo ?? errorApi.message,
        })
      }
    }
    setSubiendo(null)
    setResultados((anteriores) => [...nuevos, ...anteriores])
    await recargar()
  }

  if (cargando) return <Cargando texto="Abriendo el enlace…" />
  if (error) {
    return (
      <>
        <h1>Subir fotos</h1>
        <Aviso tipo="error">{error.message}</Aviso>
      </>
    )
  }

  const deshabilitado = Boolean(subiendo) || datos.restantes <= 0
  return (
    <div className="carga-movil">
      <h1>Subir fotos al caso {datos.numero}</h1>
      <p className="nota">
        Las fotos se suben tal cual, sin modificarlas, y aparecen en la computadora donde está abierto el
        caso. Este enlace vence a las {horaLocal(datos.vence_en)} y permite {datos.restantes} foto
        {datos.restantes === 1 ? '' : 's'} más.
      </p>
      <input
        id="galeria"
        type="file"
        accept={TIPOS_ACEPTADOS}
        multiple
        className="solo-lectores"
        onChange={subir}
        disabled={deshabilitado}
      />
      <input
        id="camara"
        type="file"
        accept="image/*"
        capture="environment"
        className="solo-lectores"
        onChange={subir}
        disabled={deshabilitado}
      />
      <div className="carga-movil__botones">
        <label htmlFor="galeria" className="boton">
          <Icono nombre="imagen" tamanio={20} />
          Elegir de la galería
        </label>
        <label htmlFor="camara" className="boton boton--secundario">
          <Icono nombre="camara" tamanio={20} />
          Sacar una foto
        </label>
      </div>
      <p className="nota">
        Sacar la foto en el momento conserva más datos, como la ubicación. Al elegirla de la galería, algunos
        celulares quitan la ubicación.
      </p>
      <div aria-live="polite">
        {subiendo && <Cargando texto={`Subiendo ${subiendo.actual} de ${subiendo.total}…`} />}
        {resultados.length > 0 && (
          <ul className="resultados-carga" aria-label="Fotos subidas">
            {resultados.map((resultado, indice) => (
              <li key={indice} className={resultado.ok ? 'resultado--ok' : 'resultado--error'}>
                <strong>{resultado.nombre}</strong>: {resultado.mensaje}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
