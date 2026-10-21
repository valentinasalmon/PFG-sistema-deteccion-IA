/**
 * Pantalla "Mi perfil": datos personales, cambio de contraseña, cambio de
 * correo, copia de los datos personales y eliminación de la cuenta.
 *
 * El perfil (Abogado o Aseguradora) se muestra pero no puede modificarse
 * (RN01). El cambio de correo pide la contraseña y queda pendiente hasta
 * confirmarlo desde la dirección nueva.
 *
 * La eliminación de la cuenta muestra primero qué falta resolver (casos a
 * cargo y organizaciones sin otro Referente) y solo entonces pide la
 * contraseña (RN05, RN08).
 *
 * Realiza: RF06 a RF09; RN01, RN02; CA16 a CA19 de la funcionalidad 002 y
 * CA1, CA5 a CA10 de la 019.
 */
import { useState } from 'react'
import { Link } from 'react-router'
import {
  actualizarPerfil,
  cambiarContrasenia,
  eliminarCuenta,
  situacionParaBaja,
  solicitarCambioCorreo,
  solicitarCopiaDeDatos,
} from '../api/perfil.js'
import Aviso from '../componentes/Aviso.jsx'
import Etiqueta from '../componentes/Etiqueta.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import SeccionPlan from '../componentes/SeccionPlan.jsx'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'
import { formatearFecha } from '../utilidades/fechas.js'

const NOMBRES_PERFIL = { abogado: 'Abogado o abogada', aseguradora: 'Aseguradora' }

