/**
 * Pantalla de inicio con sesión iniciada.
 *
 * Saluda y muestra cuántos casos accesibles hay en cada estado, con accesos
 * directos al listado filtrado y a la creación de un caso. El panel completo
 * llega con la funcionalidad 013.
 *
 * Realiza: CA7 de la funcionalidad 002; resumen de casos de la 005.
 */
import { Link } from 'react-router'
import { resumenDeCasos } from '../api/casos.js'
import Aviso from '../componentes/Aviso.jsx'
import Cargando from '../componentes/Cargando.jsx'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { OPCIONES_ESTADO } from '../utilidades/casos.js'

export default function PaginaInicio() {
  const { usuario } = useSesion()
  const { datos: porEstado, error, cargando } = useDatos(resumenDeCasos)
  const total = porEstado ? Object.values(porEstado).reduce((suma, cantidad) => suma + cantidad, 0) : 0

  return (
    <>
      <h1>Hola, {usuario.nombre}</h1>
      <p className="subtitulo">
        Desde acá vas a poder crear casos, cargar imágenes y descargar los informes de análisis.
      </p>
      <section className="seccion" aria-labelledby="titulo-casos">
        <h2 id="titulo-casos">Tus casos</h2>
        {cargando && <Cargando />}
        {error && <Aviso tipo="error">{error.message}</Aviso>}
        {porEstado && total === 0 && <p>Todavía no tenés casos.</p>}
        {porEstado && total > 0 && (
          <ul className="resumen-estados">
            {OPCIONES_ESTADO.map(({ valor, texto }) => (
              <li key={valor}>
                <Link to={`/casos?estado=${valor}`}>
                  <span className="resumen-estados__cantidad">{porEstado[valor] ?? 0}</span>
                  {texto}
                </Link>
              </li>
            ))}
          </ul>
        )}
        <div className="acciones-en-linea">
          <Link to="/casos" className="boton boton--secundario">
            Ver mis casos
          </Link>
          <Link to="/casos/nuevo" className="boton">
            Nuevo caso
          </Link>
        </div>
      </section>
    </>
  )
}
