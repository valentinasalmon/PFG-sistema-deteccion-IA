/**
 * Pantalla "Organizaciones": las organizaciones del usuario con su rol y las
 * invitaciones pendientes a su correo, que puede aceptar o rechazar desde acá.
 *
 * Realiza: RN06, RN40; CA2, CA10 y CA13 de la funcionalidad 004 (CU11 3a);
 * CA6 y CA17 de la 021.
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
import Icono from '../componentes/Icono.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
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
  const { usuario } = useSesion()
  // Solo los abogados crean organizaciones, y solo estudios jurídicos (RN40).
  const puedeCrear = usuario.perfil === 'abogado'

  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Organizaciones</h1>
          <p className="encabezado-pagina__bajada">
            En una organización trabajás en equipo con otras personas de tu estudio jurídico o de tu
            aseguradora.
          </p>
        </div>
        {puedeCrear && (
          <Link to="/organizaciones/nueva" className="boton">
            <Icono nombre="mas" tamanio={18} />
            Crear estudio jurídico
          </Link>
        )}
      </div>

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
              <p className="estado-vacio">
                <span className="visor estado-vacio__visor">
                  <Icono nombre="organizaciones" tamanio={28} />
                </span>
                {puedeCrear
                  ? 'Todavía no pertenecés a ninguna organización. Podés crear un estudio jurídico o esperar a que te inviten.'
                  : 'Todavía no pertenecés a ninguna organización.'}
              </p>
            ) : (
              <ul className="lista-tarjetas lista-tarjetas--grilla">
                {datos.organizaciones.map((organizacion) => (
                  <li key={organizacion.id} className="tarjeta-item tarjeta-item--organizacion">
                    <span className="tarjeta-item__icono" aria-hidden="true">
                      <Icono nombre="organizaciones" tamanio={22} />
                    </span>
                    <div className="tarjeta-item__principal">
                      <Link to={`/organizaciones/${organizacion.id}`} className="tarjeta-item__titulo">
                        {organizacion.nombre}
                      </Link>
                      <span className="tarjeta-item__detalle">{organizacion.tipo_nombre}</span>
                    </div>
                    <div className="acciones-en-linea">
                      {organizacion.estado === 'pendiente' && (
                        <Etiqueta tipo="alerta">Pendiente de aprobación</Etiqueta>
                      )}
                      <Etiqueta tipo={organizacion.mi_rol === 'referente' ? 'destacada' : 'neutra'}>
                        {organizacion.mi_rol === 'referente' ? 'Referente' : 'Miembro'}
                      </Etiqueta>
                    </div>
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
