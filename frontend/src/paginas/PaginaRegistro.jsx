/**
 * Pantalla de registro de una cuenta nueva, guiada por pasos.
 *
 * Registro común (4 pasos):
 * 1. Perfil: "Abogado o abogada" o "Registrar mi aseguradora".
 * 2. Nombre y apellido.
 * 3. Colegio de abogados (opcional) o la aseguradora del catálogo de la SSN
 *    (obligatoria).
 * 4. Correo, contraseña y aceptación expresa de los Términos de Uso y de la
 *    Política de Privacidad.
 *
 * Registro con invitación (``?invitacion=<token>``): el correo viene fijado.
 * Si invita una aseguradora, el perfil también, y solo quedan los pasos 2 y
 * 4; al verificar el correo, la persona queda dentro de la aseguradora.
 *
 * Cada paso se valida antes de avanzar y los datos se conservan al volver.
 * El backend valida de forma definitiva al crear la cuenta: si rechaza un
 * dato de un paso anterior, se vuelve a ese paso con el error junto al campo.
 *
 * En el primer paso ofrece "Continuar con Google" (027), que también conserva
 * la invitación.
 *
 * Realiza: RF01, RF52; RN01, RN02, RN36; CA1 a CA5 de la funcionalidad 002, CA1 a
 * CA8 de la 020, CA9 de la 004 y CA1, CA2, CA5, CA10 de la 021; RNF10.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { registrarCuenta } from '../api/cuentas.js'
import { consultarInvitacion } from '../api/organizaciones.js'
import AceptacionTerminos from '../componentes/AceptacionTerminos.jsx'
import Aviso from '../componentes/Aviso.jsx'
import BotonGoogle from '../componentes/BotonGoogle.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import IndicadorPasos from '../componentes/IndicadorPasos.jsx'
import PasoInstitucion from '../componentes/PasoInstitucion.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import SelectorPerfil from '../componentes/SelectorPerfil.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'

const PASOS_COMUNES = ['perfil', 'datos', 'institucion', 'cuenta']
const PASOS_EMPLEADO = ['datos', 'cuenta']

const VALORES_INICIALES = {
  nombre: '',
  apellido: '',
  correo: '',
  contrasenia: '',
  perfil: '',
  colegio: '',
  id_aseguradora: null,
  acepta_terminos: false,
}

/** Paso del formulario en el que se carga cada campo (CA7 de la 020). */
const PASO_DE_CADA_CAMPO = {
  perfil: 'perfil',
  nombre: 'datos',
  apellido: 'datos',
  colegio: 'institucion',
  empresa: 'institucion',
  id_aseguradora: 'institucion',
  correo: 'cuenta',
  contrasenia: 'cuenta',
  acepta_terminos: 'cuenta',
}

/** Arma el cuerpo de la solicitud con solo los datos que corresponden. */
function armarSolicitud({ colegio, id_aseguradora: idAseguradora, ...datos }, token) {
  const solicitud = { ...datos }
  if (token) solicitud.token_invitacion = token
  if (datos.perfil === 'abogado' && colegio.trim()) solicitud.colegio = colegio
  if (datos.perfil === 'aseguradora' && !token) solicitud.id_aseguradora = idAseguradora
  return solicitud
}

/**
 * Valida en el navegador los datos obligatorios del paso, para no avanzar
 * con datos faltantes. Devuelve el mensaje de error de cada campo.
 */
function validarPaso(paso, valores) {
  const errores = {}
  if (paso === 'perfil' && !valores.perfil) {
    errores.perfil = 'Elegí cómo vas a usar la plataforma.'
  }
  if (paso === 'datos') {
    if (!valores.nombre.trim()) errores.nombre = 'Ingresá tu nombre.'
    if (!valores.apellido.trim()) errores.apellido = 'Ingresá tu apellido.'
  }
  if (paso === 'institucion' && valores.perfil === 'aseguradora' && !valores.id_aseguradora) {
    errores.id_aseguradora = 'Elegí tu aseguradora del listado.'
  }
  return errores
}

/** Título de cada paso; el de la institución depende del perfil elegido. */
function tituloDelPaso(paso, perfil) {
  if (paso === 'perfil') return '¿Cómo vas a usar la plataforma?'
  if (paso === 'datos') return 'Tus datos'
  if (paso === 'institucion') {
    return perfil === 'abogado' ? 'Tu colegio de abogados' : 'Tu aseguradora'
  }
  return 'Tu cuenta'
}

