/**
 * Pantalla "Mi perfil": datos personales, cambio de contraseña y cambio de
 * correo.
 *
 * El perfil (Abogado o Aseguradora) se muestra pero no puede modificarse
 * (RN01). El cambio de correo pide la contraseña y queda pendiente hasta
 * confirmarlo desde la dirección nueva.
 *
 * Realiza: RF06, RF07; RN01, RN02 y CA16 a CA19 de la funcionalidad 002.
 */
import { useState } from 'react'
import { actualizarPerfil, cambiarContrasenia, solicitarCambioCorreo } from '../api/perfil.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'

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
      {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
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
      {mensaje && <Aviso tipo="exito">{mensaje}</Aviso>}
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

export default function PaginaPerfil() {
  return (
    <>
      <h1>Mi perfil</h1>
      <SeccionDatos />
      <SeccionContrasenia />
      <SeccionCorreo />
    </>
  )
}
