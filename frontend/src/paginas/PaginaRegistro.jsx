/**
 * Pantalla de registro de una cuenta nueva, guiada en cuatro pasos.
 *
 * 1. Perfil (Abogado o Aseguradora), que no podrá cambiarse después.
 * 2. Nombre y apellido.
 * 3. Colegio de abogados o empresa, según el perfil, como dato opcional.
 * 4. Correo, contraseña y aceptación expresa de los Términos de Uso y de la
 *    Política de Privacidad.
 *
 * Cada paso se valida antes de avanzar y los datos se conservan al volver.
 * El backend valida de forma definitiva al crear la cuenta: si rechaza un
 * dato de un paso anterior, se vuelve a ese paso con el error junto al campo.
 * Al registrarse, la cuenta queda pendiente hasta verificar el correo.
 *
 * Realiza: RF01; RN01, RN02; CA1 a CA5 de la funcionalidad 002, CA1 a CA8
 * de la funcionalidad 020 y CA9 de la 004 (correo precargado); RNF10.
 */
import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { registrarCuenta } from '../api/cuentas.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import IndicadorPasos from '../componentes/IndicadorPasos.jsx'
import OpcionTarjeta from '../componentes/OpcionTarjeta.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import { useFormulario } from '../hooks/useFormulario.js'

const TOTAL_PASOS = 4

const VALORES_INICIALES = {
  nombre: '',
  apellido: '',
  correo: '',
  contrasenia: '',
  perfil: '',
  colegio: '',
  empresa: '',
  acepta_terminos: false,
}

/** Paso del formulario en el que se carga cada campo (CA7). */
const PASO_DE_CADA_CAMPO = {
  perfil: 1,
  nombre: 2,
  apellido: 2,
  colegio: 3,
  empresa: 3,
  correo: 4,
  contrasenia: 4,
  acepta_terminos: 4,
}

/** Arma el cuerpo de la solicitud enviando solo el dato que corresponde al perfil. */
function armarSolicitud({ colegio, empresa, ...datos }) {
  const solicitud = { ...datos }
  if (datos.perfil === 'abogado' && colegio.trim()) solicitud.colegio = colegio
  if (datos.perfil === 'aseguradora' && empresa.trim()) solicitud.empresa = empresa
  return solicitud
}

/**
 * Valida en el navegador los datos obligatorios del paso, para no avanzar
 * con datos faltantes (CA2, CA3). Devuelve el mensaje de error de cada campo.
 */
function validarPaso(paso, valores) {
  const errores = {}
  if (paso === 1 && !valores.perfil) {
    errores.perfil = 'Elegí cómo vas a usar la plataforma.'
  }
  if (paso === 2) {
    if (!valores.nombre.trim()) errores.nombre = 'Ingresá tu nombre.'
    if (!valores.apellido.trim()) errores.apellido = 'Ingresá tu apellido.'
  }
  return errores
}

/** Devuelve el primer paso que tiene un campo con error, o null si no hay ninguno. */
function primerPasoConError(errores) {
  const pasos = Object.keys(errores)
    .map((campo) => PASO_DE_CADA_CAMPO[campo])
    .filter(Boolean)
  return pasos.length ? Math.min(...pasos) : null
}

/** Título de cada paso; el del paso 3 depende del perfil elegido. */
function tituloDelPaso(paso, perfil) {
  if (paso === 1) return '¿Cómo vas a usar la plataforma?'
  if (paso === 2) return 'Tus datos'
  if (paso === 3) return perfil === 'abogado' ? 'Tu colegio de abogados' : 'Tu empresa'
  return 'Tu cuenta'
}

