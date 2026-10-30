/**
 * Pantalla de registro de una cuenta nueva, guiada por pasos.
 *
 * Desde la funcionalidad 032 hay tres caminos:
 *
 * - Abogado independiente (4 pasos): cómo vas a usarla, tus datos, colegio de
 *   abogados (opcional) y tu cuenta.
 * - Abogado con estudio jurídico (6 pasos): además del nombre del estudio en
 *   el primer paso, el plan antes de la cuenta y el pago al final.
 * - Aseguradora (6 pasos): la aseguradora del catálogo de la SSN, el plan, la
 *   cuenta y el pago; después la aprueba el Administrador.
 *
 * El paso de la cuenta pide el correo, la contraseña y la aceptación expresa
 * de los Términos de Uso y de la Política de Privacidad. Los pasos se ven con
 * su nombre en el panel de la izquierda y la tarjeta es más ancha.
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
import { listarPlanes } from '../api/pagos.js'
import AceptacionTerminos from '../componentes/AceptacionTerminos.jsx'
import Aviso from '../componentes/Aviso.jsx'
import BotonGoogle from '../componentes/BotonGoogle.jsx'
import CampoContrasenia from '../componentes/CampoContrasenia.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import IndicadorPasos from '../componentes/IndicadorPasos.jsx'
import PanelPago from '../componentes/PanelPago.jsx'
import PanelPasos from '../componentes/PanelPasos.jsx'
import PasoInstitucion from '../componentes/PasoInstitucion.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import ResultadoPago from '../componentes/ResultadoPago.jsx'
import SelectorCamino from '../componentes/SelectorCamino.jsx'
import SelectorPlan from '../componentes/SelectorPlan.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { caminoConPago, perfilDelCamino } from '../utilidades/registro.js'

const PASOS_INDEPENDIENTE = ['perfil', 'datos', 'institucion', 'cuenta']
const PASOS_CON_PAGO = ['perfil', 'datos', 'institucion', 'plan', 'cuenta', 'pago']
const PASOS_EMPLEADO = ['datos', 'cuenta']

/** Pasos según el camino elegido; mientras no hay camino, los del independiente. */
function pasosDelCamino(camino, esEmpleado) {
  if (esEmpleado) return PASOS_EMPLEADO
  return caminoConPago(camino) ? PASOS_CON_PAGO : PASOS_INDEPENDIENTE
}

const VALORES_INICIALES = {
  nombre: '',
  apellido: '',
  correo: '',
  contrasenia: '',
  camino: '',
  nombre_estudio: '',
  plan: 'basico',
  colegio: '',
  id_aseguradora: null,
  acepta_terminos: false,
}