function SeccionDatos() {
  const { usuario, actualizarUsuario } = useSesion()
  const esAbogado = usuario.perfil === 'abogado'
  const campoInstitucion = esAbogado ? 'colegio' : 'empresa'
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({
    nombre: usuario.nombre,
    apellido: usuario.apellido,
    [campoInstitucion]: usuario[campoInstitucion] ?? '',
  })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje(null)
    const resultado = await enviar((datos) => actualizarPerfil(datos))
    if (resultado.ok) {
      actualizarUsuario(resultado.datos)
      setMensaje('Tus datos fueron actualizados.')
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-datos">
      <h2 id="titulo-datos">Datos personales</h2>
      {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      <dl className="datos-fijos">
        <dt>Perfil</dt>
        <dd>
          {NOMBRES_PERFIL[usuario.perfil]}
          <span className="campo__ayuda"> · El perfil no puede modificarse.</span>
        </dd>
        <dt>Correo electrónico</dt>
        <dd>{usuario.correo}</dd>
      </dl>
      <form onSubmit={manejarEnvio} className="formulario" noValidate>
        <div className="formulario__fila">
          <CampoTexto
            etiqueta="Nombre"
            nombre="nombre"
            autoComplete="given-name"
            value={valores.nombre}
            onChange={cambiar}
            error={errores.nombre}
            required
          />
          <CampoTexto
            etiqueta="Apellido"
            nombre="apellido"
            autoComplete="family-name"
            value={valores.apellido}
            onChange={cambiar}
            error={errores.apellido}
            required
          />
        </div>
        <CampoTexto
          etiqueta={esAbogado ? 'Colegio de abogados' : 'Empresa'}
          nombre={campoInstitucion}
          opcional
          value={valores[campoInstitucion]}
          onChange={cambiar}
          error={errores[campoInstitucion]}
        />
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Guardando…' : 'Guardar los datos'}
        </button>
      </form>
    </section>
  )
}

const CONTRASENIAS_VACIAS = { contrasenia_actual: '', contrasenia_nueva: '', confirmacion: '' }

function SeccionContrasenia() {
  const { valores, setValores, errores, error, enviando, cambiar, enviar, marcarError } =
    useFormulario(CONTRASENIAS_VACIAS)
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje(null)
    if (valores.contrasenia_nueva !== valores.confirmacion) {
      marcarError('confirmacion', 'Las contraseñas no coinciden.')
      return
    }
    const resultado = await enviar((datos) =>
      cambiarContrasenia(datos.contrasenia_actual, datos.contrasenia_nueva),
    )
    if (resultado.ok) {
      setValores(CONTRASENIAS_VACIAS)
      setMensaje(
        'Tu contraseña fue actualizada. Cerramos las sesiones abiertas en otros dispositivos.',
      )
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-contrasenia">
      <h2 id="titulo-contrasenia">Contraseña</h2>
      {mensaje && <Aviso tipo="exito" flotante={false}>{mensaje}</Aviso>}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      <form onSubmit={manejarEnvio} className="formulario" noValidate>
        <CampoTexto
          etiqueta="Contraseña actual"
          nombre="contrasenia_actual"
          tipo="password"
          autoComplete="current-password"
          value={valores.contrasenia_actual}
          onChange={cambiar}
          error={errores.contrasenia_actual}
          required
        />
        <CampoTexto
          etiqueta="Contraseña nueva"
          nombre="contrasenia_nueva"
          tipo="password"
          autoComplete="new-password"
          value={valores.contrasenia_nueva}
          onChange={cambiar}
          error={errores.contrasenia_nueva}
          idDescripcion="reglas-contrasenia"
          required
        />
        <ReglasContrasenia contrasenia={valores.contrasenia_nueva} id="reglas-contrasenia" />
        <CampoTexto
          etiqueta="Repetí la contraseña nueva"
          nombre="confirmacion"
          tipo="password"
          autoComplete="new-password"
          value={valores.confirmacion}
          onChange={cambiar}
          error={errores.confirmacion}
          required
        />
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Guardando…' : 'Cambiar la contraseña'}
        </button>
      </form>
    </section>
  )
}

function SeccionCorreo() {
  const { valores, setValores, errores, error, enviando, cambiar, enviar } = useFormulario({
    correo_nuevo: '',
    contrasenia: '',
  })
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje(null)
    const resultado = await enviar((datos) =>
      solicitarCambioCorreo(datos.correo_nuevo, datos.contrasenia),
    )
    if (resultado.ok) {
      setMensaje(
        `${resultado.datos.mensaje} Hasta que lo confirmes, seguís ingresando con tu correo actual.`,
      )
      setValores({ correo_nuevo: '', contrasenia: '' })
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-correo">
      <h2 id="titulo-correo">Correo electrónico</h2>
      {mensaje && <Aviso tipo="exito" flotante={false}>{mensaje}</Aviso>}
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      <form onSubmit={manejarEnvio} className="formulario" noValidate>
        <CampoTexto
          etiqueta="Correo nuevo"
          nombre="correo_nuevo"
          tipo="email"
          autoComplete="email"
          value={valores.correo_nuevo}
          onChange={cambiar}
          error={errores.correo_nuevo}
          required
        />
        <CampoTexto
          etiqueta="Contraseña"
          nombre="contrasenia"
          tipo="password"
          autoComplete="current-password"
          ayuda="Por seguridad, confirmá tu contraseña para cambiar el correo."
          value={valores.contrasenia}
          onChange={cambiar}
          error={errores.contrasenia}
          required
        />
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Enviando…' : 'Cambiar el correo'}
        </button>
      </form>
    </section>
  )
}

function SeccionCopia() {
  const [copia, setCopia] = useState(null)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function generar() {
    setEnviando(true)
    setError(null)
    try {
      setCopia(await solicitarCopiaDeDatos())
    } catch (errorApi) {
      setError(errorApi.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="seccion" aria-labelledby="titulo-copia">
      <h2 id="titulo-copia">Copia de tus datos</h2>
      <p className="nota">
        Descargá los datos que la plataforma guarda sobre vos: tu cuenta, tus organizaciones, los
        casos a tu cargo y tu actividad registrada. No incluye datos de otras personas ni el
        contenido de los casos.
      </p>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {copia ? (
        <>
          <Aviso tipo="exito" flotante={false}>
            {copia.mensaje} Vencen el {formatearFecha(copia.vence_en)}.
          </Aviso>
          <div className="acciones-en-linea">
            <a className="boton" href={copia.enlaces.pdf} download>
              Descargar en PDF
            </a>
            <a className="boton boton--secundario" href={copia.enlaces.json} download>
              Descargar en JSON
            </a>
          </div>
        </>
      ) : (
        <button
          type="button"
          className="boton boton--secundario"
          onClick={generar}
          disabled={enviando}
        >
          {enviando ? 'Generando…' : 'Generar mi copia'}
        </button>
      )}
    </section>
  )
}

function cantidadDeCasos(cantidad) {
  return `${cantidad} ${cantidad === 1 ? 'caso' : 'casos'}`
}

function Pendientes({ situacion }) {
  return (
    <>
      {situacion.casos.length > 0 && (
        <>
          <h3>Casos a tu cargo</h3>
          <p className="nota">Transferí o eliminá cada caso desde su pantalla.</p>
          <ul className="lista-simple">
            {situacion.casos.map((caso) => (
              <li key={caso.id}>
                <Link to={`/casos/${caso.id}`}>{caso.numero}</Link> · {caso.espacio} ·{' '}
                {caso.estado_nombre}
              </li>
            ))}
          </ul>
        </>
      )}
      {situacion.referente_de.length > 0 && (
        <>
          <h3>Organizaciones sin otro Referente</h3>
          <p className="nota">Designá a otro miembro como Referente en cada una.</p>
          <ul className="lista-simple">
            {situacion.referente_de.map((organizacion) => (
              <li key={organizacion.id}>
                <Link to={`/organizaciones/${organizacion.id}`}>{organizacion.nombre}</Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  )
}

function SeccionEliminar() {
  const { terminarSesion } = useSesion()
  const [situacion, setSituacion] = useState(null)
  const [errorCarga, setErrorCarga] = useState(null)
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({ contrasenia: '' })

  async function revisar() {
    setErrorCarga(null)
    try {
      setSituacion(await situacionParaBaja())
    } catch (errorApi) {
      setErrorCarga(errorApi.message)
    }
  }

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) => eliminarCuenta(datos.contrasenia))
    if (resultado.ok) terminarSesion('eliminada')
  }

  return (
    <section className="seccion zona-riesgo" aria-labelledby="titulo-eliminar-cuenta">
      <h2 id="titulo-eliminar-cuenta">Eliminar mi cuenta</h2>
      <p>
        Se eliminan tu cuenta y tus datos personales de forma definitiva, y se cierran todas tus
        sesiones. No se puede deshacer.
      </p>
      {errorCarga && <Aviso tipo="error">{errorCarga}</Aviso>}
      {!situacion ? (
        <button type="button" className="boton boton--secundario" onClick={revisar}>
          Quiero eliminar mi cuenta
        </button>
      ) : (
        <>
          <Pendientes situacion={situacion} />
          {situacion.a_eliminar.length > 0 && (
            <Aviso tipo="info">
              Sos el único miembro de{' '}
              {situacion.a_eliminar
                .map((o) => `${o.nombre} (${cantidadDeCasos(o.cantidad_casos)})`)
                .join(', ')}
              : se eliminará con tu cuenta, junto con sus casos.
            </Aviso>
          )}
          {situacion.puede_eliminar ? (
            <form onSubmit={manejarEnvio} className="formulario" noValidate>
              {error && <Aviso tipo="error">{error.message}</Aviso>}
              <CampoTexto
                etiqueta="Contraseña"
                nombre="contrasenia"
                tipo="password"
                autoComplete="current-password"
                ayuda="Confirmá con tu contraseña para eliminar la cuenta."
                value={valores.contrasenia}
                onChange={cambiar}
                error={errores.contrasenia}
                required
              />
              <button
                type="submit"
                className="boton boton--peligro"
                disabled={enviando || !valores.contrasenia}
              >
                {enviando ? 'Eliminando…' : 'Eliminar mi cuenta definitivamente'}
              </button>
            </form>
          ) : (
            <button type="button" className="boton boton--secundario" onClick={revisar}>
              Volver a revisar
            </button>
          )}
        </>
      )}
    </section>
  )
}

const SECCIONES_PERFIL = [
  ['titulo-datos', 'Datos personales'],
  ['titulo-contrasenia', 'Contraseña'],
  ['titulo-correo', 'Correo electrónico'],
  ['titulo-copia', 'Copia de tus datos'],
  ['titulo-eliminar-cuenta', 'Eliminar mi cuenta'],
]

/** Tarjeta lateral con la identidad de la cuenta y el índice de secciones (022). */
function TarjetaDeCuenta() {
  const { usuario } = useSesion()
  const iniciales = `${usuario.nombre?.[0] ?? ''}${usuario.apellido?.[0] ?? ''}`.toUpperCase()
  return (
    <aside className="seccion tarjeta-cuenta" aria-label="Tu cuenta">
      <div className="visor tarjeta-cuenta__visor">
        <span className="tarjeta-cuenta__avatar" aria-hidden="true">
          {iniciales}
        </span>
      </div>
      <p className="tarjeta-cuenta__nombre">
        {usuario.nombre} {usuario.apellido}
      </p>
      <p className="tarjeta-cuenta__correo">{usuario.correo}</p>
      <div className="acciones-en-linea tarjeta-cuenta__etiquetas">
        <Etiqueta tipo="destacada">{usuario.perfil === 'abogado' ? 'Abogado' : 'Aseguradora'}</Etiqueta>
        {usuario.rol === 'administrador' && <Etiqueta>Administrador</Etiqueta>}
      </div>
      <nav aria-label="Secciones del perfil" className="indice-secciones">
        {SECCIONES_PERFIL.map(([id, texto]) => (
          <a key={id} href={`#${id}`}>
            {texto}
          </a>
        ))}
      </nav>
    </aside>
  )
}

/** Plan del espacio personal; solo los abogados tienen espacio personal (RN12). */
function PlanPersonal() {
  const { usuario } = useSesion()
  return usuario.perfil === 'abogado' ? <SeccionPlan /> : null
}

export default function PaginaPerfil() {
  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Mi perfil</h1>
          <p className="encabezado-pagina__bajada">Tus datos aparecen en los informes que generás.</p>
        </div>
      </div>
      <div className="dos-columnas dos-columnas--invertidas">
        <div className="dos-columnas__lateral">
          <TarjetaDeCuenta />
          <PlanPersonal />
        </div>
        <div className="dos-columnas__principal">
          <SeccionDatos />
          <SeccionContrasenia />
          <SeccionCorreo />
          <SeccionCopia />
          <SeccionEliminar />
        </div>
      </div>
    </>
  )
}
