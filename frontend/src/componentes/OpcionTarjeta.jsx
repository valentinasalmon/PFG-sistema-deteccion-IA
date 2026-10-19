/**
 * Opción grande para elegir entre pocas alternativas, por ejemplo el perfil.
 *
 * Es un botón de opción (radio) nativo dentro de una etiqueta con forma de
 * tarjeta: se elige con clic, con toque o con las flechas del teclado, y el
 * lector de pantalla lo anuncia como una opción de un grupo.
 *
 * Realiza: CA1 de la funcionalidad 020; RNF10.
 */
export default function OpcionTarjeta({ nombre, valor, seleccionada, onChange, titulo, descripcion }) {
  return (
    <label className={seleccionada ? 'opcion-tarjeta opcion-tarjeta--elegida' : 'opcion-tarjeta'}>
      <input
        type="radio"
        name={nombre}
        value={valor}
        checked={seleccionada}
        onChange={onChange}
        className="opcion-tarjeta__control"
      />
      <span className="opcion-tarjeta__titulo">{titulo}</span>
      {descripcion && <span className="opcion-tarjeta__descripcion">{descripcion}</span>}
    </label>
  )
}
