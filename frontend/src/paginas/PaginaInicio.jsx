/**
 * Pantalla de inicio con sesión iniciada.
 *
 * Por ahora saluda y anticipa lo que vendrá: el listado de casos llega con
 * la funcionalidad 005 y el panel principal con la 013.
 *
 * Realiza: CA7 de la funcionalidad 002.
 */
import { useSesion } from '../hooks/useSesion.js'

export default function PaginaInicio() {
  const { usuario } = useSesion()

  return (
    <>
      <h1>Hola, {usuario.nombre}</h1>
      <p className="subtitulo">
        Desde acá vas a poder crear casos, cargar imágenes y descargar los informes de análisis.
      </p>
      <section className="seccion seccion--vacia" aria-labelledby="titulo-casos">
        <h2 id="titulo-casos">Tus casos</h2>
        <p>Todavía no hay casos. La gestión de casos estará disponible próximamente.</p>
      </section>
    </>
  )
}