/** Paso del formulario en el que se carga cada campo (CA7 de la 020). */
const PASO_DE_CADA_CAMPO = {
  perfil: 'perfil',
  camino: 'perfil',
  nombre_estudio: 'perfil',
  plan: 'plan',
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
function armarSolicitud(
  { camino, colegio, id_aseguradora: idAseguradora, nombre_estudio: nombreEstudio, plan, ...datos },
  token,
  esEmpleado,
) {
  const solicitud = { ...datos, perfil: esEmpleado ? 'aseguradora' : perfilDelCamino(camino) }
  if (token) solicitud.token_invitacion = token
  if (solicitud.perfil === 'abogado' && colegio.trim()) solicitud.colegio = colegio
  if (solicitud.perfil === 'aseguradora' && !token) solicitud.id_aseguradora = idAseguradora
  if (camino === 'estudio' && !token) solicitud.nombre_estudio = nombreEstudio.trim()
  if (caminoConPago(camino) && !token) solicitud.plan = plan
  return solicitud
}

/**
 * Valida en el navegador los datos obligatorios del paso, para no avanzar
 * con datos faltantes. Devuelve el mensaje de error de cada campo.
 */
function validarPaso(paso, valores) {
  const errores = {}
  if (paso === 'perfil' && !valores.camino) {
    errores.camino = 'Elegí cómo vas a usar la plataforma.'
  }
  if (paso === 'perfil' && valores.camino === 'estudio' && !valores.nombre_estudio.trim()) {
    errores.nombre_estudio = 'Escribí el nombre de tu estudio jurídico.'
  }
  if (paso === 'datos') {
    if (!valores.nombre.trim()) errores.nombre = 'Ingresá tu nombre.'
    if (!valores.apellido.trim()) errores.apellido = 'Ingresá tu apellido.'
  }
  if (paso === 'institucion' && valores.camino === 'aseguradora' && !valores.id_aseguradora) {
    errores.id_aseguradora = 'Elegí tu aseguradora del listado.'
  }
  return errores
}

/** Título de cada paso; el de la institución depende del perfil elegido. */
function tituloDelPaso(paso, valores) {
  if (paso === 'perfil') return '¿Cómo vas a usar la plataforma?'
  if (paso === 'datos') return 'Tus datos'
  if (paso === 'institucion') {
    return perfilDelCamino(valores.camino) === 'aseguradora' ? 'Tu aseguradora' : 'Tu colegio de abogados'
  }
  if (paso === 'plan') {
    return valores.camino === 'estudio'
      ? `Elegí el plan de ${valores.nombre_estudio.trim() || 'tu estudio'}`
      : 'Elegí el plan de tu aseguradora'
  }
  return 'Tu cuenta'
}

/** Paso del plan: Básico o Profesional, con sus límites (032, frame 10b). */
function PasoPlan({ valor, cambiar, error }) {
  const { datos, error: errorPlanes, cargando } = useDatos(listarPlanes)
  if (cargando) return <Cargando texto="Cargando los planes…" />
  if (errorPlanes) return <Aviso tipo="error">{errorPlanes.message}</Aviso>
  return (
    <>
      <p className="nota">
        El plan define cuántas personas suman al equipo y cuánto pueden analizar. Lo podés cambiar después
        desde la organización.
      </p>
      <SelectorPlan planes={datos.planes} valor={valor} onChange={cambiar} error={error} />
      <Aviso tipo="alerta">
        <strong>Precios a confirmar.</strong> Mientras se define el cobro con Cresium, el pago es una
        simulación: no se cobra nada.
      </Aviso>
    </>
  )
}

const CAMINOS_DESDE_LA_LANDING = new Set(['independiente', 'estudio', 'aseguradora'])
const PLANES_DESDE_LA_LANDING = new Set(['basico', 'profesional'])

function FormularioRegistro({ invitacion, token, caminoPedido, planPedido }) {
  const esEmpleado = invitacion?.organizacion.tipo === 'aseguradora'
  // La landing puede llegar con el camino y el plan ya elegidos (?tipo=estudio&plan=profesional).
  const caminoInicial = esEmpleado
    ? 'aseguradora'
    : !invitacion && CAMINOS_DESDE_LA_LANDING.has(caminoPedido)
      ? caminoPedido
      : ''
  const { valores, setValores, errores, error, enviando, cambiar, enviar, marcarErrores } =
    useFormulario({
      ...VALORES_INICIALES,
      correo: invitacion?.correo ?? '',
      camino: caminoInicial,
      plan: PLANES_DESDE_LA_LANDING.has(planPedido) ? planPedido : VALORES_INICIALES.plan,
    })
  const pasos = pasosDelCamino(valores.camino, esEmpleado)
  const [indice, setIndice] = useState(0)
  const [mensaje, setMensaje] = useState(null)
  const [tokenPago, setTokenPago] = useState(null)
  const [cobroAcreditado, setCobroAcreditado] = useState(null)
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
    const resultado = await enviar((datos) =>
      registrarCuenta(armarSolicitud(datos, token, esEmpleado)),
    )
    if (resultado.ok) {
      setMensaje(resultado.datos.mensaje)
      // El estudio y la aseguradora siguen con el pago del plan (032).
      if (resultado.datos.pago) {
        setTokenPago(resultado.datos.pago.token)
        setIndice(pasos.indexOf('pago'))
      }
      return
    }
    const indices = Object.keys(resultado.error.errores)
      .map((campo) => pasos.indexOf(PASO_DE_CADA_CAMPO[campo]))
      .filter((posicion) => posicion >= 0)
    if (indices.length && Math.min(...indices) < indice) setIndice(Math.min(...indices))
  }

  const avisoDeCorreo = (
    <>
      <Aviso tipo="info">{mensaje}</Aviso>
      <FormularioReenvio correoInicial={valores.correo} />
    </>
  )

  if (cobroAcreditado) {
    return (
      <div className="registro-ancho">
        <PanelPasos pasos={pasos} actual={pasos.length} />
        <ResultadoPago cobro={cobroAcreditado}>
          <p>Para entrar, primero confirmá tu correo con el enlace que te enviamos.</p>
          {avisoDeCorreo}
          <p className="enlaces-secundarios">
            <Link to="/iniciar-sesion">Ir a iniciar sesión</Link>
          </p>
        </ResultadoPago>
      </div>
    )
  }

  if (tokenPago) {
    return (
      <div className="registro-ancho">
        <PanelPasos pasos={pasos} actual={indice} />
        <IndicadorPasos actual={indice + 1} total={pasos.length} />
        <PanelPago token={tokenPago} alAcreditar={setCobroAcreditado} />
      </div>
    )
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
        {!invitacion && valores.camino === 'aseguradora' && (
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

  const esPasoDeCuenta = paso === 'cuenta'

  return (
    <div className="registro-ancho">
      {!esEmpleado && <PanelPasos pasos={pasos} actual={indice} />}
      <h1>Crear una cuenta</h1>
      {invitacion && (
        <Aviso tipo="info">
          Te sumás a {invitacion.organizacion.nombre} con la invitación de {invitacion.invitante}.
        </Aviso>
      )}
      {indice === 0 && <BotonGoogle invitacion={token} />}
      <IndicadorPasos actual={indice + 1} total={pasos.length} />
      <h2 id="titulo-paso" ref={refTitulo} tabIndex={-1} className="pasos__titulo">
        {tituloDelPaso(paso, valores)}
      </h2>
      {error && <Aviso tipo="error">{error.message}</Aviso>}

      <form onSubmit={esPasoDeCuenta ? crearCuenta : avanzar} className="formulario" noValidate>
        {paso === 'perfil' && (
          <SelectorCamino
            valores={valores}
            errores={errores}
            cambiar={cambiar}
            sinEstudio={Boolean(invitacion)}
          />
        )}

        {paso === 'plan' && <PasoPlan valor={valores.plan} cambiar={cambiar} error={errores.plan} />}

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
            valores={{ ...valores, perfil: perfilDelCamino(valores.camino) }}
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
            <CampoContrasenia
              etiqueta="Contraseña"
              nombre="contrasenia"
              autoComplete="new-password"
              value={valores.contrasenia}
              onChange={cambiar}
              error={errores.contrasenia}
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
          {esPasoDeCuenta ? (
            <button type="submit" className="boton" disabled={enviando}>
              {enviando
                ? 'Creando la cuenta…'
                : caminoConPago(valores.camino) && !token
                  ? 'Crear la cuenta e ir al pago'
                  : 'Crear cuenta'}
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
    </div>
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
  return (
    <FormularioRegistro
      invitacion={invitacion}
      token={token}
      caminoPedido={parametros.get('tipo')}
      planPedido={parametros.get('plan')}
    />
  )
}
