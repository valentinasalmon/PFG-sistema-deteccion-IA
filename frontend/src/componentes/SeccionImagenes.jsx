/**
 * Sección "Imágenes" de la pantalla de un caso.
 *
 * Muestra cada imagen con su vista previa, sus datos técnicos y su huella
 * SHA-256. Quien puede modificar el caso (Responsable o Colaborador, en
 * Borrador o Analizado) carga varios archivos a la vez: se envían de a uno y
 * se informa el resultado de cada uno. Las vistas previas usan enlaces
 * firmados que vencen a los 5 minutos; si una vence, se puede recargar.
 *
 * Realiza: RF34 (CA1 a CA5), RF35, RF36; CA1 a CA9 de la funcionalidad 006.
 */
import { useCallback, useId, useState } from 'react'
import { cargarImagen, eliminarImagen, enlaceDeDescarga, listarImagenes } from '../api/imagenes.js'
import { useDatos } from '../hooks/useDatos.js'
import { abrirDescarga, formatearTamanio } from '../utilidades/archivos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import Aviso from './Aviso.jsx'
import BotonConfirmar from './BotonConfirmar.jsx'
import Cargando from './Cargando.jsx'

const TIPOS_ACEPTADOS = 'image/jpeg,image/png,.jpg,.jpeg,.png'

function Carga({ idCaso, tamanioMaximo, alTerminar }) {
  const idCampo = useId()
  const [cargando, setCargando] = useState(null)
  const [resultados, setResultados] = useState([])
  const maximoMb = Math.round(tamanioMaximo / (1024 * 1024))

  async function cargar(archivos) {
    const nuevos = []
    for (const [indice, archivo] of archivos.entries()) {
      setCargando({ actual: indice + 1, total: archivos.length })
      if (archivo.size > tamanioMaximo) {
        nuevos.push({
          nombre: archivo.name,
          ok: false,
          mensaje: `Supera el máximo de ${maximoMb} MB.`,
        })
        continue
      }
      try {
        await cargarImagen(idCaso, archivo)
        nuevos.push({ nombre: archivo.name, ok: true, mensaje: 'Cargada.' })
      } catch (error) {
        nuevos.push({
          nombre: archivo.name,
          ok: false,
          mensaje: error.errores?.archivo ?? error.message,
        })
      }
    }
    setCargando(null)
    setResultados(nuevos)
    await alTerminar()
  }

  function alElegir(evento) {
    const archivos = Array.from(evento.target.files ?? [])
    evento.target.value = ''
    if (archivos.length) cargar(archivos)
  }

  return (
    <div className="carga-imagenes">
      {/* El campo queda oculto a la vista y la etiqueta funciona como botón;
          el foco del teclado se marca en la etiqueta con CSS. */}
      <input
        id={idCampo}
        type="file"
        accept={TIPOS_ACEPTADOS}
        multiple
        className="solo-lectores"
        onChange={alElegir}
        disabled={Boolean(cargando)}
      />
      <label htmlFor={idCampo} className="boton">
        Elegir imágenes
      </label>
      <p className="nota">
        JPEG o PNG, hasta {maximoMb} MB cada una. El archivo original no se modifica.
      </p>
      <div aria-live="polite">
        {cargando && <Cargando texto={`Cargando ${cargando.actual} de ${cargando.total}…`} />}
        {!cargando && resultados.length > 0 && (
          <ul className="resultados-carga" aria-label="Resultado de la carga">
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

function TarjetaImagen({ imagen, puedeModificar, alDescargar, alEliminar, alVencerVistaPrevia }) {
  const [sinVistaPrevia, setSinVistaPrevia] = useState(false)

  return (
    <li className="tarjeta-imagen">
      <div className="tarjeta-imagen__vista">
        {sinVistaPrevia ? (
          <button
            type="button"
            className="boton boton--secundario boton--chico"
            onClick={alVencerVistaPrevia}
          >
            Volver a cargar la vista previa
          </button>
        ) : (
          <img
            src={imagen.miniatura}
            alt={`Vista previa de ${imagen.nombre}`}
            loading="lazy"
            onError={() => setSinVistaPrevia(true)}
          />
        )}
      </div>
      <div className="tarjeta-imagen__datos">
        <span className="tarjeta-item__titulo">{imagen.nombre}</span>
        <span className="tarjeta-item__detalle">
          {imagen.formato} · {imagen.ancho} × {imagen.alto} px · {formatearTamanio(imagen.tamanio)}
        </span>
        <span className="tarjeta-item__detalle">
          Cargada el {formatearFecha(imagen.cargada_en)} por {imagen.cargada_por}
        </span>
        <span className="huella" title="Huella SHA-256">
          SHA-256: {imagen.huella}
        </span>
        <div className="acciones-en-linea">
          <button
            type="button"
            className="boton boton--secundario boton--chico"
            onClick={alDescargar}
            aria-label={`Descargar el original de ${imagen.nombre}`}
          >
            Descargar original
          </button>
          {puedeModificar && imagen.en_informe && (
            <span className="nota">Está en un informe: no se puede eliminar.</span>
          )}
          {puedeModificar && !imagen.en_informe && (
            <BotonConfirmar
              texto="Eliminar"
              pregunta={`¿Eliminar ${imagen.nombre}? Se borra el archivo de forma definitiva.`}
              textoConfirmar="Eliminar"
              peligro
              onConfirmar={alEliminar}
            />
          )}
        </div>
      </div>
    </li>
  )
}

export default function SeccionImagenes({ idCaso }) {
  const cargar = useCallback(() => listarImagenes(idCaso), [idCaso])
  const { datos, error, cargando, recargar } = useDatos(cargar)
  const [aviso, setAviso] = useState(null)

  async function ejecutar(accion, exito) {
    setAviso(null)
    try {
      await accion()
      if (exito) setAviso({ tipo: 'exito', texto: exito })
    } catch (errorApi) {
      setAviso({ tipo: 'error', texto: errorApi.message })
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-imagenes" aria-busy={cargando}>
      <h2 id="titulo-imagenes">
        Imágenes{datos ? ` (${datos.imagenes.length} de ${datos.limite})` : ''}
      </h2>
      {cargando && <Cargando texto="Cargando las imágenes…" />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      {datos && (
        <>
          {datos.puede_modificar && (
            <Carga idCaso={idCaso} tamanioMaximo={datos.tamanio_maximo} alTerminar={recargar} />
          )}
          {datos.imagenes.length === 0 ? (
            <p className="nota">Todavía no hay imágenes en este caso.</p>
          ) : (
            <ul className="galeria">
              {datos.imagenes.map((imagen) => (
                <TarjetaImagen
                  key={imagen.id}
                  imagen={imagen}
                  puedeModificar={datos.puede_modificar}
                  alVencerVistaPrevia={recargar}
                  alDescargar={() =>
                    ejecutar(async () => abrirDescarga(await enlaceDeDescarga(idCaso, imagen.id)))
                  }
                  alEliminar={() =>
                    ejecutar(async () => {
                      await eliminarImagen(idCaso, imagen.id)
                      await recargar()
                    }, `Se eliminó «${imagen.nombre}».`)
                  }
                />
              ))}
            </ul>
          )}
          <p className="nota">
            El análisis de las imágenes y los informes estarán disponibles próximamente.
          </p>
        </>
      )}
    </section>
  )
}
