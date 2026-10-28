/**
 * Página que abre un enlace de carga de fotos, sin iniciar sesión.
 *
 * Hay dos enlaces (funcionalidades 024 y 028):
 *
 * - El del celular, que se abre al escanear el código QR de un caso: muestra
 *   el número del caso y sube las fotos a nombre de quien lo generó.
 * - El de la persona afectada (CP-32): no muestra ningún dato del caso, solo
 *   quién pide las fotos. Antes de subir, la persona acepta una declaración
 *   (las fotos son suyas o tiene permiso para compartirlas). Al terminar ve
 *   una confirmación y puede cerrar la página.
 *
 * En los dos casos se puede elegir de la galería o sacar la foto en el
 * momento, y se acepta HEIC para que el iPhone entregue el original sin
 * convertirlo.
 *
 * Realiza: RF53 (CA2 a CA4); CP-32.
 */
import { useCallback, useId, useState } from 'react'
import { Link, useParams } from 'react-router'
import { cargarConEnlace, consultarEnlaceCarga } from '../api/cargaCelular.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Icono from '../componentes/Icono.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { formatearTamanio } from '../utilidades/archivos.js'
import { formatearDia } from '../utilidades/fechas.js'

const TIPOS_ACEPTADOS = 'image/jpeg,image/png,image/heic,image/heif,.jpg,.jpeg,.png,.heic,.heif'

function horaLocal(venceEn) {
  return new Date(`${venceEn}Z`).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
}

/** Sube los archivos de a uno y devuelve el resultado de cada uno. */
function useSubida(token, datos, recargar, declaracion = false) {
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
        await cargarConEnlace(token, archivo, declaracion)
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

  return { subiendo, resultados, subir }
}

/** Botones para elegir de la galería o sacar la foto, con sus campos ocultos. */
function BotonesDeFoto({ deshabilitado, alElegir, camaraPrimero = false }) {
  const idGaleria = useId()
  const idCamara = useId()
  const galeria = (
    <label
      key="galeria"
      htmlFor={idGaleria}
      className={`boton ${camaraPrimero ? 'boton--secundario' : ''}`}
      aria-disabled={deshabilitado}
    >
      <Icono nombre="imagen" tamanio={20} />
      Elegir de la galería
    </label>
  )
  const camara = (
    <label
      key="camara"
      htmlFor={idCamara}
      className={`boton ${camaraPrimero ? '' : 'boton--secundario'}`}
      aria-disabled={deshabilitado}
    >
      <Icono nombre="camara" tamanio={20} />
      Sacar una foto
    </label>
  )
  return (
    <>
      <input
        id={idGaleria}
        type="file"
        accept={TIPOS_ACEPTADOS}
        multiple
        className="solo-lectores"
        onChange={alElegir}
        disabled={deshabilitado}
      />
      <input
        id={idCamara}
        type="file"
        accept="image/*"
        capture="environment"
        className="solo-lectores"
        onChange={alElegir}
        disabled={deshabilitado}
      />
      <div className="carga-movil__botones">{camaraPrimero ? [camara, galeria] : [galeria, camara]}</div>
    </>
  )
}

