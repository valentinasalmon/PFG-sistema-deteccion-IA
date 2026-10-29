/**
 * "Pedírselas a la persona afectada": crea un enlace para que la persona
 * afectada suba sus propias fotos al caso desde su celular, sin crear una
 * cuenta (funcionalidad 028, CP-32).
 *
 * El enlace vence a los 7 días (se puede elegir otra vigencia), no muestra
 * datos del caso, pide aceptar una declaración y se puede anular en cualquier
 * momento. Se muestra una sola vez, al crearlo: en la base solo queda su
 * huella. Se manda por WhatsApp, por correo o copiándolo.
 *
 * Realiza: RF53 (CA2); CP-32.
 */
import { useCallback, useState } from 'react'
import {
  anularEnlacePersonaAfectada,
  crearEnlacePersonaAfectada,
  listarEnlacesPersonaAfectada,
} from '../api/cargaCelular.js'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { formatearDia } from '../utilidades/fechas.js'
import Aviso from './Aviso.jsx'
import BotonConfirmar from './BotonConfirmar.jsx'
import CampoSeleccion from './CampoSeleccion.jsx'
import CampoTexto from './CampoTexto.jsx'
import Icono from './Icono.jsx'

const OPCIONES_VIGENCIA = [
  { valor: '1', texto: '1 día' },
  { valor: '3', texto: '3 días' },
  { valor: '7', texto: '7 días' },
  { valor: '14', texto: '14 días' },
  { valor: '30', texto: '30 días' },
]

/** Mensaje para mandar el enlace: sin datos del caso, solo quién pide y hasta cuándo. */
function mensajeDelPedido(enlace, solicitante) {
  const saludo = enlace.destinatario ? `Hola, ${enlace.destinatario}.` : 'Hola.'
  return (
    `${saludo} ${solicitante} te pide las fotos del hecho para tu reclamo. ` +
    `Podés subirlas desde tu celular, hasta el ${formatearDia(enlace.vence_en)}, en este enlace: ${enlace.url}`
  )
}

function EnlaceListo({ enlace }) {
  const { usuario } = useSesion()
  const [copiado, setCopiado] = useState(false)
  const mensaje = mensajeDelPedido(enlace, `${usuario.nombre} ${usuario.apellido}`)

  async function copiar() {
    try {
      await navigator.clipboard.writeText(enlace.url)
      setCopiado(true)
    } catch {
      setCopiado(false)
    }
  }

  return (
    <div className="enlace-afectada__listo">
      <CampoTexto
        etiqueta="Enlace listo"
        nombre="enlace"
        value={enlace.url}
        readOnly
        onFocus={(evento) => evento.target.select()}
        ayuda="Se muestra una sola vez: copialo o mandalo ahora. Si lo perdés, creá otro."
      />
      <div className="enlace-afectada__envios">
        <button type="button" className="boton" onClick={copiar}>
          <Icono nombre="copiar" tamanio={18} />
          {copiado ? 'Enlace copiado' : 'Copiar el enlace'}
        </button>
        <a
          className="boton boton--secundario"
          href={`https://wa.me/?text=${encodeURIComponent(mensaje)}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          Enviar por WhatsApp
        </a>
        <a
          className="boton boton--secundario"
          href={`mailto:?subject=${encodeURIComponent('Fotos del hecho para tu reclamo')}&body=${encodeURIComponent(mensaje)}`}
        >
          Enviar por correo
        </a>
      </div>
    </div>
  )
}

function EnlacesVigentes({ idCaso, enlaces, alAnular }) {
  const [error, setError] = useState(null)
  if (enlaces.length === 0) return null
  return (
    <div className="enlace-afectada__vigentes">
      <h4>Enlaces vigentes</h4>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <ul className="lista-simple">
        {enlaces.map((enlace) => (
          <li key={enlace.id} className="enlace-afectada__vigente">
            <div>
              <strong>{enlace.destinatario ?? 'Sin nombre'}</strong>
              <span className="nota">
                Vence el {formatearDia(enlace.vence_en)} · {enlace.cargas} foto{enlace.cargas === 1 ? '' : 's'}{' '}
                recibida{enlace.cargas === 1 ? '' : 's'}
              </span>
            </div>
            <BotonConfirmar
              texto="Anular"
              pregunta="¿Anular el enlace? Deja de servir en el momento."
              textoConfirmar="Anular"
              peligro
              onConfirmar={async () => {
                setError(null)
                try {
                  await anularEnlacePersonaAfectada(idCaso, enlace.id)
                  await alAnular()
                } catch (errorApi) {
                  setError(errorApi.message)
                }
              }}
            />
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function EnlacePersonaAfectada({ idCaso }) {
  const cargar = useCallback(() => listarEnlacesPersonaAfectada(idCaso), [idCaso])
  const { datos, recargar } = useDatos(cargar)
  const [destinatario, setDestinatario] = useState('')
  const [dias, setDias] = useState('7')
  const [enlace, setEnlace] = useState(null)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function crear(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      const respuesta = await crearEnlacePersonaAfectada(idCaso, Number(dias), destinatario)
      setEnlace(respuesta.enlace)
      setDestinatario('')
      await recargar()
    } catch (errorApi) {
      setError(errorApi.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="panel-carga enlace-afectada" aria-labelledby="titulo-enlace-afectada">
      <h3 id="titulo-enlace-afectada">Enlace para la persona afectada</h3>
      <p className="nota">
        Solo permite subir fotos a este caso. La persona no ve ningún dato del caso: solo tu nombre y, si
        corresponde, tu organización. Antes de subir, declara que las fotos son suyas o que tiene permiso para
        compartirlas. Podés anularlo cuando quieras.
      </p>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <form className="enlace-afectada__formulario" onSubmit={crear} noValidate>
        <CampoTexto
          etiqueta="Para quién"
          nombre="destinatario"
          opcional
          value={destinatario}
          onChange={(evento) => setDestinatario(evento.target.value)}
          maxLength={100}
          ayuda="Solo lo ve tu equipo, para reconocer el enlace."
        />
        <CampoSeleccion
          etiqueta="Vence en"
          nombre="dias"
          value={dias}
          onChange={(evento) => setDias(evento.target.value)}
          opciones={OPCIONES_VIGENCIA}
        />
        <button type="submit" className="boton" disabled={enviando}>
          <Icono nombre="enlace" tamanio={18} />
          {enviando ? 'Creando…' : 'Crear el enlace'}
        </button>
      </form>
      {enlace && <EnlaceListo enlace={enlace} />}
      {datos && <EnlacesVigentes idCaso={idCaso} enlaces={datos.enlaces} alAnular={recargar} />}
    </section>
  )
}
