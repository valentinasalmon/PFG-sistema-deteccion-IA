/**
 * Pantalla de un caso: datos, estado, accesos, transferencia y eliminación.
 *
 * Solo se muestran las acciones que el permiso habilita, según la lista
 * ``acciones`` que calcula el backend (RF24 CA1, RN20). Las imágenes están
 * en ``SeccionImagenes`` (006) y los análisis en ``SeccionAnalisis`` (007); los
 * informes llegan con la funcionalidad 008.
 *
 * Realiza: RF24, RF25, RF27 a RF33; CA4, CA7 a CA19 de la funcionalidad 005.
 */
import { useCallback, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router'
import {
  cambiarEstadoCaso,
  cancelarTransferencia,
  compartirCaso,
  editarCaso,
  eliminarCaso,
  modificarAcceso,
  obtenerCaso,
  revocarAcceso,
  transferirCaso,
} from '../api/casos.js'
import { listarMiembros } from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import BotonConfirmar from '../componentes/BotonConfirmar.jsx'
import CampoAreaTexto from '../componentes/CampoAreaTexto.jsx'
import CampoSeleccion from '../componentes/CampoSeleccion.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import SeccionAnalisis from '../componentes/SeccionAnalisis.jsx'
import SeccionImagenes from '../componentes/SeccionImagenes.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { OPCIONES_NIVEL, OPCIONES_TIPO, tipoDeEtiquetaDeEstado } from '../utilidades/casos.js'
import { formatearDia, formatearFecha, hoyIso } from '../utilidades/fechas.js'

async function cargarCaso(id) {
  const datos = await obtenerCaso(id)
  const { caso } = datos
  const necesitaMiembros =
    caso.espacio.tipo === 'organizacion' && (caso.acciones.compartir || caso.acciones.transferir)
  const miembros = necesitaMiembros ? await listarMiembros(caso.espacio.id) : []
  return { ...datos, miembros }
}

function SeccionDatos({ caso, alGuardar }) {
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({
    tipo: caso.tipo,
    fecha_hecho: caso.fecha_hecho,
    lugar: caso.lugar,
    expediente: caso.expediente ?? '',
    descripcion: caso.descripcion ?? '',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) => editarCaso(caso.id, datos))
    if (resultado.ok) await alGuardar(resultado.datos.mensaje)
  }

  return (
    <section className="seccion" aria-labelledby="titulo-datos-caso">
      <h2 id="titulo-datos-caso">Datos del caso</h2>
      <dl className="datos-fijos">
        <dt>Responsable</dt>
        <dd>{caso.responsable.nombre}</dd>
        <dt>Creado</dt>
        <dd>{formatearFecha(caso.creado_en)}</dd>
        {caso.retencion_vence && (
          <>
            <dt>Retención</dt>
            <dd>Los datos se conservan hasta el {formatearFecha(caso.retencion_vence)}</dd>
          </>
        )}
        {!caso.acciones.editar && (
          <>
            <dt>Tipo</dt>
            <dd>{caso.tipo_nombre}</dd>
            <dt>Fecha del hecho</dt>
            <dd>{formatearDia(caso.fecha_hecho)}</dd>
            <dt>Lugar</dt>
            <dd>{caso.lugar}</dd>
            <dt>Expediente</dt>
            <dd>{caso.expediente ?? '—'}</dd>
            <dt>Descripción</dt>
            <dd>{caso.descripcion ?? '—'}</dd>
          </>
        )}
      </dl>
      {caso.acciones.editar ? (
        <form onSubmit={manejarEnvio} className="formulario" noValidate>
          {error && <Aviso tipo="error">{error.message}</Aviso>}
          <div className="formulario__fila">
            <CampoSeleccion
              etiqueta="Tipo"
              nombre="tipo"
              value={valores.tipo}
              onChange={cambiar}
              opciones={OPCIONES_TIPO}
              error={errores.tipo}
            />
            <CampoTexto
              etiqueta="Fecha del hecho"
              nombre="fecha_hecho"
              tipo="date"
              max={hoyIso()}
              value={valores.fecha_hecho}
              onChange={cambiar}
              error={errores.fecha_hecho}
            />
          </div>
          <CampoTexto etiqueta="Lugar del hecho" nombre="lugar" value={valores.lugar} onChange={cambiar} error={errores.lugar} />
          <CampoTexto
            etiqueta="Expediente"
            nombre="expediente"
            opcional
            value={valores.expediente}
            onChange={cambiar}
            error={errores.expediente}
          />
          <CampoAreaTexto
            etiqueta="Descripción"
            nombre="descripcion"
            opcional
            value={valores.descripcion}
            onChange={cambiar}
            error={errores.descripcion}
          />
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar los datos'}
          </button>
        </form>
      ) : (
        caso.estado === 'cerrado' || caso.estado === 'archivado' ? (
          <p className="nota">El caso es de solo lectura. Para editarlo, su Responsable tiene que reabrirlo.</p>
        ) : null
      )}
    </section>
  )
}

