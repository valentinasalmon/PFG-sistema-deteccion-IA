/**
 * Pantalla "Nuevo caso": espacio de trabajo, tipo, fecha del hecho, lugar y,
 * opcionales, expediente y descripción.
 *
 * Los abogados pueden elegir su espacio personal o un estudio; quienes
 * trabajan en una aseguradora solo ven sus aseguradoras activas (RN12, 021).
 *
 * Al costado se muestra qué pasa después de crear el caso, para que el flujo
 * completo se entienda antes de empezar (022).
 *
 * Realiza: RF23; CA1 a CA3 de la funcionalidad 005 (CU18); RNF10.
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
import Icono from '../componentes/Icono.jsx'
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
      <fieldset className="opciones-tarjeta opciones-tarjeta--dos" aria-describedby={errores.tipo ? 'error-tipo' : undefined}>
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
      <div className="encabezado-pagina">
        <div>
          <h1>Nuevo caso</h1>
          <p className="encabezado-pagina__bajada">Los datos del hecho identifican el caso en el informe.</p>
        </div>
      </div>
      {error && <Aviso tipo="error">{error.message}</Aviso>}
      {espacios.length === 0 ? (
        <Aviso tipo="info">
          Para crear casos tenés que pertenecer a una aseguradora aprobada por el Administrador.
        </Aviso>
      ) : (
        <div className="dos-columnas">
          <section className="seccion dos-columnas__principal">
            <Formulario espacios={espacios} />
          </section>
          <aside className="seccion dos-columnas__lateral" aria-labelledby="titulo-despues">
            <h2 id="titulo-despues">Qué sigue</h2>
            <ol className="pasos-flujo">
              <li>
                <Icono nombre="casos" tamanio={18} />
                <span><strong>Creás el caso</strong> con los datos del hecho.</span>
              </li>
              <li>
                <Icono nombre="imagen" tamanio={18} />
                <span><strong>Cargás las imágenes.</strong> Se guarda el original y su huella SHA-256.</span>
              </li>
              <li>
                <Icono nombre="analisis" tamanio={18} />
                <span><strong>Pedís el análisis.</strong> Te avisamos por correo cuando termina.</span>
              </li>
              <li>
                <Icono nombre="documento" tamanio={18} />
                <span><strong>Descargás el informe PDF</strong> con los indicios de cada imagen.</span>
              </li>
            </ol>
          </aside>
        </div>
      )}
    </>
  )
}
