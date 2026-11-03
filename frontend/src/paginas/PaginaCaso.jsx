/**
 * Pantalla de un caso: datos, estado, accesos, transferencia y eliminación.
 *
 * Solo se muestran las acciones que el permiso habilita, según la lista
 * ``acciones`` que calcula el backend (RF24 CA1, RN20). Las imágenes están
 * en ``SeccionImagenes`` (006), los análisis en ``SeccionAnalisis`` (007) y los
 * informes PDF en ``SeccionInformes`` (008).
 *
 * Disposición (022 y 028): a la izquierda el trabajo sobre la evidencia y a la
 * derecha los datos del caso y su gestión, plegada. Desde la 028 el trabajo
 * sobre la evidencia se divide en tres etapas (cargar imágenes, análisis e
 * informe), y desde la 034 se muestran como un flujo vertical continuo
 * (``FlujoDelCaso``) en el que solo se abre una por vez. La etapa
 * elegida queda en la dirección (``?etapa=``); sin elegir, se abre la que
 * corresponde al estado del caso. Los datos se ven resumidos y se editan al
 * tocar "Editar los datos".
 *
 * Realiza: RF24, RF25, RF27 a RF33; CA4, CA7 a CA19 de la funcionalidad 005; RNF10.
 */
import { useCallback, useState } from 'react'
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router'
import {
  cambiarEstadoCaso,
  cancelarTransferencia,
  compartirCaso,
  editarCaso,
  eliminarCaso,
  modificarAcceso,
  obtenerCaso,
  prorrogarRetencion,
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
import EtiquetaEstado from '../componentes/EtiquetaEstado.jsx'
import Icono from '../componentes/Icono.jsx'
import SeccionAnalisis from '../componentes/SeccionAnalisis.jsx'
import SeccionImagenes from '../componentes/SeccionImagenes.jsx'
import SeccionInformes from '../componentes/SeccionInformes.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'
import { OPCIONES_NIVEL, OPCIONES_TIPO } from '../utilidades/casos.js'
import { textosDelRubro } from '../utilidades/lenguaje.js'
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
  const [editando, setEditando] = useState(false)
  const { usuario } = useSesion()
  const referencia = textosDelRubro(usuario.perfil).etiquetaReferencia
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
    if (resultado.ok) {
      setEditando(false)
      await alGuardar(resultado.datos.mensaje)
    }
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
        {!editando && (
          <>
            <dt>Tipo</dt>
            <dd>{caso.tipo_nombre}</dd>
            <dt>Fecha del hecho</dt>
            <dd>{formatearDia(caso.fecha_hecho)}</dd>
            <dt>{referencia}</dt>
            <dd>{caso.expediente ?? '—'}</dd>
            <dt>Descripción</dt>
            <dd>{caso.descripcion ?? '—'}</dd>
          </>
        )}
      </dl>
      {caso.acciones.editar && !editando && (
        <button
          type="button"
          className="boton boton--secundario boton--ancho"
          onClick={() => setEditando(true)}
        >
          Editar los datos
        </button>
      )}
      {caso.acciones.editar ? (
        editando && (
          <form onSubmit={manejarEnvio} className="formulario" noValidate>
            {error && <Aviso tipo="error">{error.message}</Aviso>}
            <div className="formulario__fila formulario__fila--apilada">
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
            <CampoTexto
              etiqueta="Lugar del hecho"
              nombre="lugar"
              value={valores.lugar}
              onChange={cambiar}
              error={errores.lugar}
            />
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
            <div className="pasos__acciones">
              <button type="button" className="boton boton--fantasma" onClick={() => setEditando(false)}>
                Cancelar
              </button>
              <button type="submit" className="boton" disabled={enviando}>
                {enviando ? 'Guardando…' : 'Guardar los datos'}
              </button>
            </div>
          </form>
        )
      ) : caso.estado === 'cerrado' || caso.estado === 'archivado' ? (
        <p className="nota">El caso es de solo lectura. Para editarlo, su Responsable tiene que reabrirlo.</p>
      ) : null}
    </section>
  )
}