function SeccionEstado({ caso, ejecutar }) {
  const { acciones } = caso
  if (!acciones.cerrar && !acciones.archivar && !acciones.desarchivar && !acciones.reabrir) return null
  return (
    <section className="seccion" aria-labelledby="titulo-estado">
      <h2 id="titulo-estado">Estado</h2>
      <p className="nota">
        Cerrar deja el caso en solo lectura y comienza el plazo de retención de 2 años; al
        reabrirlo, el plazo se detiene.
      </p>
      <div className="acciones-en-linea">
        {acciones.cerrar && (
          <BotonConfirmar
            texto="Cerrar el caso"
            pregunta="¿Cerrar el caso? Queda en solo lectura y comienza el plazo de retención."
            textoConfirmar="Cerrar"
            onConfirmar={() => ejecutar(() => cambiarEstadoCaso(caso.id, 'cerrar'))}
          />
        )}
        {acciones.archivar && (
          <BotonConfirmar
            texto="Archivar"
            pregunta="¿Archivar el caso? Deja de aparecer en el listado por defecto."
            textoConfirmar="Archivar"
            onConfirmar={() => ejecutar(() => cambiarEstadoCaso(caso.id, 'archivar'))}
          />
        )}
        {acciones.desarchivar && (
          <BotonConfirmar
            texto="Desarchivar"
            pregunta="¿Desarchivar el caso? Vuelve a Cerrado."
            textoConfirmar="Desarchivar"
            onConfirmar={() => ejecutar(() => cambiarEstadoCaso(caso.id, 'desarchivar'))}
          />
        )}
        {acciones.reabrir && (
          <BotonConfirmar
            texto="Reabrir"
            pregunta="¿Reabrir el caso? Se detiene el plazo de retención."
            textoConfirmar="Reabrir"
            onConfirmar={() => ejecutar(() => cambiarEstadoCaso(caso.id, 'reabrir'))}
          />
        )}
      </div>
    </section>
  )
}

