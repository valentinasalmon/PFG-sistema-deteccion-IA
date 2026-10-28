/**
 * Sección "Imágenes" de la pantalla de un caso.
 *
 * Muestra cada imagen con su vista previa, sus datos técnicos y su huella
 * SHA-256. Quien puede modificar el caso (Responsable o Colaborador, en
 * Borrador o Analizado) carga varios archivos a la vez: se envían de a uno y
 * se informa el resultado de cada uno. Las vistas previas usan enlaces
 * firmados que vencen a los 5 minutos; si una vence, se puede recargar.
 *
 * También permite elegir imágenes y pedir su análisis: por defecto quedan
 * elegidas las que todavía no se analizaron (CU27).
 *
 * Desde la funcionalidad 028 es la etapa "Cargar imágenes" del caso: tres
 * caminos bien distinguidos (esta computadora, el propio celular con un QR y
 * un enlace para la persona afectada), cada imagen dice de dónde vino y una
 * barra fija abajo pide el análisis.
 *
 * Realiza: RF34 (CA1 a CA5), RF35, RF36, RF38 (CA1, CA2); CA1 a CA9 de la
 * funcionalidad 006 y CA1, CA2 de la 007; CP-32.
 */
import { useCallback, useId, useState } from 'react'
import { solicitarAnalisis } from '../api/analisis.js'
import { cargarImagen, eliminarImagen, enlaceDeDescarga, listarImagenes } from '../api/imagenes.js'
import { useDatos } from '../hooks/useDatos.js'
import { useEnlaceCelular } from '../hooks/useEnlaceCelular.js'
import { abrirDescarga, formatearTamanio } from '../utilidades/archivos.js'
import { formatearFecha } from '../utilidades/fechas.js'
import Aviso from './Aviso.jsx'
import BotonConfirmar from './BotonConfirmar.jsx'
import CargaDesdeCelular from './CargaDesdeCelular.jsx'
import Cargando from './Cargando.jsx'
import EnlacePersonaAfectada from './EnlacePersonaAfectada.jsx'
import Icono from './Icono.jsx'

// HEIC/HEIF: formato por defecto del iPhone. Se lista explícitamente para que el
// navegador entregue el original sin convertirlo (funcionalidad 024).
const TIPOS_ACEPTADOS = 'image/jpeg,image/png,image/heic,image/heif,.jpg,.jpeg,.png,.heic,.heif'

// De dónde vino cada imagen (028); las anteriores a la 028 no lo indican.
const ORIGENES = {
  computadora: 'Computadora',
  celular: 'Celular',
  persona_afectada: 'Persona afectada',
}

/** Una de las tres maneras de sumar imágenes, con su ícono y su botón. */
function OpcionDeCarga({ icono, titulo, texto, elegida, children }) {
  return (
    <div className={`opcion-carga${elegida ? ' opcion-carga--elegida' : ''}`}>
      <span className="opcion-carga__icono" aria-hidden="true">
        <Icono nombre={icono} tamanio={22} />
      </span>
      <h3>{titulo}</h3>
      <p className="nota">{texto}</p>
      <div className="opcion-carga__accion">{children}</div>
    </div>
  )
}

