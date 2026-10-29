/**
 * Completar el registro después de elegir "Continuar con Google" (027).
 *
 * Google ya verificó el correo y da el nombre y el apellido, pero no el
 * rubro. Por eso, la primera vez, la persona tiene que elegir el perfil
 * (Abogado o Aseguradora), completar la institución y aceptar los Términos
 * antes de entrar. Es el mismo recorrido por pasos que el registro común,
 * sin el paso de correo y contraseña.
 *
 * Si llegó desde la invitación de una aseguradora, el perfil ya está
 * fijado y solo quedan sus datos y los Términos.
 *
 * Desde la funcionalidad 032 ofrece los mismos tres caminos que el registro
 * común: el estudio jurídico y la aseguradora eligen el plan y, al crear la
 * cuenta, pasan a la página de pago.
 *
 * Realiza: RF52 (CA1); RN01, RN02, RN36.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { completarRegistroGoogle, obtenerRegistroGoogle } from '../api/google.js'
import { consultarInvitacion } from '../api/organizaciones.js'
import { listarPlanes } from '../api/pagos.js'
import AceptacionTerminos from '../componentes/AceptacionTerminos.jsx'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import IndicadorPasos from '../componentes/IndicadorPasos.jsx'
import PasoInstitucion from '../componentes/PasoInstitucion.jsx'
import SelectorCamino from '../componentes/SelectorCamino.jsx'
import SelectorPlan from '../componentes/SelectorPlan.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'
import { caminoConPago, perfilDelCamino } from '../utilidades/registro.js'

const PASOS_INDEPENDIENTE = ['perfil', 'datos', 'institucion', 'terminos']
const PASOS_CON_PAGO = ['perfil', 'datos', 'institucion', 'plan', 'terminos']
const PASOS_EMPLEADO = ['datos', 'terminos']

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
  acepta_terminos: 'terminos',
}

const TITULOS = {
  perfil: '¿Cómo vas a usar la plataforma?',
  datos: 'Tus datos',
  plan: 'Elegí el plan',
  terminos: 'Últimos detalles',
}

function validarPaso(paso, valores) {
  const errores = {}
  if (paso === 'perfil' && !valores.camino) errores.camino = 'Elegí cómo vas a usar la plataforma.'
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
  if (paso === 'terminos' && !valores.acepta_terminos) {
    errores.acepta_terminos = 'Tenés que aceptar los Términos de Uso y la Política de Privacidad.'
  }
  return errores
}

/** Cuerpo de la solicitud, con solo los datos que corresponden al perfil. */
function armarSolicitud(
  { camino, colegio, id_aseguradora: idAseguradora, nombre_estudio: nombreEstudio, plan, ...datos },
  invitacion,
) {
  const solicitud = { ...datos, perfil: perfilDelCamino(camino) }
  if (invitacion) solicitud.token_invitacion = invitacion
  if (solicitud.perfil === 'abogado' && colegio.trim()) solicitud.colegio = colegio
  if (solicitud.perfil === 'aseguradora' && !invitacion) solicitud.id_aseguradora = idAseguradora
  if (camino === 'estudio' && !invitacion) solicitud.nombre_estudio = nombreEstudio.trim()
  if (caminoConPago(camino) && !invitacion) solicitud.plan = plan
  return solicitud
}

function PasoPlan({ valor, cambiar, error }) {
  const { datos, error: errorPlanes, cargando } = useDatos(listarPlanes)
  if (cargando) return <Cargando texto="Cargando los planes…" />
  if (errorPlanes) return <Aviso tipo="error">{errorPlanes.message}</Aviso>
  return <SelectorPlan planes={datos.planes} valor={valor} onChange={cambiar} error={error} />
}

