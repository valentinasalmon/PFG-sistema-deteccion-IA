/**
 * Pantalla "Organizaciones": las organizaciones del usuario con su rol y las
 * invitaciones pendientes a su correo, que puede aceptar o rechazar desde acá.
 *
 * Realiza: RN06; CA2, CA10 y CA13 de la funcionalidad 004 (CU11 3a).
 */
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import {
  aceptarInvitacion,
  listarOrganizaciones,
  misInvitaciones,
  rechazarInvitacion,
} from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { formatearFecha } from '../utilidades/fechas.js'

async function cargarPantalla() {
  const [organizaciones, invitaciones] = await Promise.all([
    listarOrganizaciones(),
    misInvitaciones(),
  ])
  return { organizaciones, invitaciones }
}

function InvitacionesPendientes({ invitaciones, alResponder }) {
  const navegar = useNavigate()
  const [error, setError] = useState(null)
  const [mensaje, setMensaje] = useState(null)

  async function responder(invitacion, aceptar) {
    setError(null)
    setMensaje(null)
    try {
      if (aceptar) {
        await aceptarInvitacion(invitacion.id)
        navegar(`/organizaciones/${invitacion.organizacion.id}`, {
          state: { mensaje: `Ya sos miembro de ${invitacion.organizacion.nombre}.` },
        })
        return
      }
      await rechazarInvitacion(invitacion.id)
      setMensaje(`Rechazaste la invitación de ${invitacion.organizacion.nombre}.`)
      await alResponder()
    } catch (errorApi) {
      setError(errorApi.message)
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-invitaciones">
      <h2 id="titulo-invitaciones">Invitaciones pendientes</h2>
      {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
      {error && <Aviso tipo="error">{error}</Aviso>}
      {invitaciones.length === 0 ? (
        <p className="nota">No tenés invitaciones pendientes.</p>
      ) : (
        <ul className="lista-tarjetas">
          {invitaciones.map((invitacion) => (
            <li key={invitacion.id} className="tarjeta-item">
              <div className="tarjeta-item__principal">
                <span className="tarjeta-item__titulo">{invitacion.organizacion.nombre}</span>
                <span className="tarjeta-item__detalle">
                  {invitacion.organizacion.tipo_nombre} · Te invitó {invitacion.invitante}
                  {invitacion.cargo && ` como ${invitacion.cargo}`} · Vence el{' '}
                  {formatearFecha(invitacion.vence_en)}
                </span>
              </div>
              <div className="acciones-en-linea">
                <button
                  type="button"
                  className="boton boton--chico"
                  onClick={() => responder(invitacion, true)}
                  aria-label={`Aceptar la invitación de ${invitacion.organizacion.nombre}`}
                >
                  Aceptar
                </button>
                <button
                  type="button"
                  className="boton boton--secundario boton--chico"
                  onClick={() => responder(invitacion, false)}
                  aria-label={`Rechazar la invitación de ${invitacion.organizacion.nombre}`}
                >
                  Rechazar
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default function PaginaOrganizaciones() {
  // cargarPantalla está definida fuera del componente: no cambia entre renderizados.
  const { datos, error, cargando, recargar } = useDatos(cargarPantalla)
  const { state } = useLocation()

  return (
    <>
      <div className="encabezado-pagina">
        <h1>Organizaciones</h1>
        <Link to="/organizaciones/nueva" className="boton">
          Crear organización
        </Link>
      </div>
      <p className="subtitulo">
        En una organización podés trabajar en equipo con otras personas de tu estudio o de tu
        aseguradora.
      </p>

      {state?.mensaje && <Aviso tipo="exito">{state.mensaje}</Aviso>}
      {cargando && <Cargando texto="Cargando tus organizaciones…" />}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {datos && (
        <>
          {datos.invitaciones.length > 0 && (
            <InvitacionesPendientes invitaciones={datos.invitaciones} alResponder={recargar} />
          )}
          <section className="seccion" aria-labelledby="titulo-mis-organizaciones">
            <h2 id="titulo-mis-organizaciones">Tus organizaciones</h2>
            {datos.organizaciones.length === 0 ? (
              <p className="nota">
                Todavía no pertenecés a ninguna organización. Podés crear una o esperar a que te
                inviten.
              </p>
            ) : (
              <ul className="lista-tarjetas">
                {datos.organizaciones.map((organizacion) => (
                  <li key={organizacion.id} className="tarjeta-item">
                    <div className="tarjeta-item__principal">
                      <Link to={`/organizaciones/${organizacion.id}`} className="tarjeta-item__titulo">
                        {organizacion.nombre}
                      </Link>
                      <span className="tarjeta-item__detalle">{organizacion.tipo_nombre}</span>
                    </div>
                    <Etiqueta tipo={organizacion.mi_rol === 'referente' ? 'destacada' : 'neutra'}>
                      {organizacion.mi_rol === 'referente' ? 'Referente' : 'Miembro'}
                    </Etiqueta>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </>
  )
}
