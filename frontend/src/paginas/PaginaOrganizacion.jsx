/**
 * Pantalla de una organización: datos, plan, miembros e invitaciones.
 *
 * Lo que se muestra depende del rol: cualquier miembro ve los datos y los
 * miembros y puede abandonar la organización; el Referente además edita los
 * datos, invita, gestiona invitaciones y miembros, transfiere su rol y
 * elimina la organización.
 *
 * Realiza: RF11 a RF18; CA3, CA8, CA14 a CA20 y CA22 de la funcionalidad 004.
 */
import { useCallback, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router'
import {
  abandonarOrganizacion,
  cancelarInvitacion,
  designarReferente,
  desvincularMiembro,
  editarCargo,
  editarOrganizacion,
  eliminarOrganizacion,
  invitar,
  listarInvitaciones,
  listarMiembros,
  obtenerOrganizacion,
  reenviarInvitacion,
} from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import BotonConfirmar from '../componentes/BotonConfirmar.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'
import { formatearFecha } from '../utilidades/fechas.js'

const NOMBRES_PERFIL = { abogado: 'Abogado o abogada', aseguradora: 'Aseguradora' }

async function cargarOrganizacion(id) {
  const organizacion = await obtenerOrganizacion(id)
  const [miembros, invitaciones] = await Promise.all([
    listarMiembros(id),
    organizacion.mi_rol === 'referente' ? listarInvitaciones(id) : Promise.resolve([]),
  ])
  return { organizacion, miembros, invitaciones }
}

/** Ejecuta una acción, muestra su mensaje y recarga la pantalla. */
function useAccion(recargar) {
  const [resultado, setResultado] = useState(null)
  const ejecutar = useCallback(
    async (accion) => {
      setResultado(null)
      try {
        const respuesta = await accion()
        setResultado({ tipo: 'exito', texto: respuesta?.mensaje ?? 'Listo.' })
        await recargar()
      } catch (error) {
        setResultado({ tipo: 'error', texto: error.message })
      }
    },
    [recargar],
  )
  return { resultado, ejecutar }
}

function SeccionDatos({ organizacion, esReferente, alGuardar }) {
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({
    nombre: organizacion.nombre,
    tipo: organizacion.tipo,
    correo_contacto: organizacion.correo_contacto ?? '',
    telefono: organizacion.telefono ?? '',
  })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje(null)
    const resultado = await enviar((datos) => editarOrganizacion(organizacion.id, datos))
    if (resultado.ok) {
      setMensaje(resultado.datos.mensaje)
      await alGuardar()
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-datos-organizacion">
      <h2 id="titulo-datos-organizacion">Datos de la organización</h2>
      <dl className="datos-fijos">
        <dt>Plan</dt>
        <dd>
          {organizacion.plan.nombre} · hasta {organizacion.plan.limite_miembros} miembros
        </dd>
        {!esReferente && (
          <>
            <dt>Tipo</dt>
            <dd>{organizacion.tipo_nombre}</dd>
            <dt>Correo de contacto</dt>
            <dd>{organizacion.correo_contacto ?? '—'}</dd>
            <dt>Teléfono</dt>
            <dd>{organizacion.telefono ?? '—'}</dd>
          </>
        )}
      </dl>
      {esReferente && (
        <form onSubmit={manejarEnvio} className="formulario" noValidate>
          {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
          {error && <Aviso tipo="error">{error.message}</Aviso>}
          <CampoTexto
            etiqueta="Nombre"
            nombre="nombre"
            value={valores.nombre}
            onChange={cambiar}
            error={errores.nombre}
            required
          />
          <div className="campo">
            <label htmlFor="tipo-organizacion" className="campo__etiqueta">
              Tipo
            </label>
            <select
              id="tipo-organizacion"
              name="tipo"
              className="campo__control"
              value={valores.tipo}
              onChange={cambiar}
            >
              <option value="estudio_juridico">Estudio Jurídico</option>
              <option value="aseguradora">Aseguradora</option>
            </select>
          </div>
          <div className="formulario__fila">
            <CampoTexto
              etiqueta="Correo de contacto"
              nombre="correo_contacto"
              tipo="email"
              opcional
              value={valores.correo_contacto}
              onChange={cambiar}
              error={errores.correo_contacto}
            />
            <CampoTexto
              etiqueta="Teléfono"
              nombre="telefono"
              tipo="tel"
              opcional
              value={valores.telefono}
              onChange={cambiar}
              error={errores.telefono}
            />
          </div>
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar los datos'}
          </button>
        </form>
      )}
    </section>
  )
}

function FormularioCargo({ organizacion, miembro, alTerminar }) {
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({
    cargo: miembro.cargo ?? '',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) =>
      editarCargo(organizacion.id, miembro.id_usuario, datos.cargo || null),
    )
    if (resultado.ok) await alTerminar(resultado.datos.mensaje)
  }

  return (
    <form onSubmit={manejarEnvio} className="formulario formulario--compacto" noValidate>
      {error && !errores.cargo && <Aviso tipo="error">{error.message}</Aviso>}
      <CampoTexto
        etiqueta={`Cargo de ${miembro.nombre} ${miembro.apellido}`}
        nombre="cargo"
        opcional
        value={valores.cargo}
        onChange={cambiar}
        error={errores.cargo}
      />
      <div className="acciones-en-linea">
        <button type="submit" className="boton boton--chico" disabled={enviando}>
          Guardar el cargo
        </button>
        <button
          type="button"
          className="boton boton--secundario boton--chico"
          onClick={() => alTerminar(null)}
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}

function SeccionMiembros({ organizacion, miembros, esReferente, idUsuario, recargar }) {
  const { resultado, ejecutar } = useAccion(recargar)
  const [editando, setEditando] = useState(null)
  const [mensajeCargo, setMensajeCargo] = useState(null)
  const aviso = mensajeCargo ? { tipo: 'exito', texto: mensajeCargo } : resultado

  async function terminarEdicion(mensaje) {
    setEditando(null)
    setMensajeCargo(mensaje)
    if (mensaje) await recargar()
  }

  return (
    <section className="seccion" aria-labelledby="titulo-miembros">
      <h2 id="titulo-miembros">
        Miembros ({miembros.length} de {organizacion.plan.limite_miembros})
      </h2>
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}
      <ul className="lista-tarjetas">
        {miembros.map((miembro) => {
          const nombre = `${miembro.nombre} ${miembro.apellido}`
          const esYo = miembro.id_usuario === idUsuario
          return (
            <li key={miembro.id_usuario} className="tarjeta-item">
              <div className="tarjeta-item__principal">
                <span className="tarjeta-item__titulo">
                  {nombre} {esYo && <span className="nota">(vos)</span>}
                </span>
                <span className="tarjeta-item__detalle">
                  {NOMBRES_PERFIL[miembro.perfil]}
                  {miembro.cargo && ` · ${miembro.cargo}`} · Desde el{' '}
                  {formatearFecha(miembro.incorporado_en)}
                </span>
              </div>
              <Etiqueta tipo={miembro.rol === 'referente' ? 'destacada' : 'neutra'}>
                {miembro.rol === 'referente' ? 'Referente' : 'Miembro'}
              </Etiqueta>
              {esReferente && editando === miembro.id_usuario && (
                <FormularioCargo
                  organizacion={organizacion}
                  miembro={miembro}
                  alTerminar={terminarEdicion}
                />
              )}
              {esReferente && editando !== miembro.id_usuario && (
                <div className="acciones-en-linea">
                  <button
                    type="button"
                    className="boton boton--secundario boton--chico"
                    onClick={() => {
                      setMensajeCargo(null)
                      setEditando(miembro.id_usuario)
                    }}
                    aria-label={`Editar el cargo de ${nombre}`}
                  >
                    Editar cargo
                  </button>
                  {!esYo && (
                    <>
                      <BotonConfirmar
                        texto="Designar Referente"
                        pregunta={`¿Designar a ${nombre} como Referente? Vas a pasar a ser miembro.`}
                        textoConfirmar="Designar"
                        onConfirmar={() =>
                          ejecutar(() => designarReferente(organizacion.id, miembro.id_usuario))
                        }
                      />
                      <BotonConfirmar
                        texto="Desvincular"
                        pregunta={`¿Desvincular a ${nombre}?`}
                        textoConfirmar="Desvincular"
                        peligro
                        onConfirmar={() =>
                          ejecutar(() => desvincularMiembro(organizacion.id, miembro.id_usuario))
                        }
                      />
                    </>
                  )}
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}

function SeccionInvitaciones({ organizacion, invitaciones, recargar }) {
  const { resultado, ejecutar } = useAccion(recargar)
  const { valores, setValores, errores, error, enviando, cambiar, enviar } = useFormulario({
    correo: '',
    cargo: '',
  })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje(null)
    const respuesta = await enviar((datos) => invitar(organizacion.id, datos.correo, datos.cargo))
    if (respuesta.ok) {
      setMensaje(respuesta.datos.mensaje)
      setValores({ correo: '', cargo: '' })
      await recargar()
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-invitar">
      <h2 id="titulo-invitar">Invitar miembros</h2>
      <p className="nota">
        Podés invitar a cualquier correo, tenga o no una cuenta. La invitación vence a los 7 días
        y ocupa un lugar del plan mientras esté pendiente.
      </p>
      <form onSubmit={manejarEnvio} className="formulario" noValidate>
        {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
        {error && <Aviso tipo="error">{error.message}</Aviso>}
        <div className="formulario__fila">
          <CampoTexto
            etiqueta="Correo electrónico"
            nombre="correo"
            tipo="email"
            value={valores.correo}
            onChange={cambiar}
            error={errores.correo}
            required
          />
          <CampoTexto
            etiqueta="Cargo"
            nombre="cargo"
            opcional
            value={valores.cargo}
            onChange={cambiar}
            error={errores.cargo}
          />
        </div>
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Enviando…' : 'Enviar invitación'}
        </button>
      </form>

      <h3>Invitaciones pendientes</h3>
      {resultado && <Aviso tipo={resultado.tipo}>{resultado.texto}</Aviso>}
      {invitaciones.length === 0 ? (
        <p className="nota">No hay invitaciones pendientes.</p>
      ) : (
        <ul className="lista-tarjetas">
          {invitaciones.map((invitacion) => (
            <li key={invitacion.id} className="tarjeta-item">
              <div className="tarjeta-item__principal">
                <span className="tarjeta-item__titulo">{invitacion.correo}</span>
                <span className="tarjeta-item__detalle">
                  {invitacion.cargo && `${invitacion.cargo} · `}
                  {invitacion.vigente
                    ? `Vence el ${formatearFecha(invitacion.vence_en)}`
                    : 'Vencida'}
                </span>
              </div>
              {!invitacion.vigente && <Etiqueta tipo="alerta">Vencida</Etiqueta>}
              <div className="acciones-en-linea">
                <button
                  type="button"
                  className="boton boton--secundario boton--chico"
                  onClick={() => ejecutar(() => reenviarInvitacion(organizacion.id, invitacion.id))}
                  aria-label={`Reenviar la invitación a ${invitacion.correo}`}
                >
                  Reenviar
                </button>
                <BotonConfirmar
                  texto="Cancelar invitación"
                  pregunta={`¿Cancelar la invitación a ${invitacion.correo}?`}
                  textoConfirmar="Cancelar invitación"
                  peligro
                  onConfirmar={() =>
                    ejecutar(() => cancelarInvitacion(organizacion.id, invitacion.id))
                  }
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function SeccionSalida({ organizacion, esReferente, unicoMiembro }) {
  const navegar = useNavigate()
  const [error, setError] = useState(null)
  const [confirmacion, setConfirmacion] = useState('')
  const [enviando, setEnviando] = useState(false)
  const nombreCoincide = confirmacion.trim() === organizacion.nombre

  async function salir(accion) {
    setError(null)
    setEnviando(true)
    try {
      const respuesta = await accion()
      navegar('/organizaciones', { state: { mensaje: respuesta.mensaje } })
    } catch (errorApi) {
      setError(errorApi.message)
      setEnviando(false)
    }
  }

  const textoAbandono = unicoMiembro
    ? 'Sos el único miembro: si abandonás la organización, se eliminará.'
    : esReferente
      ? 'Sos el Referente: para abandonar la organización, primero designá a otro miembro como Referente.'
      : 'Vas a dejar de tener acceso a la organización.'

  return (
    <section className="seccion zona-riesgo" aria-labelledby="titulo-salida">
      <h2 id="titulo-salida">Salir o eliminar</h2>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <h3>Abandonar la organización</h3>
      <p>{textoAbandono}</p>
      <BotonConfirmar
        texto="Abandonar la organización"
        pregunta={unicoMiembro ? '¿Abandonar y eliminar la organización?' : '¿Abandonar la organización?'}
        textoConfirmar="Abandonar"
        peligro
        deshabilitado={esReferente && !unicoMiembro}
        onConfirmar={() => salir(() => abandonarOrganizacion(organizacion.id, unicoMiembro))}
      />

      {esReferente && (
        <>
          <h3>Eliminar la organización</h3>
          <p>
            Se eliminan la organización, sus miembros y sus invitaciones, y se avisa por correo a
            todos los miembros. No se puede deshacer.
          </p>
          <form
            className="formulario"
            onSubmit={(evento) => {
              evento.preventDefault()
              salir(() => eliminarOrganizacion(organizacion.id, confirmacion))
            }}
            noValidate
          >
            <CampoTexto
              etiqueta={`Para confirmar, escribí el nombre: ${organizacion.nombre}`}
              nombre="confirmacion"
              value={confirmacion}
              onChange={(evento) => setConfirmacion(evento.target.value)}
              autoComplete="off"
            />
            <button
              type="submit"
              className="boton boton--peligro"
              disabled={!nombreCoincide || enviando}
            >
              Eliminar la organización
            </button>
          </form>
        </>
      )}
    </section>
  )
}

export default function PaginaOrganizacion() {
  const { id } = useParams()
  const { state } = useLocation()
  const { usuario } = useSesion()
  const cargar = useCallback(() => cargarOrganizacion(id), [id])
  const { datos, error, cargando, recargar } = useDatos(cargar)

  if (cargando) return <Cargando texto="Cargando la organización…" />
  if (error) {
    return (
      <>
        <h1>Organización</h1>
        <Aviso tipo="error">{error.message}</Aviso>
      </>
    )
  }

  const { organizacion, miembros, invitaciones } = datos
  const esReferente = organizacion.mi_rol === 'referente'

  return (
    <>
      <div className="encabezado-pagina">
        <h1>{organizacion.nombre}</h1>
        <Etiqueta tipo={esReferente ? 'destacada' : 'neutra'}>
          {esReferente ? 'Sos Referente' : 'Sos miembro'}
        </Etiqueta>
      </div>
      <p className="subtitulo">{organizacion.tipo_nombre}</p>
      {state?.mensaje && <Aviso tipo="exito">{state.mensaje}</Aviso>}

      <SeccionMiembros
        organizacion={organizacion}
        miembros={miembros}
        esReferente={esReferente}
        idUsuario={usuario.id}
        recargar={recargar}
      />
      {esReferente && (
        <SeccionInvitaciones
          organizacion={organizacion}
          invitaciones={invitaciones}
          recargar={recargar}
        />
      )}
      <SeccionDatos
        key={organizacion.nombre + organizacion.tipo}
        organizacion={organizacion}
        esReferente={esReferente}
        alGuardar={recargar}
      />
      <SeccionSalida
        organizacion={organizacion}
        esReferente={esReferente}
        unicoMiembro={miembros.length === 1}
      />
    </>
  )
}
