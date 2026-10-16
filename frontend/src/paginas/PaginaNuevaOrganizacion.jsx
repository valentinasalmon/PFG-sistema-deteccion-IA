/**
 * Pantalla "Crear estudio jurídico": nombre y datos de contacto opcionales.
 * Solo los abogados crean organizaciones, y solo del tipo Estudio Jurídico
 * (RN40, funcionalidad 021).
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
import { useFormulario } from '../hooks/useFormulario.js'

export default function PaginaNuevaOrganizacion() {
  const navegar = useNavigate()
  const { valores, errores, error, enviando, cambiar, enviar } = useFormulario({
    nombre: '',
    tipo: 'estudio_juridico',
    correo_contacto: '',
    telefono: '',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const resultado = await enviar((datos) => crearOrganizacion(datos))
    if (resultado.ok) {
      navegar(`/organizaciones/${resultado.datos.id}`, {
        state: { mensaje: 'La organización fue creada. Ya podés invitar a tu equipo.' },
      })
    }
  }

  return (
    <>
      <h1>Crear estudio jurídico</h1>
      <p className="subtitulo">
        Vas a ser su Referente: quien invita y administra a los miembros. Las aseguradoras se
        registran desde el registro de la plataforma.
      </p>
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
              {enviando ? 'Creando…' : 'Crear estudio jurídico'}
            </button>
          </div>
        </form>
      </section>
    </>
  )
}