function FormularioRegistro({ invitacion, token }) {
  const esEmpleado = invitacion?.organizacion.tipo === 'aseguradora'
  const pasos = esEmpleado ? PASOS_EMPLEADO : PASOS_COMUNES
  const { valores, setValores, errores, error, enviando, cambiar, enviar, marcarErrores } =
    useFormulario({
      ...VALORES_INICIALES,
      correo: invitacion?.correo ?? '',
      perfil: esEmpleado ? 'aseguradora' : '',
    })
  const [indice, setIndice] = useState(0)
  const [mensaje, setMensaje] = useState(null)
  const refTitulo = useRef(null)
  const primeraVez = useRef(true)
  const paso = pasos[indice]

  // Al cambiar de paso, el foco pasa al título del paso nuevo para que el
  // lector de pantalla lo anuncie (CA8 de la 020). Al abrir la pantalla no se mueve.
  useEffect(() => {
    if (primeraVez.current) {
      primeraVez.current = false
      return
    }
    refTitulo.current?.focus()
  }, [indice])

  function avanzar(evento) {
    evento.preventDefault()
    const erroresDelPaso = validarPaso(paso, valores)
    marcarErrores(erroresDelPaso)
    if (Object.keys(erroresDelPaso).length === 0) setIndice(indice + 1)
  }

  function volver() {
    marcarErrores({})
    setIndice(indice - 1)
  }

  async function crearCuenta(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) => registrarCuenta(armarSolicitud(datos, token)))
    if (resultado.ok) {
      setMensaje(resultado.datos.mensaje)
      return
    }
    const indices = Object.keys(resultado.error.errores)
      .map((campo) => pasos.indexOf(PASO_DE_CADA_CAMPO[campo]))
      .filter((posicion) => posicion >= 0)
    if (indices.length && Math.min(...indices) < indice) setIndice(Math.min(...indices))
  }

  if (mensaje) {
    return (
      <>
        <h1>Revisá tu correo</h1>
        <Aviso tipo="exito">{mensaje}</Aviso>
        <p>
          El enlace vence en 24 horas. Si no lo encontrás, revisá la carpeta de correo no
          deseado o pedí que te lo enviemos de nuevo.
        </p>
        {esEmpleado && (
          <p>Cuando verifiques tu correo, vas a quedar dentro de {invitacion.organizacion.nombre}.</p>
        )}
        {!invitacion && valores.perfil === 'aseguradora' && (
          <p>
            Después de verificar tu correo, el Administrador de la plataforma va a revisar el
            registro de la aseguradora. Te avisamos por correo cuando esté aprobada.
          </p>
        )}
        <FormularioReenvio correoInicial={valores.correo} />
        <p className="enlaces-secundarios">
          <Link to="/iniciar-sesion">Ir a iniciar sesión</Link>
        </p>
      </>
    )
  }

  const esUltimoPaso = indice === pasos.length - 1

  return (
    <>
      <h1>Crear una cuenta</h1>
      {invitacion && (
        <Aviso tipo="info">
          Te sumás a {invitacion.organizacion.nombre} con la invitación de {invitacion.invitante}.
        </Aviso>
      )}
      {indice === 0 && <BotonGoogle invitacion={token} />}
      <IndicadorPasos actual={indice + 1} total={pasos.length} />
      <h2 id="titulo-paso" ref={refTitulo} tabIndex={-1} className="pasos__titulo">
        {tituloDelPaso(paso, valores.perfil)}
      </h2>
      {error && <Aviso tipo="error">{error.message}</Aviso>}

      <form onSubmit={esUltimoPaso ? crearCuenta : avanzar} className="formulario" noValidate>
        {paso === 'perfil' && (
          <SelectorPerfil valor={valores.perfil} onChange={cambiar} error={errores.perfil} />
        )}

        {paso === 'datos' && (
          <>
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
          </>
        )}

        {paso === 'institucion' && (
          <PasoInstitucion
            valores={valores}
            errores={errores}
            cambiar={cambiar}
            setValores={setValores}
          />
        )}

        {paso === 'cuenta' && (
          <>
            <CampoTexto
              etiqueta="Correo electrónico"
              nombre="correo"
              tipo="email"
              autoComplete="email"
              value={valores.correo}
              onChange={cambiar}
              error={errores.correo}
              readOnly={Boolean(invitacion)}
              ayuda={invitacion ? 'Es el correo al que llegó la invitación.' : undefined}
              required
            />
            <CampoTexto
              etiqueta="Contraseña"
              nombre="contrasenia"
              tipo="password"
              autoComplete="new-password"
              value={valores.contrasenia}
              onChange={cambiar}
              error={errores.contrasenia}
              idDescripcion="reglas-contrasenia"
              required
            />
            <ReglasContrasenia contrasenia={valores.contrasenia} id="reglas-contrasenia" />

            <AceptacionTerminos
              aceptado={valores.acepta_terminos}
              onChange={cambiar}
              error={errores.acepta_terminos}
            />
          </>
        )}

        <div className="pasos__acciones">
          {indice > 0 && (
            <button type="button" className="boton boton--secundario" onClick={volver}>
              Atrás
            </button>
          )}
          {esUltimoPaso ? (
            <button type="submit" className="boton" disabled={enviando}>
              {enviando ? 'Creando la cuenta…' : 'Crear cuenta'}
            </button>
          ) : (
            <button type="submit" className="boton">
              Siguiente
            </button>
          )}
        </div>
      </form>

      <p className="enlaces-secundarios">
        <span>
          ¿Ya tenés cuenta? <Link to="/iniciar-sesion">Iniciá sesión</Link>
        </span>
      </p>
    </>
  )
}

export default function PaginaRegistro() {
  const [parametros] = useSearchParams()
  const token = parametros.get('invitacion')
  const cargar = useCallback(
    () => (token ? consultarInvitacion(token) : Promise.resolve(null)),
    [token],
  )
  const { datos: invitacion, error, cargando } = useDatos(cargar)

  if (cargando) return <Cargando texto="Preparando el registro…" />
  if (error || (invitacion && !invitacion.vigente)) {
    return (
      <>
        <h1>Crear una cuenta</h1>
        <Aviso tipo="error">
          {error?.message ??
            'La invitación ya no está vigente. Pedile a la organización que te invite de nuevo.'}
        </Aviso>
        <p className="enlaces-secundarios">
          <Link to="/registro">Crear una cuenta sin invitación</Link>
        </p>
      </>
    )
  }
  return <FormularioRegistro invitacion={invitacion} token={token} />
}