function SeccionAccesos({ caso, accesos, miembros, ejecutar }) {
  const [destino, setDestino] = useState('organizacion')
  const [nivel, setNivel] = useState('lectura')
  const puedeCompartir = caso.acciones.compartir
  const destinatarios = [
    { valor: 'organizacion', texto: 'Toda la organización' },
    ...miembros
      .filter((miembro) => miembro.id_usuario !== caso.responsable.id)
      .map((miembro) => ({ valor: String(miembro.id_usuario), texto: `${miembro.nombre} ${miembro.apellido}` })),
  ]

  return (
    <section className="seccion" aria-labelledby="titulo-accesos">
      <h2 id="titulo-accesos">Accesos</h2>
      {accesos.length === 0 ? (
        <p className="nota">Solo el Responsable tiene acceso a este caso.</p>
      ) : (
        <ul className="lista-tarjetas">
          {accesos.map((acceso) => {
            const nombre = acceso.toda_organizacion ? 'Toda la organización' : acceso.usuario.nombre
            return (
              <li key={acceso.id} className="tarjeta-item">
                <div className="tarjeta-item__principal">
                  <span className="tarjeta-item__titulo">{nombre}</span>
                  <span className="tarjeta-item__detalle">Desde el {formatearFecha(acceso.otorgado_en)}</span>
                </div>
                {puedeCompartir ? (
                  <div className="acciones-en-linea">
                    <label className="solo-lectores" htmlFor={`nivel-${acceso.id}`}>
                      Permiso de {nombre}
                    </label>
                    <select
                      id={`nivel-${acceso.id}`}
                      className="campo__control campo__control--chico"
                      value={acceso.nivel}
                      onChange={(evento) => ejecutar(() => modificarAcceso(caso.id, acceso.id, evento.target.value))}
                    >
                      <option value="lectura">Lectura</option>
                      <option value="colaboracion">Colaboración</option>
                    </select>
                    <BotonConfirmar
                      texto="Revocar"
                      pregunta={`¿Revocar el acceso de ${nombre}?`}
                      textoConfirmar="Revocar"
                      peligro
                      onConfirmar={() => ejecutar(() => revocarAcceso(caso.id, acceso.id))}
                    />
                  </div>
                ) : (
                  <Etiqueta>{acceso.nivel_nombre}</Etiqueta>
                )}
              </li>
            )
          })}
        </ul>
      )}
      {puedeCompartir && (
        <form
          className="formulario"
          onSubmit={(evento) => {
            evento.preventDefault()
            ejecutar(() => compartirCaso(caso.id, nivel, destino === 'organizacion' ? null : Number(destino)))
          }}
        >
          <h3>Compartir</h3>
          <div className="formulario__fila">
            <CampoSeleccion
              etiqueta="Con quién"
              nombre="destino"
              value={destino}
              onChange={(evento) => setDestino(evento.target.value)}
              opciones={destinatarios}
            />
            <CampoSeleccion
              etiqueta="Permiso"
              nombre="nivel"
              value={nivel}
              onChange={(evento) => setNivel(evento.target.value)}
              opciones={OPCIONES_NIVEL}
            />
          </div>
          <button type="submit" className="boton">
            Compartir el caso
          </button>
        </form>
      )}
    </section>
  )
}

function SeccionTransferir({ caso, miembros, ejecutar }) {
  const esPersonal = caso.espacio.tipo === 'personal'
  const candidatos = miembros.filter((miembro) => miembro.id_usuario !== caso.responsable.id)
  const [destino, setDestino] = useState(esPersonal ? '' : String(candidatos[0]?.id_usuario ?? ''))
  const [conservar, setConservar] = useState(true)

  if (caso.transferencia_pendiente) {
    return (
      <section className="seccion" aria-labelledby="titulo-transferir">
        <h2 id="titulo-transferir">Transferir</h2>
        <Aviso tipo="info">
          Le pediste a {caso.transferencia_pendiente.nombre} ({caso.transferencia_pendiente.correo})
          que acepte el caso. Seguís siendo Responsable hasta que lo acepte.
        </Aviso>
        <button
          type="button"
          className="boton boton--secundario"
          onClick={() => ejecutar(() => cancelarTransferencia(caso.id))}
        >
          Cancelar la transferencia
        </button>
      </section>
    )
  }

  return (
    <section className="seccion" aria-labelledby="titulo-transferir">
      <h2 id="titulo-transferir">Transferir</h2>
      <p className="nota">
        {esPersonal
          ? 'El caso pasa al espacio personal de otra persona registrada con perfil Abogado, cuando acepte.'
          : 'Otro miembro de la organización pasa a ser Responsable del caso.'}
      </p>
      {!esPersonal && candidatos.length === 0 ? (
        <p className="nota">No hay otros miembros en la organización.</p>
      ) : (
        <form
          className="formulario"
          onSubmit={(evento) => {
            evento.preventDefault()
            ejecutar(() => transferirCaso(caso.id, destino, conservar))
          }}
        >
          {esPersonal ? (
            <CampoTexto
              etiqueta="Correo de la persona"
              nombre="destino"
              tipo="email"
              value={destino}
              onChange={(evento) => setDestino(evento.target.value)}
              required
            />
          ) : (
            <>
              <CampoSeleccion
                etiqueta="Nuevo Responsable"
                nombre="destino"
                value={destino}
                onChange={(evento) => setDestino(evento.target.value)}
                opciones={candidatos.map((miembro) => ({
                  valor: String(miembro.id_usuario),
                  texto: `${miembro.nombre} ${miembro.apellido}`,
                }))}
              />
              <label className="opcion">
                <input
                  type="checkbox"
                  checked={conservar}
                  onChange={(evento) => setConservar(evento.target.checked)}
                />
                Conservar el permiso de Colaboración
              </label>
            </>
          )}
          <button type="submit" className="boton boton--secundario">
            Transferir el caso
          </button>
        </form>
      )}
    </section>
  )
}