/** Prórroga de la retención con motivo obligatorio (RF51, funcionalidad 015). */
function FormularioProrroga({ caso, ejecutar }) {
  const [abierto, setAbierto] = useState(false)
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState(null)

  if (!abierto) {
    return (
      <button type="button" className="boton boton--secundario" onClick={() => setAbierto(true)}>
        Prorrogar 1 año
      </button>
    )
  }
  return (
    <form
      className="formulario formulario--compacto"
      noValidate
      onSubmit={async (evento) => {
        evento.preventDefault()
        if (!motivo.trim()) {
          setError('Indicá el motivo de la prórroga, por ejemplo, un juicio en trámite.')
          return
        }
        await ejecutar(() => prorrogarRetencion(caso.id, motivo))
      }}
    >
      <CampoTexto
        etiqueta="Motivo de la prórroga"
        nombre="motivo"
        value={motivo}
        onChange={(evento) => setMotivo(evento.target.value)}
        error={error}
        ayuda="Queda registrado en la auditoría del caso."
        required
      />
      <div className="acciones-en-linea">
        <button type="button" className="boton boton--fantasma" onClick={() => setAbierto(false)}>
          Cancelar
        </button>
        <button type="submit" className="boton">
          Prorrogar
        </button>
      </div>
    </form>
  )
}

/**
 * Gestión del caso plegada en la columna lateral (028): el título y un
 * resumen a la vista, el detalle al tocarlo.
 */
function Plegable({ id, titulo, resumen, abierto = false, children }) {
  return (
    <details className="plegable" open={abierto}>
      <summary>
        <h2 id={id}>{titulo}</h2>
        {resumen && <span className="plegable__resumen">{resumen}</span>}
      </summary>
      <div className="plegable__cuerpo">{children}</div>
    </details>
  )
}