export default function PaginaRegistro() {
  // El enlace de una invitación precarga el correo invitado (CU11 3a).
  const [parametros] = useSearchParams()
  const { valores, errores, error, enviando, cambiar, enviar, marcarErrores } = useFormulario({
    ...VALORES_INICIALES,
    correo: parametros.get('correo') ?? '',
  })
  const [paso, setPaso] = useState(1)
  const [mensaje, setMensaje] = useState(null)
  const refTitulo = useRef(null)
  const primeraVez = useRef(true)

  // Al cambiar de paso, el foco pasa al título del paso nuevo para que el
  // lector de pantalla lo anuncie (CA8). Al abrir la pantalla no se mueve.
  useEffect(() => {
    if (primeraVez.current) {
      primeraVez.current = false
      return
    }
    refTitulo.current?.focus()
  }, [paso])

  function avanzar(evento) {
    evento.preventDefault()
    const erroresDelPaso = validarPaso(paso, valores)
    marcarErrores(erroresDelPaso)
    if (Object.keys(erroresDelPaso).length === 0) setPaso(paso + 1)
  }

  function volver() {
    marcarErrores({})
    setPaso(paso - 1)
  }

  async function crearCuenta(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) => registrarCuenta(armarSolicitud(datos)))
    if (resultado.ok) {
      setMensaje(resultado.datos.mensaje)
      return
    }
    const pasoConError = primerPasoConError(resultado.error.errores)
    if (pasoConError && pasoConError < paso) setPaso(pasoConError)
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
        <FormularioReenvio correoInicial={valores.correo} />
        <p className="enlaces-secundarios">
          <Link to="/iniciar-sesion">Ir a iniciar sesión</Link>
        </p>
      </>
    )
  }

  const titulo = tituloDelPaso(paso, valores.perfil)
  const esUltimoPaso = paso === TOTAL_PASOS

  return (
    <>
      <h1>Crear una cuenta</h1>
      <IndicadorPasos actual={paso} total={TOTAL_PASOS} />
      <h2 id="titulo-paso" ref={refTitulo} tabIndex={-1} className="pasos__titulo">
        {titulo}
      </h2>
      {error && <Aviso tipo="error">{error.message}</Aviso>}

      <form onSubmit={esUltimoPaso ? crearCuenta : avanzar} className="formulario" noValidate>
        {paso === 1 && (
          <fieldset
            className="opciones-tarjeta"
            aria-labelledby="titulo-paso"
            aria-describedby={errores.perfil ? 'ayuda-perfil error-perfil' : 'ayuda-perfil'}
          >
            <OpcionTarjeta
              nombre="perfil"
              valor="abogado"
              seleccionada={valores.perfil === 'abogado'}
              onChange={cambiar}
              titulo="Abogado o abogada"
              descripcion="Para analizar imágenes que vas a presentar o recibir en un caso."
            />
            <OpcionTarjeta
              nombre="perfil"
              valor="aseguradora"
              seleccionada={valores.perfil === 'aseguradora'}
              onChange={cambiar}
              titulo="Aseguradora"
              descripcion="Para analizar imágenes de siniestros y reclamos."
            />
            <p id="ayuda-perfil" className="campo__ayuda">
              El perfil no puede cambiarse después del registro.
            </p>
            {errores.perfil && (
              <p id="error-perfil" className="campo__error">
                {errores.perfil}
              </p>
            )}
          </fieldset>
        )}

        {paso === 2 && (
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

        {paso === 3 && valores.perfil === 'abogado' && (
          <CampoTexto
            etiqueta="Colegio de abogados"
            nombre="colegio"
            opcional
            ayuda="Podés dejarlo vacío y completarlo después desde tu perfil."
            value={valores.colegio}
            onChange={cambiar}
            error={errores.colegio}
          />
        )}
        {paso === 3 && valores.perfil === 'aseguradora' && (
          <CampoTexto
            etiqueta="Empresa"
            nombre="empresa"
            autoComplete="organization"
            opcional
            ayuda="Podés dejarlo vacío y completarlo después desde tu perfil."
            value={valores.empresa}
            onChange={cambiar}
            error={errores.empresa}
          />
        )}

        {paso === 4 && (
          <>
            <CampoTexto
              etiqueta="Correo electrónico"
              nombre="correo"
              tipo="email"
              autoComplete="email"
              value={valores.correo}
              onChange={cambiar}
              error={errores.correo}
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

            <div className="campo">
              <label className="opcion">
                <input
                  type="checkbox"
                  name="acepta_terminos"
                  checked={valores.acepta_terminos}
                  onChange={cambiar}
                  aria-invalid={errores.acepta_terminos ? 'true' : undefined}
                  aria-describedby={errores.acepta_terminos ? 'error-terminos' : undefined}
                />
                <span>
                  Leí y acepto los{' '}
                  <Link to="/terminos" target="_blank" rel="noopener">
                    Términos de Uso
                  </Link>{' '}
                  y la{' '}
                  <Link to="/privacidad" target="_blank" rel="noopener">
                    Política de Privacidad
                  </Link>
                  .
                </span>
              </label>
              {errores.acepta_terminos && (
                <p id="error-terminos" className="campo__error">
                  {errores.acepta_terminos}
                </p>
              )}
            </div>
          </>
        )}

        <div className="pasos__acciones">
          {paso > 1 && (
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
