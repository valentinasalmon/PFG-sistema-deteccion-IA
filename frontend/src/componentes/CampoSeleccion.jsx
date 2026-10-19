/**
 * Lista desplegable accesible con etiqueta, ayuda y error (RNF10).
 *
 * @param {{opciones: Array<{valor: string, texto: string}>}} propiedades
 */
import { useId } from 'react'

export default function CampoSeleccion({ etiqueta, nombre, opciones, error, ayuda, ...propiedades }) {
  const id = useId()
  const descripciones = [ayuda && `${id}-ayuda`, error && `${id}-error`].filter(Boolean).join(' ')
  return (
    <div className="campo">
      <label htmlFor={id} className="campo__etiqueta">
        {etiqueta}
      </label>
      <select
        id={id}
        name={nombre}
        className={error ? 'campo__control campo__control--error' : 'campo__control'}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={descripciones || undefined}
        {...propiedades}
      >
        {opciones.map((opcion) => (
          <option key={opcion.valor} value={opcion.valor}>
            {opcion.texto}
          </option>
        ))}
      </select>
      {ayuda && (
        <p id={`${id}-ayuda`} className="campo__ayuda">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="campo__error">
          {error}
        </p>
      )}
    </div>
  )
}