function SeccionEliminar({ caso }) {
  const navegar = useNavigate()
  const [confirmacion, setConfirmacion] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const coincide = confirmacion.trim().toUpperCase() === caso.numero

  async function eliminar(evento) {
    evento.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      const respuesta = await eliminarCaso(caso.id, confirmacion)
      navegar('/casos', { state: { mensaje: respuesta.mensaje } })
    } catch (errorApi) {
      setError(errorApi.message)
      setEnviando(false)
    }
  }

  return (
    <section className="seccion zona-riesgo" aria-labelledby="titulo-eliminar">
      <h2 id="titulo-eliminar">Eliminar el caso</h2>
      <p>
        Se eliminan el caso y sus datos de forma definitiva, y se avisa a quienes tenían acceso. No
        se puede deshacer.
      </p>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <form className="formulario" onSubmit={eliminar} noValidate>
        <CampoTexto
          etiqueta={`Para confirmar, escribí el número: ${caso.numero}`}
          nombre="confirmacion"
          value={confirmacion}
          onChange={(evento) => setConfirmacion(evento.target.value)}
          autoComplete="off"
        />
        <button type="submit" className="boton boton--peligro" disabled={!coincide || enviando}>
          Eliminar el caso
        </button>
      </form>
    </section>
  )
}

export default function PaginaCaso() {
  const { id } = useParams()
  const { state } = useLocation()
  const cargar = useCallback(() => cargarCaso(id), [id])
  const { datos, error, cargando, recargar } = useDatos(cargar)
  const [aviso, setAviso] = useState(state?.mensaje ? { tipo: 'exito', texto: state.mensaje } : null)

  const ejecutar = useCallback(
    async (accion) => {
      setAviso(null)
      try {
        const respuesta = await accion()
        await recargar()
        setAviso({ tipo: 'exito', texto: respuesta?.mensaje ?? 'Listo.' })
      } catch (errorApi) {
        setAviso({ tipo: 'error', texto: errorApi.message })
      }
    },
    [recargar],
  )

  if (cargando) return <Cargando texto="Cargando el caso…" />
  if (error) {
    return (
      <>
        <h1>Caso</h1>
        <Aviso tipo="error">{error.message}</Aviso>
      </>
    )
  }

  const { caso, accesos, miembros } = datos
  return (
    <>
      <div className="encabezado-pagina">
        <h1>{caso.numero}</h1>
        <div className="acciones-en-linea">
          <Etiqueta tipo={tipoDeEtiquetaDeEstado(caso.estado)}>{caso.estado_nombre}</Etiqueta>
          <Etiqueta>{caso.mi_permiso_nombre}</Etiqueta>
        </div>
      </div>
      <p className="subtitulo">
        {caso.tipo_nombre} · {caso.espacio.nombre} · Hecho del {formatearDia(caso.fecha_hecho)}
      </p>
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}

      <SeccionDatos
        key={`${caso.actualizado_en}-${caso.estado}`}
        caso={caso}
        alGuardar={async (mensaje) => {
          setAviso({ tipo: 'exito', texto: mensaje })
          await recargar()
        }}
      />
      {/* Se vuelve a montar al cambiar el estado: cerrar o reabrir cambia qué se puede hacer. */}
      <SeccionImagenes key={caso.estado} idCaso={caso.id} alSolicitarAnalisis={recargar} />
      <SeccionAnalisis key={`analisis-${caso.estado}`} idCaso={caso.id} alTerminar={recargar} />
      <SeccionEstado caso={caso} ejecutar={ejecutar} />
      {caso.espacio.tipo === 'organizacion' && (
        <SeccionAccesos caso={caso} accesos={accesos} miembros={miembros} ejecutar={ejecutar} />
      )}
      {caso.acciones.transferir && <SeccionTransferir caso={caso} miembros={miembros} ejecutar={ejecutar} />}
      {caso.acciones.eliminar && <SeccionEliminar caso={caso} />}
    </>
  )
}