function SeccionEstado({ caso, ejecutar }) {
  const { acciones } = caso
  if (!acciones.cerrar && !acciones.archivar && !acciones.desarchivar && !acciones.reabrir) return null
  const vence = caso.retencion_vence ? new Date(caso.retencion_vence) : null
  const diasRestantes = vence ? Math.ceil((vence - new Date()) / 86400000) : null
  return (
    <Plegable
      id="titulo-estado"
      titulo="Estado"
      resumen={caso.estado_nombre}
      abierto={diasRestantes !== null && diasRestantes <= 30}
    >
      <p className="nota">
        Cerrar deja el caso en solo lectura y comienza el plazo de retención de 5 años; al reabrirlo, el plazo
        se detiene.
      </p>
      {vence && (
        <div className={`retencion ${diasRestantes <= 30 ? 'retencion--proxima' : ''}`}>
          <p>
            Se elimina el <strong>{formatearFecha(caso.retencion_vence)}</strong>
            {diasRestantes <= 30 && ` (en ${Math.max(diasRestantes, 0)} días)`}.
          </p>
          {acciones.prorrogar && <FormularioProrroga caso={caso} ejecutar={ejecutar} />}
        </div>
      )}
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
    </Plegable>
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
      .map((miembro) => ({
        valor: String(miembro.id_usuario),
        texto: `${miembro.nombre} ${miembro.apellido}`,
      })),
  ]

  return (
    <Plegable
      id="titulo-accesos"
      titulo="Accesos"
      resumen={accesos.length === 0 ? 'Solo el Responsable' : `${accesos.length} con acceso`}
    >
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
                      onChange={(evento) =>
                        ejecutar(() => modificarAcceso(caso.id, acceso.id, evento.target.value))
                      }
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
    </Plegable>
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
          Le pediste a {caso.transferencia_pendiente.nombre} ({caso.transferencia_pendiente.correo}) que
          acepte el caso. Seguís siendo Responsable hasta que lo acepte.
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
        Se eliminan el caso y sus datos de forma definitiva, y se avisa a quienes tenían acceso. No se puede
        deshacer.
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

const ETAPAS = ['imagenes', 'analisis', 'informe']

/** Etapa que se abre sin elegir otra, según el estado del caso (028). */
function etapaPorDefecto(caso) {
  if (caso.estado === 'borrador') return 'imagenes'
  if (caso.estado === 'en_analisis') return 'analisis'
  return caso.cantidad_informes > 0 ? 'informe' : 'analisis'
}

/** Texto y situación (hecha, actual o pendiente) de cada etapa. */
function describirEtapas(caso) {
  const conImagenes = caso.cantidad_imagenes > 0
  const analizado = ['analizado', 'cerrado', 'archivado'].includes(caso.estado)
  return {
    imagenes: {
      texto:
        conImagenes && caso.estado !== 'borrador'
          ? `Imágenes cargadas (${caso.cantidad_imagenes})`
          : 'Cargar imágenes',
      hecha: caso.estado !== 'borrador' && conImagenes,
    },
    analisis: {
      texto:
        caso.estado === 'en_analisis' ? 'Análisis en curso' : analizado ? 'Análisis terminado' : 'Análisis',
      hecha: analizado,
    },
    informe: {
      texto: caso.cantidad_informes > 1 ? `Informes (${caso.cantidad_informes})` : 'Informe',
      hecha: false,
    },
  }
}

const ICONO_DE_ETAPA = { imagenes: 'imagen', analisis: 'analisis', informe: 'documento' }

/** Resumen corto y si el paso ya se puede abrir (034). */
function resumirEtapas(caso) {
  const conImagenes = caso.cantidad_imagenes > 0
  const analizado = ['analizado', 'cerrado', 'archivado'].includes(caso.estado)
  const informes = caso.cantidad_informes
  return {
    imagenes: {
      resumen: conImagenes
        ? `${caso.cantidad_imagenes} ${caso.cantidad_imagenes === 1 ? 'foto' : 'fotos'}`
        : 'Sumá las fotos del hecho',
      disponible: true,
    },
    analisis: {
      resumen:
        caso.estado === 'en_analisis'
          ? 'En curso'
          : analizado
            ? 'Listo · revisá los indicios'
            : 'Se habilita cuando cargues las fotos',
      disponible: conImagenes,
    },
    informe: {
      resumen:
        informes > 0
          ? `${informes} ${informes === 1 ? 'informe' : 'informes'}`
          : 'Se genera al terminar el análisis',
      disponible: analizado || informes > 0,
    },
  }
}

/**
 * El caso como un flujo vertical continuo (034): Imágenes → Análisis →
 * Informe unidos por una línea. El paso abierto muestra su contenido; los
 * terminados quedan plegados en verde con su resumen; los pendientes dicen
 * cuándo se habilitan. Cada título es un enlace (``?etapa=``) para abrirlo.
 */
function FlujoDelCaso({ caso, actual, alElegir, children }) {
  const etapas = describirEtapas(caso)
  const resumenes = resumirEtapas(caso)
  return (
    <ol className="flujo-caso" aria-label="Etapas del caso">
      {ETAPAS.map((etapa) => {
        const { texto, hecha } = etapas[etapa]
        const { resumen, disponible } = resumenes[etapa]
        const abierta = etapa === actual
        const estado = abierta ? 'actual' : hecha ? 'hecho' : 'pendiente'
        const abrir = (evento) => {
          evento.preventDefault()
          alElegir(etapa)
        }
        return (
          <li key={etapa} className={`flujo-caso__paso flujo-caso__paso--${estado}`}>
            <span className="flujo-caso__nodo" aria-hidden="true">
              <Icono nombre={hecha && !abierta ? 'marca' : ICONO_DE_ETAPA[etapa]} tamanio={20} />
            </span>
            <div className="flujo-caso__cabecera">
              {disponible || abierta ? (
                <a
                  href={`?etapa=${etapa}`}
                  className="flujo-caso__titulo"
                  aria-current={abierta ? 'page' : undefined}
                  onClick={abrir}
                >
                  {texto}
                </a>
              ) : (
                <span className="flujo-caso__titulo">{texto}</span>
              )}
              {hecha && !abierta && <span className="flujo-caso__chip flujo-caso__chip--listo">Listo</span>}
              {abierta && <span className="flujo-caso__chip">Abierto</span>}
              {!abierta && <span className="flujo-caso__resumen">{resumen}</span>}
              {!abierta && disponible && (
                <button type="button" className="boton boton--fantasma boton--chico" onClick={abrir}>
                  {hecha ? 'Ver' : 'Abrir'}
                </button>
              )}
            </div>
            {abierta && <div className="flujo-caso__cuerpo">{children}</div>}
          </li>
        )
      })}
    </ol>
  )
}

export default function PaginaCaso() {
  const { id } = useParams()
  const { state } = useLocation()
  const cargar = useCallback(() => cargarCaso(id), [id])
  const { datos, error, cargando, recargar } = useDatos(cargar)
  const [aviso, setAviso] = useState(state?.mensaje ? { tipo: 'exito', texto: state.mensaje } : null)
  const [parametros, setParametros] = useSearchParams()

  const elegirEtapa = useCallback((etapa) => setParametros({ etapa }, { replace: true }), [setParametros])

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
  const pedida = parametros.get('etapa')
  const etapa = ETAPAS.includes(pedida) ? pedida : etapaPorDefecto(caso)
  return (
    <>
      <Link to="/casos" className="volver">
        <Icono nombre="derecha" tamanio={16} />
        Casos
      </Link>
      <header className="cabecera-caso">
        <div className="cabecera-caso__titulo">
          <h1>{caso.numero}</h1>
          <div className="acciones-en-linea">
            <EtiquetaEstado estado={caso.estado}>{caso.estado_nombre}</EtiquetaEstado>
            <Etiqueta>{caso.mi_permiso_nombre}</Etiqueta>
          </div>
        </div>
        <p className="cabecera-caso__lugar">{caso.lugar}</p>
        <p className="subtitulo">
          {caso.tipo_nombre} · {caso.espacio.nombre} · Hecho del {formatearDia(caso.fecha_hecho)}
        </p>
      </header>
      {aviso && <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>}

      <div className="dos-columnas dos-columnas--caso">
        <div className="dos-columnas__principal">
          <FlujoDelCaso caso={caso} actual={etapa} alElegir={elegirEtapa}>
            {/* Se vuelven a montar al cambiar el estado: cerrar o reabrir cambia qué se puede hacer. */}
            {etapa === 'imagenes' && (
              <SeccionImagenes
                key={caso.estado}
                idCaso={caso.id}
                alCambiar={recargar}
                alSolicitarAnalisis={async () => {
                  await recargar()
                  elegirEtapa('analisis')
                }}
              />
            )}
            {etapa === 'analisis' && (
              <SeccionAnalisis
                key={`analisis-${caso.estado}`}
                idCaso={caso.id}
                puedeGenerar={caso.acciones.editar}
                alTerminar={recargar}
                alVerInforme={() => elegirEtapa('informe')}
                alCargarImagenes={() => elegirEtapa('imagenes')}
              />
            )}
            {etapa === 'informe' && (
              <SeccionInformes
                key={`informes-${caso.actualizado_en}`}
                idCaso={caso.id}
                alVerAnalisis={() => elegirEtapa('analisis')}
              />
            )}
          </FlujoDelCaso>
        </div>
        <div className="dos-columnas__lateral">
          <SeccionDatos
            key={`${caso.actualizado_en}-${caso.estado}`}
            caso={caso}
            alGuardar={async (mensaje) => {
              setAviso({ tipo: 'exito', texto: mensaje })
              await recargar()
            }}
          />
          <SeccionEstado caso={caso} ejecutar={ejecutar} />
          {caso.espacio.tipo === 'organizacion' && (
            <SeccionAccesos caso={caso} accesos={accesos} miembros={miembros} ejecutar={ejecutar} />
          )}
          {(caso.acciones.transferir || caso.acciones.eliminar) && (
            <details className="plegable plegable--peligro" open={Boolean(caso.transferencia_pendiente)}>
              <summary>
                <span className="plegable__titulo">Transferir o eliminar el caso</span>
              </summary>
              <div className="plegable__cuerpo">
                {caso.acciones.transferir && (
                  <SeccionTransferir caso={caso} miembros={miembros} ejecutar={ejecutar} />
                )}
                {caso.acciones.eliminar && <SeccionEliminar caso={caso} />}
              </div>
            </details>
          )}
        </div>
      </div>
    </>
  )
}
