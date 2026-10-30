/**
 * Pantalla "Crear estudio jurídico": nombre y datos de contacto opcionales.
 * Solo los abogados crean organizaciones, y solo del tipo Estudio Jurídico
 * (RN40, funcionalidad 021).
 *
 * Desde la funcionalidad 032 (frame 10e) son tres pasos: los datos del
 * estudio, el plan (Básico o Profesional) y el pago. Al crearlo, el usuario
 * queda como Referente y pasa a la página de pago; el estudio queda activo
 * cuando el pago se acredita.
 *
 * Realiza: RF10; CA1 de la funcionalidad 004; CA9 de la 032.
 */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { crearOrganizacion } from '../api/organizaciones.js'
import { listarPlanes } from '../api/pagos.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import SelectorPlan from '../componentes/SelectorPlan.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'

const PASOS = ['Datos del estudio', 'Plan', 'Pago']

function Pasitos({ actual }) {
  return (
    <ol className="pasitos" aria-label="Pasos para crear el estudio">
      {PASOS.map((paso, indice) => {
        const situacion = indice < actual ? 'hecho' : indice === actual ? 'actual' : 'pendiente'
        return (
          <li
            key={paso}
            className={`pasito pasito--${situacion}`}
            aria-current={situacion === 'actual' ? 'step' : undefined}
          >
            <span className="pasito__numero" aria-hidden="true">
              {situacion === 'hecho' ? '✓' : indice + 1}
            </span>
            {paso}
          </li>
        )
      })}
    </ol>
  )
}

function PasoPlan({ valor, cambiar, error }) {
  const { datos, error: errorPlanes, cargando } = useDatos(listarPlanes)
  if (cargando) return <Cargando texto="Cargando los planes…" />
  if (errorPlanes) return <Aviso tipo="error">{errorPlanes.message}</Aviso>
  return <SelectorPlan planes={datos.planes} valor={valor} onChange={cambiar} error={error} />
}

export default function PaginaNuevaOrganizacion() {
  const navegar = useNavigate()
  const { recargarUsuario } = useSesion()
  const [paso, setPaso] = useState(0)
  const { valores, errores, error, enviando, cambiar, enviar, marcarErrores } = useFormulario({
    nombre: '',
    tipo: 'estudio_juridico',
    correo_contacto: '',
    telefono: '',
    plan: 'basico',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    if (paso === 0) {
      if (!valores.nombre.trim()) {
        marcarErrores({ nombre: 'Escribí el nombre del estudio.' })
        return
      }
      marcarErrores({})
      setPaso(1)
      return
    }
    const resultado = await enviar((datos) => crearOrganizacion(datos))
    if (resultado.ok) {
      // El menú pasa a mostrar «Organizaciones» (028).
      await recargarUsuario().catch(() => {})
      navegar(`/pago/${resultado.datos.pago.token}`)
    } else if (resultado.error.errores.nombre) {
      setPaso(0)
    }
  }

  return (
    <>
      <h1>Crear tu estudio jurídico</h1>
      <p className="subtitulo">
        Vas a ser su Referente: quien invita y administra a los miembros. Tus casos personales siguen siendo
        tuyos. Las aseguradoras se registran desde el registro de la plataforma.
      </p>
      <Pasitos actual={paso} />
      <section className="seccion">
        {error && <Aviso tipo="error">{error.message}</Aviso>}
        <form onSubmit={manejarEnvio} className="formulario" noValidate>
          {paso === 0 ? (
            <>
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
            </>
          ) : (
            <>
              <h2 id="titulo-paso" className="pasos__titulo">
                Elegí el plan de {valores.nombre.trim()}
              </h2>
              <PasoPlan valor={valores.plan} cambiar={cambiar} error={errores.plan} />
              <Aviso tipo="info">
                Después del pago el estudio queda activo y en el menú aparece «Organizaciones».
              </Aviso>
            </>
          )}
          <div className="pasos__acciones">
            {paso === 0 ? (
              <Link to="/perfil" className="boton boton--secundario">
                Cancelar
              </Link>
            ) : (
              <button type="button" className="boton boton--secundario" onClick={() => setPaso(0)}>
                Atrás
              </button>
            )}
            <button type="submit" className="boton" disabled={enviando}>
              {paso === 0 ? 'Siguiente' : enviando ? 'Creando…' : 'Ir al pago'}
            </button>
          </div>
        </form>
      </section>
    </>
  )
}