function FormularioGoogle({ pendiente, invitacion }) {
  const { recargarUsuario } = useSesion()
  const navegar = useNavigate()
  const esEmpleado = invitacion?.organizacion.tipo === 'aseguradora'
  const { valores, setValores, errores, error, enviando, cambiar, enviar, marcarErrores } =
    useFormulario({
      nombre: pendiente.nombre ?? '',
      apellido: pendiente.apellido ?? '',
      camino: esEmpleado ? 'aseguradora' : '',
      nombre_estudio: '',
      plan: 'basico',
      colegio: '',
      id_aseguradora: null,
      acepta_terminos: false,
    })
  const pasos = esEmpleado
    ? PASOS_EMPLEADO
    : caminoConPago(valores.camino)
      ? PASOS_CON_PAGO
      : PASOS_INDEPENDIENTE
  const [indice, setIndice] = useState(0)
  const refTitulo = useRef(null)
  const primeraVez = useRef(true)
  const paso = pasos[indice]
  const esUltimoPaso = indice === pasos.length - 1

  useEffect(() => {
    if (primeraVez.current) {
      primeraVez.current = false
      return
    }
    refTitulo.current?.focus()
  }, [indice])

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const erroresDelPaso = validarPaso(paso, valores)
    marcarErrores(erroresDelPaso)
    if (Object.keys(erroresDelPaso).length > 0) return
    if (!esUltimoPaso) {
      setIndice(indice + 1)
      return
    }
    const resultado = await enviar((datos) =>
      completarRegistroGoogle(armarSolicitud(datos, pendiente.invitacion)),
    )
    if (resultado.ok) {
      // El estudio o la aseguradora pagan su plan antes de seguir (032).
      if (resultado.datos.pago) navegar(`/pago/${resultado.datos.pago.token}`)
      // Con la sesión iniciada, la guarda de las pantallas de acceso lleva al inicio.
      await recargarUsuario()
      return
    }
    const indices = Object.keys(resultado.error.errores)
      .map((campo) => pasos.indexOf(PASO_DE_CADA_CAMPO[campo]))
      .filter((posicion) => posicion >= 0)
    if (indices.length && Math.min(...indices) < indice) setIndice(Math.min(...indices))
  }

  const titulo =
    paso === 'institucion'
      ? perfilDelCamino(valores.camino) === 'aseguradora'
        ? 'Tu aseguradora'
        : 'Tu colegio de abogados'
      : TITULOS[paso]

  return (
    <>
      <h1>Completá tu registro</h1>
      <Aviso tipo="info">
        <span>
          Ingresaste con Google como <strong>{pendiente.correo}</strong>. Antes de empezar, contanos
          cómo vas a usar la plataforma. Lo pedimos una sola vez.
        </span>
      </Aviso>
      {esEmpleado && (
        <Aviso tipo="info">
          Te sumás a {invitacion.organizacion.nombre} con la invitación de {invitacion.invitante}.
        </Aviso>
      )}
      <IndicadorPasos actual={indice + 1} total={pasos.length} />
      <h2 id="titulo-paso" ref={refTitulo} tabIndex={-1} className="pasos__titulo">
        {titulo}
      </h2>
      {error && <Aviso tipo="error">{error.message}</Aviso>}

      <form onSubmit={manejarEnvio} className="formulario" noValidate>
        {paso === 'perfil' && (
          <SelectorCamino
            valores={valores}
            errores={errores}
            cambiar={cambiar}
            sinEstudio={Boolean(pendiente.invitacion)}
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
        {paso === 'terminos' && (
          <AceptacionTerminos
            aceptado={valores.acepta_terminos}
            onChange={cambiar}
            error={errores.acepta_terminos}
          />
        )}

        <div className="pasos__acciones">
          {indice > 0 && (
            <button
              type="button"
              className="boton boton--secundario"
              onClick={() => {
                marcarErrores({})
                setIndice(indice - 1)
              }}
            >
              Atrás
            </button>
          )}
          <button type="submit" className="boton" disabled={enviando}>
            {esUltimoPaso ? (enviando ? 'Creando la cuenta…' : 'Crear cuenta') : 'Siguiente'}
          </button>
        </div>
      </form>
    </>
  )
}

export default function PaginaRegistroGoogle() {
  const cargar = useCallback(async () => {
    const pendiente = await obtenerRegistroGoogle()
    const invitacion = pendiente.invitacion
      ? await consultarInvitacion(pendiente.invitacion).catch(() => null)
      : null
    return { pendiente, invitacion }
  }, [])
  const { datos, error, cargando } = useDatos(cargar)

  if (cargando) return <Cargando texto="Preparando el registro…" />
  if (error) {
    return (
      <>
        <h1>Completá tu registro</h1>
        <Aviso tipo="error">{error.message}</Aviso>
        <p className="enlaces-secundarios">
          <Link to="/iniciar-sesion">Volver a iniciar sesión</Link>
        </p>
      </>
    )
  }
  return <FormularioGoogle pendiente={datos.pendiente} invitacion={datos.invitacion} />
}
