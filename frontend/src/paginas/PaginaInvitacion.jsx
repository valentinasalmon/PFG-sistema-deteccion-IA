/**
 * Pantalla del enlace de invitación recibido por correo.
 *
 * Muestra qué organización invita y a qué correo, con o sin sesión. Según la
 * sesión ofrece responder, iniciar sesión con el correo invitado o crear una
 * cuenta con ese correo; después de registrarse, la invitación aparece en la
 * pantalla de organizaciones.
 *
 * Realiza: RF13; CA9 a CA12 de la funcionalidad 004 (CU11).
 */
import { useCallback, useState } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router'
import {
  aceptarInvitacion,
  consultarInvitacion,
  rechazarInvitacion,
} from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { formatearFecha } from '../utilidades/fechas.js'

function Respuesta({ invitacion }) {
  const navegar = useNavigate()
  const [estado, setEstado] = useState({ enviando: false, error: null, rechazada: false })

  async function responder(aceptar) {
    setEstado({ enviando: true, error: null, rechazada: false })
    try {
      if (aceptar) {
        const respuesta = await aceptarInvitacion(invitacion.id)
        navegar(`/organizaciones/${respuesta.id_organizacion}`, {
          state: { mensaje: respuesta.mensaje },
        })
        return
      }
      await rechazarInvitacion(invitacion.id)
      setEstado({ enviando: false, error: null, rechazada: true })
    } catch (error) {
      setEstado({ enviando: false, error: error.message, rechazada: false })
    }
  }

  if (estado.rechazada) {
    return (
      <>
        <Aviso tipo="exito">Rechazaste la invitación.</Aviso>
        <p className="enlaces-secundarios">
          <Link to="/organizaciones">Ir a mis organizaciones</Link>
        </p>
      </>
    )
  }

  return (
    <>
      {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}
      <div className="pasos__acciones">
        <button
          type="button"
          className="boton boton--secundario"
          onClick={() => responder(false)}
          disabled={estado.enviando}
        >
          Rechazar
        </button>
        <button
          type="button"
          className="boton"
          onClick={() => responder(true)}
          disabled={estado.enviando}
        >
          Aceptar la invitación
        </button>
      </div>
    </>
  )
}

function Acciones({ invitacion, token }) {
  const { usuario } = useSesion()
  const { pathname, search } = useLocation()

  if (invitacion.sesion_con_el_correo) return <Respuesta invitacion={invitacion} />
  if (usuario) {
    return (
      <Aviso tipo="info">
        Iniciaste sesión como {usuario.correo}, pero esta invitación es para {invitacion.correo}.
        Cerrá la sesión e ingresá con ese correo para responderla.
      </Aviso>
    )
  }
  return (
    <>
      <p>Para responder, ingresá con el correo {invitacion.correo}.</p>
      <div className="pasos__acciones">
        <Link
          to={`/registro?invitacion=${encodeURIComponent(token)}`}
          className="boton boton--secundario"
        >
          Crear una cuenta
        </Link>
        <Link
          to="/iniciar-sesion"
          state={{ desde: `${pathname}${search}` }}
          className="boton"
        >
          Iniciar sesión
        </Link>
      </div>
      <p className="nota">
        {invitacion.organizacion.tipo === 'aseguradora'
          ? 'Si creás una cuenta, al verificar tu correo vas a quedar dentro de la aseguradora.'
          : 'Si creás una cuenta, después de verificar tu correo vas a encontrar la invitación en la sección Organizaciones.'}
      </p>
    </>
  )
}

export default function PaginaInvitacion() {
  const [parametros] = useSearchParams()
  const token = parametros.get('token') ?? ''
  const { cargando: cargandoSesion } = useSesion()
  const cargar = useCallback(() => consultarInvitacion(token), [token])
  const { datos: invitacion, error, cargando } = useDatos(cargar)

  if (cargando || cargandoSesion) return <Cargando texto="Buscando la invitación…" />
  if (error) {
    return (
      <>
        <h1>Invitación</h1>
        <Aviso tipo="error">{error.message}</Aviso>
        <p className="enlaces-secundarios">
          <Link to="/">Ir al inicio</Link>
        </p>
      </>
    )
  }

  return (
    <>
      <h1>Te invitaron a {invitacion.organizacion.nombre}</h1>
      <dl className="datos-fijos">
        <dt>Organización</dt>
        <dd>
          {invitacion.organizacion.nombre} ({invitacion.organizacion.tipo_nombre})
        </dd>
        <dt>Invitó</dt>
        <dd>{invitacion.invitante ?? '—'}</dd>
        <dt>Correo invitado</dt>
        <dd>{invitacion.correo}</dd>
        {invitacion.cargo && (
          <>
            <dt>Cargo</dt>
            <dd>{invitacion.cargo}</dd>
          </>
        )}
        <dt>Vence</dt>
        <dd>{formatearFecha(invitacion.vence_en)}</dd>
      </dl>
      {invitacion.vigente ? (
        <Acciones invitacion={invitacion} token={token} />
      ) : (
        <Aviso tipo="error">
          Esta invitación ya no está vigente: venció, fue cancelada o ya fue respondida. Pedile a
          la organización que te invite de nuevo.
        </Aviso>
      )}
    </>
  )
}
