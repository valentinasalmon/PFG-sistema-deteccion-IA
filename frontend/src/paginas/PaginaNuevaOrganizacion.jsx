/**
 * Pantalla "Crear organización": nombre, tipo y datos de contacto opcionales.
 *
 * Al crearla, el usuario queda como Referente y pasa a la pantalla de la
 * organización, donde puede invitar a su equipo (CU08 paso 5).
 *
 * Realiza: RF10; CA1 de la funcionalidad 004.
 */
import { Link, useNavigate } from 'react-router'
import { crearOrganizacion } from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import OpcionTarjeta from '../componentes/OpcionTarjeta.jsx'
import { useFormulario } from '../hooks/useFormulario.js'

export default function PaginaNuevaOrganizacion() {
  const navegar = useNavigate()
  const { valores, errores, error, enviando, cambiar, enviar, marcarError } = useFormulario({
    nombre: '',
    tipo: '',
    correo_contacto: '',
    telefono: '',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    if (!valores.tipo) {
      marcarError('tipo', 'Elegí el tipo de organización.')
      return
    }
    const resultado = await enviar((datos) => crearOrganizacion(datos))
    if (resultado.ok) {
      navegar(`/organizaciones/${resultado.datos.id}`, {
        state: { mensaje: 'La organización fue creada. Ya podés invitar a tu equipo.' },
      })
    }
  }

  return (
    <>
      <h1>Crear organización</h1>
      <p className="subtitulo">Vas a ser su Referente: quien invita y administra a los miembros.</p>
      <section className="seccion">
        {error && <Aviso tipo="error">{error.message}</Aviso>}
        <form onSubmit={manejarEnvio} className="formulario" noValidate>
          <CampoTexto
            etiqueta="Nombre"
            nombre="nombre"
            autoComplete="organization"
            value={valores.nombre}
            onChange={cambiar}
            error={errores.nombre}
            required
          />
          <fieldset
            className="opciones-tarjeta"
            aria-describedby={errores.tipo ? 'error-tipo' : undefined}
          >
            <legend className="campo__etiqueta">Tipo de organización</legend>
            <OpcionTarjeta
              nombre="tipo"
              valor="estudio_juridico"
              seleccionada={valores.tipo === 'estudio_juridico'}
              onChange={cambiar}
              titulo="Estudio Jurídico"
            />
            <OpcionTarjeta
              nombre="tipo"
              valor="aseguradora"
              seleccionada={valores.tipo === 'aseguradora'}
              onChange={cambiar}
              titulo="Aseguradora"
            />
            {errores.tipo && (
              <p id="error-tipo" className="campo__error">
                {errores.tipo}
              </p>
            )}
          </fieldset>
          <div className="formulario__fila">
            <CampoTexto
              etiqueta="Correo de contacto"
              nombre="correo_contacto"
              tipo="email"
              autoComplete="email"
              opcional
              value={valores.correo_contacto}
              onChange={cambiar}
              error={errores.correo_contacto}
            />
            <CampoTexto
              etiqueta="Teléfono"
              nombre="telefono"
              tipo="tel"
              autoComplete="tel"
              opcional
              value={valores.telefono}
              onChange={cambiar}
              error={errores.telefono}
            />
          </div>
          <div className="pasos__acciones">
            <Link to="/organizaciones" className="boton boton--secundario">
              Cancelar
            </Link>
            <button type="submit" className="boton" disabled={enviando}>
              {enviando ? 'Creando…' : 'Crear organización'}
            </button>
          </div>
        </form>
      </section>
    </>
  )
}