function ResultadosDeSubida({ subiendo, resultados, titulo }) {
  return (
    <div aria-live="polite">
      {subiendo && <Cargando texto={`Subiendo ${subiendo.actual} de ${subiendo.total}…`} />}
      {resultados.length > 0 && (
        <ul className="resultados-carga" aria-label={titulo}>
          {resultados.map((resultado, indice) => (
            <li key={indice} className={resultado.ok ? 'resultado--ok' : 'resultado--error'}>
              <strong>{resultado.nombre}</strong>: {resultado.mensaje}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function CargaDesdeMiCelular({ token, datos, recargar }) {
  const { subiendo, resultados, subir } = useSubida(token, datos, recargar)
  const deshabilitado = Boolean(subiendo) || datos.restantes <= 0
  return (
    <div className="carga-movil">
      <h1>Subir fotos al caso {datos.numero}</h1>
      <p className="nota">
        Las fotos se suben tal cual, sin modificarlas, y aparecen en la computadora donde está abierto el
        caso. Este enlace vence a las {horaLocal(datos.vence_en)} y permite {datos.restantes} foto
        {datos.restantes === 1 ? '' : 's'} más.
      </p>
      <BotonesDeFoto deshabilitado={deshabilitado} alElegir={subir} />
      <p className="nota">
        Sacar la foto en el momento conserva más datos, como la ubicación. Al elegirla de la galería, algunos
        celulares quitan la ubicación.
      </p>
      <ResultadosDeSubida subiendo={subiendo} resultados={resultados} titulo="Fotos subidas" />
    </div>
  )
}

function iniciales(nombre) {
  return nombre
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0])
    .join('')
    .toUpperCase()
}

/** Lo que ve la persona afectada al abrir el enlace que le mandaron (028, CP-32). */
function CargaDePersonaAfectada({ token, datos, recargar }) {
  const [acepta, setAcepta] = useState(datos.declaracion_aceptada)
  const [terminado, setTerminado] = useState(false)
  const { subiendo, resultados, subir } = useSubida(token, datos, recargar, true)
  const enviadas = resultados.filter((resultado) => resultado.ok).length
  const deshabilitado = !acepta || Boolean(subiendo) || datos.restantes <= 0

  if (terminado) {
    return (
      <div className="carga-movil carga-movil--final" role="status">
        <span className="visor carga-movil__listo" aria-hidden="true">
          <Icono nombre="marca" tamanio={32} />
        </span>
        <h1>¡Listo, gracias!</h1>
        <p>
          Enviaste {enviadas} foto{enviadas === 1 ? '' : 's'} a {datos.solicitante}. Ya podés cerrar esta
          página.
        </p>
      </div>
    )
  }

  return (
    <div className="carga-movil">
      <h1>Te piden fotos del hecho</h1>
      <div className="carga-movil__quien">
        <span className="carga-movil__avatar" aria-hidden="true">
          {iniciales(datos.solicitante)}
        </span>
        <div>
          <strong>{datos.solicitante}</strong>
          {datos.organizacion && <span className="nota">{datos.organizacion}</span>}
        </div>
      </div>
      <ol className="carga-movil__pasos">
        <li>Sacá las fotos en el momento o elegilas de la galería.</li>
        <li>Mandá las originales: no las edites ni las recortes.</li>
        <li>Este enlace vence el {formatearDia(datos.vence_en.slice(0, 10))}.</li>
      </ol>
      <label className="carga-movil__declaracion">
        <input
          type="checkbox"
          checked={acepta}
          onChange={(evento) => setAcepta(evento.target.checked)}
        />
        <span>
          {datos.declaracion} Leé la <Link to="/privacidad">Política de Privacidad</Link>.
        </span>
      </label>
      <BotonesDeFoto deshabilitado={deshabilitado} alElegir={subir} camaraPrimero />
      {!acepta && <p className="nota carga-movil__ayuda">Marcá la declaración para continuar.</p>}
      <ResultadosDeSubida subiendo={subiendo} resultados={resultados} titulo="Tus fotos" />
      {enviadas > 0 && !subiendo && (
        <button type="button" className="boton boton--ancho" onClick={() => setTerminado(true)}>
          Terminé
        </button>
      )}
    </div>
  )
}

export default function PaginaCargaCelular() {
  const { token } = useParams()
  const consultar = useCallback(() => consultarEnlaceCarga(token), [token])
  const { datos, error, cargando, recargar } = useDatos(consultar)

  if (cargando) return <Cargando texto="Abriendo el enlace…" />
  if (error) {
    return (
      <>
        <h1>Subir fotos</h1>
        <Aviso tipo="error">{error.message}</Aviso>
      </>
    )
  }
  if (datos.tipo === 'persona_afectada') {
    return <CargaDePersonaAfectada token={token} datos={datos} recargar={recargar} />
  }
  return <CargaDesdeMiCelular token={token} datos={datos} recargar={recargar} />
}
