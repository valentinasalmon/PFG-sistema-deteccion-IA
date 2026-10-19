/**
 * Pantalla "Nuevo caso": espacio de trabajo, tipo, fecha del hecho, lugar y,
 * opcionales, expediente y descripción.
 *
 * Los abogados pueden elegir su espacio personal o un estudio; quienes
 * trabajan en una aseguradora solo ven sus aseguradoras activas (RN12, 021).
 *
 * Realiza: RF23; CA1 a CA3 de la funcionalidad 005 (CU18).
 */
import { useCallback } from 'react'
import { Link, useNavigate } from 'react-router'
import { crearCaso } from '../api/casos.js'
import { listarOrganizaciones } from '../api/organizaciones.js'
import Aviso from '../componentes/Aviso.jsx'
import CampoAreaTexto from '../componentes/CampoAreaTexto.jsx'
import CampoSeleccion from '../componentes/CampoSeleccion.jsx'
import CampoTexto from '../componentes/CampoTexto.jsx'
import Cargando from '../componentes/Cargando.jsx'
import OpcionTarjeta from '../componentes/OpcionTarjeta.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useFormulario } from '../hooks/useFormulario.js'
import { useSesion } from '../hooks/useSesion.js'
import { hoyIso } from '../utilidades/fechas.js'

function Formulario({ espacios }) {
  const navegar = useNavigate()
  const { valores, errores, error, enviando, cambiar, enviar, marcarErrores } = useFormulario({
    espacio: espacios[0].valor,
    tipo: '',
    fecha_hecho: '',
    lugar: '',
    expediente: '',
    descripcion: '',
  })

  async function manejarEnvio(evento) {
    evento.preventDefault()
    const faltantes = {}
    if (!valores.tipo) faltantes.tipo = 'Elegí el tipo de caso.'
    if (!valores.fecha_hecho) faltantes.fecha_hecho = 'Indicá la fecha del hecho.'
    if (!valores.lugar.trim()) faltantes.lugar = 'Indicá el lugar del hecho.'
    if (Object.keys(faltantes).length) {
      marcarErrores(faltantes)
      return
    }
    const resultado = await enviar((datos) => crearCaso(datos))
    if (resultado.ok) {
      navegar(`/casos/${resultado.datos.id}`, {
        state: { mensaje: `Se creó el caso ${resultado.datos.numero}.` },
      })
    }
  }

  return (
    <form onSubmit={manejarEnvio} className="formulario" noValidate>
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {espacios.length > 1 ? (
        <CampoSeleccion
          etiqueta="Espacio de trabajo"
          nombre="espacio"
          value={valores.espacio}
          onChange={cambiar}
          opciones={espacios}
          error={errores.espacio}
          ayuda="No se puede cambiar después. Solo los casos de una organización se comparten."
        />
      ) : (
        <p className="nota">
          Espacio de trabajo: <strong>{espacios[0].texto}</strong>
        </p>
      )}
      <fieldset className="opciones-tarjeta" aria-describedby={errores.tipo ? 'error-tipo' : undefined}>
        <legend className="campo__etiqueta">Tipo de caso</legend>
        <OpcionTarjeta
          nombre="tipo"
          valor="automovilistico"
          seleccionada={valores.tipo === 'automovilistico'}
          onChange={cambiar}
          titulo="Automovilístico"
          descripcion="Siniestros de tránsito y reclamos a aseguradoras."
        />
        <OpcionTarjeta
          nombre="tipo"
          valor="laboral"
          seleccionada={valores.tipo === 'laboral'}
          onChange={cambiar}
          titulo="Laboral"
          descripcion="Accidentes y reclamos del ámbito laboral."
        />
        {errores.tipo && (
          <p id="error-tipo" className="campo__error">
            {errores.tipo}
          </p>
        )}
      </fieldset>
      <div className="formulario__fila">
        <CampoTexto
          etiqueta="Fecha del hecho"
          nombre="fecha_hecho"
          tipo="date"
          max={hoyIso()}
          value={valores.fecha_hecho}
          onChange={cambiar}
          error={errores.fecha_hecho}
          required
        />
        <CampoTexto
          etiqueta="Expediente"
          nombre="expediente"
          opcional
          value={valores.expediente}
          onChange={cambiar}
          error={errores.expediente}
        />
      </div>
      <CampoTexto
        etiqueta="Lugar del hecho"
        nombre="lugar"
        value={valores.lugar}
        onChange={cambiar}
        error={errores.lugar}
        required
      />
      <CampoAreaTexto
        etiqueta="Descripción"
        nombre="descripcion"
        opcional
        value={valores.descripcion}
        onChange={cambiar}
        error={errores.descripcion}
      />
      <div className="pasos__acciones">
        <Link to="/casos" className="boton boton--secundario">
          Cancelar
        </Link>
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? 'Creando…' : 'Crear caso'}
        </button>
      </div>
    </form>
  )
}

export default function PaginaNuevoCaso() {
  const { usuario } = useSesion()
  const cargar = useCallback(() => listarOrganizaciones(), [])
  const { datos: organizaciones, error, cargando } = useDatos(cargar)

  if (cargando) return <Cargando texto="Preparando el formulario…" />
  const espacios = [
    ...(usuario.perfil === 'abogado' ? [{ valor: 'personal', texto: 'Personal' }] : []),
    ...(organizaciones ?? [])
      .filter((organizacion) => organizacion.estado !== 'pendiente')
      .map((organizacion) => ({ valor: String(organizacion.id), texto: organizacion.nombre })),
  ]

  return (
    <>
      <h1>Nuevo caso</h1>
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {espacios.length === 0 ? (
        <Aviso tipo="info">
          Para crear casos tenés que pertenecer a una aseguradora aprobada por el Administrador.
        </Aviso>
      ) : (
        <section className="seccion">
          <Formulario espacios={espacios} />
        </section>
      )}
    </>
  )
}