function Carga({ idCaso, tamanioMaximo, alTerminar }) {
  const idCampo = useId()
  const [cargando, setCargando] = useState(null)
  const [resultados, setResultados] = useState([])
  const [panel, setPanel] = useState(null)
  const [arrastrando, setArrastrando] = useState(false)
  const celular = useEnlaceCelular(idCaso, alTerminar)
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

  // Arrastrar archivos sobre las opciones también los carga (028).
  function alSoltar(evento) {
    evento.preventDefault()
    setArrastrando(false)
    const archivos = Array.from(evento.dataTransfer?.files ?? [])
    if (archivos.length && !cargando) cargar(archivos)
  }

  async function mostrarCelular() {
    setPanel('celular')
    await celular.abrir()
  }

  async function elegirPanel(nuevo) {
    if (panel === 'celular' && nuevo !== 'celular') await celular.cerrar()
    setPanel(panel === nuevo ? null : nuevo)
  }

  return (
    <div
      className={`carga-imagenes${arrastrando ? ' carga-imagenes--arrastrando' : ''}`}
      onDragOver={(evento) => {
        evento.preventDefault()
        setArrastrando(true)
      }}
      onDragLeave={() => setArrastrando(false)}
      onDrop={alSoltar}
    >
      <div>
        <h3 className="carga-imagenes__titulo">¿Cómo querés sumar las imágenes?</h3>
        <p className="nota">
          JPEG, PNG o HEIC (iPhone), hasta {maximoMb} MB cada una. El original no se modifica y se guarda su
          huella.
        </p>
      </div>
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
      <div className="opciones-carga">
        <OpcionDeCarga
          icono="computadora"
          titulo="Desde esta computadora"
          texto="Elegí los archivos o arrastralos hasta acá."
        >
          <label htmlFor={idCampo} className="boton">
            Elegir imágenes
          </label>
        </OpcionDeCarga>
        <OpcionDeCarga
          icono="celular"
          titulo="Desde tu celular"
          texto="Escaneás un QR y sacás o elegís las fotos. Vence en 15 minutos."
          elegida={panel === 'celular'}
        >
          <button
            type="button"
            className="boton boton--secundario"
            aria-expanded={panel === 'celular'}
            onClick={() => (panel === 'celular' ? elegirPanel(null) : mostrarCelular())}
          >
            {panel === 'celular' ? 'Ocultar el QR' : 'Mostrar el QR'}
          </button>
        </OpcionDeCarga>
        <OpcionDeCarga
          icono="enlace"
          titulo="Pedírselas a la persona afectada"
          texto="Le mandás un enlace y las sube desde su celular, sin crear una cuenta."
          elegida={panel === 'persona'}
        >
          <button
            type="button"
            className="boton boton--secundario"
            aria-expanded={panel === 'persona'}
            onClick={() => elegirPanel('persona')}
          >
            {panel === 'persona' ? 'Ocultar' : 'Crear el enlace'}
          </button>
        </OpcionDeCarga>
      </div>
      {panel === 'celular' && <CargaDesdeCelular {...celular} />}
      {panel === 'persona' && <EnlacePersonaAfectada idCaso={idCaso} />}
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

function TarjetaImagen({
  imagen,
  puedeModificar,
  elegida,
  alElegir,
  alDescargar,
  alEliminar,
  alVencerVistaPrevia,
}) {
  const [sinVistaPrevia, setSinVistaPrevia] = useState(false)

  return (
    <li className={`tarjeta-imagen${elegida ? ' tarjeta-imagen--elegida' : ''}`}>
      <div className="tarjeta-imagen__vista">
        {ORIGENES[imagen.origen] && (
          <span className="tarjeta-imagen__origen">{ORIGENES[imagen.origen]}</span>
        )}
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
        {imagen.analizada && <span className="tarjeta-item__detalle">Ya analizada</span>}
        {puedeModificar && (
          <label className="opcion">
            <input type="checkbox" checked={elegida} onChange={alElegir} />
            Incluir en el análisis
          </label>
        )}
        <span className="tarjeta-item__detalle">
          {imagen.formato} · {imagen.ancho} × {imagen.alto} px · {formatearTamanio(imagen.tamanio)}
        </span>
        <span className="tarjeta-item__detalle">
          Cargada el {formatearFecha(imagen.cargada_en)} por {imagen.cargada_por}
        </span>
        <span className="huella" title="Huella SHA-256">
          SHA-256: {imagen.huella}
        </span>
        <SelloDeTiempo sello={imagen.sello} />
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

/** Barra fija al pie de la etapa: cuántas imágenes se van a analizar y el botón para hacerlo (028). */
function BarraAnalisis({ cantidad, total, alElegirTodas, alAnalizar }) {
  const [enviando, setEnviando] = useState(false)

  async function analizar() {
    setEnviando(true)
    await alAnalizar()
    setEnviando(false)
  }

  const textoBoton =
    cantidad === 1 ? 'Analizar la imagen' : `Analizar las ${cantidad} imágenes`
  return (
    <div className="barra-analisis" role="region" aria-label="Pedir el análisis">
      <div className="barra-analisis__texto">
        <strong>
          {cantidad} de {total} elegida{total === 1 ? '' : 's'}
        </strong>
        <span className="nota">El análisis tarda unos segundos por imagen.</span>
        <span className="barra-analisis__eleccion">
          <button type="button" className="boton-enlace" onClick={() => alElegirTodas(true)}>
            Elegir todas
          </button>
          <button type="button" className="boton-enlace" onClick={() => alElegirTodas(false)}>
            Ninguna
          </button>
        </span>
      </div>
      <button
        type="button"
        className="boton boton--lima"
        onClick={analizar}
        disabled={cantidad === 0 || enviando}
      >
        {enviando ? 'Pidiendo el análisis…' : textoBoton}
        <Icono nombre="derecha" tamanio={18} />
      </button>
    </div>
  )
}

/** Estado del sello de la huella en Hedera, con enlace al explorador público (funcionalidad 023, RF37). */
function SelloDeTiempo({ sello }) {
  if (!sello?.estado) return null
  if (sello.estado === 'sellado') {
    return (
      <span className={`sello sello--${sello.simulado ? 'simulado' : 'ok'}`}>
        {sello.simulado
          ? 'Sello simulado (entorno de pruebas)'
          : `Registrada en Hedera el ${formatearFecha(sello.fecha)} · ${sello.referencia}`}
        {sello.enlace && (
          <>
            {' · '}
            <a href={sello.enlace} target="_blank" rel="noopener noreferrer">
              Verificar en HashScan
            </a>
          </>
        )}
      </span>
    )
  }
  if (sello.estado === 'fallido') {
    return <span className="sello sello--fallido">Sin sello de Hedera</span>
  }
  return <span className="sello">Sello en Hedera en curso…</span>
}

export default function SeccionImagenes({ idCaso, alSolicitarAnalisis, alCambiar }) {
  const cargar = useCallback(() => listarImagenes(idCaso), [idCaso])
  const { datos, error, cargando, recargar: recargarImagenes } = useDatos(cargar)
  // Al cargar o eliminar, también cambia la cantidad que muestran las etapas del caso.
  const recargar = useCallback(async () => {
    await recargarImagenes()
    await alCambiar?.()
  }, [recargarImagenes, alCambiar])
  const [aviso, setAviso] = useState(null)
  // Sin elección propia, quedan elegidas las imágenes que todavía no se analizaron.
  const [eleccion, setEleccion] = useState(null)
  const imagenes = datos?.imagenes ?? []
  const elegidas = new Set(
    (eleccion ?? imagenes.filter((imagen) => !imagen.analizada).map((imagen) => imagen.id)).filter((id) =>
      imagenes.some((imagen) => imagen.id === id),
    ),
  )

  function alternar(id) {
    const nuevas = new Set(elegidas)
    if (nuevas.has(id)) nuevas.delete(id)
    else nuevas.add(id)
    setEleccion([...nuevas])
  }

  async function analizar() {
    setAviso(null)
    try {
      await solicitarAnalisis(idCaso, [...elegidas])
      await alSolicitarAnalisis()
    } catch (errorApi) {
      setAviso({ tipo: 'error', texto: errorApi.errores?.imagenes ?? errorApi.message })
    }
  }

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
    <section className="seccion etapa-imagenes" aria-labelledby="titulo-imagenes" aria-busy={cargando}>
      <h2 id="titulo-imagenes" className="solo-lectores">
        Cargar imágenes
      </h2>
      {cargando && <Cargando texto="Cargando las imágenes…" />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      {datos && (
        <>
          {datos.puede_modificar && (
            <Carga idCaso={idCaso} tamanioMaximo={datos.tamanio_maximo} alTerminar={recargar} />
          )}
          <h3 className="etapa-imagenes__titulo-galeria">
            Imágenes cargadas ({datos.imagenes.length} de {datos.limite})
          </h3>
          {datos.imagenes.length === 0 ? (
            <p className="nota">Todavía no hay imágenes en este caso.</p>
          ) : (
            <ul className="galeria">
              {datos.imagenes.map((imagen) => (
                <TarjetaImagen
                  key={imagen.id}
                  imagen={imagen}
                  puedeModificar={datos.puede_modificar}
                  elegida={elegidas.has(imagen.id)}
                  alElegir={() => alternar(imagen.id)}
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
          {datos.puede_modificar && imagenes.length > 0 && (
            <BarraAnalisis
              cantidad={elegidas.size}
              total={imagenes.length}
              alElegirTodas={(todas) => setEleccion(todas ? imagenes.map((i) => i.id) : [])}
              alAnalizar={analizar}
            />
          )}
        </>
      )}
    </section>
  )
}
