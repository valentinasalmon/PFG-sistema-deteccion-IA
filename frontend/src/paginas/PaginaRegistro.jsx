/**
 * Pantalla de registro de una cuenta nueva.
 *
 * Pide los datos personales, el perfil (Abogado o Aseguradora, que no podrá
 * cambiarse después) y la aceptación expresa de los Términos de Uso y de la
 * Política de Privacidad. Al registrarse, la cuenta queda pendiente hasta
 * verificar el correo.
 *
 * Realiza: RF01; RN01, RN02 y CA1 a CA5 de la funcionalidad 002.
 */
import { useState } from 'react'
import { Link } from 'react-router'
import { registrarCuenta } from '../api/cuentas.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import FormularioReenvio from '../componentes/FormularioReenvio.jsx'
import ReglasContrasenia from '../componentes/ReglasContrasenia.jsx'
import { useFormulario } from '../hooks/useFormulario.js'

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

/** Arma el cuerpo de la solicitud enviando solo el dato que corresponde al perfil. */
function armarSolicitud({ colegio, empresa, ...datos }) {
  const solicitud = { ...datos }
  if (datos.perfil === 'abogado' && colegio.trim()) solicitud.colegio = colegio
  if (datos.perfil === 'aseguradora' && empresa.trim()) solicitud.empresa = empresa
  return solicitud
}

export default function PaginaRegistro() {
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario(VALORES_INICIALES)
  const [mensaje, setMensaje] = useState(null)

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) => registrarCuenta(armarSolicitud(datos)))
    if (resultado.ok) setMensaje(resultado.datos.mensaje)
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

  return (
    <>
      <h1>Crear una cuenta</h1>
      {error && <Aviso tipo="error">{error.message}</Aviso>}

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

        <fieldset
          className="campo campo--grupo"
          aria-describedby={errores.perfil ? 'error-perfil' : 'ayuda-perfil'}
        >
          <legend className="campo__etiqueta">Perfil</legend>
          <p id="ayuda-perfil" className="campo__ayuda">
            El perfil no puede cambiarse después del registro.
          </p>
          <label className="opcion">
            <input
              type="radio"
              name="perfil"
              value="abogado"
              checked={valores.perfil === 'abogado'}
              onChange={cambiar}
            />
            Abogado o abogada
          </label>
          <label className="opcion">
            <input
              type="radio"
              name="perfil"
              value="aseguradora"
              checked={valores.perfil === 'aseguradora'}
              onChange={cambiar}
            />
            Aseguradora
          </label>
          {errores.perfil && (
            <p id="error-perfil" className="campo__error">
              {errores.perfil}
            </p>
          )}
        </fieldset>

        {valores.perfil === 'abogado' && (
          <CampoTexto
            etiqueta="Colegio de abogados"
            nombre="colegio"
            opcional
            value={valores.colegio}
            onChange={cambiar}
            error={errores.colegio}
          />
        )}
        {valores.perfil === 'aseguradora' && (
          <CampoTexto
            etiqueta="Empresa"
            nombre="empresa"
            autoComplete="organization"
            opcional
            value={valores.empresa}
            onChange={cambiar}
            error={errores.empresa}
          />
        )}

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

        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Creando la cuenta…' : 'Crear cuenta'}
        </button>
      </form>

      <p className="enlaces-secundarios">
        <span>
          ¿Ya tenés cuenta? <Link to="/iniciar-sesion">Iniciá sesión</Link>
        </span>
      </p>
    </>
  )
}
